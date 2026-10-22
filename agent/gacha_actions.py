import functools
import time

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
BANNER_RECRUIT_NODE = "Gacha_Banner_Recruit"
BANNER_NEWBIE_NODE = "Gacha_Banner_Newbie"
BANNER_LIMITED_NODE = "Gacha_Banner_Limited"
BANNER_RIGHT_NODE = "Gacha_Banner_Right"
BANNER_LEFT_NODE = "Gacha_Banner_Left"
BANNER_TEN_NODE = "Gacha_PullTen_Click"
BANNER_STEPS = {"초보자": 1, "한정": 2, "통상": 3}
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


def banner_kind(context: Context, image: np.ndarray) -> str | None:
    if hit(context, BANNER_RECRUIT_NODE, image):
        return "공개모집"
    if hit(context, BANNER_NEWBIE_NODE, image):
        return "초보자"
    if not hit(context, BANNER_TEN_NODE, image):
        return None
    if hit(context, BANNER_LIMITED_NODE, image):
        return "한정"
    return "통상"


def turn_right(context: Context, before: np.ndarray) -> bool:
    for _ in range(TURN_RETRY):
        if context.tasker.stopping:
            return False
        context.run_action(BANNER_RIGHT_NODE)
        deadline = time.monotonic() + CHANGE_WAIT_MS / 1000
        while time.monotonic() < deadline:
            sleep_ms(LOOP_INTERVAL_MS)
            if changed(before, screencap(context)):
                return True
        log("SelectBanner", "click ignored, retrying")
    return False


def select_by_position(context: Context, banner: str, deadline: float) -> bool:
    log("SelectBanner", f"{banner}: not found, counting from 공개모집")
    while not hit(context, BANNER_RECRUIT_NODE, settled(context)):
        if context.tasker.stopping or time.monotonic() >= deadline:
            return False
        context.run_action(BANNER_LEFT_NODE)
    for _ in range(BANNER_STEPS[banner]):
        if not turn_right(context, settled(context)):
            log("SelectBanner", f"{banner}: cannot move right")
            return False
    log("SelectBanner", f"{banner}: selected by position")
    return True


@AgentServer.custom_action("SelectBanner")
class SelectBanner(CustomAction):
    PARAMS = {"required": ["banner"], "choices": {"banner": ["초보자", "한정", "통상"]}}

    @guard_run
    def run(self, context: Context, argv: CustomAction.RunArg) -> bool:
        params = load_params(self, argv.custom_action_param)
        if params is None:
            return False
        banner = params["banner"]

        deadline = time.monotonic() + BANNER_TIMEOUT_S
        while time.monotonic() < deadline:
            if context.tasker.stopping:
                return False
            image = settled(context)
            if hit(context, LOADING_NODE, image):
                sleep_ms(LOOP_INTERVAL_MS)
                continue
            kind = banner_kind(context, image)
            if kind == banner:
                log("SelectBanner", f"{banner}: selected")
                return True

            log("SelectBanner", f"{banner}: at {kind or '?'}, moving right")
            if not turn_right(context, image):
                return select_by_position(context, banner, deadline)

        log("SelectBanner", f"{banner}: timeout")
        return False
