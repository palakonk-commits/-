@echo off
REM Network Impairment Tool - Run as Administrator
REM This script launches the application with admin privileges

REM Check if already running as admin
net session >nul 2>&1
if %errorlevel% neq 0 (
    REM Re-launch as administrator
    powershell -Command "Start-Process cmd -ArgumentList '/c cd /d \"%~dp0\" && python main.py' -Verb RunAs"
    exit /b
)

REM Already admin, run the app
cd /d "%~dp0"

REM Activate virtual environment if it exists
if exist venv (
    call venv\Scripts\activate.bat
)

REM Run the application
echo Launching Network Impairment Tool...
python main.py

pause
