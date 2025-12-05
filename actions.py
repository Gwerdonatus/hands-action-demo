import os
import platform
import subprocess
import time
import winsound
import pyautogui
import cv2
from pathlib import Path

# Global reference to the frame (set in hand_actions.py)
CURRENT_FRAME = None

# ---------- Helper to overlay text ----------
def overlay_text(msg, color=(0, 255, 0)):
    global CURRENT_FRAME
    if CURRENT_FRAME is not None:
        cv2.putText(
            CURRENT_FRAME,
            msg,
            (10, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            color,
            2,
            cv2.LINE_AA
        )

# ---------- Actions ----------
def play_beep_success():
    try:
        winsound.Beep(700, 220)
        overlay_text("✅ Success Beep")
    except Exception:
        pass

def play_beep_alert():
    try:
        winsound.Beep(480, 180)
        overlay_text("⚠ Alert Beep", color=(0,0,255))
    except Exception:
        pass

def open_chrome(chrome_path=None):
    try:
        if platform.system() == "Windows":
            if chrome_path and Path(chrome_path).exists():
                os.startfile(chrome_path)
            else:
                subprocess.Popen(["start", "https://www.google.com"], shell=True)
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", "-a", "Google Chrome"])
        else:
            for cmd in (["google-chrome"], ["google-chrome-stable"], ["chromium"], ["chromium-browser"]):
                try:
                    subprocess.Popen(cmd)
                    break
                except FileNotFoundError:
                    continue
            else:
                subprocess.Popen(["xdg-open", "https://www.google.com"])
        overlay_text("🌐 Chrome Opened")
        return True
    except Exception as e:
        print("open_chrome error:", e)
        overlay_text("❌ Chrome Open Error", color=(0,0,255))
        return False

def close_chrome():
    try:
        if platform.system() == "Windows":
            subprocess.Popen(["taskkill", "/IM", "chrome.exe", "/F"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        elif platform.system() == "Darwin":
            subprocess.Popen(["pkill", "Google Chrome"])
        else:
            subprocess.Popen(["pkill", "chrome"])
        overlay_text("✖ Chrome Closed", color=(0,0,255))
        return True
    except Exception as e:
        print("close_chrome error:", e)
        overlay_text("❌ Chrome Close Error", color=(0,0,255))
        return False

def start_django(django_path=None):
    try:
        if not django_path:
            print("Django path not set.")
            overlay_text("❌ Django Path Missing", color=(0,0,255))
            return False
        manage_file = os.path.join(django_path, "manage.py")
        if not os.path.exists(manage_file):
            print("manage.py not found in", django_path)
            overlay_text("❌ manage.py Missing", color=(0,0,255))
            return False
        subprocess.Popen(["python", "manage.py", "runserver"], cwd=django_path)
        overlay_text("🚀 Django Started")
        return True
    except Exception as e:
        print("start_django error:", e)
        overlay_text("❌ Django Error", color=(0,0,255))
        return False

def take_screenshot(dst_folder="screenshots"):
    try:
        p = Path(dst_folder)
        p.mkdir(parents=True, exist_ok=True)
        ts = int(time.time())
        filename = p / f"screenshot_{ts}.png"
        img = pyautogui.screenshot()
        img.save(str(filename))
        overlay_text(f"📸 Screenshot Saved")
        # Open automatically
        try:
            from PIL import Image
            Image.open(str(filename)).show()
        except Exception:
            pass
        return str(filename)
    except Exception as e:
        print("screenshot error:", e)
        overlay_text("❌ Screenshot Error", color=(0,0,255))
        return None

def switch_tab(direction="next"):
    try:
        if direction == "next":
            pyautogui.hotkey('ctrl', 'tab')
            overlay_text("➡ Next Tab")
        else:
            pyautogui.hotkey('ctrl', 'shift', 'tab')
            overlay_text("⬅ Prev Tab")
        return True
    except Exception as e:
        print("switch_tab error:", e)
        overlay_text("❌ Tab Switch Error", color=(0,0,255))
        return False

def control_volume(delta_steps):
    try:
        key = 'volumeup' if delta_steps > 0 else 'volumedown'
        for _ in range(abs(delta_steps)):
            pyautogui.press(key)
            time.sleep(0.05)
        overlay_text(f"🔊 Volume {'+' if delta_steps>0 else '-'}{abs(delta_steps)}")
        return True
    except Exception as e:
        print("control_volume error:", e)
        overlay_text("❌ Volume Error", color=(0,0,255))
        return False

def move_mouse_to(x, y):
    try:
        pyautogui.moveTo(x, y, duration=0.05)
        return True
    except Exception as e:
        print("move_mouse error:", e)
        overlay_text("❌ Mouse Error", color=(0,0,255))
        return False

def click_mouse():
    try:
        pyautogui.click()
        overlay_text("🖱 Click")
        return True
    except Exception as e:
        print("click_mouse error:", e)
        overlay_text("❌ Click Error", color=(0,0,255))
        return False
