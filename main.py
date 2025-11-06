import pyautogui as pag
import pygetwindow as pgw
import time
import os
import sys
import random
import threading
import traceback
import json
import tkinter as tk
from tkinter import messagebox
from pynput.keyboard import Key, Listener, Controller
from pynput.mouse import Button, Controller as MouseController

# ============================================================================
# CONFIGURATION LOADING
# ============================================================================

# Handle both script and PyInstaller executable paths
if getattr(sys, 'frozen', False):
    # Running as compiled executable (PyInstaller)
    BASE_DIR = sys._MEIPASS
else:
    # Running as script
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Load configuration from config.json
CONFIG_PATH = os.path.join(BASE_DIR, "config.json")

def load_config():
    """Load configuration from config.json file."""
    try:
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config
    except FileNotFoundError:
        print(f"Error: config.json not found at {CONFIG_PATH}")
        print("Please ensure config.json exists in the same directory as the script.")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in config.json: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error loading config.json: {e}")
        sys.exit(1)

# Load configuration
config = load_config()

# Application name
app = config.get("app_name", "Duet Night Abyss  ")

# Key press configuration
MIN_KEY_PRESSES = config.get("key_press", {}).get("min_key_presses", 15)
MAX_KEY_PRESSES = config.get("key_press", {}).get("max_key_presses", 25)
MIN_KEY_DELAY = config.get("key_press", {}).get("min_key_delay", 0.1)
MAX_KEY_DELAY = config.get("key_press", {}).get("max_key_delay", 0.3)
MIN_KEY_HOLD_TIME = config.get("key_press", {}).get("min_key_hold_time", 0.05)
MAX_KEY_HOLD_TIME = config.get("key_press", {}).get("max_key_hold_time", 0.15)
MOVEMENT_ARRAY = config.get("key_press", {}).get("movement_array", ["w", "a", "s", "d"])
MOVEMENT_ARRAY_GLEVUM_PIT_ELEVATOR = config.get("key_press", {}).get("movement_array_glevum_pit_elevator", ["w", "space"])

# Feature flags
ENABLE_RANDOM_KEY_PRESSES = config.get("features", {}).get("enable_random_key_presses", True)
ENABLE_NOTIFICATIONS = config.get("features", {}).get("enable_notifications", True)
ENABLE_WINDOW_DETECTION = config.get("features", {}).get("enable_window_detection", True)
ENABLE_MAP_DETECTION = config.get("features", {}).get("enable_map_detection", True)

# Image recognition confidence levels
CONFIDENCE_CHALLENGE_START = config.get("confidence", {}).get("challenge_start", 0.9)
CONFIDENCE_CONTINUE_RETREAT = config.get("confidence", {}).get("continue_retreat", 0.8)
CONFIDENCE_WAVE8 = config.get("confidence", {}).get("wave8", 0.99)
CONFIDENCE_MAP_DETECTION = config.get("confidence", {}).get("map_detection", 0.8)

# Window configuration
WINDOW_TARGET_X = config.get("window", {}).get("target_x", 0)
WINDOW_TARGET_Y = config.get("window", {}).get("target_y", 0)
WINDOW_TARGET_WIDTH = config.get("window", {}).get("target_width", 1920)
WINDOW_TARGET_HEIGHT = config.get("window", {}).get("target_height", 1080)

# ============================================================================
# INITIALIZATION
# ============================================================================

# Initialize pynput keyboard controller as fallback
_keyboard_controller = Controller()

# Initialize pynput mouse controller as fallback
_mouse_controller = MouseController()

# Mouse control using pydirectinput-rgx (fallback for games)
try:
    import pydirectinput
    HAS_PYDIRECTINPUT = True
except ImportError:
    HAS_PYDIRECTINPUT = False
    pydirectinput = None

# Windows notification support
_toaster = None
try:
    from win10toast import ToastNotifier
    try:
        _toaster = ToastNotifier()
        HAS_WIN10TOAST = True
    except Exception:
        HAS_WIN10TOAST = False
        _toaster = None
except ImportError:
    HAS_WIN10TOAST = False
    _toaster = None

try:
    from plyer import notification
    HAS_PLYER = True
except ImportError:
    HAS_PLYER = False

