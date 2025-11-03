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
python3 -m PyInstaller DNA-Bot-Expulsion.spec

echo ""
echo "Build complete! Check the 'dist' folder for DNA-Bot-Expulsion"
echo ""

