from difflib import SequenceMatcher

from maa.agent.agent_server import AgentServer
from maa.context import Context
from maa.custom_action import CustomAction
from maa.custom_recognition import CustomRecognition

from common import DIALOG_NEXT_NODE, WHITESPACE, guard_run, load_params

AREA_NODES = {"upper": "DialogArea", "lower": "LowerDialogArea"}
DIALOG_SIMILARITY = 0.8


@AgentServer.custom_recognition("Dialog")
class Dialog(CustomRecognition):
    PARAMS = {"required": ["text", "area"], "choices": {"area": ["upper", "lower"]}}

    def analyze(self, context: Context, argv: CustomRecognition.AnalyzeArg) -> CustomRecognition.AnalyzeResult:
        params = load_params(self, argv.custom_recognition_param)
        if params is None:
            return CustomRecognition.AnalyzeResult(box=None, detail="param error")
        text = params["text"]
        node = AREA_NODES[params["area"]]

        detail = context.run_recognition(node, argv.image)
        if detail is None or not detail.all_results:
            return CustomRecognition.AnalyzeResult(box=None, detail=text)

        results = sorted(detail.all_results, key=lambda r: r.box[0])
        full_line = WHITESPACE.sub("", "".join(r.text for r in results))
        if len(full_line) < len(text):
            return CustomRecognition.AnalyzeResult(box=None, detail=f"{text} | {full_line} | short")

        line = full_line[: len(text)]
        ratio = SequenceMatcher(None, text, line).ratio()
        box = results[0].box if ratio >= DIALOG_SIMILARITY else None
        return CustomRecognition.AnalyzeResult(box=box, detail=f"{text} | {line} | {ratio:.2f}")


@AgentServer.custom_action("SetSpeakers")
class SetSpeakers(CustomAction):
    PARAMS = {"required": ["templates"]}

    @guard_run
    def run(self, context: Context, argv: CustomAction.RunArg) -> bool:
        params = load_params(self, argv.custom_action_param)
        if params is None:
            return False
        return context.override_pipeline({DIALOG_NEXT_NODE: {"recognition": {"param": {"template": params["templates"]}}}})