CHALLENGE_PATH = os.path.join(BASE_DIR, "assets", "buttons", "challenge_again.png")
START_PATH = os.path.join(BASE_DIR, "assets", "buttons", "start.png")
CONTINUE_PATH = os.path.join(BASE_DIR, "assets", "buttons", "continue.png")
RETREAT_PATH = os.path.join(BASE_DIR, "assets", "buttons", "retreat.png")
WAVE6_PATH = os.path.join(BASE_DIR, "assets", "buttons", "wave_06.png")
WAVE8_PATH = os.path.join(BASE_DIR, "assets", "buttons", "wave_8.png")

# Map image paths
GLEVUM_PIT_ELEVATOR_PATH = os.path.join(BASE_DIR, "assets", "maps", "glevum_pit_elevator.png")

# Hidden tkinter root for messageboxes
root = tk.Tk()
root.withdraw()

# Thread control
_stop_event = threading.Event()
_worker_thread = None
_worker_lock = threading.Lock()
_locked_game_window = None  # Store the locked game window

def detect_current_map():
    """Detect which map is currently visible in the game window.
    Returns: 'glevum_pit_elevator', or None if no match found."""
    if not _locked_game_window:
        return None
    
    try:
        # Check for glevum_pit_elevator
        try:
            loc_glevum_pit_elevator = pag.locateOnWindow(
                GLEVUM_PIT_ELEVATOR_PATH, app, confidence=CONFIDENCE_MAP_DETECTION, grayscale=True
            )
            if loc_glevum_pit_elevator is not None:
                print("Glevum pit elevator map detected")
                sys.stdout.flush()
                return 'glevum_pit_elevator'
        except (pag.ImageNotFoundException, Exception):
            pass
        
        return None
    except Exception as e:
        print(f"Error detecting map: {e}")
        sys.stdout.flush()
        return None

def press_keys_randomly(stop_event=None):
    """Press keys from movement_array randomly between MIN_KEY_PRESSES and MAX_KEY_PRESSES times.
    Each key is held down for a random duration between MIN_KEY_HOLD_TIME and MAX_KEY_HOLD_TIME.
    Can be interrupted immediately if stop_event is set.
    Automatically detects current map and uses map-specific movement array if map detection is enabled."""
    
    # Detect current map and select appropriate movement array (if map detection is enabled)
    movement_array_to_use = MOVEMENT_ARRAY  # Default movement array
    
    if ENABLE_MAP_DETECTION:
        current_map = detect_current_map()
        
        if current_map == 'glevum_pit_elevator':
            movement_array_to_use = MOVEMENT_ARRAY_GLEVUM_PIT_ELEVATOR
            print("Using glevum pit elevator movement array")
            sys.stdout.flush()
        else:
            print("No map detected, using default movement array")
            sys.stdout.flush()
            current_map = None
    else:
        print("Map detection disabled, using default movement array")
        sys.stdout.flush()
        current_map = None
    
    # Get random number of presses for each key in movement array
    key_press_counts = {}
    for key in movement_array_to_use:
        key_press_counts[key] = random.randint(MIN_KEY_PRESSES, MAX_KEY_PRESSES)
    
    # Create notification message
    key_list = ", ".join([f"{k.upper()}: {key_press_counts[k]}" for k in movement_array_to_use])
    map_info = f" ({current_map})" if current_map else ""
    notify("Pressing keys randomly", f"Keys: {key_list}{map_info}")
    
    # Press each key in the movement array
    for key in movement_array_to_use:
        # Check if we should stop before processing each key
        if stop_event and stop_event.is_set():
            print("Key pressing interrupted by stop signal.")
            sys.stdout.flush()
            return
        
        presses = key_press_counts[key]
        print(f"Pressing {key.upper()} key {presses} times...")
        sys.stdout.flush()
        
        for _ in range(presses):
            # Check if we should stop before each key press
            if stop_event and stop_event.is_set():
                print("Key pressing interrupted by stop signal.")
                sys.stdout.flush()
                return
            
            try:
                pag.keyDown(key)
                time.sleep(random.uniform(MIN_KEY_HOLD_TIME, MAX_KEY_HOLD_TIME))
                pag.keyUp(key)
            except Exception as e:
                print(f"Error with PyAutoGUI key press, using pynput fallback: {e}")
                sys.stdout.flush()
                # Fallback to pynput - handle special keys like "space"
                try:
                    if key == "space":
                        _keyboard_controller.press(Key.space)
                        time.sleep(random.uniform(MIN_KEY_HOLD_TIME, MAX_KEY_HOLD_TIME))
                        _keyboard_controller.release(Key.space)
                    else:
                        _keyboard_controller.press(key)
                        time.sleep(random.uniform(MIN_KEY_HOLD_TIME, MAX_KEY_HOLD_TIME))
                        _keyboard_controller.release(key)
                except Exception as e2:
                    print(f"Error with pynput fallback: {e2}")
                    sys.stdout.flush()
            
            # Check stop event before delay to make it more responsive
            if stop_event and stop_event.is_set():
                print("Key pressing interrupted by stop signal.")
                sys.stdout.flush()
                return
            
            time.sleep(random.uniform(MIN_KEY_DELAY, MAX_KEY_DELAY))
    
    print("Key presses completed.")
    sys.stdout.flush()

