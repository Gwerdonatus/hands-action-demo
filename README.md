🖐️ Hands Action Demo
Real-time Hand Gesture → Desktop Automation (Python + MediaPipe + PyAutoGUI)

This project is a gesture-controlled automation system that uses computer vision to detect hand poses and trigger real desktop actions — without touching the keyboard or mouse.

Built with Python, MediaPipe, TensorFlow Lite, and PyAutoGUI, it demonstrates real-time vision processing, gesture classification, and system automation.

✨ Features
🎯 Hand Gesture Detection

Uses MediaPipe Hands + TensorFlow Lite for fast real-time tracking.

Detects:

👍 Thumbs Up

✌️ Peace Sign

✋ Open Palm

👊 Fist

🤲 Two Hands

👆 Swipe Left / Swipe Right

⚡ Desktop Automation Actions

Each gesture triggers an OS-level action:

Gesture	Action
✋ Open Palm	Alert beep
👍 Thumbs Up	Success beep
✌️ Peace Sign	Open Chrome
🤲 Two Hands	Take screenshot
👊 Fist	Close Chrome
👈 Swipe Left	Next Tab (Ctrl + Tab)
👉 Swipe Right	Previous Tab (Ctrl + Shift + Tab)

All actions run instantly using PyAutoGUI, winsound, and OS-specific subprocess calls.

🧠 How It Works

The system runs a loop that:

Captures webcam frames

Runs hand detection → extracts landmarks

Classifies gesture using custom logic

Triggers mapped actions from actions.py

You can customize or add new gestures easily.

🗂️ Project Structure
hands-action-demo/
│── actions.py          # Executes system-level actions (Chrome, screenshot, beeps, tabs, volume)
│── gestures.py         # Gesture recognition + classification
│── hand_actions.py     # Main entry point (runs webcam + connections)
│── utils.py            # Helpers
│── config.json         # Stores your Chrome path, Django path, etc.
│── requirements.txt    # Dependencies
│── screenshots/        # Auto-generated screenshots
│── README.md
│── .gitignore

🚀 Getting Started
1. Install dependencies
pip install -r requirements.txt

2. Add your paths (optional)

Edit config.json:

{
  "chrome_path": "C:/Program Files/Google/Chrome/Application/chrome.exe",
  "django_path": ""
}

3. Run the program
python hand_actions.py


Press q to quit.

🧩 Add Your Own Gestures

Want to add a new gesture like ✍️ "draw in the air" or 👌 "open VS Code"?

Just edit:

gestures.py → detect gesture

actions.py → execute custom action

This is a great playground to experiment with gesture-controlled UI automation.

🌟 Why This Project is Valuable

This repo shows your skills in:

Computer Vision

Real-time systems

Gesture recognition

Automation engineering

Python scripting

OS-level process management

User experience design for hands-free control

This is portfolio-grade material that stands out.

📜 License

MIT License.
