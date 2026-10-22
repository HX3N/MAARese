import time

from maa.agent.agent_server import AgentServer
from maa.context import Context
from maa.custom_action import CustomAction
from maa.define import Rect

from common import CHECK_INTERVAL_MS, LOADING_NODE, click_center, guard_run, load_params, log, screencap, sleep_ms
from run_state import continuing, run_info

GUIDE_TEXT_MS = 500
CLICK_WAIT_MS = 1500
IN_PLACE_MARGIN = 10


def in_place_override(node: str, box: Rect) -> dict:
    x = max(box.x - IN_PLACE_MARGIN, 0)
    y = max(box.y - IN_PLACE_MARGIN, 0)
    roi = [x, y, box.w + 2 * IN_PLACE_MARGIN, box.h + 2 * IN_PLACE_MARGIN]
    return {node: {"recognition": {"param": {"roi": roi}}}}


@AgentServer.custom_action("ClickRetry")
class ClickRetry(CustomAction):
    PARAMS = {"optional": {"wait_ms": CLICK_WAIT_MS, "click": None, "pre_click": False, "until": []}}

    @guard_run
    def run(self, context: Context, argv: CustomAction.RunArg) -> bool:
        params = load_params(self, argv.custom_action_param)
        if params is None:
            return False
        wait = params["wait_ms"]
        click = params["click"]
        pre_click = params["pre_click"]
        until = params["until"]
        box = argv.box
        recheck = in_place_override(argv.node_name, box)
        for attempt in range(2):
            if context.tasker.stopping:
                return False
            if attempt:
                log("ClickRetry", f"{argv.node_name}: retry")
            if pre_click:
                click_center(context, box)
                sleep_ms(GUIDE_TEXT_MS)
            click_center(context, Rect(*click) if click else box)

            deadline = time.monotonic() + wait / 1000
            while time.monotonic() < deadline:
                if context.tasker.stopping:
                    return False
                sleep_ms(CHECK_INTERVAL_MS)
                image = screencap(context)
                loading = context.run_recognition(LOADING_NODE, image)
                if loading is not None and loading.hit:
                    return True
                for node in until:
                    done = context.run_recognition(node, image)
                    if done is not None and done.hit:
                        return True
                detail = context.run_recognition(argv.node_name, image, recheck)
                if detail is None or not detail.hit:
                    return True
                box = detail.box
        return False


@AgentServer.custom_action("StartNode")
class StartNode(CustomAction):
    PARAMS = {"required": ["node"]}

    @guard_run
    def run(self, context: Context, argv: CustomAction.RunArg) -> bool:
        params = load_params(self, argv.custom_action_param)
        if params is None:
            return False
        node = params["node"]
        if node:
            context.override_next(argv.node_name, [node])
        return True


@AgentServer.custom_action("RunLimit")
class RunLimit(CustomAction):
    PARAMS = {"required": ["max_runs"]}

    @guard_run
    def run(self, context: Context, argv: CustomAction.RunArg) -> bool:
        params = load_params(self, argv.custom_action_param)
        if params is None:
            return False
        max_runs = int(params["max_runs"])
        run, _, _ = run_info(argv.task_detail.task_id)
        if max_runs > 0 and run >= max_runs and not continuing.get(argv.task_detail.task_id):
            context.override_next(argv.node_name, [])
            log("run", f"limit reached: {run}")
        return True
