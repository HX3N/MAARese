import time
from typing import Callable

import numpy as np
from maa.agent.agent_server import AgentServer
from maa.context import Context
from maa.custom_action import CustomAction
from maa.custom_recognition import CustomRecognition
from maa.define import Rect

from common import CHECK_INTERVAL_MS, DIALOG_NEXT_NODE, center, guard_run, load_params, log, run_handle, screencap, sleep_ms

COST_NODE = "DeployCost"
SWIPE_NODE = "DeploySwipe"
CARD_NODE = "DeployCard"
RELEASE_NODE = "DeployRelease"
CARD_ACTIVE_NODE = "DeployCardActive"
SPEED_NODE = "BattleSpeed"
DRAG_DURATION = 300
DRAG_END_HOLD = 100
DRAG_SETTLE_MS = 100
DIRECTION_DURATION = 150
DIRECTION_DISTANCE = 400
DIRECTION_OFFSETS = {
    "right": (DIRECTION_DISTANCE, 0),
    "left": (-DIRECTION_DISTANCE, 0),
    "down": (0, DIRECTION_DISTANCE),
    "up": (0, -DIRECTION_DISTANCE),
}
SCREEN_W = 1280
SCREEN_H = 720
DEPLOY_HANDLE_NODES = ["SkipPlotConfirm", "SkipPlot", DIALOG_NEXT_NODE]
DEPLOY_TIMEOUT_S = 30
DEPLOY_WAIT_MS = 500


def swipe(context: Context, begin: list[int], end: list[int], duration: int, end_hold: int = 0) -> None:
    param = {"begin": begin, "end": end, "duration": duration, "end_hold": end_hold}
    context.run_action(SWIPE_NODE, pipeline_override={SWIPE_NODE: {"action": {"type": "Swipe", "param": param}}})


def card_override(node: str, operator: str) -> dict:
    return {node: {"recognition": {"param": {"template": f"Battle/{operator}.png"}}}}


def speed_visible(context: Context, image: np.ndarray) -> bool:
    detail = context.run_recognition(SPEED_NODE, image)
    return detail is not None and detail.hit


def card_box(context: Context, image: np.ndarray, operator: str) -> Rect | None:
    detail = context.run_recognition(CARD_NODE, image, card_override(CARD_NODE, operator))
    if detail is None or not detail.hit:
        return None
    return detail.box


def poll(context: Context, wait_ms: int, check: Callable[[np.ndarray], bool]) -> bool:
    poll_end = time.monotonic() + wait_ms / 1000
    while True:
        if context.tasker.stopping:
            return False
        remaining_ms = (poll_end - time.monotonic()) * 1000
        sleep_ms(max(0, min(CHECK_INTERVAL_MS, remaining_ms)))
        if check(screencap(context)):
            return True
        if time.monotonic() >= poll_end:
            return False


def read_cost(context: Context, image: np.ndarray) -> tuple[int | None, Rect | None]:
    detail = context.run_recognition(COST_NODE, image)
    if detail is None or not detail.hit or detail.best_result is None:
        return None, None
    try:
        return int(detail.best_result.text), detail.box
    except ValueError:
        return None, None


@AgentServer.custom_recognition("DeployReady")
class DeployReady(CustomRecognition):
    PARAMS = {"optional": {"operator": None, "cost": None}, "one_of": [["operator", "cost"]]}

    def analyze(self, context: Context, argv: CustomRecognition.AnalyzeArg) -> CustomRecognition.AnalyzeResult:
        params = load_params(self, argv.custom_recognition_param)
        if params is None:
            return CustomRecognition.AnalyzeResult(box=None, detail="param error")
        operator = params["operator"]
        required = params["cost"]

        if operator is None:
            cost, cost_box = read_cost(context, argv.image)
            if cost is None or cost < required:
                return CustomRecognition.AnalyzeResult(box=None, detail=f"cost {cost}")
            return CustomRecognition.AnalyzeResult(box=cost_box, detail=f"cost {cost}")

        detail = context.run_recognition(CARD_NODE, argv.image, card_override(CARD_NODE, operator))
        if detail is None or not detail.hit:
            return CustomRecognition.AnalyzeResult(box=None, detail="no card")
        if required is None:
            return CustomRecognition.AnalyzeResult(box=detail.box, detail="card")

        cost, _ = read_cost(context, argv.image)
        if cost is not None and cost >= required:
            return CustomRecognition.AnalyzeResult(box=detail.box, detail=f"cost {cost}")

        left = max(detail.box.x - 10, 0)
        top = max(detail.box.y - 10, 0)
        right = min(detail.box.x + detail.box.w + 10, SCREEN_W)
        bottom = min(detail.box.y + detail.box.h + 10, SCREEN_H)
        active_override = card_override(CARD_ACTIVE_NODE, operator)
        active_override[CARD_ACTIVE_NODE]["recognition"]["param"]["roi"] = [left, top, right - left, bottom - top]
        active = context.run_recognition(CARD_ACTIVE_NODE, argv.image, active_override)
        if active is not None and active.hit:
            return CustomRecognition.AnalyzeResult(box=detail.box, detail="active")
        return CustomRecognition.AnalyzeResult(box=None, detail=f"cost {cost}")


