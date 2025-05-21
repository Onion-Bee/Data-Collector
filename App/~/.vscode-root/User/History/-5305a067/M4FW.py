import subprocess
import sys
import threading
import time

# Start head.py as a background thread
head_proc = subprocess.Popen([sys.executable, "head.py"])

try:
    # Run the Kid Info and M-CHAT-RF script
    subprocess.run([sys.executable, "info.py"], check=True)

    # Run the Bubble Pop Game
    subprocess.run([sys.executable, "game.py"], check=True)

    # Wait a short time if needed or do other tasks here
    time.sleep(2)

finally:
    # Ensure head.py is terminated when the other scripts complete
    head_proc.terminate()
    head_proc.wait()
