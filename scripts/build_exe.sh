#!/bin/bash

# Navigate to the project directory
cd "$(dirname "$0")/.."

# Create the executable using PyInstaller
pyinstaller --onefile --windowed src/main.py

# Move the executable to the desired location (optional)
mv dist/main ../

# Clean up build files
rm -rf build dist src/*.spec

echo "Executable built successfully!"