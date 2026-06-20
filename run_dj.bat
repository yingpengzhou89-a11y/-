@echo off
setlocal

cd /d "%~dp0"
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1

if exist "C:\miniconda\envs\DJ\python.exe" (
    if /I "%~x1"==".py" (
        "C:\miniconda\envs\DJ\python.exe" %*
    ) else (
        "C:\miniconda\envs\DJ\python.exe" daily_tasks.py %*
    )
    exit /b %ERRORLEVEL%
)

call "C:\miniconda\Scripts\activate.bat" DJ
if /I "%~x1"==".py" (
    python %*
) else (
    python daily_tasks.py %*
)
