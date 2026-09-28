# Stereo 3D for Half-Life 2: puts Valve's sourcevr.dll back and removes the
# 3D menu. Usage: uninstall.bat [path to the "Half-Life 2" folder]
param([string]$GameDir = "")
$ErrorActionPreference = "Stop"
if (-not $GameDir) {
    $steam = (Get-ItemProperty -Path "HKCU:\Software\Valve\Steam" -ErrorAction SilentlyContinue).SteamPath
    $libs = @($steam)
    $vdf = Join-Path $steam "steamapps/libraryfolders.vdf"
    if (Test-Path $vdf) { foreach ($m in [regex]::Matches((Get-Content $vdf -Raw), '"path"\s+"([^"]+)"')) { $libs += $m.Groups[1].Value -replace '\\\\', '\' } }
    foreach ($l in $libs) { $d = Join-Path $l "steamapps/common/Half-Life 2"; if (Test-Path (Join-Path $d "hl2.exe")) { $GameDir = $d; break } }
}
if (-not $GameDir) { Write-Host "Half-Life 2 not found. Drag its folder onto uninstall.bat."; exit 1 }
# While these markers exist the module still holds your own crosshair,
# motion blur, anisotropic filtering or video mode, to put back at the next
# start (the game quit with 3D on). Valve's module would not put them back.
$pending = @()
foreach ($sub in @("bin", "bin/x64", "bin/win64")) {
    $bin = Join-Path $GameDir $sub
    foreach ($f in @("svrtv-crosshair-off", "svrtv-blur-restore", "svrtv-restore-mode") + @(Get-ChildItem -Path $bin -Filter "svrtv-restore-*" -Name -ErrorAction SilentlyContinue)) {
        if ($f -and (Test-Path (Join-Path $bin $f))) { $pending += (Join-Path $bin $f) }
    }
}
if ($pending.Count -gt 0) {
    Write-Host "The game last quit with 3D on, so your own settings are still waiting to be restored:"
    $pending | Sort-Object -Unique | ForEach-Object { Write-Host "  $_" }
    Write-Host "Start Half-Life 2, set Options > Video > Stereo 3D to off, Apply, quit, then run uninstall.bat again."
    exit 1
}
foreach ($sub in @("bin", "bin/x64", "bin/win64")) {
    $bin = Join-Path $GameDir $sub
    $keep = Join-Path $bin "sourcevr.dll.valve"
    $mark = Join-Path $bin "svrtv-installed.txt"
    if (Test-Path $keep) { Move-Item $keep (Join-Path $bin "sourcevr.dll") -Force; Write-Host "  ${sub}: Valve's sourcevr.dll back" }
    elseif (Test-Path $mark) { Remove-Item (Join-Path $bin "sourcevr.dll") -ErrorAction SilentlyContinue; Write-Host "  ${sub}: our sourcevr.dll removed (Valve had none here)" }
    foreach ($f in @("svrtv.ini", "svrtv-launch-3d", "svrtv-installed.txt")) {
        $p = Join-Path $bin $f; if (Test-Path $p) { Remove-Item $p }
    }
}
$menu = Join-Path $GameDir "hl2/custom/svrtv-3d-menu"
if (Test-Path $menu) { Remove-Item $menu -Recurse; Write-Host "  3D menu removed" }
Write-Host "Done. The log (bin\svrtv.log), if any, is left for you to keep or delete."
