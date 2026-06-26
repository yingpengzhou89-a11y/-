@echo off
setlocal

cd /d "%~dp0"
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1
title Daily Dashboard

echo Starting Daily Dashboard...

if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" check_env.py
    if errorlevel 1 goto END
    ".venv\Scripts\python.exe" web_dashboard.py
    goto END
)

where py >nul 2>nul
if not errorlevel 1 (
    py -3 check_env.py
    if errorlevel 1 goto END
    py -3 web_dashboard.py
    goto END
)

where python >nul 2>nul
if not errorlevel 1 (
    python check_env.py
    if errorlevel 1 goto END
    python web_dashboard.py
    goto END
)

echo Python was not found.
echo Please install Python 3, or create .venv in this project folder.

:END
echo.
echo Dashboard stopped or failed to start.
pause
