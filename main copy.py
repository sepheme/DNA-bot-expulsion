import pyautogui as pag
import pygetwindow as pgw
import time
import os

allTitles = pgw.getAllTitles()
allWindows = pgw.getAllWindows()
app = "Duet Night Abyss  "
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CHALLENGE_PATH = os.path.join(BASE_DIR, "assets", "img", "challenge_again.png")
START_PATH = os.path.join(BASE_DIR, "assets", "img", "start.png")

CONTINUE_PATH = os.path.join(BASE_DIR, "assets", "img", "continue.png")

RETREAT_PATH = os.path.join(BASE_DIR, "assets", "img", "retreat.png")
WAVE6_PATH = os.path.join(BASE_DIR, "assets", "img", "wave_06.png")
WAVE8_PATH = os.path.join(BASE_DIR, "assets", "img", "wave8.png")
""""""
def run_app():
    while app in allTitles:
        os.system("cls")
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


run_app()