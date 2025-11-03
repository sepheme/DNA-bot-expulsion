# Building DNA Bot Expulsion Executable

## Prerequisites

1. Install Python 3.7 or higher
2. Install all required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Building the Executable

### Windows

1. Open Command Prompt or PowerShell in the project directory
2. Run the build script:
   ```bash
   scripts\build_exe.bat
   ```
   
   Or manually run:
   ```bash
   pyinstaller --onefile --console --name "DNA-Bot-Expulsion" --icon=NONE --add-data "assets;assets" --hidden-import=win10toast --hidden-import=pynput.keyboard --hidden-import=pyautogui --hidden-import=pygetwindow --hidden-import=tkinter main.py
   ```

3. The executable will be created in the `dist` folder: `DNA-Bot-Expulsion.exe`

### macOS/Linux

1. Open Terminal in the project directory
2. Make the build script executable:
   ```bash
   chmod +x scripts/build_exe.sh
   ```
3. Run the build script:
   ```bash
   ./scripts/build_exe.sh
   ```

## PyInstaller Options Explained

- `--onefile`: Creates a single executable file
- `--windowed`: Prevents console window from showing (Windows only)
- `--name`: Sets the output executable name
- `--add-data`: Includes the assets folder with images
- `--hidden-import`: Ensures these modules are included in the bundle

## Including Assets

The build script automatically includes the `assets` folder containing all image files needed for button detection.

## Distribution

After building, you can distribute:
- Windows: `dist/DNA-Bot-Expulsion.exe` (and the assets folder if not bundled)
- The executable is standalone and includes all dependencies

## Troubleshooting

If the executable doesn't work:
1. Make sure all assets are included (check `assets/buttons/` folder exists)
2. Run from command line to see error messages:
   ```bash
   DNA-Bot-Expulsion.exe
   ```
3. Check that all image files are present in the assets folder

## Notes

- On Windows, you may need to run as Administrator for keyboard input to work
- The executable will show Windows notifications when F4 is pressed to start/stop the bot
- Make sure the game window is visible and matches the expected window title

