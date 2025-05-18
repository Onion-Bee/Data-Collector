import pandas as pd
from gtts import gTTS
import pygame
import time
import os

# 1. Read name from CSV
df = pd.read_csv("kid_info.csv")
first_name = df.iloc[0]['name']

# 2. Create greeting
greeting = f"Hello {first_name}, how are you!"

# 3. Save greeting to audio file using gTTS
audio_file = "greeting.mp3"
tts = gTTS(text=greeting, lang='en')
tts.save(audio_file)

if not os.path.exists(audio_file):
    raise FileNotFoundError(f"Audio file '{audio_file}' was not created.")

print(f"✅ Audio saved as {audio_file}")

# 4. Play using pygame
pygame.mixer.init()
pygame.mixer.music.load(audio_file)
pygame.mixer.music.play()

print("🔊 Playing the greeting...")

while pygame.mixer.music.get_busy():
    time.sleep(0.1)

pygame.mixer.quit()
print("✅ Playback finished.")
