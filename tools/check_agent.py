import ast
import json
import re
import sys
from pathlib import Path

from maa.resource import Resource

ROOT = Path(__file__).resolve().parent.parent
REGISTERED = {
    "custom_action": re.compile(r"@AgentServer\.custom_action\(\s*[\"']([^\"']+)[\"']"),
    "custom_recognition": re.compile(r"@AgentServer\.custom_recognition\(\s*[\"']([^\"']+)[\"']"),
}
SINK = re.compile(r"@AgentServer\.context_sink\(")
PARAM_KEY = {"custom_action": "custom_action_param", "custom_recognition": "custom_recognition_param"}
LIST_NODE_KEYS = ("handle", "until")
STR_NODE_KEYS = ("done", "node")


def registered_names(sources: dict[str, str]) -> dict[str, set[str]]:
    return {
        kind: {name for source in sources.values() for name in pattern.findall(source)}
        for kind, pattern in REGISTERED.items()
    }


def parse_specs(sources: dict[str, str]) -> dict[str, dict[str, dict]]:
    specs: dict[str, dict[str, dict]] = {kind: {} for kind in REGISTERED}
    for source in sources.values():
        for cls in ast.walk(ast.parse(source)):
            if not isinstance(cls, ast.ClassDef):
                continue
            kinds = []
            for deco in cls.decorator_list:
                if (
                    isinstance(deco, ast.Call)
                    and isinstance(deco.func, ast.Attribute)
                    and deco.func.attr in REGISTERED
                    and deco.args
                    and isinstance(deco.args[0], ast.Constant)
                ):
                    kinds.append((deco.func.attr, deco.args[0].value))
            for stmt in cls.body:
                if (
                    kinds
                    and isinstance(stmt, ast.Assign)
                    and any(isinstance(t, ast.Name) and t.id == "PARAMS" for t in stmt.targets)
                    and isinstance(stmt.value, ast.Dict)
                ):
                    spec = parse_spec(stmt.value)
                    for kind, name in kinds:
                        specs[kind][name] = spec
    return specs


def parse_spec(node: ast.Dict) -> dict:
    spec: dict = {"required": [], "optional": {}, "choices": {}, "one_of": []}
    for key, value in zip(node.keys, node.values):
        if not isinstance(key, ast.Constant) or key.value not in spec:
            continue
        if key.value == "optional" and isinstance(value, ast.Dict):
            spec["optional"] = {
                k.value: isinstance(v, ast.Constant) and v.value is None
                for k, v in zip(value.keys, value.values)
                if isinstance(k, ast.Constant)
            }
        else:
            spec[key.value] = ast.literal_eval(value)
    return spec


def is_placeholder(value: object) -> bool:
    return isinstance(value, str) and "{" in value


def node_refs(params: dict) -> list[tuple[str, str]]:
    refs = []
    for key in LIST_NODE_KEYS:
        if isinstance(params.get(key), list):
            refs += [(key, name) for name in params[key] if isinstance(name, str)]
    for key in STR_NODE_KEYS:
        if isinstance(params.get(key), str) and params[key]:
            refs.append((key, params[key]))
    if isinstance(params.get("branches"), dict):
        for branch, target in params["branches"].items():
            refs.append(("branches", branch))
            if isinstance(target, str):
                refs.append(("branches", target))
    return refs


def check_params(spec: dict, params: object, where: str, kind: str, name: str) -> list[str]:
    label = f"{where}: {kind} '{name}'"
    if isinstance(params, str):
        try:
            params = json.loads(params) if params else {}
        except json.JSONDecodeError as e:
            return [f"{label}: invalid json param ({e})"]
    if params is None:
        params = {}
    if not isinstance(params, dict):
        return [f"{label}: param must be an object"]
    required, optional = spec["required"], spec["optional"]
    problems = []
    unknown = [key for key in params if key not in required and key not in optional]
    if unknown:
        problems.append(f"{label}: unknown param key {unknown}")
    missing = [key for key in required if key not in params]
    if missing:
        problems.append(f"{label}: missing required param {missing}")
    for key, values in spec["choices"].items():
        if key in params and not is_placeholder(params[key]) and params[key] not in values:
            problems.append(f"{label}: param {key}={params[key]!r} not in {values}")
    for group in spec["one_of"]:
        if not any(params[key] is not None if key in params else (key in optional and not optional[key]) for key in group):
            problems.append(f"{label}: one of {group} is required")
    return problems


