import subprocess
import sys
import threading
import time

#Start head.py as a background thread

head_proc = subprocess.Popen([sys.executable, "head_monitor.py"])

try:
    # Run the Kid Info and M-CHAT-RF script
    subprocess.run([sys.executable, "info.py"], check=True)

    # Run the Bubble Pop Game

    subprocess.run([sys.executable, "game.py"], check=True)

    subprocess.run([sys.executable, "name.py"], check=True)
    # Wait a short time if needed or do other tasks here
    subprocess.run([sys.executable, "video_player.py"], check=True)
    time.sleep(2)

finally:
    # Ensure head.py is terminated when the other scripts completeAdd commentMore actions
    head_proc.terminate()
    head_proc.wait() 
    time.sleep(1)
    subprocess.run([sys.executable, "run_openface_batch.py"], check=True)