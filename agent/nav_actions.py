import time

from maa.agent.agent_server import AgentServer
from maa.context import Context
from maa.custom_action import CustomAction

from common import LOADING_NODE, LOOP_INTERVAL_MS, guard_run, hit, load_params, log, run_handle, screencap, sleep_ms

NAV_HANDLE_NODES = ["EarnReward", "ClosePopup"]
VOICE_POPUP_NODE = "VoiceResourceLater"
NAV_TIMEOUT_S = 60
HOME_STABLE_S = 2
NAV_OPEN_S = 2
NAV_OPENED_NODE = "NavOpened"
OPEN_NAV_NODE = "OpenNavigation"
HOME_NODE = "Home"
HOME_OPERATION_NODE = "HomeOperation"
NAV_NODE_PREFIX = "Nav"
HOME_NODE_PREFIX = "Home"


@AgentServer.custom_action("Navigate")
class Navigate(CustomAction):
    PARAMS = {
        "required": ["dest"],
        "optional": {"handle": NAV_HANDLE_NODES, "direct": False},
        "choices": {"dest": ["Home", "Squad", "Operator", "Operation", "Headhunting"]},
    }

    @guard_run
    def run(self, context: Context, argv: CustomAction.RunArg) -> bool:
        params = load_params(self, argv.custom_action_param)
        if params is None:
            return False
        dest = params["dest"]
        handle = params["handle"]
        direct = params["direct"]

        deadline = time.monotonic() + NAV_TIMEOUT_S
        home_since = None
        opening_until = 0
        first_frame = True
        arriving = False
        while time.monotonic() < deadline:
            if context.tasker.stopping:
                return False
            image = screencap(context)
            departing, first_frame = first_frame, False

            if hit(context, LOADING_NODE, image):
                home_since = None
                sleep_ms(LOOP_INTERVAL_MS)
                continue

            if hit(context, NAV_OPENED_NODE, image):
                log("Navigate", f"{dest}: opened, clicking")
                context.run_action(f"{NAV_NODE_PREFIX}{dest}")
                if dest != "Home":
                    return True
                log("Navigate", f"{dest}: nav clicked, waiting home")
                home_since = None
                sleep_ms(LOOP_INTERVAL_MS)
                continue

            if time.monotonic() < opening_until:
                sleep_ms(LOOP_INTERVAL_MS)
                continue

            handled = run_handle(context, image, [VOICE_POPUP_NODE, *handle])
            if handled:
                log("Navigate", f"{dest}: handle {handled}")
                home_since = None
                sleep_ms(LOOP_INTERVAL_MS)
                continue

            opener = hit(context, OPEN_NAV_NODE, image)
            if opener and arriving:
                log("Navigate", f"{dest}: arrived from home")
                return True
            if opener:
                context.run_action(OPEN_NAV_NODE, box=opener.box)
                opening_until = time.monotonic() + NAV_OPEN_S
                sleep_ms(LOOP_INTERVAL_MS)
                continue

            home = hit(context, HOME_NODE, image)
            if not home:
                home_since = None
                sleep_ms(LOOP_INTERVAL_MS)
                continue
            arriving = False
            if home_since is None:
                home_since = time.monotonic()
            stable = time.monotonic() - home_since >= HOME_STABLE_S
            if dest == "Home" and stable:
                return True
            if dest != "Home" and (departing or stable):
                log("Navigate", f"{dest}: starting at home, leaving" if departing else f"{dest}: home stable, leaving")
                context.run_action(f"{HOME_NODE_PREFIX}{dest}" if direct else HOME_OPERATION_NODE, box=home.box)
                arriving = direct
                home_since = None
            sleep_ms(LOOP_INTERVAL_MS)

        log("Navigate", f"{dest}: timeout")
        return False
