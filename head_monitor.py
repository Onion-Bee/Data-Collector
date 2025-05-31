import os
import glob
import re
import cv2
import mediapipe as mp
import numpy as np
import time
from collections import deque
import threading
import keyboard  
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

# Sampling configuration
SAMPLE_RATE_HZ   = 10.0  # samples per second
_sample_interval = 1.0 / SAMPLE_RATE_HZ
_last_sample_time = 0.0

start_time = time.time()

# MSE helper
def multiscale_entropy(time_series, m=2, r=0.15):
    def _phi(dim):
        x = np.array([time_series[i:i+dim] for i in range(len(time_series)-dim+1)])
        C = np.sum(np.max(np.abs(x[:, None] - x[None, :]), axis=2) <= r, axis=0) / (len(time_series)-dim+1)
        return np.sum(np.log(C)) / (len(time_series)-dim+1)
    if len(time_series) < m + 1:
        return np.nan
    r *= np.std(time_series)
    return _phi(m) - _phi(m+1)

# toggle display
show_window = False
def toggle_window_listener():
    global show_window
    while True:
        keyboard.wait('v')
        show_window = not show_window
        print(f"Window {'shown' if show_window else 'hidden'}")
threading.Thread(target=toggle_window_listener, daemon=True).start()

# Mediapipe init
mp_face_mesh = mp.solutions.face_mesh
mp_drawing    = mp.solutions.drawing_utils
mp_styles     = mp.solutions.drawing_styles
face_mesh = mp_face_mesh.FaceMesh(
    static_image_mode=False,
    max_num_faces=1,
    min_detection_confidence=0.5,
    refine_landmarks=False
)

# landmark indices
LEFT_EYEBROW = [55,65,52,53,46]
RIGHT_EYEBROW= [285,295,282,283,276]
MOUTH        = [78,191,80,81,82,13,312,311,310,415,308]
LEFT_EYE     = [33,160,158,133,153,144]
RIGHT_EYE    = [362,385,387,263,373,380]
NOSE_TIP     = 1

# thresholds
EAR_CLOSE        = 0.22
EAR_OPEN         = 0.25
MIN_CONSEC_FRAMES= 3
NOSE_MOVE_THRESH = 15

# state
blink_count       = 0
eye_closed_frames = 0
head_movements    = 0
last_nose_pos     = None

# history deques
HISTORY_LENGTH = 50
le_x, le_y = deque(maxlen=HISTORY_LENGTH), deque(maxlen=HISTORY_LENGTH)
re_x, re_y = deque(maxlen=HISTORY_LENGTH), deque(maxlen=HISTORY_LENGTH)
m_x,  m_y  = deque(maxlen=HISTORY_LENGTH), deque(maxlen=HISTORY_LENGTH)

cap = cv2.VideoCapture(0)

video_writer = None

def eye_aspect_ratio(eye):
    A = np.linalg.norm(eye[1]-eye[5])
    B = np.linalg.norm(eye[2]-eye[4])
    C = np.linalg.norm(eye[0]-eye[3])
    return (A+B)/(2.0*C)

def compute_motion_energy(traj):
    pts = list(traj)
    if len(pts)<2: return 0.0
    arr = np.array(pts)
    return np.sum(np.linalg.norm(np.diff(arr,axis=0),axis=1))

