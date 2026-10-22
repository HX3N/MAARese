import base64
import io
import tarfile

from common import PACKAGE

APP_DIR = f"/data/data/{PACKAGE}"
PLAYERPREFS = f"{PACKAGE}.v2.playerprefs.xml"
ACCOUNT_KEY = "u8sdk_cached_uid"
GMS_ADID_FILE = "/data/data/com.google.android.gms/shared_prefs/adid_settings.xml"
REMOTE_B64 = "/data/local/tmp/maarese_restore.b64"
CHUNK_SIZE = 4000
OK_MARK = "MAARESE_OK"


def backup_command(app_dir: str = APP_DIR) -> str:
    return f"tar -czf - -C {app_dir} shared_prefs | base64"


def decode_archive(output: str) -> bytes:
    data = base64.b64decode("".join(output.split()), validate=True)
    with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as tar:
        if not tar.getnames():
            raise ValueError("empty archive")
    return data


def wipe_command(app_dir: str = APP_DIR) -> str:
    prefs_dir = f"{app_dir}/shared_prefs"
    # Unity PlayerPrefs keeps the downloaded resource version;
    # deleting it makes the game re-download its hot-update resources.
    steps = [
        f"am force-stop {PACKAGE}",
        f'for f in {prefs_dir}/*; do [ "$f" = {prefs_dir}/{PLAYERPREFS} ] || rm -rf "$f"; done',
        f'sed -i "/{ACCOUNT_KEY}/d" {prefs_dir}/{PLAYERPREFS}',
        f"rm -f {GMS_ADID_FILE}",
        "am force-stop com.google.android.gms",
        f'[ -z "$(ls {prefs_dir} | grep -v -x {PLAYERPREFS})" ] '
        f"&& ! grep -q {ACCOUNT_KEY} {prefs_dir}/{PLAYERPREFS} "
        f"&& echo {OK_MARK}",
    ]
    return "; ".join(steps)


def upload_commands(b64: str, remote_path: str = REMOTE_B64) -> list[str]:
    chunks = [b64[i : i + CHUNK_SIZE] for i in range(0, len(b64), CHUNK_SIZE)]
    return [f": > {remote_path}"] + [f"echo -n {c} >> {remote_path}" for c in chunks]


def extract_command(app_dir: str = APP_DIR, remote_path: str = REMOTE_B64) -> str:
    return (
        f"base64 -d {remote_path} | tar -tzf - > /dev/null "
        f"&& rm -rf {app_dir}/shared_prefs "
        f"&& base64 -d {remote_path} | tar -xzf - -C {app_dir}"
    )


def restore_command() -> str:
    uid = f"$(stat -c %u {APP_DIR})"
    return (
        f"am force-stop {PACKAGE}; "
        f"{extract_command()} "
        f"&& chown -R {uid}:{uid} {APP_DIR}/shared_prefs "
        f"&& restorecon -R {APP_DIR}/shared_prefs "
        f"&& echo {OK_MARK}; "
        f"rm -f {REMOTE_B64}"
    )
