# DNA Bot Expulsion

Automated bot for Duet Night Abyss game that handles challenge loops, wave management, and window switching.

[![Latest Release](https://img.shields.io/github/v/release/sepheme/DNA-bot-expulsion?label=Latest%20Release&style=for-the-badge)](https://github.com/sepheme/DNA-bot-expulsion/releases/latest)

**Download the latest executable:** [Latest Release](https://github.com/sepheme/DNA-bot-expulsion/releases/latest)

## Table of Contents

- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
  - [Windows](#windows)
  - [Running the Bot](#running-the-bot)
- [Configuration](#configuration)
  - [Key Press Configuration](#key-press-configuration)
  - [Feature Flags](#feature-flags)
  - [Image Recognition Confidence](#image-recognition-confidence)
- [Required Assets](#required-assets)
- [How It Works](#how-it-works)
- [Building Executable](#building-executable)
  - [Download Pre-built Executable (Recommended)](#download-pre-built-executable-recommended)
  - [Build Locally](#build-locally)
- [Notes](#notes)
- [Known Issues](#known-issues)
- [Contributing](#contributing)
- [Troubleshooting](#troubleshooting)
- [Dependencies](#dependencies)
- [License](#license)

## Features

- **Automatic Window Detection**: Automatically finds and switches to the game window using Alt+Tab (optional, configurable)
- **Window Management**: Automatically resizes and repositions game window to 1920x1080 at (0,0) (optional, configurable)
- **Challenge Loop Automation**: Automatically clicks "Challenge Again" and "Start" buttons
- **Wave Management**: Intelligently handles Continue/Retreat based on wave detection (Wave 8)
- **Random Key Presses**: Optional feature to press configurable movement keys (default: W, A, S, D) randomly when buttons are not found
- **Windows Notifications**: Optional Windows toast notifications for bot status
- **Keyboard Controls**: Press F4 to start/stop the bot instantly (can interrupt key pressing), Ctrl+C to exit
- **Robust Mouse Control**: Uses fallback chain (pyautogui → pynput → pydirectinput) for reliable clicking
- **Thread-safe**: Runs in background thread, can be started/stopped at any time
- **Window Locking**: Locks onto the game window at startup for consistent operation

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

**Step-by-step instructions:**

1. **First, run the EXE** (executable file):
   - Right-click on the downloaded executable
   - Select "Run as administrator"
   - The bot will start and wait for keyboard input

2. **Then, run DNA** (Duet Night Abyss game):
   - Launch the game normally

3. **Navigate to combat and choose commissions**:
   - Go to Combat section in the game
   - Select commissions that are infinite and can be AFK farmable:
     - **Expulsion** for Demon Wedge Farming
     - **Exploration** (with minimal human intervention at the start)
   - Enter the selected commission

4. **Once in the commission, control the bot**:
   - Press **F4** to start the bot
   - Press **F4** again to stop the bot instantly (can interrupt key pressing)
   - Press **Ctrl+C** to exit the program

## Configuration

All configuration variables are located in `config.json` for easy modification. **Make sure `config.json` is in the same directory as the executable or script.** The configuration file includes:

### Key Press Configuration
- `key_press.min_key_presses` / `key_press.max_key_presses`: Range for random key presses (default: 15-25)
- `key_press.min_key_delay` / `key_press.max_key_delay`: Delay between key presses in seconds (default: 0.1-0.3)
- `key_press.min_key_hold_time` / `key_press.max_key_hold_time`: Time to hold each key down in seconds (default: 0.05-0.15)
- `key_press.movement_array`: Array of keys to press randomly (default: `["w", "a", "s", "d"]`)

### Feature Flags
- `features.enable_random_key_presses`: Enable random key presses from movement_array when buttons not found (default: `true`)
- `features.enable_notifications`: Enable Windows notifications (default: `true`)
- `features.enable_window_detection`: Enable automatic window detection, activation, and resizing (default: `true`)

### Image Recognition Confidence
- `confidence.challenge_start`: Confidence for Challenge Again and Start buttons (default: `0.9`)
- `confidence.continue_retreat`: Confidence for Continue and Retreat buttons (default: `0.8`)
- `confidence.wave8`: Confidence for Wave 8 detection (default: `0.99`)

### Window Configuration
- `window.target_x` / `window.target_y`: Target window position (default: 0, 0)
- `window.target_width` / `window.target_height`: Target window size (default: 1920x1080)

## Required Assets

The bot requires image assets in the `assets/img/` directory:
- `challenge_again.png` - Challenge Again button
- `start.png` - Start button
- `continue.png` - Continue button
- `retreat.png` - Retreat button
- `wave_8.png` - Wave 8 indicator
- `wave_06.png` - Wave 6 indicator (optional)

## How It Works

1. **Admin Check**: On Windows, checks if running as administrator (exits if not)
2. **Window Locking**: On startup, searches for and locks onto the game window titled "Duet Night Abyss"
3. **Window Management** (if enabled): Resizes window to configured size and moves to configured position
4. **Auto-switch**: If the game window is not active, it performs Alt+Tab to switch to it (if enabled)
5. **Image Recognition**: Uses PyAutoGUI with OpenCV to locate buttons on screen by matching images
6. **Mouse Clicking**: Uses fallback chain:
   - First tries `pyautogui`
   - Falls back to `pynput.mouse` if pyautogui fails
   - Falls back to `pydirectinput` if pynput fails
7. **Random Key Presses** (if enabled): When buttons are not found, presses keys from `movement_array` randomly (default: W, A, S, D)
8. **Wave Logic**: 
   - Only checks for waves when both Continue and Retreat buttons are visible
   - If Wave 6 or Wave 8 is detected → clicks Retreat
   - If no wave is detected → clicks Continue
9. **Loop**: Continuously checks for buttons and clicks them when found
10. **Instant Stop**: F4 can interrupt the bot immediately, even during key pressing

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
- **Configuration**: The bot requires `config.json` in the same directory as the executable/script
- Make sure the game window is visible and the images match your screen resolution
- The bot uses image matching, so ensure your game UI matches the reference images
- On Windows, administrator privileges are required for mouse/keyboard simulation
- Mouse clicking uses a fallback chain to ensure reliability across different systems
- The bot locks onto the game window at startup - make sure the game is running before starting the bot

## Known Issues

- **Stuck enemies**: Due to unpredictable spawn locations, enemies may sometimes get stuck, requiring human intervention to resolve.

## Contributing

If you're interested in collaborating and improving this project, feel free to make a PR (Pull Request)! Contributions are welcome.

## Troubleshooting

- **"Administrator privileges are required" error**: Run the script/executable as Administrator on Windows
- **"config.json not found" error**: Ensure `config.json` is in the same directory as the executable or script
- **Bot not finding game window**: Make sure the game is running before starting the bot. The bot locks onto the window at startup.
- **Buttons not being clicked**: 
  - Check that the image files in `assets/img/` match your game's UI
  - Try adjusting confidence levels in `config.json`
  - Check console logs to see which mouse click method is being used
- **Window switching issues**: Ensure you have proper permissions and `enable_window_detection` is set to `true` in `config.json`
- **Mouse clicks not working**: The bot uses a fallback chain - check console logs to see which method succeeded/failed
- **Bot not stopping immediately**: Press F4 again - it should interrupt within a fraction of a second

## Dependencies

- `pyautogui` - GUI automation and image recognition
- `opencv-python` - Required for PyAutoGUI's confidence parameter
- `pygetwindow` - Window management
- `pynput` - Keyboard and mouse control (fallback)
- `pydirectinput-rgx` - DirectInput for game compatibility (fallback)
- `win10toast` - Windows toast notifications (optional)
- `pywin32` - Windows API access (Windows only)
- `pyinstaller` - Building executables

## License

[Add your license here]