while True:
    ret, frame = cap.read()
    if not ret: break

    # Initialize video writer after first frame is captured
    if video_writer is None:
        fourcc = cv2.VideoWriter_fourcc(*"XVID")
        fps = cap.get(cv2.CAP_PROP_FPS) or 30  # fallback to 30 if unable to get FPS
        height, width = frame.shape[:2]
        video_writer = cv2.VideoWriter(video_filename, fourcc, fps, (width, height))
        print(f"Started recording video at {fps} FPS, size: {width}x{height}")

    # Write frame to video
    video_writer.write(frame)

    h,w = frame.shape[:2]
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    res = face_mesh.process(rgb)

    # defaults
    avg_ear = None

    if res.multi_face_landmarks:
        lm     = res.multi_face_landmarks[0]
        coords = np.array([[p.x*w, p.y*h] for p in lm.landmark])

        # blink
        left_eye  = coords[LEFT_EYE]
        right_eye = coords[RIGHT_EYE]
        avg_ear   = (eye_aspect_ratio(left_eye)+eye_aspect_ratio(right_eye))/2
        if avg_ear < EAR_CLOSE:
            eye_closed_frames += 1
        elif eye_closed_frames >= MIN_CONSEC_FRAMES:
            blink_count += 1
            eye_closed_frames = 0
        else:
            eye_closed_frames = 0

        # head moves
        nose = coords[NOSE_TIP]
        if last_nose_pos is not None and np.linalg.norm(nose-last_nose_pos)>NOSE_MOVE_THRESH:
            head_movements += 1
        last_nose_pos = nose

        # trajectories
        le_pts, re_pts, m_pts = coords[LEFT_EYEBROW], coords[RIGHT_EYEBROW], coords[MOUTH]
        le_x.append(np.mean(le_pts[:,0])); le_y.append(np.mean(le_pts[:,1]))
        re_x.append(np.mean(re_pts[:,0])); re_y.append(np.mean(re_pts[:,1]))
        m_x .append(np.mean(m_pts[:,0]));  m_y.append(np.mean(m_pts[:,1]))

        # MSE
        if len(le_x)==HISTORY_LENGTH:
            mse_le_x = multiscale_entropy(np.array(le_x))
            mse_le_y = multiscale_entropy(np.array(le_y))
            mse_re_x = multiscale_entropy(np.array(re_x))
            mse_re_y = multiscale_entropy(np.array(re_y))
            mse_m_x  = multiscale_entropy(np.array(m_x))
            mse_m_y  = multiscale_entropy(np.array(m_y))
        else:
            mse_le_x=mse_le_y=mse_re_x=mse_re_y=mse_m_x=mse_m_y=np.nan

        # motion energy
        me_le = compute_motion_energy(zip(le_x,le_y))
        me_re = compute_motion_energy(zip(re_x,re_y))
        me_m  = compute_motion_energy(zip(m_x,m_y ))

        # elapsed time for rates
        elapsed = time.time() - start_time
        blink_rate = (blink_count/elapsed)*60 if elapsed>0 else 0
        head_rate  = (head_movements/elapsed)*60 if elapsed>0 else 0

        mp_drawing.draw_landmarks(
        frame,
        lm,
        mp_face_mesh.FACEMESH_TESSELATION,
        landmark_drawing_spec=None,
        connection_drawing_spec=mp_styles.get_default_face_mesh_tesselation_style())

    # overlay text
    timestamp = datetime.now().strftime("%H:%M:%S")
    info = [
        f"Time: {timestamp}",
        f"EAR: {avg_ear:.3f}" if avg_ear is not None else "EAR: N/A",
        f"Blinks: {blink_count}",
        f"Head mvts: {head_movements}",
        f"LE: ({le_x[-1]:.0f},{le_y[-1]:.0f})" if le_x else "",
        f"RE: ({re_x[-1]:.0f},{re_y[-1]:.0f})" if re_x else "",
        f"M:  ({m_x[-1]:.0f},{m_y[-1]:.0f})" if m_x else "",
    ]
    for i,txt in enumerate(info):
        cv2.putText(frame, txt, (10, 30+30*i),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)

    # show/hide window
    cv2.imshow("Facial Dynamics", frame)
    try:
        if show_window:
            cv2.moveWindow("Facial Dynamics", 100, 100)
        else:
            cv2.moveWindow("Facial Dynamics", -3000, -3000)
    except cv2.error:
        pass

    if cv2.waitKey(1)&0xFF==ord('q'):
        break

cap.release()
if video_writer:
    video_writer.release()
cv2.destroyAllWindows()
