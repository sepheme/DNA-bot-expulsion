import pyautogui as pag
import pygetwindow as pgw
import time
import os
import sys
import random
import threading
import tkinter as tk
from tkinter import messagebox
from pynput.keyboard import Key, Listener

# Windows notification support
try:
    from win10toast import ToastNotifier
    HAS_WIN10TOAST = True
except ImportError:
    HAS_WIN10TOAST = False
    try:
        from plyer import notification
        HAS_PLYER = True
    except ImportError:
        HAS_PLYER = False

app = "Duet Night Abyss  "

# Handle both script and PyInstaller executable paths
if getattr(sys, 'frozen', False):
    # Running as compiled executable (PyInstaller)
    BASE_DIR = sys._MEIPASS
else:
    # Running as script
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CHALLENGE_PATH = os.path.join(BASE_DIR, "assets", "img", "challenge_again.png")
START_PATH = os.path.join(BASE_DIR, "assets", "img", "start.png")
CONTINUE_PATH = os.path.join(BASE_DIR, "assets", "img", "continue.png")
RETREAT_PATH = os.path.join(BASE_DIR, "assets", "img", "retreat.png")
WAVE6_PATH = os.path.join(BASE_DIR, "assets", "img", "wave_06.png")
WAVE8_PATH = os.path.join(BASE_DIR, "assets", "img", "wave8.png")

# Configuration variables
MIN_KEY_PRESSES = 15  # Minimum number of key presses for W and D keys
MAX_KEY_PRESSES = 25  # Maximum number of key presses for W and D keys
MIN_KEY_DELAY = 0.1  # Minimum delay between key presses (seconds)
MAX_KEY_DELAY = 0.3  # Maximum delay between key presses (seconds)
MIN_KEY_HOLD_TIME = 0.05  # Minimum time to hold each key down (seconds)
MAX_KEY_HOLD_TIME = 0.15  # Maximum time to hold each key down (seconds)
CONFIDENCE_CHALLENGE_START = 0.9  # Confidence for Challenge Again and Start buttons
CONFIDENCE_CONTINUE_RETREAT = 0.8  # Confidence for Continue and Retreat buttons
CONFIDENCE_WAVE8 = 0.99  # Confidence for Wave 8 detection

# Hidden tkinter root for messageboxes
root = tk.Tk()
root.withdraw()

# Thread control
_stop_event = threading.Event()
_worker_thread = None
_worker_lock = threading.Lock()

def press_keys_randomly():
    """Press W key randomly between MIN_KEY_PRESSES and MAX_KEY_PRESSES times, then D key the same.
    Each key is held down for a random duration between MIN_KEY_HOLD_TIME and MAX_KEY_HOLD_TIME."""
    w_presses = random.randint(MIN_KEY_PRESSES, MAX_KEY_PRESSES)
    d_presses = random.randint(MIN_KEY_PRESSES, MAX_KEY_PRESSES)
    
    print(f"Pressing W key {w_presses} times...")
    sys.stdout.flush()
    for _ in range(w_presses):
        pag.keyDown('w')
        time.sleep(random.uniform(MIN_KEY_HOLD_TIME, MAX_KEY_HOLD_TIME))
        pag.keyUp('w')
        time.sleep(random.uniform(MIN_KEY_DELAY, MAX_KEY_DELAY))
    
    print(f"Pressing D key {d_presses} times...")
    sys.stdout.flush()
    for _ in range(d_presses):
        pag.keyDown('d')
        time.sleep(random.uniform(MIN_KEY_HOLD_TIME, MAX_KEY_HOLD_TIME))
        pag.keyUp('d')
        time.sleep(random.uniform(MIN_KEY_DELAY, MAX_KEY_DELAY))
    
    print("Key presses completed.")
    sys.stdout.flush()

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
    try:
        print("Bot thread started.")
        sys.stdout.flush()
        
        while not stop_event.is_set():
            try:
                # Find and activate game window
                game_window = find_game_window()
                
                if not game_window:
                    print(f"Game window '{app}' not found. Waiting...")
                    time.sleep(1.0)
                    continue
                
                os.system("cls" if os.name == 'nt' else "clear")
                
                try:
                    loc_CA = pag.locateOnWindow(
                        CHALLENGE_PATH, app, confidence=CONFIDENCE_CHALLENGE_START, grayscale=True
                    )
                    if loc_CA is not None:
                        pag.moveTo(loc_CA[0] + 50, loc_CA[1] + 25)
                        pag.click()
                    else:
                        # Button not found, press keys randomly
                        press_keys_randomly()
                except pag.ImageNotFoundException:
                    # Button not found, press keys randomly
                    press_keys_randomly()
                except Exception as e:
                    print(f"Error locating Challenge Again: {e}")
                    sys.stdout.flush()
                
                time.sleep(1.00)
                
                try:
                    loc_START = pag.locateOnWindow(
                        START_PATH, app, confidence=CONFIDENCE_CHALLENGE_START, grayscale=True
                    )
                    if loc_START is not None:
                        pag.moveTo(loc_START[0] + 50, loc_START[1] + 25)
                        pag.click()
                    else:
                        # Button not found, press keys randomly
                        press_keys_randomly()
                except pag.ImageNotFoundException:
                    # Button not found, press keys randomly
                    press_keys_randomly()
                except Exception as e:
                    print(f"Error locating Start: {e}")
                    sys.stdout.flush()
                
                time.sleep(1.00)
                wave_looping()
                
                # Small delay between iterations to prevent CPU spinning
                time.sleep(0.5)
                
            except Exception as e:
                print(f"Error in bot loop: {e}")
                import traceback
                traceback.print_exc()
                sys.stdout.flush()
                time.sleep(1.0)
        
        print("Bot thread stopping.")
        sys.stdout.flush()
    except Exception as e:
        print(f"FATAL ERROR in run_app thread: {e}")
        import traceback
        traceback.print_exc()
        sys.stdout.flush()
        raise  # Re-raise so we can see what went wrong


