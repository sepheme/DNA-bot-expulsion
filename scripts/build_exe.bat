@echo off
echo Building DNA Bot Expulsion executable...
echo.

REM Change to project root directory
cd /d "%~dp0.."

REM Check if PyInstaller is installed
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo Installing PyInstaller...
    python -m pip install pyinstaller
)

echo.
echo Creating executable...
python -m PyInstaller DNA-Bot-Expulsion.spec

echo.
echo Build complete! Check the 'dist' folder for DNA-Bot-Expulsion.exe
echo.
pause

