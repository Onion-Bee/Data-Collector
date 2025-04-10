import cv2
from PIL import Image, ImageTk
import time
import threading

class VideoPlayer:
    def __init__(self, video_path, label):
        self.video_path = video_path
        self.label = label
        self.cap = cv2.VideoCapture(self.video_path)
        self.running = False

    def play(self):
        self.running = True
        threading.Thread(target=self._play_video).start()

    def _play_video(self):
        while self.running and self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret:
                break
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = ImageTk.PhotoImage(Image.fromarray(frame))
            self.label.config(image=frame)
            self.label.image = frame
            time.sleep(0.03)

    def stop(self):
        self.running = False
        self.cap.release()
