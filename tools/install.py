import argparse
import json
import shutil
import subprocess
import sys
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / ".cache"
DIST = ROOT / "dist"
ARCHS = {
    "x64": {
        "rid": "win-x64",
        "maafw": "x86_64",
        "python": "amd64",
        "uv": "x86_64-pc-windows-msvc",
    },
    "arm64": {
        "rid": "win-arm64",
        "maafw": "aarch64",
        "python": "arm64",
        "uv": "aarch64-pc-windows-msvc",
    },
}
LOCALE_DLL = ROOT / "tools" / "locale" / "MFAAvalonia.Core.resources.dll"
CORE_DLL = ROOT / "tools" / "locale" / "MFAAvalonia.Core.dll"
CONFIG_TEMPLATE = ROOT / "tools" / "config.template.json"
ZIP_ENTRIES = (
    "MFAAvalonia.exe",
    "MFAAvalonia.dll",
    "MFAAvalonia.deps.json",
    "MFAAvalonia.runtimeconfig.json",
    "libloader.dll",
    "DependencySetup_依赖库安装_win.bat",
    "libs",
    "MaaAgentBinary",
    "plugins",
    "runtimes",
    "python",
    "resource",
    "agent",
    "LICENSE",
    "licenses",
    "setup.cmd",
    "tools/setup.ps1",
)
NATIVE_IGNORE = shutil.ignore_patterns(
    "*MaaDbgControlUnit*",
    "*MaaThriftControlUnit*",
    "*MaaRpc*",
    "*MaaHttp*",
    "plugins",
    "*.node",
    "*MaaPiCli*",
)


def fail(message):
    print(f"ERROR: {message}", file=sys.stderr)
    sys.exit(1)


def download(url):
    dest = CACHE / url.rsplit("/", 1)[1]
    if dest.exists():
        return dest
    CACHE.mkdir(exist_ok=True)
    print(f"Downloading {url}")
    tmp = dest.with_name(dest.name + ".part")
    request = urllib.request.Request(url, headers={"User-Agent": "MAARese-install"})
    with urllib.request.urlopen(request) as response, open(tmp, "wb") as f:
        shutil.copyfileobj(response, f)
    tmp.replace(dest)
    return dest


def install_mfa(archive):
    with zipfile.ZipFile(archive) as z:
        members = [m for m in z.namelist() if not m.startswith("runtimes/")]
        z.extractall(ROOT, members)
    shutil.rmtree(ROOT / "runtimes", ignore_errors=True)


def install_locale():
    dest = ROOT / "libs" / "locales" / "en-US"
    dest.mkdir(parents=True, exist_ok=True)
    shutil.copy2(LOCALE_DLL, dest / LOCALE_DLL.name)
    shutil.copy2(CORE_DLL, ROOT / "libs" / CORE_DLL.name)


def install_config_template():
    if (ROOT / "config" / "config.json").exists():
        return
    (ROOT / "config").mkdir(exist_ok=True)
    shutil.copy2(CONFIG_TEMPLATE, ROOT / "config" / CONFIG_TEMPLATE.name)


def install_maafw(archive, rid):
    extracted = CACHE / archive.stem
    if not extracted.exists():
        with zipfile.ZipFile(archive) as z:
            z.extractall(extracted)
    shutil.copytree(
        extracted / "bin",
        ROOT / "runtimes" / rid / "native",
        ignore=NATIVE_IGNORE,
        dirs_exist_ok=True,
    )
    shutil.copytree(
        extracted / "share" / "MaaAgentBinary",
        ROOT / "libs" / "MaaAgentBinary",
        dirs_exist_ok=True,
    )
    plugins = extracted / "bin" / "plugins"
    if plugins.exists():
        shutil.copytree(
            plugins, ROOT / "plugins" / rid, dirs_exist_ok=True
        )


def maafw_installed(site_packages, version):
    return any(
        p.name.lower() == f"maafw-{version}.dist-info"
        for p in site_packages.glob("*.dist-info")
    )


def install_python(versions, arch):
    python_dir = ROOT / "python"
    if not (python_dir / "python.exe").exists():
        archive = download(
            f"https://www.python.org/ftp/python/{versions['python']}/"
            f"python-{versions['python']}-embed-{arch['python']}.zip"
        )
        with zipfile.ZipFile(archive) as z:
            z.extractall(python_dir)
        pth = next(python_dir.glob("python*._pth"))
        stdlib_zip = next(python_dir.glob("python*.zip")).name
        pth.write_text(
            f"{stdlib_zip}\n.\nLib\\site-packages\nimport site\n", encoding="utf-8"
        )

    site_packages = python_dir / "Lib" / "site-packages"
    if maafw_installed(site_packages, versions["maafw_pip"]):
        return
    if site_packages.exists():
        shutil.rmtree(site_packages)
    subprocess.run(
        [
            "uv", "pip", "install",
            "--target", str(site_packages),
            "--python-version", "3.12",
            "--python-platform", arch["uv"],
            f"MaaFw=={versions['maafw_pip']}",
        ],
        check=True,
    )


def zip_files(entry):
    if entry.is_file():
        yield entry
        return
    for path in sorted(entry.rglob("*")):
        if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc":
            yield path


def make_zip(version, rid):
    DIST.mkdir(exist_ok=True)
    target = DIST / f"MAARese-{rid}-{version}.zip"
    target.unlink(missing_ok=True)
    interface = json.loads((ROOT / "interface.json").read_text(encoding="utf-8-sig"))
    interface["version"] = version
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr(
            "interface.json",
            json.dumps(interface, ensure_ascii=False, indent=4) + "\n",
        )
        for name in ZIP_ENTRIES:
            entry = ROOT / name
            if not entry.exists():
                continue
            for path in zip_files(entry):
                z.write(path, path.relative_to(ROOT).as_posix())
        z.write(CONFIG_TEMPLATE, "config/config.template.json")
    print(f"Wrote {target}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", default="dev")
    parser.add_argument("--zip", action="store_true")
    parser.add_argument("--arch", choices=ARCHS, default="x64")
    args = parser.parse_args()
    arch = ARCHS[args.arch]

    if not (ROOT / "interface.json").is_file():
        fail(f"{ROOT / 'interface.json'} not found")
    for name in ("pipeline", "image", "model"):
        if not (ROOT / "resource" / name).is_dir():
            fail(f"{ROOT / 'resource' / name} not found")

    versions = json.loads((ROOT / "tools" / "versions.json").read_text(encoding="utf-8"))
    mfa = versions["mfaavalonia"]
    maafw = versions["maafw"]
    mfa_zip = download(
        f"https://github.com/MaaXYZ/MFAAvalonia/releases/download/{mfa}/MFAAvalonia-{mfa}-{arch['rid']}.zip"
    )
    maafw_zip = download(
        f"https://github.com/MaaXYZ/MaaFramework/releases/download/{maafw}/MAA-win-{arch['maafw']}-{maafw}.zip"
    )

    install_mfa(mfa_zip)
    install_locale()
    install_config_template()
    install_maafw(maafw_zip, arch["rid"])
    install_python(versions, arch)
    if args.zip:
        make_zip(args.version, arch["rid"])
    print(f"Install to {ROOT} successfully.")


if __name__ == "__main__":
    main()
