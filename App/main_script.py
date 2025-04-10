# Main Application
import tkinter as tk
import threading
from video_player import VideoPlayer
from simple_game import SimpleGame

# Main Application
class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Video and Game Transition GUI")

        self.video_label = tk.Label(root)
        self.video_label.pack()

        self.video_player = VideoPlayer("sample_video.mp4", self.video_label)
        self.simple_game = SimpleGame()

        threading.Thread(target=self.run_sequence).start()

    def run_sequence(self):
        while True:
            # Play Video
            self.video_player.play()
            self.video_player.wait_until_done()

            # Play Game
            self.video_player.stop()
            self.simple_game.start()

# Run the application
if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
