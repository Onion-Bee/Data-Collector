import subprocess
import sys
import time

def run_with_head_monitor(script_name):
    # Start head_monitor.py
    head_proc = subprocess.Popen([sys.executable, "head_monitor.py"])
    try:
        # Run the target script
        subprocess.run([sys.executable, script_name], check=True)
    finally:
        # Terminate head_monitor.py after the script
        head_proc.terminate()
        head_proc.wait()
        time.sleep(1)  # Small buffer time between scripts

# Run info.py (no head monitor needed)
subprocess.run([sys.executable, "info.py"], check=True)

# Run game.py with head monitor
run_with_head_monitor("game.py")

# Run name.py with head monitor
run_with_head_monitor("name.py")

# Run video_player.py with head monitor
subprocess.run([sys.executable, "video_player.py"], check=True)

# Run the OpenFace batch script after everything
subprocess.run([sys.executable, "run_openface_batch.py"], check=True)

