@echo off
setlocal
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "scripts\build_windows.ps1" %*
exit /b %errorlevel%
