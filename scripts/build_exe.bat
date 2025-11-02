@echo off
REM This script builds the executable for the DNA bot application using PyInstaller.

REM Navigate to the src directory
cd ..\src

REM Use PyInstaller to create the executable
pyinstaller --onefile --windowed main.py

REM Move the generated executable to the scripts directory
move dist\main.exe ..\scripts

REM Clean up the build files
rmdir /s /q build
rmdir /s /q dist
del main.spec

echo Build complete! The executable is located in the scripts directory.