def move_and_click(x, y):
    """Move mouse to coordinates and click with fallback chain.
    Tries: pyautogui -> pynput.mouse -> pydirectinput
    
    Args:
        x: Absolute x coordinate on screen
        y: Absolute y coordinate on screen
    
    Returns:
        bool: True if successful, False otherwise
    """
    x_int = int(x)
    y_int = int(y)
    
    print(f"Attempting to move mouse to ({x_int}, {y_int})")
    sys.stdout.flush()
    
    # Method 1: Try pyautogui first
    try:
        pag.moveTo(x_int, y_int)
        time.sleep(0.05)  # Small delay for movement to complete
        pag.click()
        print(f"Mouse click successful using pyautogui at ({x_int}, {y_int})")
        sys.stdout.flush()
        return True
    except Exception as e:
        print(f"pyautogui failed: {e}")
        sys.stdout.flush()
        # Fall through to next method
    
    # Method 2: Try pynput.mouse
    try:
        _mouse_controller.position = (x_int, y_int)
        time.sleep(0.05)  # Small delay for movement to complete
        _mouse_controller.click(Button.left)
        print(f"Mouse click successful using pynput.mouse at ({x_int}, {y_int})")
        sys.stdout.flush()
        return True
    except Exception as e:
        print(f"pynput.mouse failed: {e}")
        sys.stdout.flush()
        # Fall through to next method
    
    # Method 3: Try pydirectinput (last resort)
    if HAS_PYDIRECTINPUT:
        try:
            pydirectinput.moveTo(x_int, y_int)
            time.sleep(0.05)  # Small delay for movement to complete
            pydirectinput.click()
            print(f"Mouse click successful using pydirectinput at ({x_int}, {y_int})")
            sys.stdout.flush()
            return True
        except Exception as e:
            print(f"pydirectinput failed: {e}")
            sys.stdout.flush()
    else:
        print("pydirectinput not available.")
        sys.stdout.flush()
    
    # All methods failed
    print(f"All mouse click methods failed for ({x_int}, {y_int})")
    sys.stdout.flush()
    traceback.print_exc()
    sys.stdout.flush()
    return False

def find_and_lock_game_window():
    """Find and lock the game window on startup. Returns True if found, False otherwise."""
    global _locked_game_window
    try:
        windows = pgw.getWindowsWithTitle(app)
        if windows:
            _locked_game_window = windows[0]
            print(f"DNA window found: {_locked_game_window.title}")
            sys.stdout.flush()
            return True
        else:
            print(f"Game window '{app}' not found. Please start the game and run this script again.")
            sys.stdout.flush()
            return False
    except Exception as e:
        print(f"Error finding game window: {str(e)}")
        sys.stdout.flush()
        return False

