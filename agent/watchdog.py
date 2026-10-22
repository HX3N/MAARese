import re
import time

from maa.agent.agent_server import AgentServer
from maa.context import Context, ContextEventSink
from maa.event_sink import NotificationType

from common import log, node_attach
from run_state import PROGRESS_NODE, count_pull, runs

RESTART_NODES = ["GameDownReset"]
NON_LOOP_MARKS = ("◆", "⚠", "★")
COLOR_TAG = re.compile(r"^\[color:#[0-9a-fA-F]{6}\]")

loops: dict[int, dict] = {}


def next_names(entries: list) -> list[str]:
    names = []
    for entry in entries:
        if isinstance(entry, str):
            names.append(entry)
            continue
        name = entry["name"]
        if entry.get("jump_back"):
            name = f"[JumpBack]{name}"
        if entry.get("anchor"):
            name = f"[Anchor]{name}"
        names.append(name)
    return names


def loop_limit_s(context: Context) -> int:
    return int(node_attach(context, RESTART_NODES[0], "loop_limit_min")) * 60


def restart_loop(context: Context, loop: dict, names: list[str]) -> None:
    for name in names:
        data = context.get_node_data(name)
        if data is None or name in loop["saved"]:
            continue
        loop["saved"][name] = {
            "next": next_names(data.get("next", [])),
            "on_error": next_names(data.get("on_error", [])),
        }
        context.override_pipeline({name: {"next": RESTART_NODES, "on_error": RESTART_NODES}})


def restore_loop(context: Context, loop: dict) -> None:
    for name, saved in loop["saved"].items():
        restored = {"next": saved["next"]}
        if saved["on_error"]:
            restored["on_error"] = saved["on_error"]
        context.override_pipeline({name: restored})
    loop["saved"] = {}
    loop["start"] = time.monotonic()


@AgentServer.context_sink()
class WatchSink(ContextEventSink):
    def on_node_pipeline_node(
        self,
        context: Context,
        noti_type: NotificationType,
        detail: ContextEventSink.NodePipelineNodeDetail,
    ) -> None:
        if noti_type != NotificationType.Starting:
            return

        name = detail.name
        state = runs.get(detail.task_id)
        if state is not None:
            count_pull(state, name)

        loop = loops.setdefault(detail.task_id, {"name": "", "start": time.monotonic(), "limit": 0, "saved": {}})
        if name in RESTART_NODES:
            if loop["saved"]:
                restore_loop(context, loop)
            return

        if isinstance(detail.focus, str) and not COLOR_TAG.sub("", detail.focus).startswith(NON_LOOP_MARKS):
            if name != loop["name"]:
                if loop["saved"]:
                    restore_loop(context, loop)
                loop["name"] = name
                loop["start"] = time.monotonic()
                loop["limit"] = loop_limit_s(context)
        elif name == PROGRESS_NODE:
            loop["start"] = time.monotonic()

        stuck = int(time.monotonic() - loop["start"])
        if loop["name"] and stuck > loop["limit"]:
            if not loop["saved"]:
                log("watchdog", f"loop {loop['name']} stuck {stuck}s, restarting")
            restart_loop(context, loop, list(dict.fromkeys([loop["name"], name])))
