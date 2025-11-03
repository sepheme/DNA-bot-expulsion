# DNA Bot Expulsion

## Overview
DNA Bot Expulsion is a Python application designed to automate interactions with the "Duet Night Abyss" game. The bot monitors the game window and uses OCR (Optical Character Recognition) to detect and click on specific text elements like "Challenge Again" and "Start" buttons.

## Features
- **Window Detection**: Automatically finds and activates the Duet Night Abyss game window
- **OCR-Based Interaction**: Uses Tesseract OCR to detect text on screen
- **Automated Clicking**: Clicks on detected buttons automatically
- **Hotkey Control**: Toggle the bot on/off with a simple keypress
- **Thread-Safe**: Runs in a separate thread to prevent blocking

## Requirements
- Python 3.x
- Tesseract OCR (must be installed separately)
  - Windows: Download from [Tesseract GitHub](https://github.com/UB-Mannheim/tesseract/wiki)
  - Default installation path: `C:\Program Files\Tesseract-OCR\tesseract.exe`

## Project Structure
```
DNA-bot-expulsion/
├── main.py              # Main application logic and bot functionality
├── assets/
│   └── img/            # Image assets used by the application
├── requirements.txt     # Python dependencies for the project
├── pyinstaller.spec     # Configuration for creating executable files
├── scripts/
│   └── build_exe.bat   # Batch script for building the executable on Windows
├── start.bat           # Quick start script
├── README.md           # Documentation for the project
└── LICENSE             # Licensing information
```

## Installation
1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd DNA-bot-expulsion
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Install Tesseract OCR:
   - **Windows**: Download and install from [Tesseract GitHub](https://github.com/UB-Mannheim/tesseract/wiki)
   - **macOS**: `brew install tesseract`
   - **Linux**: `sudo apt-get install tesseract-ocr` (Ubuntu/Debian)

4. **Important**: Update the Tesseract path in `main.py` if your installation differs:
   ```python
   pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
   ```

## Usage
1. Start the game "Duet Night Abyss"
2. Run the bot:
   ```bash
   python main.py
   ```
   Or on Windows:
   ```bash
   start.bat
   ```

3. **Controls**:
   - Press **F4** to toggle the bot on/off
   - Press **Ctrl+C** to exit the application

4. The bot will:
   - Find and activate the game window automatically
   - Search for "Challenge Again" text and click it when found
   - Search for "Start" text and click it when found
   - Continuously loop until stopped

## Configuration
You can adjust the following settings in `main.py`:
- `CONFIDENCE`: Image detection confidence level (currently 0.6)
- `app`: Window title to search for (default: "Duet Night Abyss  ")
- Tesseract OCR path: Update if installed in a different location

## Building Executable
To create a standalone executable file for Windows:

```bash
scripts/build_exe.bat
```

Note: The executable will require Tesseract OCR to be installed on the target system.

## Troubleshooting
- **Game window not found**: Ensure the game is running and the window title matches exactly (check for trailing spaces)
- **OCR not working**: Verify Tesseract OCR is installed and the path in `main.py` is correct
- **Buttons not clicking**: Check that the game window is visible and not minimized

## License
This project is licensed under the MIT License. See the LICENSE file for more details.