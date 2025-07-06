import sys
import os
import time
import threading
import pandas as pd
from gtts import gTTS
import pygame
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QPushButton, QVBoxLayout,
    QLabel, QGraphicsDropShadowEffect, QFrame
)
from PyQt5.QtGui import QPixmap, QPalette, QBrush, QFont
from PyQt5.QtCore import Qt, QRect, QPropertyAnimation, QEasingCurve

# Base logs directory
BASE_LOGS_DIR = "logs"
os.makedirs(BASE_LOGS_DIR, exist_ok=True)

# Determine active child folder
current_folder_file = os.path.join(BASE_LOGS_DIR, "current_folder.txt")
try:
    with open(current_folder_file, 'r') as cf:
        folder_name = cf.read().strip()
    logs_dir = os.path.join(BASE_LOGS_DIR, folder_name) if folder_name else BASE_LOGS_DIR
except FileNotFoundError:
    logs_dir = BASE_LOGS_DIR
os.makedirs(logs_dir, exist_ok=True)

# Read child info CSV and format name
df_path = os.path.join(logs_dir, "kid_info.csv")
if not os.path.exists(df_path):
    raise FileNotFoundError(f"No kid_info.csv found in {logs_dir}")
df = pd.read_csv(df_path)
first_name_raw = df.iloc[0]['name']
first_name = first_name_raw.replace('_', ' ')

# Prepare greeting audio
greeting_text = f"Hello {first_name}, how are you!"
audio_file = os.path.join(logs_dir, "greeting.mp3")
if not os.path.exists(audio_file):
    tts = gTTS(text=greeting_text, lang='en')
    tts.save(audio_file)

# Play greeting audio in background
def play_greeting():
    try:
        pygame.mixer.init()
        pygame.mixer.music.load(audio_file)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.delay(100)
        pygame.mixer.quit()
        os.remove(audio_file)
    except Exception:
        pass

# Log user's response
def record_response(answer, duration):
    log_file = os.path.join(logs_dir, f"{first_name}_Response.csv")
    df_entry = pd.DataFrame([{'response': answer, 'response_time': duration}])
    header = not os.path.exists(log_file)
    df_entry.to_csv(log_file, mode='a', header=header, index=False)

# Main application window
class GreetingWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # Preload background pixmap to ensure it's available
        self.bg_pixmap = QPixmap('src/background.jpg')
        # Placeholder for animation before UI init
        self.anim = None
        self.start_time = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("How are you?")
        self.showFullScreen()

        # Apply background image
        palette = QPalette()
        palette.setBrush(QPalette.Window, QBrush(self.bg_pixmap.scaled(
            self.size(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation)))
        self.setPalette(palette)

        # Overlay frame
        self.overlay = QFrame(self)
        self.overlay.setStyleSheet(
            "background-color: rgba(255, 255, 255, 200);"
            "border-radius: 30px;"
        )
        shadow = QGraphicsDropShadowEffect(blurRadius=30, xOffset=0, yOffset=0)
        self.overlay.setGraphicsEffect(shadow)

        # Layout inside overlay
        vbox = QVBoxLayout(self.overlay)
        vbox.setSpacing(40)
        vbox.setContentsMargins(50, 50, 50, 50)
        vbox.setAlignment(Qt.AlignCenter)

        # Prompt
        prompt = QLabel("Hello, how are you?")
        prompt.setFont(QFont('Helvetica', 36, QFont.Bold))
        prompt.setAlignment(Qt.AlignCenter)
        vbox.addWidget(prompt)

        # Buttons container
        btn_frame = QFrame()
        btn_layout = QVBoxLayout(btn_frame)
        btn_layout.setSpacing(30)
        btn_layout.setAlignment(Qt.AlignCenter)

        for text in ["I am good", "I am not good"]:
            btn = QPushButton(text)
            btn.setFixedSize(400, 100)
            btn.setFont(QFont('Helvetica', 24))
            btn.setStyleSheet(
                "QPushButton { background-color: #28a745; color: white; border-radius: 50px; padding: 15px; }"
                "QPushButton:hover { background-color: #218838; }"
            )
            btn.clicked.connect(self.handle_click)
            btn_layout.addWidget(btn)

        vbox.addWidget(btn_frame)

        # Central widget
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.addWidget(self.overlay, alignment=Qt.AlignCenter)
        self.setCentralWidget(container)

        # Resize animation for overlay
        self.anim = QPropertyAnimation(self.overlay, b"geometry")
        self.anim.setDuration(800)
        self.anim.setEasingCurve(QEasingCurve.OutBack)

        # Track start time
        self.start_time = time.time()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Update background on resize
        palette = self.palette()
        palette.setBrush(QPalette.Window, QBrush(self.bg_pixmap.scaled(
            self.size(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation)))
        self.setPalette(palette)

        # Center and animate overlay
        w, h = self.width() * 0.6, self.height() * 0.6
        x = (self.width() - w) / 2
        y = (self.height() - h) / 2
        if self.anim:
            self.anim.stop()
            self.anim.setStartValue(self.overlay.geometry())
            self.anim.setEndValue(QRect(int(x), int(y), int(w), int(h)))
            self.anim.start()

    def handle_click(self):
        btn = self.sender()
        duration = time.time() - self.start_time
        record_response(btn.text(), duration)
        QApplication.instance().quit()

# Entry point
if __name__ == '__main__':
    threading.Thread(target=play_greeting, daemon=True).start()
    app = QApplication(sys.argv)
    window = GreetingWindow()
    sys.exit(app.exec_())
