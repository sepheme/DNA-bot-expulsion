import pyautogui as pag
import pygetwindow as pgw
import time
import os
import sys
import threading
import tkinter as tk
from tkinter import messagebox
from pynput.keyboard import Key, Listener
import pytesseract
from PIL import ImageGrab, ImageFilter
import numpy as np

# Tesseract Setup - dynamically detect path for bundled or standalone execution
if getattr(sys, 'frozen', False):
    # Running as compiled executable (PyInstaller)
    base_path = sys._MEIPASS
    bundled_tesseract = os.path.join(base_path, 'Tesseract-OCR', 'tesseract.exe')
    bundled_tessdata = os.path.join(base_path, 'Tesseract-OCR', 'tessdata')
    if os.path.exists(bundled_tesseract):
        pytesseract.pytesseract.tesseract_cmd = bundled_tesseract
        # Set TESSDATA_PREFIX so Tesseract can find language data files
        if os.path.exists(bundled_tessdata):
            os.environ['TESSDATA_PREFIX'] = os.path.dirname(bundled_tesseract)
        print(f"Using bundled Tesseract: {bundled_tesseract}")
    else:
        # Fallback to system installation if bundled version not found
        default_path = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        if os.path.exists(default_path):
            pytesseract.pytesseract.tesseract_cmd = default_path
        else:
            print("WARNING: Tesseract OCR not found in bundle or system installation!")
else:
    # Running as script - use system installation
    # Try common installation paths
    possible_paths = [
        r'C:\Program Files\Tesseract-OCR\tesseract.exe',
        r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
    ]
    tesseract_found = False
    for path in possible_paths:
        if os.path.exists(path):
            pytesseract.pytesseract.tesseract_cmd = path
            tesseract_found = True
            break
    if not tesseract_found:
        print("WARNING: Tesseract OCR not found in common installation paths.")
        print("Please ensure Tesseract is installed or update the path in main.py")

# Configuration
CONFIDENCE = 0.6  # Confidence level for image detection (0.0 to 1.0, higher = more exact match)
app = "Duet Night Abyss  "

# Paths - handle both frozen executable and script execution
if getattr(sys, 'frozen', False):
    # Running as compiled executable (PyInstaller)
    BASE_DIR = sys._MEIPASS