def find_game_window():
    """Find and activate the game window. Uses locked window if available."""
    global _locked_game_window
    
    # If we have a locked window, use it and handle window management
    if _locked_game_window is not None:
        try:
            # Refresh the window object to get current state
            windows = pgw.getWindowsWithTitle(app)
            if windows:
                # Find the window that matches our locked window
                for w in windows:
                    if w.title == _locked_game_window.title or w._hWnd == getattr(_locked_game_window, '_hWnd', None):
                        _locked_game_window = w  # Update reference
                        break
                else:
                    _locked_game_window = windows[0]  # Fallback to first match
            else:
                # Window might have closed, try to find it again
                _locked_game_window = None
                return None
        except Exception:
            # If we can't refresh, try to find window again
            try:
                windows = pgw.getWindowsWithTitle(app)
                if windows:
                    _locked_game_window = windows[0]
                else:
                    _locked_game_window = None
                    return None
            except Exception:
                return None
        
        game_window = _locked_game_window
        
        # Only perform window management if enabled
        if ENABLE_WINDOW_DETECTION:
            # Set window position and size if needed
            target_x = WINDOW_TARGET_X
            target_y = WINDOW_TARGET_Y
            target_width = WINDOW_TARGET_WIDTH
            target_height = WINDOW_TARGET_HEIGHT
            
            needs_resize = (game_window.width != target_width or game_window.height != target_height)
            needs_reposition = (game_window.left != target_x or game_window.top != target_y)
            
            if needs_resize or needs_reposition:
                try:
                    print(f"Resizing window from {game_window.width}x{game_window.height} to {target_width}x{target_height}")
                    print(f"Repositioning window from ({game_window.left}, {game_window.top}) to ({target_x}, {target_y})")
                    sys.stdout.flush()
                    game_window.resizeTo(target_width, target_height)
                    game_window.moveTo(target_x, target_y)
                    time.sleep(0.3)  # Give window time to resize/reposition
                    print("Window resized and repositioned successfully")
                    sys.stdout.flush()
                except Exception as e:
                    print(f"Error resizing/repositioning window: {e}")
                    sys.stdout.flush()

            # First check if game window is active
            if not game_window.isActive:
                print("Game is not the active window. Performing Alt+Tab once...")
                sys.stdout.flush()
                # Press Alt+Tab once
                try:
                    pag.keyDown('alt')
                    pag.press('tab')
                    pag.keyUp('alt')
                except Exception as e:
                    print(f"Error with PyAutoGUI Alt+Tab, using pynput fallback: {e}")
                    sys.stdout.flush()
                    # Fallback to pynput
                    _keyboard_controller.press(Key.alt)
                    _keyboard_controller.press(Key.tab)
                    _keyboard_controller.release(Key.tab)
                    _keyboard_controller.release(Key.alt)
                time.sleep(0.3)  # Give window time to activate
                
                # Check if window is now active
                if game_window.isActive:
                    print("Successfully switched to game window")
                    sys.stdout.flush()
                    time.sleep(0.5)  # Let window settle
                else:
                    print("Game window is still not active after Alt+Tab")
                    sys.stdout.flush()
        else:
            print("Window detection disabled. Skipping window management.")
            sys.stdout.flush()
        
        return game_window
    
    # If no locked window, fall back to original behavior
    try:
        windows = pgw.getWindowsWithTitle(app)
        if windows:
            game_window = windows[0]
            print(f"Found game window: {game_window.title}")
            sys.stdout.flush()
            return game_window
        return None
    except Exception as e:
        print(f"Error finding game window: {str(e)}")
        sys.stdout.flush()
        return None

