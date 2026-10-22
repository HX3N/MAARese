import json
import sys
from pathlib import Path
from urllib.request import urlopen

DEFAULT_OUT = Path(__file__).resolve().parent.parent / "agent" / "operator_data.json"
CHARACTER_TABLE_URL = (
    "https://raw.githubusercontent.com/ArknightsAssets/ArknightsGamedata/HEAD/"
    "kr/gamedata/excel/character_table.json"
)


def fetch_json(url: str):
    with urlopen(url) as response:
        return json.loads(response.read().decode("utf-8"))


def parse_rarity(rarity: int | str) -> int:
    return rarity if isinstance(rarity, int) else int(rarity.removeprefix("TIER_"))


def load_operators(table: dict) -> list[dict]:
    operators: dict[str, dict] = {}
    for char_id, char in table.items():
        name = char.get("name")
        if not char_id.startswith("char_") or char.get("isNotObtainable") or not name:
            continue
        operators.setdefault(name, {"name": name, "rarity": parse_rarity(char["rarity"])})
    return list(operators.values())


def dump(operators: list[dict]) -> str:
    lines = ",\n".join("  " + json.dumps(op, ensure_ascii=False) for op in operators)
    return f"[\n{lines}\n]\n"


def main() -> int:
    operators = load_operators(fetch_json(CHARACTER_TABLE_URL))
    DEFAULT_OUT.write_text(dump(operators), encoding="utf-8", newline="\n")
    six_star = sum(op["rarity"] == 6 for op in operators)
    print(f"operators={len(operators)} six_star={six_star}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
