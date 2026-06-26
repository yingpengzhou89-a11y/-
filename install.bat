@echo off
setlocal

cd /d "%~dp0"
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1

echo Installing Daily Dashboard dependencies...
echo.

set "BOOTSTRAP_PY="

where py >nul 2>nul
if not errorlevel 1 (
    set "BOOTSTRAP_PY=py -3"
)

if not defined BOOTSTRAP_PY (
    where python >nul 2>nul
    if not errorlevel 1 (
        set "BOOTSTRAP_PY=python"
    )
)

if not defined BOOTSTRAP_PY (
    echo Python was not found. Please install Python 3.9+ first.
    pause
    exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
    echo Creating virtual environment: .venv
    %BOOTSTRAP_PY% -m venv .venv
    if errorlevel 1 goto FAIL
)

echo Upgrading pip...
".venv\Scripts\python.exe" -m pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple
if errorlevel 1 goto FAIL

echo Installing requirements...
".venv\Scripts\python.exe" -m pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
if errorlevel 1 goto FAIL

echo.
echo Configuring MuMu / ADB path...
".venv\Scripts\python.exe" configure_adb.py
if errorlevel 1 goto FAIL

echo.
echo Running environment check...
".venv\Scripts\python.exe" check_env.py
if errorlevel 1 goto FAIL

echo.
echo Installation finished.
pause
exit /b 0

:FAIL
echo.
echo Installation failed. Please copy the error above and send it for diagnosis.
pause
exit /b 1
