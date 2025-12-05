import cv2
import mediapipe as mp
import time
import math
from collections import deque
from utils import load_config
from gestures import *
from actions import *
import pyautogui

# ---------- Load config ----------
cfg = load_config()
CHROME_PATH = cfg.get("chrome_path")
DJANGO_PATH = cfg.get("django_path")
COOLDOWN = cfg.get("cooldown_seconds", 2.5)  # increased to reduce spam
FRAMES_REQUIRED = cfg.get("frames_required", 3)

# ---------- Mediapipe ----------
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils
hands_detector = mp_hands.Hands(
    max_num_hands=2,
    model_complexity=0,
    min_detection_confidence=0.6,
    min_tracking_confidence=0.5
)

# ---------- State ----------
gesture_counters = {
    "thumbs": 0,
    "peace": 0,
    "fist": 0,
    "palm": 0,
    "pinky": 0,
    "index": 0
}
last_trigger_time = 0
last_gesture = None  # new: track last gesture fired

# swipe detection buffer
centroid_buffer = deque(maxlen=8)
SWIPE_THRESHOLD = 0.25  # normalized fraction of frame width

# Mouse mapping smoothing
screen_w, screen_h = pyautogui.size()

def normalized_to_screen(x_norm, y_norm, frame_w, frame_h):
    x = int(x_norm * frame_w)
    y = int(y_norm * frame_h)
    sx = int((x / frame_w) * screen_w)
    sy = int((y / frame_h) * screen_h)
    return sx, sy

def reset_counters():
    for k in gesture_counters:
        gesture_counters[k] = 0

def try_trigger(name, action_func, *args, **kwargs):
    global last_trigger_time, last_gesture
    now = time.time()
    if now - last_trigger_time < COOLDOWN:
        return False
    print(f"[ACTION] {name} -> executing")
    try:
        action_func(*args, **kwargs)
    except Exception as e:
        print("Action error:", e)
    last_trigger_time = now
    last_gesture = name
    reset_counters()
    centroid_buffer.clear()
    return True

def main():
    global last_trigger_time, last_gesture
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Cannot open camera")
        return

    print("Hand gesture control running. Press 'q' to quit.")
    last_mouse_x, last_mouse_y = None, None

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.flip(frame, 1)
        frame_h, frame_w, _ = frame.shape

        # resize for speed
        max_w = 800
        if frame_w > max_w:
            scale = max_w / frame_w
            frame = cv2.resize(frame, (int(frame_w*scale), int(frame_h*scale)))
            frame_h, frame_w, _ = frame.shape

        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands_detector.process(img_rgb)
        multi = results.multi_hand_landmarks

        if multi:
            for idx, hand_landmarks in enumerate(multi):
                lm = hand_landmarks.landmark
                mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                # --- Gesture counters ---
                gesture_counters["thumbs"] = gesture_counters["thumbs"] + 1 if is_thumbs_up(lm) else 0
                gesture_counters["peace"] = gesture_counters["peace"] + 1 if is_peace(lm) else 0
                gesture_counters["fist"] = gesture_counters["fist"] + 1 if is_fist(lm) else 0
                gesture_counters["palm"] = gesture_counters["palm"] + 1 if is_open_palm(lm) else 0
                gesture_counters["pinky"] = gesture_counters["pinky"] + 1 if is_pinky_up(lm) else 0
                gesture_counters["index"] = gesture_counters["index"] + 1 if index_up(lm) else 0

                # --- Mouse control ---
                if gesture_counters["index"] >= FRAMES_REQUIRED:
                    tip = lm[8]
                    sx, sy = normalized_to_screen(tip.x, tip.y, frame_w, frame_h)
                    if last_mouse_x is None:
                        last_mouse_x, last_mouse_y = sx, sy
                    else:
                        sx = int(last_mouse_x + (sx - last_mouse_x) * 0.35)
                        sy = int(last_mouse_y + (sy - last_mouse_y) * 0.35)
                    try:
                        move_mouse_to(sx, sy)
                    except Exception:
                        pass
                    last_mouse_x, last_mouse_y = sx, sy
                    # click if thumb close to index
                    thumb_tip = lm[4]
                    dx = abs(thumb_tip.x - tip.x)
                    dy = abs(thumb_tip.y - tip.y)
                    if math.hypot(dx, dy) < 0.03:
                        click_mouse()
                        try_trigger("Index Click", lambda: None)

                # --- Swipe detection ---
                cx, cy = hand_centroid(lm)
                centroid_buffer.append(cx)

            # --- Swipe left/right ---
            if len(centroid_buffer) >= centroid_buffer.maxlen:
                dx = centroid_buffer[-1] - centroid_buffer[0]
                if dx > SWIPE_THRESHOLD:
                    if last_gesture != "Swipe Right -> Prev Tab":
                        try_trigger("Swipe Right -> Prev Tab", switch_tab, "prev")
                elif dx < -SWIPE_THRESHOLD:
                    if last_gesture != "Swipe Left -> Next Tab":
                        try_trigger("Swipe Left -> Next Tab", switch_tab, "next")

            # --- Gesture triggers ---
            if gesture_counters["thumbs"] >= FRAMES_REQUIRED and last_gesture != "Thumbs Up -> Success Beep":
                try_trigger("Thumbs Up -> Success Beep", play_beep_success)
            elif gesture_counters["peace"] >= FRAMES_REQUIRED and last_gesture != "Peace Sign -> Open Chrome":
                try_trigger("Peace Sign -> Open Chrome", open_chrome, CHROME_PATH)
            elif gesture_counters["fist"] >= FRAMES_REQUIRED and last_gesture != "Fist -> Close Chrome":
                try_trigger("Fist -> Close Chrome", close_chrome)
            elif gesture_counters["palm"] >= FRAMES_REQUIRED and last_gesture != "Open Palm -> Alert Beep":
                try_trigger("Open Palm -> Alert Beep", play_beep_alert)
            elif gesture_counters["pinky"] >= FRAMES_REQUIRED and last_gesture != "Pinky Up -> Start Django":
                try_trigger("Pinky Up -> Start Django", start_django, DJANGO_PATH)

            # --- Two hands open for screenshot ---
            if len(multi) == 2:
                h0, h1 = multi[0].landmark, multi[1].landmark
                if is_open_palm(h0) and is_open_palm(h1) and last_gesture != "Two Hands -> Screenshot":
                    try_trigger("Two Hands -> Screenshot", take_screenshot)

        # Overlay instructions
        cv2.putText(frame, "Gestures: 👍 Thumbs | ✌ Peace | ✊ Fist | 🖐 Palm | 🤙 Pinky | ✋✋ TwoHands=screenshot", 
                    (10,25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 2)

        cv2.imshow("Hand Actions Demo", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        time.sleep(0.02)

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
