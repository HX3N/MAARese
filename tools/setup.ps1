$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

$root = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
Set-Location $root

$arch = if ([Runtime.InteropServices.RuntimeInformation]::OSArchitecture -eq 'Arm64') { 'arm64' } else { 'x64' }
$uvArch = @{ x64 = 'x86_64'; arm64 = 'aarch64' }[$arch]

$mfaExe = Join-Path $root 'MFAAvalonia.exe'
if (Get-Process MFAAvalonia -ErrorAction SilentlyContinue | Where-Object { $_.Path -eq $mfaExe }) {
    Write-Host 'MFAAvalonia 가 이미 실행 중입니다. 종료한 뒤 다시 실행해 주세요.'
    exit 1
}

if (Test-Path (Join-Path $root 'tools\install.py')) {
    if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
        $uvDir = Join-Path $root '.cache\uv'
        if (-not (Test-Path (Join-Path $uvDir 'uv.exe'))) {
            Write-Host 'uv 를 내려받습니다...'
            New-Item -ItemType Directory -Force $uvDir | Out-Null
            $uvZip = Join-Path $uvDir 'uv.zip'
            Invoke-WebRequest -UseBasicParsing -Uri "https://github.com/astral-sh/uv/releases/latest/download/uv-$uvArch-pc-windows-msvc.zip" -OutFile $uvZip
            Expand-Archive -Path $uvZip -DestinationPath $uvDir -Force
        }
        $env:PATH = "$uvDir;$env:PATH"
    }

    Write-Host '실행 환경을 구성합니다...'
    & uv run --no-project --python 3.12 tools/install.py --arch $arch
    if ($LASTEXITCODE -ne 0) { throw "구성에 실패했습니다. (종료 코드 $LASTEXITCODE)" }
}

function Get-MissingRuntimes {
    $missing = @()
    if (-not (Test-Path (Join-Path $env:ProgramFiles 'dotnet\shared\Microsoft.WindowsDesktop.App\10.*'))) {
        $missing += '.NET 10 Desktop Runtime'
    }
    $vc = Get-ItemProperty "HKLM:\SOFTWARE\Microsoft\VisualStudio\14.0\VC\Runtimes\$arch" -ErrorAction SilentlyContinue
    if (-not $vc -or $vc.Installed -ne 1) {
        $missing += 'Visual C++ 재배포 패키지'
    }
    return $missing
}

$missing = Get-MissingRuntimes
if ($missing) {
    Write-Host "필요한 런타임이 없습니다: $($missing -join ', ')"
    Write-Host '관리자 권한으로 설치 스크립트를 실행합니다. 설치가 끝나면 그 창에서 아무 키나 눌러 주세요.'
    Start-Process -FilePath (Join-Path $root 'DependencySetup_依赖库安装_win.bat') -Verb RunAs -Wait
    $missing = Get-MissingRuntimes
    if ($missing) { throw "런타임 설치를 확인하지 못했습니다: $($missing -join ', ')" }
}

Write-Host 'MFAAvalonia 를 실행합니다.'
Start-Process -FilePath $mfaExe -WorkingDirectory $root
