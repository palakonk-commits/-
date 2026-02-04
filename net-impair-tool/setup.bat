@echo off
REM Installation script for Network Impairment Tool
REM This script sets up the development environment

echo.
echo ============================================================
echo Network Impairment Tool - Setup Script
echo ============================================================
echo.

REM Check for Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.10+ from https://www.python.org
    pause
    exit /b 1
)

echo [1/4] Python found: 
python --version

REM Create virtual environment
echo.
echo [2/4] Creating virtual environment...
if exist venv (
    echo Virtual environment already exists
) else (
    python -m venv venv
    if %errorlevel% neq 0 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo [3/4] Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo [4/4] Installing dependencies...
pip install -r requirements.txt --upgrade
if %errorlevel% neq 0 (
    echo WARNING: Some dependencies failed to install
    echo This might be okay if you have limited permissions
)

echo.
echo ============================================================
echo Setup complete!
echo ============================================================
echo.
echo Next steps:
echo 1. Install WinDivert from https://www.reqrypt.org/windivert.html
echo 2. Run with: python main.py (as Administrator)
echo    OR use: run_as_admin.bat
echo.
echo For help, see README.md
echo.
pause
