"""Convert ArknightsGamedata obt story scripts into docs/gamedata/<path>.md."""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SOURCE = ROOT.parent / "ArknightsGamedata" / "kr" / "gamedata"
OUT = ROOT / "docs" / "gamedata"

STORIES = [
    "guide/beg/0_welcome_to_guide",
    "guide/beg/1a_guide_1to2",
    "guide/beg/1b_guide_1to2",
    "guide/beg/2_guide_to_home",
    "guide/l0-0/0_home_ui",
    "guide/l0-0/1_recruit_adv",
    "guide/l0-0/2_make_squad",
    "guide/l0-0/3_battle_ui",
    "guide/l0-1/0_mission_main",
    "guide/l0-1/1_training_level",
    "main/level_main_00-01_beg",
    "main/level_main_00-01_end",
    *[f"tutorial/level/guide_01_{c}" for c in "abcd"],
    *[f"tutorial/level/guide_02_{c}" for c in "abcdefghi"],
    "tutorial/level/main_00-01",
    "tutorial/training/training_1_a",
    "tutorial/training/training_1_b",
    "guide/stage/stagepage_v2_intro",
    *[f"guide/train/tr_0{n}" for n in (1, 3, 4, 5, 6)],
    "guide/l0-2/0_recruit_normal",
    "guide/l0-4/0_upgrade_char",
    "guide/l0-6/0_upgrade_skill",
    "guide/l0-6/0_upgrade_skill_mastery",
    "guide/misc/assist_char",
    "guide/misc/auto_battle",
    "guide/l0-9/0_mission_others",
    "guide/l0-10/0_weekly_daily",
    "guide/shop/0_main_and_extraqc",
    "guide/l0-11/0_building_init",
    *[f"guide/l0-11/1{c}_slot_clean" for c in "abcd"],
    "guide/l0-11/2a_build_elect",
    "guide/l0-11/2b_build_manu",
    "guide/l0-11/2c_build_trade",
    "guide/l0-11/3a_station_manu",
    "guide/l0-11/3b_op_manu",
    "guide/l0-11/3c_station_trade",
    "guide/l0-11/3d_op_trade",
    *[f"main/level_main_00-{s}" for s in (
        "02_beg", "02_end", "04_beg", "06_end", "07_beg", "07_end", "08_beg", "09_end", "10_beg", "11_end",
    )],
    *[f"tutorial/level/main_00-{n:02d}" for n in range(2, 12)],
    *[f"tutorial/training/training_{s}" for s in ("2_a", "2_b", "3", "4_a", "4_b", "5_a", "5_b", "6_a", "6_b", "7")],
]

AVATARS = {
    "$avatar_amiya": "아미야",
    "$avatar_doberm": "도베르만",
    "$avatar_sys": "PRTS",
    "$avatar_jesica": "제시카",
    "$avatar_closure": "클로저",
    "$avatar_ace": "에이스",
}

COMMAND = re.compile(r"^\[(?P<name>[A-Za-z_.]+)(?:\((?P<args>.*)\))?\]\s*(?P<text>.*)$", re.S)
NAME = re.compile(r'^\[name="(?P<speaker>[^"]*)"\]\s*(?P<text>.*)$', re.S)
ARG = re.compile(r'(\w+)\s*=\s*("[^"]*"|[^,\s]+)')
TAG = re.compile(r"<[@$][^>]*>|</>")


def char_name(char_table, char_id):
    name = char_table.get(char_id, {}).get("name")
    return f"{char_id}({name})" if name else char_id


def parse_args(raw):
    return {k: v.strip('"') for k, v in ARG.findall(raw or "")}


def clean(text):
    return TAG.sub("", text).strip()


def logical_lines(path):
    buf = ""
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.rstrip()
        if line.endswith("\\"):
            buf += line[:-1].strip() + " "
            continue
        yield (buf + line.strip()).strip()
        buf = ""


def convert(line, char_table):
    m = NAME.match(line)
    if m:
        return f"[{m['speaker'] or '무명'}] {clean(m['text'])}"
    m = COMMAND.match(line)
    if not m:
        return f"(지문) {clean(line)}" if line and not line.startswith("[") else None
    name, args, text = m["name"], parse_args(m["args"]), clean(m["text"])
    if name.startswith("Battle."):
        if "charId" in args:
            args["charId"] = char_name(char_table, args["charId"])
        shown = ", ".join(f"{k}={v}" for k, v in args.items())
        return f"(전투) {name}({shown})" if shown else f"(전투) {name}"
    if name == "Decision":
        return "(선택지) " + " / ".join(args.get("options", "").split(";"))
    if name in ("Tutorial", "PopupDialog"):
        notes = [f"{k}={args[a]}" for k, a in (("anim", "animStyle"), ("target", "target"), ("signal", "waitForSignal")) if a in args]
        if not text:
            return "(대기) " + ", ".join(notes) if notes else None
        speaker = AVATARS.get(args.get("dialogHead"), args.get("dialogHead", "?"))
        return f"[{speaker}] {text}" + (" — " + ", ".join(notes) if notes else "")
    return None


def trigger_line(story_table, key):
    entry = story_table.get(f"obt/{key}")
    if not entry:
        return "없음"
    trigger = entry["trigger"]
    return " ".join(p for p in (trigger["type"], trigger["key"]) if p)


def main():
    source = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_SOURCE
    excel = source / "excel"
    story_table = json.loads((excel / "story_table.json").read_text(encoding="utf-8"))
    char_table = json.loads((excel / "character_table.json").read_text(encoding="utf-8"))
    for key in STORIES:
        raw = logical_lines(source / "story" / "obt" / f"{key}.txt")
        lines = [c for c in (convert(line, char_table) for line in raw) if c]
        body = "\n".join(f"{i}. {c}" for i, c in enumerate(lines, 1))
        out = OUT / f"{key}.md"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(f"# {key}\ntrigger: {trigger_line(story_table, key)}\n\n{body}\n", encoding="utf-8")


if __name__ == "__main__":
    main()
