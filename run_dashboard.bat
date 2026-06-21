@echo off
cd /d "%~dp0"

echo Cleaning up duplicate background processes...
powershell -Command "Get-CimInstance Win32_Process -Filter \"name='python.exe' and CommandLine like '%%web_dashboard.py%%'\" | Stop-Process -Force" 2>nul

set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1
title Daily Dashboard

if exist "C:\miniconda\envs\DJ\python.exe" (
    "C:\miniconda\envs\DJ\python.exe" web_dashboard.py
    pause
    exit /b %ERRORLEVEL%
)

call "C:\miniconda\Scripts\activate.bat" DJ
python web_dashboard.py
pause
