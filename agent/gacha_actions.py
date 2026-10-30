import functools
import time
from typing import Callable

import numpy as np
from maa.agent.agent_server import AgentServer
from maa.context import Context
from maa.custom_action import CustomAction
from maa.define import RecognitionDetail

import operator_match
from account_actions import save_account
from common import LOADING_NODE, LOOP_INTERVAL_MS, guard_run, hit, load_params, log, node_attach, screencap, sleep_ms
from run_state import continuing, count_scan, run_info

ACTIVE_NODE = "Gacha_Scan_Active"
RESULT_NODE = "Gacha_Scan_Result"
DETAIL_NODE = "Gacha_Scan_Detail"
ACCOUNT_NODE = "Account"
NAME_NODE = "Gacha_OperatorName"
NAME_ROIS = ([23, 349, 625, 29], [27, 669, 618, 27])
STAR_NODE = "Gacha_SixStar"
STAR_ROIS = ([23, 85, 625, 35], [27, 403, 618, 35])
RESULT_EVENTS = (
    "Node.Recognition.Starting",
    "Node.Recognition.Succeeded",
    "Node.Action.Starting",
    "Node.Action.Succeeded",
    "Node.PipelineNode.Starting",
)
BANNER_TIMEOUT_S = 60
BANNER_ICON_NODE = "Gacha_Banner_Icon"
BANNER_ICON_SELECT_NODE = "Gacha_Banner_IconSelect"
BANNER_SELECT_NODE = "Gacha_Banner_Select"
BANNER_UNSELECT_NODE = "Gacha_Banner_Unselect"
BANNER_GUIDE_NODE = "Gacha_Banner_Guide"
BANNER_MISSING_NODE = "Gacha_Banner_Missing"
BANNER_RIGHT_ARROW_NODE = "Gacha_Banner_RightArrow"
MISSING_CONFIRM = 2
BANNER_RIGHT_NODE = "Gacha_Banner_Right"
BANNER_LEFT_NODE = "Gacha_Banner_Left"
BANNER_POSITIONS = 6
ICON_SIZE = (44, 25)
SLOT_OFFSET = (66, 8)
SLOT_PITCH = 64
SLOT_SIZE = (47, 11)
SLOT_PAD = 3
CHANGE_WAIT_MS = 3000
CHANGE_DIFF = 10
TURN_RETRY = 3

@functools.cache
def get_matcher() -> operator_match.OperatorMatcher:
    return operator_match.load()


def recognize(context: Context, image: np.ndarray, node: str, roi: list[int]) -> RecognitionDetail | None:
    return context.run_recognition(node, image, {node: {"recognition": {"param": {"roi": roi}}}})


def read_names(context: Context, image: np.ndarray) -> list[str]:
    texts = []
    for roi in NAME_ROIS:
        detail = recognize(context, image, NAME_NODE, roi)
        if detail is not None:
            texts += [result.text for result in detail.all_results]
    return texts


def count_six_star_icons(context: Context, image: np.ndarray) -> int:
    count = 0
    for roi in STAR_ROIS:
        detail = recognize(context, image, STAR_NODE, roi)
        if detail is not None:
            count += len(detail.filtered_results)
    return count


def red(text: str) -> str:
    return f"[color:#FF5555]{text}[/color]"


def green(text: str) -> str:
    return f"[color:#3FBF6F]{text}[/color]"


def result_lines(
    run: int, count: int, names: list[str], pulls: int, elapsed_s: int, stamp: str
) -> tuple[list[str], list[str]]:
    minutes, seconds = divmod(elapsed_s, 60)
    head = f"★ 헤드헌팅 {pulls}회 · 6성 "
    summary = [
        green(f"★ 리세 결과 · {run}회차 · {minutes}분 {seconds}초"),
        red(f"{head}{count}개") if count > 0 else green(f"{head}0개"),
    ]
    detail = [red("★ " + " · ".join(names))] if names else []
    detail.append(green(f"★ 기록 완료 · {stamp}" if stamp else "★ 기록 없음 · 조건 미달"))
    return summary, detail


