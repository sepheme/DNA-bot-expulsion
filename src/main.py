import pyautogui as pag
import pygetwindow as pgw
import time
import os
import threading
import tkinter as tk
from tkinter import messagebox
from pynput.keyboard import Key, Listener

allTitles = pgw.getAllTitles()
allWindows = pgw.getAllWindows()
app = "Duet Night Abyss  "
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CHALLENGE_PATH = os.path.join(BASE_DIR, "assets", "img", "challenge_again.png")
START_PATH = os.path.join(BASE_DIR, "assets", "img", "start.png")

root = tk.Tk()
root.withdraw()

_stop_event = threading.Event()
_worker_thread = None
_worker_lock = threading.Lock()

def run_app(stop_event):
    print("Bot thread started.")
    while not stop_event.is_set():
        try:
            titles = pgw.getAllTitles()
            if app in titles:
                try:
                    loc_CA = pag.locateOnWindow(
                        CHALLENGE_PATH, app, confidence=0.9, grayscale=True
                    )
                    if loc_CA is not None:
                        pag.moveTo(loc_CA[0] + 50, loc_CA[1] + 25)
                        pag.click()
                except Exception:
                    pass

                time.sleep(1.75)

                try:
                    loc_START = pag.locateOnWindow(
                        START_PATH, app, confidence=0.9, grayscale=True
                    )
                    if loc_START is not None:
                        pag.moveTo(loc_START[0] + 50, loc_START[1] + 25)
                        pag.click()
                except Exception:
                    pass

                time.sleep(1.75)
            else:
                time.sleep(1.0)
        except Exception as e:
            print(f"Error in bot loop: {e}")
            time.sleep(1.0)
    print("Bot thread stopping.")

def start_bot():
    global _worker_thread, _stop_event
    with _worker_lock:
        if _worker_thread is not None and _worker_thread.is_alive():
            return False
        _stop_event.clear()
        _worker_thread = threading.Thread(target=run_app, args=(_stop_event,), daemon=True)
        _worker_thread.start()
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
        print(message)

def on_press(key):
    try:
        if key == Key.f1:
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
                    notify("Bot is already running or stopping. Press F1 again to toggle.")
        elif key == Key.esc:
            print(">>> ESC pressed — stopping everything.")
            stop_bot()
            return False
    except Exception as e:
        print(f"Keyboard handler error: {e}")

if __name__ == "__main__":
    print("-" * 50)
    print("F1 toggles the bot on/off. ESC exits.")
    print("-" * 50)

    with Listener(on_press=on_press) as listener:
        listener.join()