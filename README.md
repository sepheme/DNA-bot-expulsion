# DNA Bot Expulsion

## Overview
DNA Bot Expulsion is a Python application designed to automate interactions with the "Duet Night Abyss" game. The bot listens for specific window titles and performs actions based on the presence of certain images on the screen.

## Project Structure
```
DNA-bot-expulsion
├── src
│   ├── main.py          # Main application logic and bot functionality
│   ├── bot.py           # Additional bot-related functions and classes
│   └── assets
│       └── img         # Image assets used by the application
├── requirements.txt     # Python dependencies for the project
├── pyinstaller.spec     # Configuration for creating executable files
├── scripts
│   ├── build_exe.bat    # Batch script for building the executable on Windows
│   └── build_exe.sh     # Shell script for building the executable on Unix-like systems
├── .gitignore           # Files and directories to ignore in Git
├── README.md            # Documentation for the project
└── LICENSE              # Licensing information
```

## Installation
1. Clone the repository:
   ```
   git clone <repository-url>
   cd DNA-bot-expulsion
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage
- Run the application by executing `src/main.py`.
- Use the F1 key to toggle the bot on and off.
- Press ESC to exit the application.

## Building Executable
To create an executable file from the application, use the provided scripts:
- For Windows:
  ```
  scripts/build_exe.bat
  ```
- For Unix-like systems:
  ```
  scripts/build_exe.sh
  ```

## License
This project is licensed under the MIT License. See the LICENSE file for more details.