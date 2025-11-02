import pyautogui as pag
import pygetwindow as pgw
import time
import os
import threading
import tkinter as tk
from tkinter import messagebox
from pynput.keyboard import Key, Listener

# Configuration
CONFIDENCE = 0.6  # Confidence level for image detection (0.0 to 1.0, higher = more exact match)
app = "Duet Night Abyss  "

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CHALLENGE_PATH = os.path.join(BASE_DIR, "assets", "img", "challenge_again.png")
START_PATH = os.path.join(BASE_DIR, "assets", "img", "start.png")

# Window info
allTitles = pgw.getAllTitles()
allWindows = pgw.getAllWindows()

# Hidden tkinter root for messageboxes
root = tk.Tk()
root.withdraw()

# Thread control
_stop_event = threading.Event()
_worker_thread = None
_worker_lock = threading.Lock()

def run_app(stop_event):
    """Main bot loop running in a background thread. Exits when stop_event is set."""
    print("Bot thread started.")
    
    def find_game_window():
        """Find and activate the game window."""
        try:
            windows = pgw.getWindowsWithTitle(app)
            if windows:
                game_window = windows[0]
                print(f"Found game window: {game_window.title}")
                
                # Get current window position and size
                current_x = game_window.left
                current_y = game_window.top
                current_width = game_window.width
                current_height = game_window.height
                
                # Check if window needs repositioning or resizing
                if not game_window.isActive:
                    print("Activating game window...")
                    game_window.activate()
                    time.sleep(0.2)  # Small delay after activation
                
                return game_window
            return None
        except Exception as e:
            print(f"Error finding game window: {str(e)}")
            return None

    def check_and_click_button(image_path, button_name, confidence=0.9):
        """Try to find and click a button in the game window."""
        try:
            print(f"Searching for '{button_name}' at: {image_path}")
            print(f"Using confidence level: {confidence} (higher = more exact match)")
            
            if not os.path.exists(image_path):
                print(f"ERROR: Image file not found: {image_path}")
                return False
                
            try:
                loc = pag.locateOnWindow(
                    image_path, 
                    app, 
                    confidence=confidence, 
                    grayscale=True
                )
                print(f"Image search completed with confidence={confidence}")
                
                if loc is not None:
                    print(f"Match found for '{button_name}':")
                    print(f"- Position: {loc}")
                    print(f"- Confidence threshold met: {confidence}")
                    
                    # Click in the center of the detected region
                    target_x = loc[0] + (loc[2] // 2)  # loc[2] is width
                    target_y = loc[1] + (loc[3] // 2)  # loc[3] is height
                    print(f"Moving mouse to center position: ({target_x}, {target_y})")
                    print(f"Image dimensions: {loc[2]}x{loc[3]} pixels")
                    pag.moveTo(target_x, target_y)
                    pag.click()
                    print(f"Successfully clicked '{button_name}' at center")
                    return True
                else:
                    print(f"No match found for '{button_name}' with confidence={confidence}")
                    print("Try adjusting the confidence level if the button exists but isn't being detected")
                    return False
                    
            except Exception as e:
                if "OpenCV" in str(e):
                    print("OpenCV Error: Make sure opencv-python is installed correctly")
                    print("Try running: pip install opencv-python")
                raise e
                
        except Exception as e:
            print(f"Error while searching for '{button_name}':")
            print(f"- Error type: {type(e).__name__}")
            print(f"- Error message: {str(e)}")
            print(f"- Image path: {image_path}")
            print(f"- Confidence level: {confidence}")
            return False

    while not stop_event.is_set():
        try:
            # Find and activate game window
            game_window = find_game_window()
            
            if not game_window:
                print(f"Game window '{app}' not found. Waiting...")
                time.sleep(1.0)
                continue
                
            # First check for Challenge Again button
            challenge_clicked = check_and_click_button(CHALLENGE_PATH, "Challenge Again", CONFIDENCE)
            if challenge_clicked:
                print("Challenge Again button clicked, waiting before checking Start button...")
                time.sleep(1.75)
                
                # Only check for Start button if Challenge Again was clicked
                start_clicked = check_and_click_button(START_PATH, "Start", CONFIDENCE)
                if start_clicked:
                    print("Start button clicked, waiting for next cycle...")
                    time.sleep(1.75)
                
        except Exception as e:
            print(f"Error in bot loop: {e}")
            time.sleep(1.0)
    
    print("Bot thread stopping.")

def start_bot():
    global _worker_thread, _stop_event
    print("Attempting to start bot...")
    with _worker_lock:
        if _worker_thread is not None and _worker_thread.is_alive():
            print("Bot is already running!")
            return False
        print("Creating new bot thread...")
        _stop_event.clear()
        _worker_thread = threading.Thread(target=run_app, args=(_stop_event,), daemon=True)
        _worker_thread.start()
        print("Bot thread created and started")
        return True

def stop_bot():
    global _worker_thread, _stop_event
    with _worker_lock:
        if _worker_thread is None or not _worker_thread.is_alive():
            return False
        _stop_event.set()
        _worker_thread.join(timeout=5.0)
        return True

def notify(message, title="Application Notification"):
    try:
        messagebox.showinfo(title, message)
    except Exception:
        # If tkinter pop-up fails, fallback to print
        print(message)

def on_press(key):
    """Toggle bot on F1 press."""
    try:
        if key == Key.f1:
            # Toggle start/stop
            started = start_bot()
            if started:
                print(">>> F1 pressed — bot started.")
                notify("Bot started. Press F1 again to stop.")
            else:
                stopped = stop_bot()
                if stopped:
                    print(">>> F1 pressed — bot stopped.")
                    notify("Bot stopped.")
                else:
                    # If start failed because already running, attempt to stop
                    notify("Bot is already running or stopping. Press F1 again to toggle.")
    except Exception as e:
        print(f"Keyboard handler error: {e}")

if __name__ == "__main__":
    print("-" * 50)
    print("F1 toggles the bot on/off.")
    print("Press Ctrl+C to exit")
    print("-" * 50)

    # Start global keyboard listener in background and block main thread on join
    listener = Listener(on_press=on_press)
    listener.start()
    
    try:
        # Keep the main thread alive
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nCtrl+C detected - shutting down...")
        # Stop the bot if it's running
        stop_bot()
        # Stop the keyboard listener
        listener.stop()
        print("Cleanup complete. Exiting...")