@echo off
cd /d "%~dp0"

echo ==========================================
echo   Investment Research AI
echo ==========================================
echo.

py --version >nul 2>&1
if errorlevel 1 (
    echo Python was not found.
    echo Please install Python 3 first, then run this file again.
    echo.
    pause
    exit /b 1
)

echo Checking dependencies...
py -m pip install -r requirements.txt --quiet

if errorlevel 1 (
    echo.
    echo Dependency installation failed.
    echo Please check your network connection and Python environment.
    echo.
    pause
    exit /b 1
)

echo Running code checks...
py -m py_compile app.py main.py
if errorlevel 1 (
    echo.
    echo Python syntax check failed.
    pause
    exit /b 1
)

py -m pyflakes app.py main.py
if errorlevel 1 (
    echo.
    echo Static code check failed.
    echo Fix the issue shown above before launching.
    pause
    exit /b 1
)

echo.
echo Starting Investment Research AI...
echo Your browser should open automatically.
echo.

py -m streamlit run app.py

pause
