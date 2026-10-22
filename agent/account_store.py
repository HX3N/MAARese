import re
from datetime import datetime, timedelta
from pathlib import Path

ACCOUNTS_DIR = Path(__file__).resolve().parent.parent / "accounts"
PREFS_DIRNAME = "_shared_prefs"
INSTANCE_FILENAME = "instance"
ARCHIVE_NAME = "shared_prefs.tar.gz"
LATEST = "latest"
STAMP_FORMAT = "%Y%m%d-%H%M%S"
STAMP_PATTERN = re.compile(r"^\d{8}-\d{6}$")


def new_stamp(now: datetime | None = None) -> str:
    return (now or datetime.now()).strftime(STAMP_FORMAT)


def save(
    archive: bytes,
    screenshot_png: bytes | None,
    root: Path = ACCOUNTS_DIR,
    stamp: str | None = None,
    folder: str = "",
    suffix: str = "",
    *,
    instance: str = "",
) -> str:
    stamp = stamp or new_stamp()
    while True:
        target = root / PREFS_DIRNAME / stamp
        try:
            target.mkdir(parents=True, exist_ok=False)
            break
        except FileExistsError:
            taken = datetime.strptime(stamp, STAMP_FORMAT)
            stamp = new_stamp(taken + timedelta(seconds=1))
    if instance:
        (target / INSTANCE_FILENAME).write_text(instance, encoding="utf-8")
    part = target / (ARCHIVE_NAME + ".part")
    part.write_bytes(archive)
    part.replace(target / ARCHIVE_NAME)
    if screenshot_png is not None:
        shot_dir = root / folder
        shot_dir.mkdir(parents=True, exist_ok=True)
        (shot_dir / f"{stamp}{suffix}.png").write_bytes(screenshot_png)
    return stamp


def list_stamps(root: Path = ACCOUNTS_DIR) -> list[str]:
    prefs = root / PREFS_DIRNAME
    if not prefs.is_dir():
        return []
    return sorted(
        d.name
        for d in prefs.iterdir()
        if STAMP_PATTERN.match(d.name) and (d / ARCHIVE_NAME).is_file()
    )


def _belongs_to(stamp: str, instance: str, root: Path) -> bool:
    marker = root / PREFS_DIRNAME / stamp / INSTANCE_FILENAME
    if not marker.is_file():
        return True
    return marker.read_text(encoding="utf-8") == instance


def resolve(name: str, root: Path = ACCOUNTS_DIR, *, instance: str | None = None) -> str:
    name = name.strip()
    stamps = list_stamps(root)
    if name in ("", LATEST):
        if instance is not None:
            stamps = [s for s in stamps if _belongs_to(s, instance, root)]
        if not stamps:
            raise FileNotFoundError(f"no account backups in {root / PREFS_DIRNAME}")
        return stamps[-1]
    if not STAMP_PATTERN.match(name):
        raise ValueError(f"invalid account name: {name!r}")
    if name not in stamps:
        raise FileNotFoundError(f"account backup not found: {name}")
    return name


def load(stamp: str, root: Path = ACCOUNTS_DIR) -> bytes:
    stamp = resolve(stamp, root)
    return (root / PREFS_DIRNAME / stamp / ARCHIVE_NAME).read_bytes()