else:
    # Running as script
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CHALLENGE_PATH = os.path.join(BASE_DIR, "assets", "img", "challenge_again.png")
START_PATH = os.path.join(BASE_DIR, "assets", "img", "start.png")

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

                # First check if game window is active
                if not game_window.isActive:
                    print("Game is not the active window. Performing Alt+Tab once...")
                    # Press Alt+Tab once
                    pag.keyDown('alt')
                    pag.press('tab')
                    pag.keyUp('alt')
                    time.sleep(0.3)  # Give window time to activate
                    
                    # Check if window is now active
                    if game_window.isActive:
                        print("Successfully switched to game window")
                        time.sleep(0.5)  # Let window settle
                    else:
                        print("Game window is still not active after Alt+Tab")
                
                return game_window
            return None
        except Exception as e:
            print(f"Error finding game window: {str(e)}")
            return None

    def check_and_click_text(text_to_find):
        """Try to find and click text in the game window."""
        try:
            # Get the game window position for screenshot
            windows = pgw.getWindowsWithTitle(app)
            if not windows:
                print("Game window not found for screenshot")
                return False
                
            game_window = windows[0]
            region = (
                game_window.left,
                game_window.top,
                game_window.left + game_window.width,
                game_window.top + game_window.height
            )
            
            # Capture the game window
            screenshot = ImageGrab.grab(bbox=region)
            if text_to_find.lower() == "start":
                screenshot = screenshot.convert('L')
                screenshot = screenshot.point(lambda p: 0 if p < 128 else 255)
                width, height = screenshot.size
                left_x = width // 2
                top_y = height // 2
                right_x = width
                bottom_y = height
                crop_box = (left_x, top_y, right_x, bottom_y)
                screenshot = screenshot.crop(crop_box)
            # screenshot = screenshot.filter(ImageFilter.MedianFilter(size=3))
            # Save screenshot for debugging (optional - saves to executable directory when frozen)
            try:
                if getattr(sys, 'frozen', False):
                    # When frozen, save to directory where executable is located
                    exe_dir = os.path.dirname(sys.executable)
                    debug_dir = os.path.join(exe_dir, "debug_screenshots")
                else:
                    # When running as script, save to assets/img/debug
                    debug_dir = os.path.join(BASE_DIR, "assets", "img", "debug")
                os.makedirs(debug_dir, exist_ok=True)
                debug_path = os.path.join(debug_dir, f"{text_to_find}_{int(time.time())}.png")
                screenshot.save(debug_path)
            except Exception:
                # Non-critical - continue even if screenshot save fails
                pass
            
            text = pytesseract.image_to_string(screenshot)
            
            if text_to_find.lower() in text.lower():
                print(f"Found '{text_to_find}' on screen")
                # Get OCR data with positions
                data = pytesseract.image_to_data(screenshot, output_type=pytesseract.Output.DICT)
                
                print("\nDetected text positions:")
                found_position = False
                
                # Print all detected text for debugging
                for i, word in enumerate(data['text']):
                    if word.strip():  # Only print non-empty text
                        print(f"Text: '{word}' at ({data['left'][i]}, {data['top'][i]})")
                        
                        # Look for any part of the text_to_find
                        if any(part in word.lower() for part in text_to_find.lower().split()):
                            # Calculate absolute screen position
                            x = game_window.left + data['left'][i] + (data['width'][i] // 2)
                            y = game_window.top + data['top'][i] + (data['height'][i] // 2)
                            
                            print(f"Moving to click button at ({x}, {y})")
                            pag.moveTo(x, y)
                            pag.click()
                            time.sleep(0.5)  # Short delay after clicking
                            found_position = True
                            break
                
                if not found_position:
                    print("Found text but couldn't determine click position")
                    return False
                return True
                
            print(f"'{text_to_find}' not found")
            return False
            
        except Exception as e:
            print(f"Error while searching for text '{text_to_find}':")
            print(f"- Error type: {type(e).__name__}")
            print(f"- Error message: {str(e)}")
            return False

    while not stop_event.is_set():
        try:
            # Find and activate game window
            game_window = find_game_window()
            
            if not game_window:
                print(f"Game window '{app}' not found. Waiting...")
                time.sleep(1.0)
                continue
                
            # First check for Challenge Again text
            challenge_clicked = check_and_click_text("Challenge Again")
            if challenge_clicked:
                print("Challenge Again text clicked, waiting before checking Start...")
                time.sleep(1.75)
                
            start_clicked = check_and_click_text("Start")
            if start_clicked:
                print("Start text clicked, waiting for next cycle...")
                time.sleep(1.75)
            
            # Small delay between iterations to prevent CPU spinning
            if not challenge_clicked and not start_clicked:
                time.sleep(0.5)
            
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
    """Toggle bot on F4 press."""
    try:
        if key == Key.f4:
            # Toggle start/stop
            started = start_bot()
            if started:
                print(">>> F4 pressed — bot started.")
                notify("Bot started. Press F4 again to stop.")
            else:
                stopped = stop_bot()
                if stopped:
                    print(">>> F4 pressed — bot stopped.")
                    notify("Bot stopped.")
                else:
                    # If start failed because already running, attempt to stop
                    notify("Bot is already running or stopping. Press F4 again to toggle.")
    except Exception as e:
        print(f"Keyboard handler error: {e}")

if __name__ == "__main__":
    print("-" * 50)
    print("F4 toggles the bot on/off.")
    print("Press Ctrl+C to exit")
    print("-" * 50)
    
    # Validate Tesseract is accessible
    try:
        tesseract_version = pytesseract.get_tesseract_version()
        print(f"Tesseract OCR version: {tesseract_version}")
    except Exception as e:
        print(f"ERROR: Tesseract OCR is not accessible: {e}")
        print("Please ensure Tesseract is installed and the path is correct.")
        print("The bot may not work correctly without Tesseract OCR.")
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