@AgentServer.custom_action("GachaOperatorScan")
class GachaOperatorScan(CustomAction):
    PARAMS = {"required": ["min_six"]}

    @guard_run
    def run(self, context: Context, argv: CustomAction.RunArg) -> bool:
        params = load_params(self, argv.custom_action_param)
        if params is None:
            return False
        min_six = params["min_six"]
        image = screencap(context)
        six_stars = []
        for text in read_names(context, image):
            found = get_matcher().match(text)
            log("GachaOperatorScan", f"ocr: {text!r} -> {found}")
            if found is not None and found[1] == 6:
                six_stars.append(found[0])
        icons = count_six_star_icons(context, image)
        count = max(len(six_stars), icons)

        log("GachaOperatorScan", f"six stars: {count} (names {len(six_stars)} {six_stars}, icons {icons})")
        stamp = ""
        if count >= min_six:
            suffix = f" ({', '.join(six_stars)})" if six_stars else ""
            stamp = save_account(context, folder=f"6성_{count}개", suffix=suffix)
        task_id = argv.task_detail.task_id
        run, elapsed, pulls = run_info(task_id)
        summary, detail = result_lines(run, count, six_stars, pulls, elapsed, stamp)
        context.override_pipeline(
            {
                RESULT_NODE: {"focus": dict(zip(RESULT_EVENTS, summary))},
                DETAIL_NODE: {"focus": dict(zip(RESULT_EVENTS, detail))},
            }
        )
        active = context.get_node_data(ACTIVE_NODE)
        first = count_scan(task_id) == 1
        go_on = first and active is not None and active.get("enabled", True) and count >= int(node_attach(context, ACTIVE_NODE, "continue_min_six"))
        continuing[task_id] = go_on
        context.override_next(DETAIL_NODE, [ACTIVE_NODE] if go_on else [ACCOUNT_NODE])
        return bool(stamp) if count >= min_six else True


def changed(before: np.ndarray, after: np.ndarray) -> bool:
    return np.abs(before.astype(np.int16) - after.astype(np.int16)).mean() > CHANGE_DIFF


def settled(context: Context) -> np.ndarray:
    deadline = time.monotonic() + CHANGE_WAIT_MS / 1000
    image = screencap(context)
    while time.monotonic() < deadline:
        sleep_ms(LOOP_INTERVAL_MS)
        current = screencap(context)
        if not changed(image, current):
            return current
        image = current
    return image


def roi_hit(context: Context, image: np.ndarray, node: str, roi: list[int]) -> bool:
    return hit(context, node, image, {node: {"recognition": {"param": {"roi": roi}}}}) is not None


def slot_roi(anchor: tuple[int, int], position: int) -> list[int]:
    x = anchor[0] + SLOT_OFFSET[0] + SLOT_PITCH * (position - 1) - SLOT_PAD
    y = anchor[1] + SLOT_OFFSET[1] - SLOT_PAD
    return [x, y, SLOT_SIZE[0] + 2 * SLOT_PAD, SLOT_SIZE[1] + 2 * SLOT_PAD]


def find_anchor(context: Context, image: np.ndarray, icon_node: str, first_slot_nodes: tuple[str, ...]) -> tuple[int, int] | None:
    detail = hit(context, icon_node, image)
    if detail is None:
        return None
    for result in detail.filtered_results:
        anchor = (result.box[0], result.box[1])
        if any(roi_hit(context, image, node, slot_roi(anchor, 1)) for node in first_slot_nodes):
            return anchor
    return None


def read_position(context: Context, image: np.ndarray) -> tuple[int, tuple[int, int]] | None:
    anchor = find_anchor(context, image, BANNER_ICON_NODE, (BANNER_SELECT_NODE, BANNER_UNSELECT_NODE))
    if anchor is not None:
        for position in range(1, BANNER_POSITIONS + 1):
            if roi_hit(context, image, BANNER_SELECT_NODE, slot_roi(anchor, position)):
                return position, anchor
        return None
    anchor = find_anchor(context, image, BANNER_ICON_SELECT_NODE, (BANNER_UNSELECT_NODE,))
    return (0, anchor) if anchor is not None else None


def banner_count(context: Context, image: np.ndarray, anchor: tuple[int, int], selected: int) -> int:
    count = 0
    while count < BANNER_POSITIONS:
        position = count + 1
        if position != selected and not roi_hit(context, image, BANNER_UNSELECT_NODE, slot_roi(anchor, position)):
            break
        count = position
    return count


