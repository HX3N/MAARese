import json
import sys
from pathlib import Path

from maa.resource import Resource


def collect_overrides(interface: dict):
    for task in interface.get("task", []):
        yield f"task '{task['name']}'", task.get("pipeline_override", {})
    for key, option in interface.get("option", {}).items():
        for case in option.get("cases", []):
            yield f"option '{key}' case '{case['name']}'", case.get("pipeline_override", {})


def collect_recognition_refs(recognition):
    if not isinstance(recognition, dict):
        return
    param = recognition.get("param", {})
    for key in ("any_of", "all_of"):
        for item in param.get(key, []):
            if isinstance(item, str):
                yield item
            else:
                yield from collect_recognition_refs(item.get("recognition"))


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: check_resource.py <resource_dir>")
        return 1

    resource_dir = Path(sys.argv[1]).resolve()
    problems = []

    resource = Resource()
    if not resource.post_pipeline(resource_dir / "pipeline").wait().succeeded:
        problems.append(f"failed to load pipeline: {resource_dir / 'pipeline'}")
    if not resource.post_image(resource_dir / "image").wait().succeeded:
        problems.append(f"failed to load images: {resource_dir / 'image'}")

    interface = json.loads(
        (resource_dir.parent / "interface.json").read_text(encoding="utf-8")
    )
    nodes = set(resource.node_list)
    for where, override in collect_overrides(interface):
        for node in override:
            if node not in nodes:
                problems.append(f"{where}: pipeline_override node '{node}' not found")

    for path in sorted((resource_dir / "pipeline").rglob("*.json")):
        for name, node in json.loads(path.read_text(encoding="utf-8")).items():
            for ref in collect_recognition_refs(node.get("recognition")):
                if ref not in nodes:
                    problems.append(f"{name}: recognition reference '{ref}' not found")

    for problem in problems:
        print(problem)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
