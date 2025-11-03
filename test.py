import pygetwindow as pgw
from PIL import ImageGrab, ImageFilter, Image
import pytesseract
import pyautogui as pag
import time
import threading
import cv2
import numpy as np
from pynput.keyboard import Key, Listener

# Configure PyAutoGUI
pag.FAILSAFE = True  # Move mouse to corner to abort

# Tesseract Setup
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Thread control
_stop_event = threading.Event()
_worker_thread = None
_worker_lock = threading.Lock()

def check_for_text(stop_event):
    app = "Duet Night Abyss  "
    
    while not stop_event.is_set():
        windows = pgw.getWindowsWithTitle(app)
        
        if not windows:
            print("Game window not found")
            time.sleep(1.0)
            continue
        
        game_window = windows[0]
        
        # Check if game window is active
        if not game_window.isActive:
            print("Game is not the active window. Alt+Tabbing to find it...")
            max_attempts = 10  # Maximum number of Alt+Tab attempts
            
            for attempt in range(max_attempts):
                # Press Alt+Tab
                pag.keyDown('alt')
                pag.press('tab')
                time.sleep(0.1)  # Small delay between tab presses
                
                # Check if we found the game window
                if game_window.isActive:
                    pag.keyUp('alt')
                    print("Successfully switched to game window")
                    time.sleep(0.5)  # Let window settle
                    break
            
            # Release alt key if we didn't find the window
            if not game_window.isActive:
                pag.keyUp('alt')
                print("Could not find game window after Alt+Tabbing")
                time.sleep(1.0)
        
        region = (
            game_window.left,
            game_window.top,
            game_window.left + game_window.width,
            game_window.top + game_window.height
        )
        
        screenshot = ImageGrab.grab(bbox=region)
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
        screenshot.save("assets\img\cropped_text_area.png")

        # img_np = np.array(screenshot)
        # thresh_img_np = cv2.adaptiveThreshold(
        #     img_np, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        # )
        # screenshot = Image.fromarray(thresh_img_np)

        text = pytesseract.image_to_string(screenshot)
        
        # Print full detected text for debugging
        print("\nFull detected text:")
        print("-" * 50)
        print(text)
        print("-" * 50)
        
        text_lower = text.lower()
        if "start" in text_lower:
            print(f"Found 'Start' on screen")
            # Get OCR data with positions
            data = pytesseract.image_to_data(screenshot, output_type=pytesseract.Output.DICT)
            
            for i, word in enumerate(data['text']):
                word_lower = word.lower()
                if "bonus" in word_lower or "booster" in word_lower:
                    if "booster" in word_lower:
                        booster_x = data['left'][i]
                        booster_y = data['top'][i]
                        booster_width = data['width'][i]
                        booster_height = data['height'][i]

                        # Define search areas
                        right_x_start = booster_x + booster_width
                        bottom_right_y_start = booster_y + booster_height

                        found_right = False
                        found_bottom_right = False

                        for j, other_word in enumerate(data['text']):
                            if i == j or not other_word.strip():
                                continue

                            other_x = data['left'][j]
                            other_y = data['top'][j]

                            # Check for text to the right
                            if other_x > right_x_start and abs(other_y - booster_y) < 20: # 20 is a tolerance
                                print(f"Found text to the right of 'No Booster': '{other_word}'")
                                found_right = True

                            # Check for text to the bottom right
                            if other_x > right_x_start and other_y > bottom_right_y_start:
                                print(f"Found text to the bottom right of 'No Booster': '{other_word}'")
                                found_bottom_right = True

                        if not found_right:
                            print("No text found to the right of 'No Booster'")
                        if not found_bottom_right:
                            print("No text found to the bottom right of 'No Booster'")

                    # Calculate absolute screen position
                    x = game_window.left + data['left'][i] + (data['width'][i] // 2)
                    y = game_window.top + data['top'][i] + (data['height'][i] // 2)
                    
                    print(f"Moving to click button at ({x}, {y})")
                    pag.moveTo(x, y)
                    pag.click()
                    time.sleep(0.5)  # Short delay after clicking
                    break  # Exit after finding and clicking the first match
            else:
                print("Found text but couldn't determine click position")
        else:
            print("'No Bonus' not found")
            
        time.sleep(1.0)  # Wait a second before next check

def start_check():
    global _worker_thread, _stop_event
    with _worker_lock:
        if _worker_thread is not None and _worker_thread.is_alive():
            return False
        _stop_event.clear()
        _worker_thread = threading.Thread(target=check_for_text, args=(_stop_event,), daemon=True)
        _worker_thread.start()
        return True

def stop_check():
    global _worker_thread, _stop_event
    with _worker_lock:
        if _worker_thread is None or not _worker_thread.is_alive():
            return False
        _stop_event.set()
        _worker_thread.join(timeout=5.0)
        return True

def on_press(key):
    """Toggle checking on F1 press."""
    try:
        if key == Key.f1:
            started = start_check()
            if started:
                print(">>> F1 pressed — checking started")
            else:
                stopped = stop_check()
                if stopped:
                    print(">>> F1 pressed — checking stopped")
                else:
                    print("Already running or stopping. Press F1 again to toggle.")
    except Exception as e:
        print(f"Keyboard handler error: {e}")

if __name__ == "__main__":
    print("-" * 50)
    print("F1 toggles text checking on/off")
    print("Press Ctrl+C to exit")
    print("-" * 50)

    # Start keyboard listener
    listener = Listener(on_press=on_press)
    listener.start()
    
    try:
        # Keep the main thread alive
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nCtrl+C detected - shutting down...")
        stop_check()
        listener.stop()
        print("Cleanup complete. Exiting...")