def run_app(stop_event):
    """Main bot loop running in a background thread. Exits when stop_event is set."""
    try:
        print("Bot thread started.")
        sys.stdout.flush()
        
        while not stop_event.is_set():
            try:
                # Use locked window if available
                if _locked_game_window is None:
                    print(f"Game window '{app}' not found. Waiting...")
                    sys.stdout.flush()
                    time.sleep(1.0)
                    continue
                
                # Find and activate game window (uses locked window)
                game_window = find_game_window()
                
                if not game_window:
                    print(f"Game window '{app}' not found. Waiting...")
                    sys.stdout.flush()
                    time.sleep(1.0)
                    continue
                
                os.system("cls" if os.name == 'nt' else "clear")
                
                # Check all buttons: Challenge Again, Start, Continue, Retreat, and Waves (if applicable)
                # OpenCV Code Below
                loc_CA = None
                loc_START = None
                loc_CONTINUE = None
                loc_RETREAT = None
                loc_WAVE6 = None
                loc_WAVE8 = None
                
                print("Checking for Challenge Again button...")
                sys.stdout.flush()
                notify("Checking screen", "Looking for Challenge Again button...")
                try:
                    loc_CA = pag.locateOnWindow(
                        CHALLENGE_PATH, app, confidence=CONFIDENCE_CHALLENGE_START, grayscale=True
                    )
                    if loc_CA is not None:
                        print(f"Challenge Again button found at ({loc_CA[0]}, {loc_CA[1]})")
                        sys.stdout.flush()
                    else:
                        print("Challenge Again button not found on screen")
                        sys.stdout.flush()
                except pag.ImageNotFoundException:
                    print("Challenge Again button not found (ImageNotFoundException)")
                    sys.stdout.flush()
                except Exception as e:
                    print(f"Error locating Challenge Again: {e}")
                    sys.stdout.flush()
                
                time.sleep(0.5)
                
                print("Checking for Start button...")
                sys.stdout.flush()
                notify("Checking screen", "Looking for Start button...")
                try:
                    loc_START = pag.locateOnWindow(
                        START_PATH, app, confidence=CONFIDENCE_CHALLENGE_START, grayscale=True
                    )
                    if loc_START is not None:
                        print(f"Start button found at ({loc_START[0]}, {loc_START[1]})")
                        sys.stdout.flush()
                    else:
                        print("Start button not found on screen")
                        sys.stdout.flush()
                except pag.ImageNotFoundException:
                    print("Start button not found (ImageNotFoundException)")
                    sys.stdout.flush()
                except Exception as e:
                    print(f"Error locating Start: {e}")
                    sys.stdout.flush()
                
                time.sleep(0.5)
                
                print("Checking for Continue button...")
                sys.stdout.flush()
                notify("Checking screen", "Looking for Continue button...")
                try:
                    loc_CONTINUE = pag.locateOnWindow(
                        CONTINUE_PATH, app, confidence=CONFIDENCE_CONTINUE_RETREAT, grayscale=True
                    )
                    if loc_CONTINUE is not None:
                        print(f"Continue button found at ({loc_CONTINUE[0]}, {loc_CONTINUE[1]})")
                        sys.stdout.flush()
                    else:
                        print("Continue button not found on screen")
                        sys.stdout.flush()
                except pag.ImageNotFoundException:
                    print("Continue button not found (ImageNotFoundException)")
                    sys.stdout.flush()
                except Exception as e:
                    print(f"Error locating Continue: {e}")
                    sys.stdout.flush()
                
                time.sleep(0.5)
                
                # Check for Retreat button
                try:
                    loc_RETREAT = pag.locateOnWindow(
                        RETREAT_PATH, app, confidence=CONFIDENCE_CONTINUE_RETREAT, grayscale=True
                    )
                    if loc_RETREAT is not None:
                        print(f"Retreat button found at ({loc_RETREAT[0]}, {loc_RETREAT[1]})")
                        sys.stdout.flush()
                    else:
                        print("Retreat button not found on screen")
                        sys.stdout.flush()
                except pag.ImageNotFoundException:
                    print("Retreat button not found (ImageNotFoundException)")
                    sys.stdout.flush()
                except Exception as e:
                    print(f"Error locating Retreat: {e}")
                    sys.stdout.flush()
                
                # Only check for Wave6 and Wave8 if both Continue and Retreat buttons are visible
                loc_WAVE6 = None
                loc_WAVE8 = None
                if loc_CONTINUE is not None and loc_RETREAT is not None:
                    print("Both Continue and Retreat buttons found. Checking for wave indicators...")
                    sys.stdout.flush()
                    time.sleep(0.5)
                    
                    # Check for Wave6
                    try:
                        loc_WAVE6 = pag.locateOnWindow(
                            WAVE6_PATH, app, confidence=CONFIDENCE_WAVE8, grayscale=True
                        )
                        if loc_WAVE6 is not None:
                            print(f"Wave 6 detected")
                            sys.stdout.flush()
                        else:
                            print("Wave 6 not detected")
                            sys.stdout.flush()
                    except pag.ImageNotFoundException:
                        print("Wave 6 not detected (ImageNotFoundException)")
                        sys.stdout.flush()
                    except Exception as e:
                        print(f"Error locating Wave6: {e}")
                        sys.stdout.flush()
                    
                    # Check for Wave8
                    try:
                        loc_WAVE8 = pag.locateOnWindow(
                            WAVE8_PATH, app, confidence=CONFIDENCE_WAVE8, grayscale=True
                        )
                        if loc_WAVE8 is not None:
                            print(f"Wave 8 detected")
                            sys.stdout.flush()
                        else:
                            print("Wave 8 not detected")
                            sys.stdout.flush()
                    except pag.ImageNotFoundException:
                        print("Wave 8 not detected (ImageNotFoundException)")
                        sys.stdout.flush()
                    except Exception as e:
                        print(f"Error locating Wave8: {e}")
                        sys.stdout.flush()
                else:
                    print("Continue or Retreat button not found. Skipping wave detection.")
                    sys.stdout.flush()
                
                # Click Challenge Again button if found
                if loc_CA is not None:
                    # Convert window-relative coordinates to absolute screen coordinates
                    absolute_x = game_window.left + loc_CA[0] + 50
                    absolute_y = game_window.top + loc_CA[1] + 25
                    print(f"Moving to absolute position: ({absolute_x}, {absolute_y})")
                    sys.stdout.flush()
                    if move_and_click(absolute_x, absolute_y):
                        print("Challenge Again button clicked")
                        sys.stdout.flush()
                    else:
                        print("Failed to click Challenge Again button")
                        sys.stdout.flush()
                
                # Click Start button if found
                if loc_START is not None:
                    # Convert window-relative coordinates to absolute screen coordinates
                    absolute_x = game_window.left + loc_START[0] + 50
                    absolute_y = game_window.top + loc_START[1] + 25
                    print(f"Moving to absolute position: ({absolute_x}, {absolute_y})")
                    sys.stdout.flush()
                    if move_and_click(absolute_x, absolute_y):
                        print("Start button clicked")
                        sys.stdout.flush()
                    else:
                        print("Failed to click Start button")
                        sys.stdout.flush()
                
                # Handle Continue/Retreat logic (wave looping)
                # Only process wave logic if both Continue and Retreat buttons are visible
                if loc_CONTINUE is not None and loc_RETREAT is not None:
                    # Check if Wave6 or Wave8 is detected
                    if loc_WAVE6 is not None or loc_WAVE8 is not None:
                        # Wave6 or Wave8 detected, click Retreat
                        absolute_x = game_window.left + loc_RETREAT[0] + 50
                        absolute_y = game_window.top + loc_RETREAT[1] + 25
                        print(f"Moving to absolute position: ({absolute_x}, {absolute_y})")
                        sys.stdout.flush()
                        if move_and_click(absolute_x, absolute_y):
                            print("Retreat button clicked (Wave6 or Wave8 detected)")
                            sys.stdout.flush()
                        else:
                            print("Failed to click Retreat button")
                            sys.stdout.flush()
                    else:
                        # No wave detected, click Continue
                        absolute_x = game_window.left + loc_CONTINUE[0] + 50
                        absolute_y = game_window.top + loc_CONTINUE[1] + 25
                        print(f"Moving to absolute position: ({absolute_x}, {absolute_y})")
                        sys.stdout.flush()
                        if move_and_click(absolute_x, absolute_y):
                            print("Continue button clicked (no wave detected)")
                            sys.stdout.flush()
                        else:
                            print("Failed to click Continue button")
                            sys.stdout.flush()
                elif loc_CONTINUE is not None:
                    # Only Continue button is visible (no Retreat), click it
                    absolute_x = game_window.left + loc_CONTINUE[0] + 50
                    absolute_y = game_window.top + loc_CONTINUE[1] + 25
                    print(f"Moving to absolute position: ({absolute_x}, {absolute_y})")
                    sys.stdout.flush()
                    if move_and_click(absolute_x, absolute_y):
                        print("Continue button clicked")
                        sys.stdout.flush()
                    else:
                        print("Failed to click Continue button")
                        sys.stdout.flush()
                
                # Only press keys randomly if NONE of Challenge Again, Start, or Continue are found
                if loc_CA is None and loc_START is None and loc_CONTINUE is None:
                    if ENABLE_RANDOM_KEY_PRESSES:
                        print("Challenge Again, Start, and Continue buttons not found. Pressing keys randomly...")
                        sys.stdout.flush()
                        press_keys_randomly(stop_event)
                    else:
                        print("Challenge Again, Start, and Continue buttons not found. Random key presses disabled.")
                        sys.stdout.flush()
                
                time.sleep(1.00)
                
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


