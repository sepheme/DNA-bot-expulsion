# DNA Bot Expulsion

Automated bot for Duet Night Abyss game that handles challenge loops, wave management, and window switching.

[![Latest Release](https://img.shields.io/github/v/release/sepheme/DNA-bot-expulsion?label=Latest%20Release&style=for-the-badge)](https://github.com/sepheme/DNA-bot-expulsion/releases/latest)

**Download the latest executable:** [Latest Release](https://github.com/sepheme/DNA-bot-expulsion/releases/latest)

## Features

- **Automatic Window Detection**: Automatically finds and switches to the game window using Alt+Tab (optional, configurable)
- **Window Management**: Automatically resizes and repositions game window to 1920x1080 at (0,0) (optional, configurable)
- **Challenge Loop Automation**: Automatically clicks "Challenge Again" and "Start" buttons
- **Wave Management**: Intelligently handles Continue/Retreat based on wave detection (Wave 8)
- **Random Key Presses**: Optional feature to press W and D keys randomly when buttons are not found
- **Windows Notifications**: Optional Windows toast notifications for bot status
- **Keyboard Controls**: Press F4 to start/stop the bot, Ctrl+C to exit
- **Robust Mouse Control**: Uses fallback chain (pyautogui → pynput → pydirectinput) for reliable clicking
- **Thread-safe**: Runs in background thread, can be started/stopped at any time

## Requirements

- Python 3.7 or higher
- **Windows**: Requires administrator privileges (run as Administrator)
- macOS/Linux: No special privileges required

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd DNA-bot-expulsion
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Windows

**IMPORTANT**: On Windows, you must run the script/executable as Administrator:

1. Right-click on `main.py` or the compiled executable
2. Select "Run as administrator"
3. Or run Command Prompt as Administrator and execute from there

### Running the Bot

1. Make sure the game "Duet Night Abyss" is running
2. Run the bot:
```bash
python main.py
```

3. **Controls**:
   - Press **F4** to start/stop the bot
   - Press **Ctrl+C** to exit the program

## Configuration

All configuration variables are located at the top of `main.py` (lines 14-37) for easy modification:

### Key Press Configuration
- `MIN_KEY_PRESSES` / `MAX_KEY_PRESSES`: Range for random key presses (default: 15-25)
- `MIN_KEY_DELAY` / `MAX_KEY_DELAY`: Delay between key presses in seconds (default: 0.1-0.3)
- `MIN_KEY_HOLD_TIME` / `MAX_KEY_HOLD_TIME`: Time to hold each key down in seconds (default: 0.05-0.15)

### Feature Flags
- `ENABLE_RANDOM_KEY_PRESSES`: Enable random W/D key presses when buttons not found (default: `False`)
- `ENABLE_NOTIFICATIONS`: Enable Windows toast notifications (default: `False`)
- `ENABLE_WINDOW_DETECTION`: Enable automatic window detection, activation, and resizing (default: `False`)

### Image Recognition Confidence
- `CONFIDENCE_CHALLENGE_START`: Confidence for Challenge Again and Start buttons (default: `0.9`)
- `CONFIDENCE_CONTINUE_RETREAT`: Confidence for Continue and Retreat buttons (default: `0.8`)
- `CONFIDENCE_WAVE8`: Confidence for Wave 8 detection (default: `0.99`)

## Required Assets

The bot requires image assets in the `assets/img/` directory:
- `challenge_again.png` - Challenge Again button
- `start.png` - Start button
- `continue.png` - Continue button
- `retreat.png` - Retreat button
- `wave8.png` - Wave 8 indicator
- `wave_06.png` - Wave 6 indicator (optional)

## How It Works

1. **Admin Check**: On Windows, checks if running as administrator (exits if not)
2. **Window Detection**: The bot searches for the game window titled "Duet Night Abyss"
3. **Window Management** (if enabled): Resizes window to 1920x1080 and moves to (0,0)
4. **Auto-switch**: If the game window is not active, it performs Alt+Tab to switch to it (if enabled)
5. **Image Recognition**: Uses PyAutoGUI to locate buttons on screen by matching images
6. **Mouse Clicking**: Uses fallback chain:
   - First tries `pyautogui`
   - Falls back to `pynput.mouse` if pyautogui fails
   - Falls back to `pydirectinput` if pynput fails
7. **Random Key Presses** (if enabled): When buttons are not found, presses W and D keys randomly
8. **Wave Logic**: 
   - If Wave 8 is detected → clicks Retreat
   - If Wave 8 is not detected → clicks Continue
9. **Loop**: Continuously checks for buttons and clicks them when found

## Building Executable

### Download Pre-built Executable (Recommended)

**Option 1: Download from Releases (Recommended)**

The easiest way to get the latest executable is from the [Releases](https://github.com/sepheme/DNA-bot-expulsion/releases/latest) page:

1. Go to the [Latest Release](https://github.com/sepheme/DNA-bot-expulsion/releases/latest) page
2. Download the `DNA-<timestamp>.exe` file from the assets section
3. Right-click and select "Run as administrator"

Releases are automatically created when version tags (e.g., `v1.0.0`) are pushed to the repository.

**Option 2: Build via GitHub Actions**

You can also manually trigger a build via GitHub Actions:

1. Go to the **Actions** tab in the GitHub repository
2. Select the **Build Windows Executable and Release** workflow
3. Click **Run workflow** button (on the right side)
4. Select the branch (usually `main` or `master`)
5. Click **Run workflow** to start the build
6. Once the workflow completes, scroll down to **Artifacts**
7. Download the executable from the artifacts

**Note:** To create a release, push a version tag (e.g., `v1.0.0`):
```bash
git tag v1.0.0
git push origin v1.0.0
```

### Build Locally

To build a standalone executable locally:

**Windows:**
```bash
cd scripts
build_exe.bat
```

**macOS/Linux:**
```bash
cd scripts
chmod +x build_exe.sh
./build_exe.sh
```

The executable will be created in the `dist/` directory.

## Notes

- The bot runs in a background thread, so it won't block your terminal
- Make sure the game window is visible and the images match your screen resolution
- The bot uses image matching, so ensure your game UI matches the reference images
- On Windows, administrator privileges are required for mouse/keyboard simulation
- Mouse clicking uses a fallback chain to ensure reliability across different systems

## Troubleshooting

- **"Administrator privileges are required" error**: Run the script/executable as Administrator on Windows
- **Bot not finding game window**: Make sure the game is running and the window title matches "Duet Night Abyss  "
- **Buttons not being clicked**: 
  - Check that the image files in `assets/img/` match your game's UI
  - Try adjusting confidence levels in configuration
  - Check console logs to see which mouse click method is being used
- **Window switching issues**: Ensure you have proper permissions and `ENABLE_WINDOW_DETECTION` is set to `True`
- **Mouse clicks not working**: The bot uses a fallback chain - check console logs to see which method succeeded/failed

## Dependencies

- `pyautogui` - GUI automation and image recognition
- `pygetwindow` - Window management
- `pynput` - Keyboard and mouse control (fallback)
- `pydirectinput-rgx` - DirectInput for game compatibility (fallback)
- `win10toast` - Windows toast notifications (optional)
- `pywin32` - Windows API access (Windows only)
- `pyinstaller` - Building executables

## License

[Add your license here]
