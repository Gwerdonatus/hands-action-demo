# gestures.py
from typing import List
import mediapipe as mp

# Helper to get landmark by index
def lm_xy(lm, i, frame_w, frame_h):
    return (int(lm[i].x * frame_w), int(lm[i].y * frame_h))

def fingers_status(landmarks):
    """
    Returns booleans for fingers: thumb, index, middle, ring, pinky
    landmarks: list of mediapipe landmarks
    Uses basic tip vs pip tests.
    """
    tips = [4, 8, 12, 16, 20]
    pips = [2, 6, 10, 14, 18]
    status = []
    for tip, pip in zip(tips, pips):
        status.append(landmarks[tip].y < landmarks[pip].y)
    # status = [thumb, index, middle, ring, pinky]
    return status

def is_thumbs_up(landmarks):
    s = fingers_status(landmarks)
    thumb, index, middle, ring, pinky = s
    wrist = landmarks[0].y
    thumb_tip = landmarks[4].y
    return thumb and (not index) and (not middle) and (not ring) and (not pinky) and (thumb_tip < wrist)

def is_peace(landmarks):
    s = fingers_status(landmarks)
    thumb, index, middle, ring, pinky = s
    # index and middle up, ring & pinky down
    # ensure index & middle are separated horizontally
    sep = abs(landmarks[8].x - landmarks[12].x) > 0.03
    return index and middle and (not ring) and (not pinky) and sep

def is_fist(landmarks):
    # all tips below their pips
    s = fingers_status(landmarks)
    return not any(s[1:])  # index..pinky all down (thumb can be either)

def is_open_palm(landmarks):
    s = fingers_status(landmarks)
    # all (index..pinky) extended
    return s[1] and s[2] and s[3] and s[4]

def is_pinky_up(landmarks):
    s = fingers_status(landmarks)
    thumb, index, middle, ring, pinky = s
    return pinky and (not index) and (not middle)

def index_up(landmarks):
    s = fingers_status(landmarks)
    return s[1] and (not s[2])  # index up, middle down

# centroid for swipe detection
def hand_centroid(landmarks):
    xs = [l.x for l in landmarks]
    ys = [l.y for l in landmarks]
    return (sum(xs)/len(xs), sum(ys)/len(ys))
