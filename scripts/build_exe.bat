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
python -m PyInstaller --onefile --console --name "DNA-Bot-Expulsion" --icon=NONE ^
    --add-data "assets;assets" ^
    --hidden-import=win10toast ^
    --hidden-import=pynput.keyboard ^
    --hidden-import=pyautogui ^
    --hidden-import=pygetwindow ^
    --hidden-import=tkinter ^
    --hidden-import=win10toast.toast ^
    --collect-all=win10toast ^
    main.py

echo.
echo Build complete! Check the 'dist' folder for DNA-Bot-Expulsion.exe
echo.
pause

