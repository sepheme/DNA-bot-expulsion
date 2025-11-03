#!/bin/bash

echo "Building DNA Bot Expulsion executable..."
echo ""

# Change to project root directory
cd "$(dirname "$0")/.."

# Check if PyInstaller is installed
if ! python3 -c "import PyInstaller" 2>/dev/null; then
    echo "Installing PyInstaller..."
    pip3 install pyinstaller
fi

echo ""
echo "Creating executable..."
python3 -m PyInstaller --onefile --name "DNA-Bot-Expulsion" \
    --add-data "assets:assets" \
    --hidden-import=win10toast \
    --hidden-import=pynput.keyboard \
    --hidden-import=pyautogui \
    --hidden-import=pygetwindow \
    --hidden-import=tkinter \
    main.py

echo ""
echo "Build complete! Check the 'dist' folder for DNA-Bot-Expulsion"
echo ""

