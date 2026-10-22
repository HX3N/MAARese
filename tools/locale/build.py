import argparse
import json
import re
import shutil
import subprocess
import sys
import urllib.request
import xml.etree.ElementTree as ET
import zipfile
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CACHE = ROOT / ".cache" / "locale"
HERE = ROOT / "tools" / "locale"
CORE = ROOT / "libs" / "MFAAvalonia.Core.dll"
BASE_URL = "https://raw.githubusercontent.com/MaaXYZ/MFAAvalonia/{tag}/MFAAvalonia/Assets/Localization/{name}"
RESOURCE_NAME = "MFAAvalonia.Assets.Localization.Strings.en-US.resources"
PLACEHOLDER = re.compile(r"\{\d+[^}]*\}")

RESX_HEADERS = (
    ("resmimetype", "text/microsoft-resx"),
    ("version", "2.0"),
    (
        "reader",
        "System.Resources.ResXResourceReader, System.Windows.Forms, Version=4.0.0.0, Culture=neutral, PublicKeyToken=b77a5c561934e089",
    ),
    (
        "writer",
        "System.Resources.ResXResourceWriter, System.Windows.Forms, Version=4.0.0.0, Culture=neutral, PublicKeyToken=b77a5c561934e089",
    ),
)

CSPROJ = """<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net10.0</TargetFramework>
    <AssemblyName>MFAAvalonia.Core</AssemblyName>
    <AssemblyVersion>{version}</AssemblyVersion>
    <EnableDefaultItems>false</EnableDefaultItems>
  </PropertyGroup>
  <ItemGroup>
    <EmbeddedResource Include="Strings.en-US.resx" LogicalName="{name}" />
  </ItemGroup>
</Project>
"""

PATCH_CSPROJ = """<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <OutputType>Exe</OutputType>
    <TargetFramework>net10.0</TargetFramework>
    <Nullable>enable</Nullable>
    <ImplicitUsings>enable</ImplicitUsings>
  </PropertyGroup>
  <ItemGroup>
    <PackageReference Include="Mono.Cecil" Version="0.11.6" />
  </ItemGroup>
</Project>
"""

PATCH_PROGRAM = """using System.Text.Json;
using Mono.Cecil;
using Mono.Cecil.Cil;

var table = JsonSerializer.Deserialize<Dictionary<string, string>>(File.ReadAllText(args[2]))!;
var resolver = new DefaultAssemblyResolver();
resolver.AddSearchDirectory(args[3]);
resolver.AddSearchDirectory(args[4]);
var assembly = AssemblyDefinition.ReadAssembly(args[0], new ReaderParameters { AssemblyResolver = resolver });
var counts = table.Keys.ToDictionary(key => key, _ => 0);

IEnumerable<TypeDefinition> Flatten(IEnumerable<TypeDefinition> types) =>
    types.SelectMany(type => new[] { type }.Concat(Flatten(type.NestedTypes)));

foreach (var type in Flatten(assembly.MainModule.Types))
    foreach (var method in type.Methods.Where(m => m.HasBody))
        foreach (var instruction in method.Body.Instructions)
            if (instruction.OpCode == OpCodes.Ldstr && instruction.Operand is string text && table.TryGetValue(text, out var replacement))
            {
                instruction.Operand = replacement;
                counts[text]++;
            }

foreach (var (key, count) in counts)
    Console.WriteLine($"{count}	{key}");
if (counts.Values.Any(count => count == 0))
{
    Console.Error.WriteLine("Some literals were not found");
    return 1;
}
assembly.Write(args[1]);
return 0;
"""

CORE_STRINGS = {
    "新建标签页": "새 탭",
    "复制标签页": "탭 복제",
    "重命名": "이름 바꾸기",
    "关闭标签页": "탭 닫기",
    "关闭其他标签页": "다른 탭 닫기",
    "关闭右侧标签页": "오른쪽 탭 닫기",
    "配置 ": "설정 ",
    "导入实例配置": "인스턴스 설정 가져오기",
}


def fail(message):
    print(f"ERROR: {message}", file=sys.stderr)
    sys.exit(1)


def download(tag, name):
    dest = CACHE / tag / name
    if dest.exists():
        return dest
    dest.parent.mkdir(parents=True, exist_ok=True)
    url = BASE_URL.format(tag=tag, name=name)
    print(f"Downloading {url}")
    tmp = dest.with_name(dest.name + ".part")
    request = urllib.request.Request(url, headers={"User-Agent": "MAARese-locale"})
    with urllib.request.urlopen(request) as response, open(tmp, "wb") as f:
        shutil.copyfileobj(response, f)
    tmp.replace(dest)
    return dest


def read_resx(path):
    # iter() also visits <data> elements nested by the upstream en-US resx's missing </data>.
    root = ET.parse(path).getroot()
    values = {}
    for data in root.iter("data"):
        value = data.find("value")
        values[data.get("name")] = (value.text or "") if value is not None else ""
    return values


