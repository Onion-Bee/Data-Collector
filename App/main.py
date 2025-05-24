import subprocess
import sys
import threading
import time


    # Run the Kid Info and M-CHAT-RF script
subprocess.run([sys.executable, "info.py"], check=True)

    # Run the Bubble Pop Game
subprocess.run([sys.executable, "game.py"], check=True)

subprocess.run([sys.executable, "name.py"], check=True)

    # Wait a short time if needed or do other tasks here
time.sleep(2)