def speed_returns(context: Context, wait_ms: int) -> bool:
    return poll(context, wait_ms, lambda image: speed_visible(context, image))


def card_after_deploy(context: Context, operator: str, wait_ms: int) -> tuple[bool, Rect | None]:
    seen = []

    def gone(image: np.ndarray) -> bool:
        found = card_box(context, image, operator)
        if found is None:
            return True
        seen.append(found)
        return False

    return poll(context, wait_ms, gone), seen[-1] if seen else None


def card_after_release(context: Context, operator: str, wait_ms: int) -> tuple[bool, Rect | None]:
    seen = []

    def watch(image: np.ndarray) -> bool:
        found = card_box(context, image, operator)
        if found is not None:
            seen.append(found)
        return False

    poll(context, wait_ms, watch)
    return not seen and not context.tasker.stopping, seen[-1] if seen else None


def settle(context: Context, operator: str, wait_ms: int, speed_check: bool) -> tuple[bool, Rect | None]:
    if speed_check:
        if speed_returns(context, wait_ms):
            return card_after_deploy(context, operator, wait_ms)
        if context.tasker.stopping:
            return False, None
        log("Deploy", f"{operator}: release")
    context.run_action(RELEASE_NODE)
    if speed_check and not speed_returns(context, wait_ms):
        log("Deploy", f"{operator}: no speed")
        return False, None
    return card_after_release(context, operator, wait_ms)


@AgentServer.custom_action("Deploy")
class Deploy(CustomAction):
    PARAMS = {
        "required": ["operator", "cell", "direction"],
        "optional": {"wait_ms": DEPLOY_WAIT_MS, "retry": True},
        "choices": {"direction": ["right", "left", "down", "up"]},
    }

    @guard_run
    def run(self, context: Context, argv: CustomAction.RunArg) -> bool:
        params = load_params(self, argv.custom_action_param)
        if params is None:
            return False
        operator = params["operator"]
        cell = params["cell"]
        dx, dy = DIRECTION_OFFSETS[params["direction"]]
        direction_end = [
            min(max(cell[0] + dx, 0), SCREEN_W - 1),
            min(max(cell[1] + dy, 0), SCREEN_H - 1),
        ]

        deadline = time.monotonic() + DEPLOY_TIMEOUT_S
        box = argv.box
        attempt = 0
        while time.monotonic() < deadline:
            if context.tasker.stopping:
                return False
            image = screencap(context)

            handled = run_handle(context, image, DEPLOY_HANDLE_NODES)
            if handled:
                log("Deploy", f"{operator}: handle {handled}")
                sleep_ms(CHECK_INTERVAL_MS)
                continue

            if attempt:
                log("Deploy", f"{operator}: retry")
            speed_check = speed_visible(context, image)
            swipe(context, center(box), cell, DRAG_DURATION, DRAG_END_HOLD)
            sleep_ms(DRAG_SETTLE_MS)
            swipe(context, cell, direction_end, DIRECTION_DURATION)

            placed, card = settle(context, operator, params["wait_ms"], speed_check)
            if placed:
                return True
            if context.tasker.stopping:
                return False
            if not params["retry"]:
                return True
            attempt += 1
            if attempt == 2:
                return False
            if card is not None:
                box = card
        log("Deploy", f"{operator}: timeout")
        return False
