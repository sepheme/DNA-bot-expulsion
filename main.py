import pyautogui as pag
import pygetwindow as pgw
import time
import os
import threading
import tkinter as tk
from tkinter import messagebox
from pynput.keyboard import Key, Listener

app = "Duet Night Abyss  "
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CHALLENGE_PATH = os.path.join(BASE_DIR, "assets", "img", "challenge_again.png")
START_PATH = os.path.join(BASE_DIR, "assets", "img", "start.png")
CONTINUE_PATH = os.path.join(BASE_DIR, "assets", "img", "continue.png")
RETREAT_PATH = os.path.join(BASE_DIR, "assets", "img", "retreat.png")
WAVE6_PATH = os.path.join(BASE_DIR, "assets", "img", "wave_06.png")
WAVE8_PATH = os.path.join(BASE_DIR, "assets", "img", "wave8.png")

# Hidden tkinter root for messageboxes
root = tk.Tk()
root.withdraw()

# Thread control
_stop_event = threading.Event()
_worker_thread = None
_worker_lock = threading.Lock()

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

def run_app(stop_event):
    """Main bot loop running in a background thread. Exits when stop_event is set."""
    print("Bot thread started.")
    
    while not stop_event.is_set():
        try:
            # Find and activate game window
            game_window = find_game_window()
            
            if not game_window:
                print(f"Game window '{app}' not found. Waiting...")
                time.sleep(1.0)
                continue
            
            os.system("cls" if os.name == 'nt' else "clear")
            print("App is running.")
            try:
                loc_CA = pag.locateOnWindow(
                    CHALLENGE_PATH, app, confidence=0.9, grayscale=True
                )
                if loc_CA is not None:
                    pag.moveTo(loc_CA[0] + 50, loc_CA[1] + 25)
                    pag.click()
            except pag.ImageNotFoundException:
                pass
            time.sleep(1.00)
            try:
                loc_START = pag.locateOnWindow(
                    START_PATH, app, confidence=0.9, grayscale=True
                )
                if loc_START is not None:
                    pag.moveTo(loc_START[0] + 50, loc_START[1] + 25)
                    pag.click()
            except pag.ImageNotFoundException:
                pass
            time.sleep(1.00)
            wave_looping()
            
            # Small delay between iterations to prevent CPU spinning
            time.sleep(0.5)
            
        except Exception as e:
            print(f"Error in bot loop: {e}")
            time.sleep(1.0)
    
    print("Bot thread stopping.")


def wave_looping():
    loc_CONTINUE = None
    loc_RETREAT = None
    loc_WAVE8 = None
    try:
        loc_CONTINUE = pag.locateOnWindow(
            CONTINUE_PATH, app, confidence=0.8, grayscale=True
        )
        loc_RETREAT = pag.locateOnWindow(
            RETREAT_PATH, app, confidence=0.8, grayscale=True
        )
        loc_WAVE8 = pag.locateOnWindow(
            WAVE8_PATH, app, confidence=0.99, grayscale=True
        )
        if loc_WAVE8 is None:
            if loc_CONTINUE is not None:
                pag.moveTo(loc_CONTINUE[0] + 50, loc_CONTINUE[1] + 25)
                pag.click()
        elif loc_WAVE8 is not None:
            if loc_RETREAT is not None:
                pag.moveTo(loc_RETREAT[0] + 50, loc_RETREAT[1] + 25)
                pag.click()
    except Exception as e:
        if loc_CONTINUE is not None:
                pag.moveTo(loc_CONTINUE[0] + 50, loc_CONTINUE[1] + 25)
                pag.click()
    time.sleep(1.00)


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