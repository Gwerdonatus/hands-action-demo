# generate_beep.py
import sys
import os
import platform
import threading
import tempfile
import wave
import numpy as np
import subprocess

def _play_via_simpleaudio(frequency=880, duration_ms=300, volume=0.3):
    try:
        import simpleaudio as sa
    except Exception:
        return False

    fs = 44100
    t = np.linspace(0, duration_ms / 1000.0, int(fs * duration_ms / 1000.0), False)
    tone = np.sin(frequency * t * 2 * np.pi)
    audio = (tone * (2**15 - 1) * volume).astype(np.int16)

    try:
        play_obj = sa.play_buffer(audio, 1, 2, fs)
        # do not block; leave it playing in background
        return True
    except Exception:
        return False

def _write_temp_wav(frequency=880, duration_ms=300, volume=0.3):
    fs = 44100
    t = np.linspace(0, duration_ms / 1000.0, int(fs * duration_ms / 1000.0), False)
    tone = np.sin(frequency * t * 2 * np.pi)
    audio = (tone * (2**15 - 1) * volume).astype(np.int16)

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    tmp_name = tmp.name
    tmp.close()

    with wave.open(tmp_name, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)  # 2 bytes for int16
        wf.setframerate(fs)
        wf.writeframes(audio.tobytes())

    return tmp_name

def _play_via_system_cmd(wav_path):
    system = platform.system()
    try:
        if system == "Darwin":  # macOS
            subprocess.Popen(["afplay", wav_path])
            return True
        elif system == "Linux":
            # Try paplay, aplay, or play
            for cmd in (["paplay", wav_path], ["aplay", wav_path], ["play", wav_path]):
                try:
                    subprocess.Popen(cmd)
                    return True
                except FileNotFoundError:
                    continue
            # last resort: xdg-open
            subprocess.Popen(["xdg-open", wav_path])
            return True
        elif system == "Windows":
            # Use powershell to play (fallback), but prefer winsound (handled elsewhere)
            subprocess.Popen(["powershell", "-c", f"(New-Object Media.SoundPlayer '{wav_path}').Play()"],
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
    except Exception:
        return False
    return False

def _play_via_winsound(frequency=880, duration_ms=300):
    try:
        import winsound
    except Exception:
        return False
    try:
        winsound.Beep(int(frequency), int(duration_ms))
        return True
    except Exception:
        return False

def _cleanup_file(path, delay=2.0):
    """Remove a temporary file after a short delay so playback can finish."""
    import time
    time.sleep(delay)
    try:
        os.remove(path)
    except Exception:
        pass

def _play_once(frequency=880, duration_ms=300, volume=0.3):
    """Attempt multiple playback methods until one works."""
    # 1) Windows winsound (safe & synchronous)
    if platform.system() == "Windows":
        ok = _play_via_winsound(frequency, duration_ms)
        if ok:
            return True

    # 2) try simpleaudio
    ok = _play_via_simpleaudio(frequency, duration_ms, volume)
    if ok:
        return True

    # 3) write temp wav and call system player
    try:
        wav = _write_temp_wav(frequency, duration_ms, volume)
        ok = _play_via_system_cmd(wav)
        if ok:
            # schedule cleanup
            t = threading.Thread(target=_cleanup_file, args=(wav, 3.0), daemon=True)
            t.start()
            return True
    except Exception:
        pass

    return False

def play_beep(frequency=880, duration_ms=300, volume=0.3):
    """
    Non-blocking wrapper that runs playback in a daemon thread.
    Returns immediately.
    """
    def _worker():
        try:
            _play_once(frequency, duration_ms, volume)
        except Exception:
            # swallow errors; main program should not crash due to audio
            pass

    t = threading.Thread(target=_worker, daemon=True)
    t.start()
    return True
