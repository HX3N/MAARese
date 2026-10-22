import re
import time

from maa.agent.agent_server import AgentServer
from maa.context import Context
from maa.custom_action import CustomAction
from maa.define import RecognitionDetail

from common import (
    DIALOG_NEXT_NODE,
    LOOP_INTERVAL_MS,
    click_center,
    guard_run,
    hit,
    load_params,
    log,
    run_handle,
    screencap,
    sleep_ms,
)

SELECT_HANDLE_NODES = [DIALOG_NEXT_NODE]
SELECT_TIMEOUT_S = 60
STAGE_NAME_NODE = "StageName"
STAGE_TEMPLATE_NODE = "StageTemplate"
STAGE_CODES = tuple(f"0-{i}" for i in range(1, 12)) + tuple(f"TR-{i}" for i in range(1, 8))
STAGE_TEMPLATE_MARGIN = 10
OPERATION_START_NODE = "OperationStart"
STAGE_DESELECT_NODE = "StageDeselect"
STAGE_MAP_SWIPE_NODE = "StageMapSwipe"
QUICK_RESET_NODE = "QuickSelectReset"
OPERATOR_LINE_NODES = ("OperatorNameUpper", "OperatorNameLower")
OPERATOR_DETAIL_NODE = "OperatorDetailName"
QUICK_SWIPE_NODE = "QuickSelectSwipe"
SELECT_WAIT_MS = 1500


def wait_hit(context: Context, node: str, wait_ms: int, override: dict | None = None) -> RecognitionDetail | None:
    deadline = time.monotonic() + wait_ms / 1000
    while time.monotonic() < deadline:
        if context.tasker.stopping:
            return None
        sleep_ms(LOOP_INTERVAL_MS)
        detail = hit(context, node, screencap(context), override)
        if detail:
            return detail
    return None


def stage_template_override(stage: str, roi: list[int] | None = None) -> dict:
    param = {"template": f"Public/Stage/{stage}.png"}
    if roi:
        param["roi"] = roi
    return {STAGE_TEMPLATE_NODE: {"recognition": {"param": param}}}


def find_stage_template(context: Context, image, stage: str) -> RecognitionDetail | None:
    found = hit(context, STAGE_TEMPLATE_NODE, image, stage_template_override(stage))
    if not found:
        return None
    x, y, w, h = found.box
    m = STAGE_TEMPLATE_MARGIN
    roi = [x - m, y - m, w + 2 * m, h + 2 * m]
    score = found.best_result.score
    for other in STAGE_CODES:
        if other == stage:
            continue
        rival = hit(context, STAGE_TEMPLATE_NODE, image, stage_template_override(other, roi))
        if rival and rival.best_result.score > score:
            log("SelectStage", f"{stage}: template {score:.3f} rejected, {other} {rival.best_result.score:.3f}")
            return None
    return found


@AgentServer.custom_action("SelectStage")
class SelectStage(CustomAction):
    PARAMS = {"required": ["stage"]}

    @guard_run
    def run(self, context: Context, argv: CustomAction.RunArg) -> bool:
        params = load_params(self, argv.custom_action_param)
        if params is None:
            return False
        stage = params["stage"]
        name_override = {STAGE_NAME_NODE: {"recognition": {"param": {"expected": f"^{re.escape(stage)}$"}}}}

        deadline = time.monotonic() + SELECT_TIMEOUT_S
        clicked = False
        while time.monotonic() < deadline:
            if context.tasker.stopping:
                return False
            image = screencap(context)

            handled = run_handle(context, image, SELECT_HANDLE_NODES)
            if handled:
                log("SelectStage", f"{stage}: handle {handled}")
                sleep_ms(LOOP_INTERVAL_MS)
                continue

            if hit(context, OPERATION_START_NODE, image):
                if clicked:
                    log("SelectStage", f"{stage}: selected")
                    return True
                log("SelectStage", f"{stage}: other stage selected, deselecting")
                context.run_action(STAGE_DESELECT_NODE)
                continue

            name = hit(context, STAGE_NAME_NODE, image, name_override)
            if not name:
                name = find_stage_template(context, image, stage)
            if name:
                click_center(context, name.box)
                if wait_hit(context, OPERATION_START_NODE, SELECT_WAIT_MS):
                    log("SelectStage", f"{stage}: selected")
                    return True
                clicked = True
                continue

            context.run_action(STAGE_MAP_SWIPE_NODE)
            sleep_ms(LOOP_INTERVAL_MS)

        log("SelectStage", f"{stage}: timeout")
        return False


@AgentServer.custom_action("SelectOperator")
class SelectOperator(CustomAction):
    PARAMS = {"required": ["operator_name"]}

    @guard_run
    def run(self, context: Context, argv: CustomAction.RunArg) -> bool:
        params = load_params(self, argv.custom_action_param)
        if params is None:
            return False
        name = params["operator_name"]
        line_override = {"recognition": {"param": {"expected": f"^{re.escape(name)}$"}}}
        detail_override = {"recognition": {"param": {"expected": re.escape(name)}}}

        deadline = time.monotonic() + SELECT_TIMEOUT_S
        while time.monotonic() < deadline:
            if context.tasker.stopping:
                return False
            image = screencap(context)

            handled = run_handle(context, image, SELECT_HANDLE_NODES)
            if handled:
                log("SelectOperator", f"{name}: handle {handled}")
                sleep_ms(LOOP_INTERVAL_MS)
                continue

            if not hit(context, QUICK_RESET_NODE, image):
                sleep_ms(LOOP_INTERVAL_MS)
                continue

            found = None
            for node in OPERATOR_LINE_NODES:
                found = hit(context, node, image, {node: line_override})
                if found:
                    break
            if found:
                click_center(context, found.box)
                if wait_hit(context, OPERATOR_DETAIL_NODE, SELECT_WAIT_MS, {OPERATOR_DETAIL_NODE: detail_override}):
                    log("SelectOperator", f"{name}: selected")
                    return True
                log("SelectOperator", f"{name}: detail mismatch, retrying")
                continue

            context.run_action(QUICK_SWIPE_NODE)
            sleep_ms(LOOP_INTERVAL_MS)

        log("SelectOperator", f"{name}: timeout")
        return False