def banner_label(position: int) -> str:
    return "공개모집" if position == 0 else str(position)


def list_line(context: Context, image: np.ndarray, at: int, anchor: tuple[int, int]) -> str:
    labels = [banner_label(position) for position in range(banner_count(context, image, anchor, at) + 1)]
    labels[at] = f"[{labels[at]}]"
    return "배너 목록 · " + " · ".join(labels)


def show_guide(context: Context, lines: list[str]) -> None:
    context.run_task(BANNER_GUIDE_NODE, {BANNER_GUIDE_NODE: {"focus": dict(zip(RESULT_EVENTS, lines))}})


def selected_at(context: Context, image: np.ndarray, anchor: tuple[int, int], position: int) -> bool:
    if position == 0:
        roi = [anchor[0] - SLOT_PAD, anchor[1] - SLOT_PAD, ICON_SIZE[0] + 2 * SLOT_PAD, ICON_SIZE[1] + 2 * SLOT_PAD]
        return roi_hit(context, image, BANNER_ICON_SELECT_NODE, roi)
    return roi_hit(context, image, BANNER_SELECT_NODE, slot_roi(anchor, position))


def turn(context: Context, node: str, moved: Callable[[np.ndarray], bool]) -> bool:
    for _ in range(TURN_RETRY):
        if context.tasker.stopping:
            return False
        context.run_action(node)
        deadline = time.monotonic() + CHANGE_WAIT_MS / 1000
        while time.monotonic() < deadline:
            sleep_ms(LOOP_INTERVAL_MS)
            if moved(screencap(context)):
                return True
        log("SelectBanner", "click ignored, retrying")
    return False


def stop_missing(context: Context, node: str, position: int) -> None:
    content = f"[color:#FFD700]⚠ {position}번 배너 없음, 작업 종료[/color]"
    focus = {"Node.Recognition.Succeeded": {"content": content, "display": ["log", "toast"]}}
    context.override_pipeline({BANNER_MISSING_NODE: {"focus": focus}})
    context.override_next(node, [BANNER_MISSING_NODE])


@AgentServer.custom_action("SelectBanner")
class SelectBanner(CustomAction):
    PARAMS = {"required": ["position"], "choices": {"position": [1, 2, 3, 4, 5, 6]}}

    @guard_run
    def run(self, context: Context, argv: CustomAction.RunArg) -> bool:
        params = load_params(self, argv.custom_action_param)
        if params is None:
            return False
        position = params["position"]

        guided = False
        blocked = 0
        deadline = time.monotonic() + BANNER_TIMEOUT_S
        while time.monotonic() < deadline:
            if context.tasker.stopping:
                return False
            image = settled(context)
            if hit(context, LOADING_NODE, image):
                sleep_ms(LOOP_INTERVAL_MS)
                continue
            current = read_position(context, image)
            if current is None:
                log("SelectBanner", f"{position}: bar not read")
                sleep_ms(LOOP_INTERVAL_MS)
                continue
            at, anchor = current
            if not guided:
                lines = [list_line(context, image, at, anchor)]
                if at != position:
                    lines.append(f"배너 이동 · [{banner_label(at)}] > [{banner_label(position)}]")
                show_guide(context, lines)
                guided = True
            if at == position:
                log("SelectBanner", f"{position}: selected")
                return True

            log("SelectBanner", f"{position}: at {at}, moving")
            node = BANNER_RIGHT_NODE if at < position else BANNER_LEFT_NODE
            if turn(context, node, lambda after: not selected_at(context, after, anchor, at)):
                blocked = 0
                continue
            count = banner_count(context, image, anchor, at)
            if at < position and at == count and not hit(context, BANNER_RIGHT_ARROW_NODE, screencap(context)):
                blocked += 1
                log("SelectBanner", f"{position}: end of {count} banners ({blocked}/{MISSING_CONFIRM})")
                if blocked >= MISSING_CONFIRM:
                    stop_missing(context, argv.node_name, position)
                    return True
            else:
                blocked = 0

        log("SelectBanner", f"{position}: timeout")
        return False
