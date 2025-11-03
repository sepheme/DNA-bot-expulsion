# DNA Bot Expulsion

Automated bot for Duet Night Abyss game that handles challenge loops, wave management, and window switching.

## Features

- **Automatic Window Detection**: Automatically finds and switches to the game window using Alt+Tab
- **Challenge Loop Automation**: Automatically clicks "Challenge Again" and "Start" buttons
- **Wave Management**: Intelligently handles Continue/Retreat based on wave detection (Wave 8)
- **Keyboard Controls**: Press F4 to start/stop the bot, Ctrl+C to exit
- **Thread-safe**: Runs in background thread, can be started/stopped at any time

## Requirements

- Python 3.7 or higher
- Windows, macOS, or Linux

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

1. Make sure the game "Duet Night Abyss" is running
2. Run the bot:
```bash
python main.py
```

3. **Controls**:
   - Press **F4** to start/stop the bot
   - Press **Ctrl+C** to exit the program

## Required Assets

The bot requires image assets in the `assets/img/` directory:
- `challenge_again.png` - Challenge Again button
- `start.png` - Start button
- `continue.png` - Continue button
- `retreat.png` - Retreat button
- `wave8.png` - Wave 8 indicator
- `wave_06.png` - Wave 6 indicator (optional)

## How It Works

1. **Window Detection**: The bot searches for the game window titled "Duet Night Abyss"
2. **Auto-switch**: If the game window is not active, it performs Alt+Tab to switch to it
3. **Image Recognition**: Uses PyAutoGUI to locate buttons on screen by matching images
4. **Wave Logic**: 
   - If Wave 8 is detected → clicks Retreat
   - If Wave 8 is not detected → clicks Continue
5. **Loop**: Continuously checks for buttons and clicks them when found

## Notes

- The bot runs in a background thread, so it won't block your terminal
- Make sure the game window is visible and the images match your screen resolution
- The bot uses image matching, so ensure your game UI matches the reference images

## Troubleshooting

- **Bot not finding game window**: Make sure the game is running and the window title matches "Duet Night Abyss  "
- **Buttons not being clicked**: Check that the image files in `assets/img/` match your game's UI
- **Window switching issues**: Ensure you have proper permissions for keyboard simulation

## License

[Add your license here]

