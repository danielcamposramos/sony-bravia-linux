@echo off
rem Stereo 3D for Half-Life 2: runs install.ps1 (drag the Half-Life 2 folder here, or run without arguments).
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0install.ps1" %*
pause