def wave_looping(game_window):
    """Handle wave looping with Continue/Retreat logic."""
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
                # Convert window-relative coordinates to absolute screen coordinates
                absolute_x = game_window.left + loc_CONTINUE[0] + 50
                absolute_y = game_window.top + loc_CONTINUE[1] + 25
                move_and_click(absolute_x, absolute_y)
        elif loc_WAVE8 is not None:
            if loc_RETREAT is not None:
                # Convert window-relative coordinates to absolute screen coordinates
                absolute_x = game_window.left + loc_RETREAT[0] + 50
                absolute_y = game_window.top + loc_RETREAT[1] + 25
                move_and_click(absolute_x, absolute_y)
    except Exception as e:
        if loc_CONTINUE is not None:
            # Convert window-relative coordinates to absolute screen coordinates
            absolute_x = game_window.left + loc_CONTINUE[0] + 50
            absolute_y = game_window.top + loc_CONTINUE[1] + 25
            move_and_click(absolute_x, absolute_y)
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
    """Show Windows notification if enabled and available, otherwise fallback to tkinter messagebox."""
    # Check if notifications are enabled
    if not ENABLE_NOTIFICATIONS:
        return
    
    global _toaster
    try:
        # Try Windows 10 toast notification first (use singleton instance)
        if HAS_WIN10TOAST and _toaster is not None:
            try:
                _toaster.show_toast(title, message, duration=3, threaded=True)
                return
            except Exception as e:
                print(f"win10toast error: {e}, falling back to plyer")
                # Try to recreate toaster once
                try:
                    _toaster = ToastNotifier()
                    _toaster.show_toast(title, message, duration=3, threaded=True)
                    return
                except Exception:
                    pass
        
        # Try plyer notification
        if HAS_PLYER:
            try:
                notification.notify(
                    title=title,
                    message=message,
                    timeout=3
                )
                return
            except Exception:
                pass
    except Exception:
        pass
    
    # Fallback to tkinter messagebox
    try:
        messagebox.showinfo(title, message)
    except Exception:
        # If all else fails, just print
        print(f"{title}: {message}")

