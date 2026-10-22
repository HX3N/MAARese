import difflib
import json
from pathlib import Path

from common import WHITESPACE

DATA_PATH = Path(__file__).resolve().parent / "operator_data.json"
NAME_CUTOFF = 0.8


def _squash(text: str) -> str:
    return WHITESPACE.sub("", text)


class OperatorMatcher:
    def __init__(self, operators: list[dict]) -> None:
        self._by_name = {_squash(op["name"]): (op["name"], op["rarity"]) for op in operators}

    def match(self, text: str) -> tuple[str, int] | None:
        text = _squash(text)
        if text in self._by_name:
            return self._by_name[text]
        close = difflib.get_close_matches(text, self._by_name, n=1, cutoff=NAME_CUTOFF)
        return self._by_name[close[0]] if close else None


def load(path: Path = DATA_PATH) -> OperatorMatcher:
    return OperatorMatcher(json.loads(Path(path).read_text(encoding="utf-8")))