def collect_params(data: object, where: str, found: list[tuple[str, str, object, str]]):
    if isinstance(data, dict):
        for kind, key in PARAM_KEY.items():
            if isinstance(data.get(kind), str) and data[kind] and key in data:
                found.append((kind, data[kind], data[key], where))
        for value in data.values():
            collect_params(value, where, found)
    elif isinstance(data, list):
        for item in data:
            collect_params(item, where, found)


def collect_partial(data: object, node_data: object, where: str, found: list[tuple[str, str, object, str]]):
    if isinstance(data, dict):
        for kind, key in PARAM_KEY.items():
            if isinstance(data.get(kind), str) and data[kind] and key in data:
                found.append((kind, data[kind], data[key], where))
            elif key in data:
                names: list[tuple[str, str, object, str]] = []
                collect_params(node_data, where, names)
                base = next((n for n in names if n[0] == kind), None)
                if base is not None and isinstance(data[key], dict) and isinstance(base[2], dict):
                    found.append((kind, base[1], {**base[2], **data[key]}, where))
                elif base is not None:
                    found.append((kind, base[1], data[key], where))
        for value in data.values():
            collect_partial(value, node_data, where, found)
    elif isinstance(data, list):
        for item in data:
            collect_partial(item, node_data, where, found)


def interface_overrides(interface: dict) -> list[tuple[str, dict]]:
    overrides = []
    for task in interface.get("task", []):
        overrides.append((f"task '{task['name']}'", task.get("pipeline_override", {})))
    for key, option in interface.get("option", {}).items():
        for case in option.get("cases", []):
            overrides.append((f"option '{key}' case '{case['name']}'", case.get("pipeline_override", {})))
        overrides.append((f"option '{key}'", option.get("pipeline_override", {})))
    return overrides


def gather_params(nodes: dict[str, object], interface: dict) -> list[tuple[str, str, object, str]]:
    found: list[tuple[str, str, object, str]] = []
    for node, data in nodes.items():
        collect_params(data, f"node '{node}'", found)
    for where, override in interface_overrides(interface):
        for node, patch in override.items():
            collect_partial(patch, nodes.get(node), f"{where} node '{node}'", found)
    return found


def check_all_params(
    specs: dict[str, dict[str, dict]], nodes: dict[str, object], interface: dict
) -> list[str]:
    problems = []
    seen = set()
    for kind, name, params, where in gather_params(nodes, interface):
        if name not in specs[kind]:
            continue
        key = (where, kind, name, json.dumps(params, sort_keys=True, default=str))
        if key in seen:
            continue
        seen.add(key)
        problems += check_params(specs[kind][name], params, where, kind, name)
    return problems


def check_node_refs(nodes: dict[str, object], interface: dict, node_names: set[str]) -> list[str]:
    problems = []
    for kind, name, params, where in gather_params(nodes, interface):
        if isinstance(params, str):
            try:
                params = json.loads(params)
            except json.JSONDecodeError:
                continue
        if not isinstance(params, dict):
            continue
        for key, ref in node_refs(params):
            if ref not in node_names and not is_placeholder(ref):
                problems.append(f"{where}: {kind} '{name}' param {key} refers to missing node '{ref}'")
    return problems


