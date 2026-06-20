@echo off
cd /d "%~dp0"
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
