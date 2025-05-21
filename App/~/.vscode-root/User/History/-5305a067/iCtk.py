# import subprocess

# # Run the Kid Info and M-CHAT-RF script
# subprocess.run(["python", "info.py"])

# # Run the Bubble Pop Game
# subprocess.run(["python", "game.py"])
import subprocess
import sys

# Start head.py as a background process
head_proc = subprocess.Popen([sys.executable, "head.py"]),

try:
    # Run the Kid Info and M-CHAT-RF script
    subprocess.run([sys.executable, "info.py"], check=True)

    # Run the Bubble Pop Game
    subprocess.run([sys.executable, "game.py"], check=True)

finally:
    # Ensure head.py is terminated when the other scripts complete
    head_proc.terminate()
    head_proc.wait()
