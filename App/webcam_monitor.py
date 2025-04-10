import cv2
from PIL import Image, ImageTk
import time
import threading

class WebcamMonitor:
    def __init__(self, label):
        self.label = label
        self.cap = cv2.VideoCapture(0)
        self.running = False

    def start(self):
        self.running = True
        threading.Thread(target=self._monitor_webcam).start()

    def _monitor_webcam(self):
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