def check_main_imports(sources: dict[str, str], main_source: str) -> list[str]:
    imported = set()
    for func in ast.walk(ast.parse(main_source)):
        if isinstance(func, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for stmt in ast.walk(func):
                if isinstance(stmt, ast.Import):
                    imported |= {alias.name for alias in stmt.names}
    registering = {
        module
        for module, source in sources.items()
        if module != "main" and (SINK.search(source) or any(p.search(source) for p in REGISTERED.values()))
    }
    problems = [f"agent/main.py: registering module '{m}' is not imported" for m in sorted(registering - imported)]
    problems += [f"agent/main.py: imports '{m}' but agent/{m}.py does not exist" for m in sorted(imported - sources.keys())]
    return problems


def check_node_constants(sources: dict[str, str], node_names: set[str]) -> list[str]:
    problems = []
    for module, source in sources.items():
        for stmt in ast.parse(source).body:
            if not isinstance(stmt, ast.Assign):
                continue
            for target in stmt.targets:
                if not isinstance(target, ast.Name):
                    continue
                if target.id.endswith("_NODE"):
                    values = [stmt.value]
                elif target.id.endswith("_NODES"):
                    if isinstance(stmt.value, (ast.List, ast.Tuple)):
                        values = stmt.value.elts
                    elif isinstance(stmt.value, ast.Dict):
                        names = stmt.value.values
                        strings = all(isinstance(v, ast.Constant) and isinstance(v.value, str) for v in names)
                        values = names if strings else stmt.value.keys
                    else:
                        continue
                else:
                    continue
                for value in values:
                    if isinstance(value, ast.Constant) and isinstance(value.value, str) and value.value not in node_names:
                        problems.append(f"agent/{module}.py: {target.id} refers to missing node '{value.value}'")
    return problems


def referenced_names(node, where: str, found: dict[str, dict[str, str]]):
    if isinstance(node, dict):
        for key, value in node.items():
            if key in REGISTERED and isinstance(value, str) and value:
                found[key].setdefault(value, where)
            else:
                referenced_names(value, where, found)
    elif isinstance(node, list):
        for item in node:
            referenced_names(item, where, found)


def find_references(nodes: dict[str, object], interface: dict) -> dict[str, dict[str, str]]:
    found: dict[str, dict[str, str]] = {kind: {} for kind in REGISTERED}
    for node, data in nodes.items():
        referenced_names(data, f"node '{node}'", found)
    for where, override in interface_overrides(interface):
        referenced_names(override, where, found)
    return found


def check_registered(found: dict[str, dict[str, str]], registered: dict[str, set[str]]) -> list[str]:
    return [
        f"{where}: {kind} '{name}' is not registered in agent/*.py"
        for kind, names in found.items()
        for name, where in names.items()
        if name not in registered[kind]
    ]


def unused_warnings(found: dict[str, dict[str, str]], registered: dict[str, set[str]]) -> list[str]:
    return [
        f"warning: {kind} '{name}' is registered but not used in resource or interface.json"
        for kind, names in registered.items()
        for name in sorted(names - found[kind].keys())
    ]


def main() -> int:
    resource_dir = ROOT / "resource"
    resource = Resource()
    if not resource.post_pipeline(resource_dir / "pipeline").wait().succeeded:
        print(f"failed to load pipeline: {resource_dir / 'pipeline'}")
        return 1
    if not resource.post_image(resource_dir / "image").wait().succeeded:
        print(f"failed to load images: {resource_dir / 'image'}")
        return 1

    nodes = {node: resource.get_node_data(node) for node in resource.node_list}
    interface = json.loads((ROOT / "interface.json").read_text(encoding="utf-8"))
    sources = {p.stem: p.read_text(encoding="utf-8") for p in (ROOT / "agent").glob("*.py")}

    found = find_references(nodes, interface)
    registered = registered_names(sources)
    node_names = set(nodes)
    problems = (
        check_registered(found, registered)
        + check_all_params(parse_specs(sources), nodes, interface)
        + check_node_refs(nodes, interface, node_names)
        + check_main_imports(sources, sources["main"])
        + check_node_constants(sources, node_names)
    )
    for problem in problems:
        print(problem)
    for warning in unused_warnings(found, registered):
        print(warning)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
