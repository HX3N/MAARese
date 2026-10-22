import time

PULL_SIZES_NODES = {"Gacha_PullTen": 10, "Gacha_PullOne": 1}
PROGRESS_NODE = "Gacha_Pull_Skip"

runs: dict[int, dict] = {}
scans: dict[int, int] = {}
continuing: dict[int, bool] = {}


def count_scan(task_id: int) -> int:
    scans[task_id] = scans.get(task_id, 0) + 1
    return scans[task_id]


def start_run(task_id: int) -> int:
    scans[task_id] = 0
    continuing[task_id] = False
    state = runs.setdefault(task_id, {"run": 0})
    state["run"] += 1
    state["start"] = time.monotonic()
    state["pulls"] = 0
    state["last_pull"] = 0
    return state["run"]


def run_info(task_id: int) -> tuple[int, int, int]:
    state = runs.get(task_id)
    if state is None:
        return 0, 0, 0
    return state["run"], int(time.monotonic() - state["start"]), state["pulls"]


def count_pull(state: dict, name: str) -> None:
    if name in PULL_SIZES_NODES:
        state["last_pull"] = PULL_SIZES_NODES[name]
    elif name == PROGRESS_NODE:
        state["pulls"] += state["last_pull"]