def is_admin():
    """Check if the script is running with administrator privileges on Windows.
    
    Returns:
        bool: True if running as admin on Windows, True on non-Windows systems
    """
    if os.name != 'nt':
        # Not Windows, assume admin mode is not required
        return True
    
    try:
        import ctypes
        # Check if the current user has admin privileges
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        # If check fails, assume not admin to be safe
        return False

def check_admin_privileges():
    """Check if running as admin and exit with error if not."""
    if not is_admin():
        error_msg = (
            "ERROR: Administrator privileges are required to run this application.\n"
            "Please run this script/executable as Administrator.\n"
            "\n"
            "On Windows:\n"
            "  - Right-click on the script/executable\n"
            "  - Select 'Run as administrator'\n"
            "\n"
            "Or run from command prompt:\n"
            "  - Right-click Command Prompt\n"
            "  - Select 'Run as administrator'\n"
            "  - Navigate to script location and run it"
        )
        print(error_msg)
        sys.stdout.flush()
        
        # Try to show error in messagebox
        try:
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("Administrator Required", error_msg)
            root.destroy()
        except Exception:
            pass
        
        sys.exit(1)

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
    # Check for admin privileges first
    check_admin_privileges()
    
    # Find and lock the game window on startup
    print("Searching for DNA game window...")
    sys.stdout.flush()
    if not find_and_lock_game_window():
        print("Warning: Game window not found. The bot will wait for the window to appear.")
        print("Please start the game and press F4 to start the bot.")
        sys.stdout.flush()
    
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