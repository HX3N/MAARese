import base64
import os
import tarfile

from maa.agent.agent_server import AgentServer
from maa.context import Context
from maa.custom_action import CustomAction
from maa.custom_recognition import CustomRecognition

import account_store
from account_commands import (
    OK_MARK,
    backup_command,
    decode_archive,
    restore_command,
    upload_commands,
    wipe_command,
)
from common import guard_run, load_params, log
from device import launch_app, screenshot_png, shell, su
from run_state import start_run

ACCOUNT_RESTART_NODE = "Account_Launch"
RESOLUTION_NOTICE_NODE = "Account_Resolution_Notice"
EXPECTED_RESOLUTION = (1280, 720)


@AgentServer.custom_recognition("ResolutionMismatch")
class ResolutionMismatch(CustomRecognition):
    PARAMS = {}

    def analyze(self, context: Context, argv: CustomRecognition.AnalyzeArg) -> CustomRecognition.AnalyzeResult:
        if load_params(self, argv.custom_recognition_param) is None:
            return CustomRecognition.AnalyzeResult(box=None, detail="param error")
        width, height = context.tasker.controller.resolution
        if (width, height) in ((0, 0), EXPECTED_RESOLUTION):
            return CustomRecognition.AnalyzeResult(box=None, detail=f"{width}x{height}")
        content = (
            f"[color:#FFD700]⚠ 해상도 {width}×{height}"
            f"(권장 {EXPECTED_RESOLUTION[0]}×{EXPECTED_RESOLUTION[1]}), 계속 진행[/color]"
        )
        context.override_pipeline(
            {
                RESOLUTION_NOTICE_NODE: {
                    "focus": {
                        "Node.Recognition.Succeeded": {"content": content, "display": ["log", "toast"]}
                    }
                }
            }
        )
        return CustomRecognition.AnalyzeResult(box=(0, 0, width, height), detail=f"{width}x{height}")


def save_account(context: Context, folder: str = "", suffix: str = "") -> str:
    try:
        screenshot = screenshot_png(context)
    except (RuntimeError, ValueError, IndexError) as e:
        log("account", f"screenshot skipped: {e}")
        screenshot = None

    output = su(context, backup_command())
    try:
        archive = decode_archive(output)
    except (ValueError, OSError, EOFError, tarfile.TarError) as e:
        log("account", f"save failed: invalid shared_prefs archive ({e})")
        return ""

    try:
        stamp = account_store.save(
            archive,
            screenshot,
            folder=folder,
            suffix=suffix,
            instance=os.environ.get("MFA_INSTANCE_ID", ""),
        )
    except OSError as e:
        log("account", f"save failed: {e}")
        return ""
    log("account", f"saved: {stamp}")
    return stamp


@AgentServer.custom_action("AccountSave")
class AccountSave(CustomAction):
    PARAMS = {}

    @guard_run
    def run(self, context: Context, argv: CustomAction.RunArg) -> bool:
        return bool(save_account(context))


@AgentServer.custom_action("AccountWipe")
class AccountWipe(CustomAction):
    PARAMS = {}

    @guard_run
    def run(self, context: Context, argv: CustomAction.RunArg) -> bool:
        run = start_run(argv.task_detail.task_id)
        context.override_pipeline({ACCOUNT_RESTART_NODE: {"focus": f"[color:#4FA3FF]▶ 게임 실행 · {run}회차[/color]"}})
        output = su(context, wipe_command())
        if OK_MARK not in output:
            log("AccountWipe", f"failed: {output!r}")
            return False
        return True


def load_account(context: Context, name: str, instance: str | None) -> bool:
    try:
        stamp = account_store.resolve(name, instance=instance)
        archive = account_store.load(stamp)
    except (ValueError, OSError) as e:
        log("AccountLoad", f"failed: {e}")
        return False

    b64 = base64.b64encode(archive).decode("ascii")
    for cmd in upload_commands(b64):
        shell(context, cmd)

    output = su(context, restore_command())
    if OK_MARK not in output:
        log("AccountLoad", f"failed: {output!r}")
        return False
    log("AccountLoad", f"loaded: {stamp}")
    return True


@AgentServer.custom_action("LaunchApp")
class LaunchApp(CustomAction):
    PARAMS = {}

    @guard_run
    def run(self, context: Context, argv: CustomAction.RunArg) -> bool:
        if not launch_app(context):
            log("LaunchApp", "failed: monkey did not inject events")
            return False
        return True


@AgentServer.custom_action("AccountLoad")
class AccountLoad(CustomAction):
    PARAMS = {"required": ["account"]}

    @guard_run
    def run(self, context: Context, argv: CustomAction.RunArg) -> bool:
        params = load_params(self, argv.custom_action_param)
        if params is None:
            return False
        return load_account(context, params["account"], os.environ.get("MFA_INSTANCE_ID") or None)
