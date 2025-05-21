import cv2
import time
import numpy as np
import mediapipe as mp

# 3D model points for solvePnP
MODEL_POINTS = np.array([
    (0.0, 0.0, 0.0),             # Nose tip
    (0.0, -330.0, -65.0),        # Chin
    (-225.0, 170.0, -135.0),     # Left eye left corner
    (225.0, 170.0, -135.0),      # Right eye right corner
    (-150.0, -150.0, -125.0),    # Left mouth corner
    (150.0, -150.0, -125.0)      # Right mouth corner
], dtype=np.float64)

LANDMARK_IDS = {
    "nose_tip": 1,
    "chin": 152,
    "left_eye_outer": 33,
    "right_eye_outer": 263,
    "left_mouth": 61,
    "right_mouth": 291
}

def get_head_pose(image_size, lm):
    # build 2D points
    image_points = np.array([
        (lm[LANDMARK_IDS["nose_tip"]].x * image_size[0],
         lm[LANDMARK_IDS["nose_tip"]].y * image_size[1]),
        (lm[LANDMARK_IDS["chin"]].x * image_size[0],
         lm[LANDMARK_IDS["chin"]].y * image_size[1]),
        (lm[LANDMARK_IDS["left_eye_outer"]].x * image_size[0],
         lm[LANDMARK_IDS["left_eye_outer"]].y * image_size[1]),
        (lm[LANDMARK_IDS["right_eye_outer"]].x * image_size[0],
         lm[LANDMARK_IDS["right_eye_outer"]].y * image_size[1]),
        (lm[LANDMARK_IDS["left_mouth"]].x * image_size[0],
         lm[LANDMARK_IDS["left_mouth"]].y * image_size[1]),
        (lm[LANDMARK_IDS["right_mouth"]].x * image_size[0],
         lm[LANDMARK_IDS["right_mouth"]].y * image_size[1]),
    ], dtype=np.float64)

    focal_length = image_size[0]
    center = (image_size[0]/2, image_size[1]/2)
    camera_matrix = np.array([
        [focal_length, 0, center[0]],
        [0, focal_length, center[1]],
        [0, 0, 1]
    ], dtype="double")
    dist_coeffs = np.zeros((4,1))

    success, rot_vec, trans_vec = cv2.solvePnP(
        MODEL_POINTS, image_points, camera_matrix, dist_coeffs, flags=cv2.SOLVEPNP_ITERATIVE
    )
    if not success:
        return None

    rot_mat, _ = cv2.Rodrigues(rot_vec)
    pose_mat = np.hstack((rot_mat, trans_vec))
    _, _, _, _, _, _, angles = cv2.decomposeProjectionMatrix(pose_mat)
    pitch, yaw, roll = float(angles[0]), float(angles[1]), float(angles[2])
    return pitch, yaw, roll

def main():
    cap = cv2.VideoCapture(0)
    mp_face = mp.solutions.face_mesh.FaceMesh(
        static_image_mode=False,
        refine_landmarks=True,
        max_num_faces=1,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )

    attended_time = 0.0
    last_time = time.time()

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        now = time.time()
        dt = now - last_time
        last_time = now

        h, w = frame.shape[:2]
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        res = mp_face.process(rgb)

        attending = False
        if res.multi_face_landmarks:
            # Face detected at least
            attending = True

            lm = res.multi_face_landmarks[0].landmark
            hp = get_head_pose((w, h), lm)
            if hp is not None:
                pitch, yaw, roll = hp
                # only count if within thresholds
                if abs(yaw) < 15 and abs(pitch) < 15:
                    attending = True
                else:
                    attending = False
                # debug overlay
                cv2.putText(frame, f"Y:{yaw:.1f} P:{pitch:.1f}", (10, h-40),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)
            else:
                # PnP failed, still count the face detection
                cv2.putText(frame, "PnP failed, using face-only", (10, h-40),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,255), 2)
        else:
            cv2.putText(frame, "No face", (10, h-40),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,255), 2)

        if attending:
            attended_time += dt

        cv2.putText(frame, f"Attended: {int(attended_time)} s", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.0,
                    (0,200,0) if attending else (0,0,200), 2)

        cv2.imshow("Attention", frame)
        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()
    print(f"Total screen-attending time: {attended_time:.2f} seconds")

if __name__ == "__main__":
    main()
