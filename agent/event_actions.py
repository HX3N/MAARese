from maa.agent.agent_server import AgentServer
from maa.context import Context
from maa.custom_action import CustomAction

from common import click_center, guard_run, hit, load_params, log, screencap

next_slots: dict[int, int] = {}


@AgentServer.custom_action("ResetEventSlot")
class ResetEventSlot(CustomAction):
    PARAMS = {}

    @guard_run
    def run(self, context: Context, argv: CustomAction.RunArg) -> bool:
        next_slots[argv.task_detail.task_id] = 0
        return True


@AgentServer.custom_action("OpenEventSlot")
class OpenEventSlot(CustomAction):
    PARAMS = {"required": ["rois", "branches", "done"]}

    @guard_run
    def run(self, context: Context, argv: CustomAction.RunArg) -> bool:
        if context.tasker.stopping:
            return False
        params = load_params(self, argv.custom_action_param)
        if params is None:
            return False
        rois = params["rois"]
        branches = params["branches"]
        done = params["done"]
        task_id = argv.task_detail.task_id

        image = screencap(context)
        for i in range(next_slots.get(task_id, 0), len(rois)):
            for icon, target in branches.items():
                override = {icon: {"recognition": {"param": {"roi": rois[i]}}}}
                found = hit(context, icon, image, override)
                if not found:
                    continue
                next_slots[task_id] = i + 1
                click_center(context, found.box)
                context.override_next(argv.node_name, [target])
                log("OpenEventSlot", f"slot {i}: {icon}")
                return True

        next_slots[task_id] = len(rois)
        context.override_next(argv.node_name, [done])
        log("OpenEventSlot", "slot: done")
        return True
