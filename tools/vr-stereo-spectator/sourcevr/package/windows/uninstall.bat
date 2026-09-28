@echo off
rem Stereo 3D for Half-Life 2: runs uninstall.ps1.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0uninstall.ps1" %*
pause
