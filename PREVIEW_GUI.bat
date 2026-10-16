@echo off
setlocal
cd /d "%~dp0"
set "PYTHON_BIN=.venv-build\Scripts\python.exe"
if not exist "%PYTHON_BIN%" set "PYTHON_BIN=.venv\Scripts\python.exe"
if not exist "%PYTHON_BIN%" (
  echo No project Python environment found in this folder.
  echo Run RUN_WINDOWS.bat once to set up the development environment.
  pause
  exit /b 1
)
echo Previewing the current Plague's Voice Studio source GUI.
echo This does not rebuild the executable or download model weights.
"%PYTHON_BIN%" launcher.py
if errorlevel 1 (
  echo Source launch returned an error. Read the traceback above.
  pause
)
endlocal
