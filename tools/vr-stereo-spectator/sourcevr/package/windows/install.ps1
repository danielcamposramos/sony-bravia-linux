# Stereo 3D for Half-Life 2 (VR Stereo Spectator): installs the display
# module and the 3D menu into a Half-Life 2 folder.
# Usage: install.bat [path to the "Half-Life 2" folder]
# Without a path it looks in every Steam library.
param([string]$GameDir = "")
$ErrorActionPreference = "Stop"
$here = Split-Path -Parent $MyInvocation.MyCommand.Path

function Find-HL2 {
    $steam = (Get-ItemProperty -Path "HKCU:\Software\Valve\Steam" -ErrorAction SilentlyContinue).SteamPath
    if (-not $steam) { return $null }
    $libs = @($steam)
    $vdf = Join-Path $steam "steamapps/libraryfolders.vdf"
    if (Test-Path $vdf) {
        foreach ($m in [regex]::Matches((Get-Content $vdf -Raw), '"path"\s+"([^"]+)"')) {
            $libs += $m.Groups[1].Value -replace '\\\\', '\'
        }
    }
    foreach ($l in $libs) {
        $d = Join-Path $l "steamapps/common/Half-Life 2"
        if (Test-Path (Join-Path $d "hl2.exe")) { return $d }
    }
    return $null
}

# The machine type in a DLL's PE header: x86 or x64.
function Get-Arch([string]$dll) {
    $b = [System.IO.File]::ReadAllBytes($dll)
    $pe = [BitConverter]::ToInt32($b, 0x3C)
    switch ([BitConverter]::ToUInt16($b, $pe + 4)) {
        0x014c { return "x86" }
        0x8664 { return "x64" }
        default { return "" }
    }
}

if (-not $GameDir) { $GameDir = Find-HL2 }
if (-not $GameDir -or -not (Test-Path (Join-Path $GameDir "hl2.exe"))) {
    Write-Host "Half-Life 2 not found. Drag the 'Half-Life 2' folder onto install.bat,"
    Write-Host "or run: install.bat ""C:\...\steamapps\common\Half-Life 2"""
    exit 1
}
Write-Host "Half-Life 2: $GameDir"

# Every engine folder in the game gets the module of its own architecture
# (today's Half-Life 2 runs the 32-bit one in bin; a 64-bit engine, where a
# game has one, lives in bin\x64 or bin\win64).
$done = 0
foreach ($sub in @("bin", "bin/x64", "bin/win64")) {
    $bin = Join-Path $GameDir $sub
    $engine = Join-Path $bin "engine.dll"
    if (-not (Test-Path $engine)) { continue }
    $arch = Get-Arch $engine
    if (-not $arch) { Write-Host "  ${sub}: unknown engine architecture, skipped"; continue }
    $dst = Join-Path $bin "sourcevr.dll"
    $keep = Join-Path $bin "sourcevr.dll.valve"
    # The first install keeps whatever module Valve shipped here; a later
    # install (the marker is there) never mistakes ours for Valve's.
    $mark = Join-Path $bin "svrtv-installed.txt"
    if (-not (Test-Path $mark) -and (Test-Path $dst) -and -not (Test-Path $keep)) {
        Copy-Item $dst $keep
        Write-Host "  ${sub}: Valve's sourcevr.dll kept as sourcevr.dll.valve"
    }
    Copy-Item (Join-Path $here "$arch/sourcevr.dll") $dst -Force
    Set-Content -Path $mark -Value "sourcevr.dll here is Stereo 3D for Half-Life 2 ($arch); uninstall.bat puts Valve's back." -Encoding ascii
    $ini = Join-Path $bin "svrtv.ini"
    if (-not (Test-Path $ini)) { Set-Content -Path $ini -Value "SVRTV_LOG=svrtv.log" -Encoding ascii }
    Write-Host "  ${sub}: $arch module installed (log: $(Join-Path $bin svrtv.log))"
    $done++
}
if ($done -eq 0) { Write-Host "No engine.dll found under bin: is this the Half-Life 2 folder?"; exit 1 }

$menu = Join-Path $GameDir "hl2/custom/svrtv-3d-menu/gamepadui"
New-Item -ItemType Directory -Force -Path $menu | Out-Null
Copy-Item (Join-Path $here "menu/gamepadui/options.res") (Join-Path $menu "options.res") -Force
Write-Host "  3D menu installed: Options > Video > Stereo 3D"
Write-Host ""
Write-Host "Steam > Half-Life 2 > Properties > Launch options:"
Write-Host "  -gamepadui -stereo3d                            (achievements on; muzzle flash beside the gun)"
Write-Host "  -gamepadui -stereo3d +sv_cheats 1 +viewmodel_fov 90   (muzzle flash on the gun; no achievements)"
Write-Host "See README.txt. Steam's 'Verify integrity of game files' puts Valve's module back: run install.bat again after it."
