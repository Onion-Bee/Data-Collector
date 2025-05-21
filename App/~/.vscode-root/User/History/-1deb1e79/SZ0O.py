import sys
import os
import time
import pandas as pd
from gtts import gTTS
import pygame
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel

# 1. Read name from CSV
DF_PATH = "kid_info.csv"
LOGS_DIR = "logs"
if not os.path.exists(LOGS_DIR):
    os.makedirs(LOGS_DIR)

df = pd.read_csv(DF_PATH)
first_name = df.iloc[0]['name']

# 2. Create greeting text and audio file
greeting = f"Hello {first_name}, how are you!"
audio_file = "greeting.mp3"

# Generate speech
tts = gTTS(text=greeting, lang='en')
tts.save(audio_file)
if not os.path.exists(audio_file):
    raise FileNotFoundError(f"Audio file '{audio_file}' was not created.")
print(f"✅ Audio saved as {audio_file}")

# 3. Play audio
pygame.mixer.init()
pygame.mixer.music.load(audio_file)

# Record start time just before playback
start_time = time.time()
pygame.mixer.music.play()
print("🔊 Playing the greeting...")

# Wait until playback finishes
while pygame.mixer.music.get_busy():
    pygame.time.delay(100)
pygame.mixer.quit()
print("✅ Playback finished.")

# 4. Show response UI
def record_response(response_text, response_time):
    # Prepare log file
    log_file = os.path.join(LOGS_DIR, f"{first_name}_Response.csv")
    header = ['response', 'response_time']
    entry = {'response': response_text, 'response_time': response_time}

    # Append to CSV
    if not os.path.exists(log_file):
        pd.DataFrame(columns=header).to_csv(log_file, index=False)
    pd.DataFrame([entry]).to_csv(log_file, mode='a', header=False, index=False)
    print(f"✅ Logged: {entry} to {log_file}")
    app.quit()

app = QApplication(sys.argv)
window = QWidget()
window.setWindowTitle('How are you?')
layout = QVBoxLayout()

prompt = QLabel('How are you?')
prompt.setStyleSheet("font-size: 24px; padding: 10px;")
layout.addWidget(prompt)

# Create buttons
def make_button(text):
    btn = QPushButton(text)
    btn.setStyleSheet("font-size: 20px; padding: 20px;")
    return btn

btn_good = make_button("I am good")
btn_not_good = make_button("I am not good")
layout.addWidget(btn_good)
layout.addWidget(btn_not_good)
window.setLayout(layout)

# Connect buttons to record function
btn_good.clicked.connect(lambda: record_response('good', time.time() - start_time))
btn_not_good.clicked.connect(lambda: record_response('not_good', time.time() - start_time))

window.show()
sys.exit(app.exec_())
