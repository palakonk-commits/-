@echo off
REM Network Impairment Tool - Build Executable
REM Requires PyInstaller: pip install pyinstaller

echo.
echo ============================================================
echo Building Network Impairment Tool as Executable
echo ============================================================
echo.

REM Check for PyInstaller
pyinstaller --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: PyInstaller not found
    echo Install with: pip install pyinstaller
    pause
    exit /b 1
)

echo [1/3] Cleaning old builds...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist *.spec del *.spec

echo [2/3] Building executable...
pyinstaller --onefile ^
  --noconsole ^
  --name "NetworkImpairment" ^
  --add-data "templates;templates" ^
  --add-data "static;static" ^
  --hidden-import=flask ^
  --hidden-import=pydivert ^
  --hidden-import=pystray ^
  --hidden-import=PIL ^
  --distpath=dist ^
  --buildpath=build ^
  main.py

if %errorlevel% neq 0 (
    echo ERROR: Build failed
    pause
    exit /b 1
)

echo [3/3] Build complete!
echo.
echo ============================================================
echo Build successful!
echo ============================================================
echo.
echo Output: dist\NetworkImpairment.exe
echo.
echo To use:
echo 1. Right-click NetworkImpairment.exe
echo 2. Select "Run as administrator"
echo.
echo Or create a shortcut with admin privileges
echo.
pause