def wave_looping():
    loc_CONTINUE = None
    loc_RETREAT = None
    loc_WAVE8 = None
    try:
        loc_CONTINUE = pag.locateOnWindow(
            CONTINUE_PATH, app, confidence=CONFIDENCE_CONTINUE_RETREAT, grayscale=True
        )
        loc_RETREAT = pag.locateOnWindow(
            RETREAT_PATH, app, confidence=CONFIDENCE_CONTINUE_RETREAT, grayscale=True
        )
        loc_WAVE8 = pag.locateOnWindow(
            WAVE8_PATH, app, confidence=CONFIDENCE_WAVE8, grayscale=True
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
        if _worker_thread is not None:
            if _worker_thread.is_alive():
                print("Bot is already running!")
                return False
            else:
                # Clean up the dead thread
                _worker_thread = None
        
        print("Creating new bot thread...")
        _stop_event.clear()
        
        # Wrap run_app to catch any startup errors
        def safe_run_app(stop_event):
            try:
                run_app(stop_event)
            except Exception as e:
                print(f"ERROR: Exception in bot thread: {e}")
                import traceback
                traceback.print_exc()
                sys.stdout.flush()
        
        _worker_thread = threading.Thread(target=safe_run_app, args=(_stop_event,), daemon=True, name="BotThread")
        _worker_thread.start()
        
        # Give thread a moment to start
        time.sleep(0.2)
        
        if _worker_thread.is_alive():
            return True
        else:
            print("ERROR: Bot thread started but immediately died!")
            _worker_thread = None
            return False

def stop_bot():
    global _worker_thread, _stop_event
    with _worker_lock:
        if _worker_thread is None or not _worker_thread.is_alive():
            return False
        _stop_event.set()
        _worker_thread.join(timeout=5.0)
        return True

def notify(message, title="Application Notification"):
    """Show Windows notification if available, otherwise fallback to tkinter messagebox."""
    try:
        # Try Windows 10 toast notification first
        if HAS_WIN10TOAST:
            toaster = ToastNotifier()
            toaster.show_toast(title, message, duration=3, threaded=True)
            return
        elif HAS_PLYER:
            notification.notify(
                title=title,
                message=message,
                timeout=3
            )
            return
    except Exception:
        pass
    
    # Fallback to tkinter messagebox
    try:
        messagebox.showinfo(title, message)
    except Exception:
        # If all else fails, just print
        print(f"{title}: {message}")

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
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("-" * 50)
    print("F4 toggles the bot on/off.")
    print("Press Ctrl+C to exit")
    print("-" * 50)
    print("Listening for keyboard input...")
    
    # Start global keyboard listener in background and block main thread on join
    try:
        listener = Listener(on_press=on_press)
        listener.start()
        print("Keyboard listener started successfully!")
    except Exception as e:
        print(f"ERROR: Failed to start keyboard listener: {e}")
        import traceback
        traceback.print_exc()
        print("\nNote: On macOS, you may need to grant accessibility permissions.")
        print("Go to System Preferences > Security & Privacy > Privacy > Accessibility")
    
    try:
        # Keep the main thread alive
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nCtrl+C detected - shutting down...")
        # Stop the bot if it's running
        stop_bot()
        # Stop the keyboard listener
        if 'listener' in locals():
            listener.stop()
        print("Cleanup complete. Exiting...")