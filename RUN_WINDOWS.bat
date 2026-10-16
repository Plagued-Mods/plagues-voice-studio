@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>&1 || (echo Install Python 3.11 first. & exit /b 1)
if not exist ".venv\Scripts\python.exe" (
  py -3.11 -m venv .venv
  if errorlevel 1 exit /b 1
  ".venv\Scripts\python.exe" -m pip install --upgrade pip
  ".venv\Scripts\python.exe" -m pip install -e .
  if errorlevel 1 exit /b 1
)
".venv\Scripts\python.exe" launcher.py
