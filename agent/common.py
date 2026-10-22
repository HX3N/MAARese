import functools
import json
import re
import time
from typing import Callable

import numpy as np
from maa.context import Context
from maa.custom_action import CustomAction
from maa.define import RecognitionDetail, Rect

LOADING_NODE = "Loading"
PACKAGE = "com.YoStarKR.Arknights"
WHITESPACE = re.compile(r"\s+")
CHECK_INTERVAL_MS = 200
LOOP_INTERVAL_MS = 300
DIALOG_NEXT_NODE = "DialogNext"


def log(tag: str, message: str) -> None:
    print(f"[{tag}] {message}", flush=True)


def sleep_ms(ms: float) -> None:
    time.sleep(ms / 1000)


def center(box: Rect) -> list[int]:
    return [box.x + box.w // 2, box.y + box.h // 2]


def screencap(context: Context) -> np.ndarray:
    image = context.tasker.controller.post_screencap().wait().get()
    if image is None:
        raise RuntimeError("screencap returned no image")
    return image


def hit(context: Context, node: str, image: np.ndarray, override: dict | None = None) -> RecognitionDetail | None:
    detail = context.run_recognition(node, image, override or {})
    return detail if detail is not None and detail.hit else None


def click_center(context: Context, box: Rect) -> None:
    x, y = center(box)
    context.tasker.controller.post_click(x, y).wait()


def run_handle(context: Context, image: np.ndarray, nodes: list[str]) -> str | None:
    for node in nodes:
        detail = hit(context, node, image)
        if detail:
            context.run_action(node, box=detail.box)
            return node
    return None


def node_attach(context: Context, node: str, key: str) -> object:
    data = context.get_node_data(node)
    if data is None:
        raise KeyError(f"node not found: {node}")
    attach = data.get("attach")
    if not attach:
        raise KeyError(f"attach missing in node: {node}")
    if key not in attach:
        raise KeyError(f"attach key missing in node {node}: {key}")
    return attach[key]


def load_params(owner: object, raw: str) -> dict | None:
    name = type(owner).__name__
    spec = type(owner).PARAMS
    required = spec.get("required", [])
    optional = spec.get("optional", {})

    def fail(reason: str) -> None:
        log(name, f"param error: {reason}")

    try:
        params = json.loads(raw) if raw else {}
    except json.JSONDecodeError as e:
        fail(f"invalid json ({e})")
        return None
    if params is None:
        params = {}
    if not isinstance(params, dict):
        fail(f"expected object, got {type(params).__name__}")
        return None
    unknown = [key for key in params if key not in required and key not in optional]
    if unknown:
        fail(f"unknown key {unknown}")
        return None
    missing = [key for key in required if key not in params]
    if missing:
        fail(f"missing key {missing}")
        return None
    for key, values in spec.get("choices", {}).items():
        if key in params and params[key] not in values:
            fail(f"{key}={params[key]!r} not in {values}")
            return None
    filled = {**optional, **params}
    for group in spec.get("one_of", []):
        if all(filled.get(key) is None for key in group):
            fail(f"one of {group} is required")
            return None
    return filled


RunMethod = Callable[[object, Context, CustomAction.RunArg], bool]


def guard_run(run: RunMethod) -> RunMethod:
    @functools.wraps(run)
    def wrapper(self: object, context: Context, argv: CustomAction.RunArg) -> bool:
        try:
            return run(self, context, argv)
        except Exception as e:
            log(type(self).__name__, f"error: {e!r}")
            return False

    return wrapper
