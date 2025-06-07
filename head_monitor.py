import os
import glob
import re
import cv2
import time
from datetime import datetime

# =============== Video Recording Setup ===============
recording_dir = "recording_dump"
os.makedirs(recording_dir, exist_ok=True)

# Find next available recording filename
existing_vids = glob.glob(os.path.join(recording_dir, "recording_*.avi"))
vid_indices = []
for fn in existing_vids:
    m = re.match(r"recording_(\d+)\.avi$", os.path.basename(fn))
    if m:
        vid_indices.append(int(m.group(1)))
vid_next_idx = max(vid_indices) + 1 if vid_indices else 1
video_filename = os.path.join(recording_dir, f"recording_{vid_next_idx}.avi")
print(f"Recording video to → {video_filename}")

cap = cv2.VideoCapture(0)
video_writer = None

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Initialize video writer after first frame is captured
    if video_writer is None:
        fourcc = cv2.VideoWriter_fourcc(*"XVID")
        fps = cap.get(cv2.CAP_PROP_FPS) or 30  # fallback to 30 if unable to get FPS
        height, width = frame.shape[:2]
        video_writer = cv2.VideoWriter(video_filename, fourcc, fps, (width, height))
        print(f"Started recording video at {fps} FPS, size: {width}x{height}")

    # Overlay timestamp onto frame (so it's baked into the recording)
    timestamp = datetime.now().strftime("%H:%M:%S")
    cv2.putText(
        frame,
        f"Time: {timestamp}",
        (10, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 255, 0),
        2
    )

    # Write frame to video file
    video_writer.write(frame)

    # No window is shown; just keep recording until externally terminated

# Cleanup
cap.release()
if video_writer:
    video_writer.release()