def powershell(expression):
    result = subprocess.run(
        ["powershell", "-NoProfile", "-Command", expression],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        fail(f"PowerShell failed: {result.stderr.strip()}")
    return result.stdout.strip()


def write_resx(path, values):
    root = ET.Element("root")
    for name, value in RESX_HEADERS:
        header = ET.SubElement(root, "resheader", name=name)
        ET.SubElement(header, "value").text = value
    for key, value in values.items():
        data = ET.SubElement(
            root, "data", {"name": key, "{http://www.w3.org/XML/1998/namespace}space": "preserve"}
        )
        ET.SubElement(data, "value").text = value
    ET.indent(root)
    ET.ElementTree(root).write(path, encoding="utf-8", xml_declaration=True)


def main():
    parser = argparse.ArgumentParser(description="Build the ko UI satellite assembly for MFAAvalonia")
    parser.add_argument("--dump", type=Path, help="write {key: {en, zh}} to PATH and exit")
    args = parser.parse_args()

    tag = json.loads((ROOT / "tools" / "versions.json").read_text(encoding="utf-8"))["mfaavalonia"]
    en = read_resx(download(tag, "Strings.en-US.resx"))
    zh = read_resx(download(tag, "Strings.resx"))
    # Keys missing from the upstream en-US resx would otherwise fall back to the Chinese neutral resource.
    en |= {key: value for key, value in zh.items() if key not in en}

    if args.dump:
        dump = {key: {"en": value, "zh": zh.get(key, "")} for key, value in en.items()}
        args.dump.write_text(json.dumps(dump, ensure_ascii=False, indent=2), encoding="utf-8")
        return

    ko_path = HERE / "ko.json"
    if not ko_path.exists():
        fail(f"{ko_path} not found")
    ko = json.loads(ko_path.read_text(encoding="utf-8"))
    unknown = [key for key in ko if key not in en]
    if unknown:
        fail("Keys not in resx: " + ", ".join(unknown))
    values = {key: ko.get(key, value) for key, value in en.items()}
    mismatched = [
        key
        for key in ko
        if Counter(PLACEHOLDER.findall(en[key])) != Counter(PLACEHOLDER.findall(values[key]))
    ]
    if mismatched:
        fail("Placeholder mismatch: " + ", ".join(mismatched))

    if not CORE.exists():
        fail(f"{CORE} not found; run the setup first")
    # The satellite must match Core.dll's AssemblyVersion, not the MFA release tag.
    version = powershell(f"[Reflection.AssemblyName]::GetAssemblyName('{CORE}').Version.ToString()")

    build = CACHE / "build"
    shutil.rmtree(build, ignore_errors=True)
    build.mkdir(parents=True)
    write_resx(build / "Strings.en-US.resx", values)
    (build / "Core.csproj").write_text(CSPROJ.format(version=version, name=RESOURCE_NAME), encoding="utf-8")

    result = subprocess.run(["dotnet", "build", "-c", "Release"], cwd=build)
    if result.returncode != 0:
        fail("dotnet build failed")
    built = next(build.glob("bin/Release/*/en-US/MFAAvalonia.Core.resources.dll"), None)
    if built is None:
        fail("Satellite assembly not found in build output")
    output = HERE / "MFAAvalonia.Core.resources.dll"
    shutil.copyfile(built, output)

    full_name = powershell(f"[Reflection.AssemblyName]::GetAssemblyName('{output}').FullName")
    expected = f"MFAAvalonia.Core.resources, Version={version}, Culture=en-US, PublicKeyToken=null"
    if full_name != expected:
        fail(f"Assembly name mismatch: {full_name} (expected {expected})")
    print(full_name)

    patch_core(tag)


def patch_core(tag):
    archive = ROOT / ".cache" / f"MFAAvalonia-{tag}-win-x64.zip"
    if not archive.exists():
        fail(f"{archive} not found; run the setup first")
    original = CACHE / tag / CORE.name
    with zipfile.ZipFile(archive) as z:
        original.write_bytes(z.read("libs/MFAAvalonia.Core.dll"))

    patch = CACHE / "patch"
    patch.mkdir(parents=True, exist_ok=True)
    (patch / "Patch.csproj").write_text(PATCH_CSPROJ, encoding="utf-8")
    (patch / "Program.cs").write_text(PATCH_PROGRAM, encoding="utf-8")
    table = patch / "strings.json"
    table.write_text(json.dumps(CORE_STRINGS, ensure_ascii=False), encoding="utf-8")

    output = HERE / CORE.name
    result = subprocess.run(
        ["dotnet", "run", "-c", "Release", "--project", str(patch), "--",
         str(original), str(output), str(table), str(CORE.parent), str(ROOT)]
    )
    if result.returncode != 0:
        fail("Core.dll patch failed")

    names = [
        powershell(f"[Reflection.AssemblyName]::GetAssemblyName('{path}').FullName")
        for path in (original, output)
    ]
    if names[0] != names[1]:
        fail(f"Core assembly name mismatch: {names[1]} (expected {names[0]})")
    print(names[1])


if __name__ == "__main__":
    main()
