@echo off
REM This script builds the executable for the DNA bot application using PyInstaller.

REM Navigate to the project root directory
cd /d "%~dp0.."

REM Use PyInstaller with the spec file to create the executable
pyinstaller pyinstaller.spec

REM Move the generated executable to the scripts directory
if exist "dist\DNA-bot-expulsion.exe" (
    move /Y "dist\DNA-bot-expulsion.exe" "scripts\DNA-bot-expulsion.exe"
    echo Build complete! The executable is located in the scripts directory.
) else (
    echo ERROR: Executable not found in dist directory!
    echo Expected: dist\DNA-bot-expulsion.exe
    exit /b 1
)

REM Clean up the build files
if exist "build" rmdir /s /q build
if exist "dist" rmdir /s /q dist

echo.
echo Build process completed successfully!
pause