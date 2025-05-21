import cv2
import time
import numpy as np
import mediapipe as mp

# 3D model points of facial landmarks in the face coordinate system
MODEL_POINTS = np.array([
    (0.0, 0.0, 0.0),             # Nose tip
    (0.0, -330.0, -65.0),        # Chin
    (-225.0, 170.0, -135.0),     # Left eye left corner
    (225.0, 170.0, -135.0),      # Right eye right corner
    (-150.0, -150.0, -125.0),    # Left mouth corner
    (150.0, -150.0, -125.0)      # Right mouth corner
], dtype=np.float64)

# Indices into MediaPipe FaceMesh.landmark for the above points
LANDMARK_IDS = {
    "nose_tip": 1,
    "chin": 152,
    "left_eye_outer": 33,
    "right_eye_outer": 263,
    "left_mouth": 61,
    "right_mouth": 291
}

def get_head_pose(image_size, landmarks):
    # 2D image points from detected landmarks
    image_points = np.array([
        (landmarks[LANDMARK_IDS["nose_tip"]].x * image_size[0],
         landmarks[LANDMARK_IDS["nose_tip"]].y * image_size[1]),
        (landmarks[LANDMARK_IDS["chin"]].x * image_size[0],
         landmarks[LANDMARK_IDS["chin"]].y * image_size[1]),
        (landmarks[LANDMARK_IDS["left_eye_outer"]].x * image_size[0],
         landmarks[LANDMARK_IDS["left_eye_outer"]].y * image_size[1]),
        (landmarks[LANDMARK_IDS["right_eye_outer"]].x * image_size[0],
         landmarks[LANDMARK_IDS["right_eye_outer"]].y * image_size[1]),
        (landmarks[LANDMARK_IDS["left_mouth"]].x * image_size[0],
         landmarks[LANDMARK_IDS["left_mouth"]].y * image_size[1]),
        (landmarks[LANDMARK_IDS["right_mouth"]].x * image_size[0],
         landmarks[LANDMARK_IDS["right_mouth"]].y * image_size[1]),
    ], dtype=np.float64)

    # Camera internals
    focal_length = image_size[0]
    center = (image_size[0] / 2, image_size[1] / 2)
    camera_matrix = np.array([
        [focal_length, 0, center[0]],
        [0, focal_length, center[1]],
        [0, 0, 1]
    ], dtype = "double")
    dist_coeffs = np.zeros((4,1))  # assume no lens distortion

    # Solve PnP
    success, rotation_vec, translation_vec = cv2.solvePnP(
        MODEL_POINTS, image_points, camera_matrix, dist_coeffs, flags=cv2.SOLVEPNP_ITERATIVE
    )
    if not success:
        return None

    # Convert rotation vector to Euler angles
    rotation_mat, _ = cv2.Rodrigues(rotation_vec)
    pose_mat = cv2.hconcat((rotation_mat, translation_vec))
    _, _, _, _, _, _, euler_angles = cv2.decomposeProjectionMatrix(pose_mat)
    pitch, yaw, roll = [float(angle) for angle in euler_angles]
    return pitch, yaw, roll

def main():
    mp_face = mp.solutions.face_mesh
    drawing = mp.solutions.drawing_utils

    cap = cv2.VideoCapture(0)
    attended_time = 0.0
    last_time = time.time()

    with mp_face.FaceMesh(
        static_image_mode=False,
        refine_landmarks=True,
        max_num_faces=1,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    ) as face_mesh:

        while True:
            ret, frame = cap.read()
            if not ret:
                break
            h, w = frame.shape[:2]
            now = time.time()
            dt = now - last_time
            last_time = now

            # Process frame
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = face_mesh.process(rgb)

            attending = False
            if results.multi_face_landmarks:
                lm = results.multi_face_landmarks[0].landmark
                head_pose = get_head_pose((w, h), lm)
                if head_pose:
                    pitch, yaw, roll = head_pose
                    # count as attending if pitch and yaw are within +/- 15 degrees
                    if abs(yaw) < 15 and abs(pitch) < 15:
                        attending = True

                    # Overlay angles for debugging
                    cv2.putText(frame, f"Yaw: {yaw:.1f}", (10, h-60),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)
                    cv2.putText(frame, f"Pitch: {pitch:.1f}", (10, h-40),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)
                    cv2.putText(frame, f"Roll: {roll:.1f}", (10, h-20),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)

            if attending:
                attended_time += dt

            # Display attended time
            cv2.putText(frame,
                        f"Attended: {int(attended_time)} s",
                        (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1.0,
                        (0, 200, 0) if attending else (0, 0, 200),
                        2)

            cv2.imshow("Screen Attention Tracker", frame)
            if cv2.waitKey(1) & 0xFF == 27:  # ESC to quit
                break

    cap.release()
    cv2.destroyAllWindows()
    print(f"Total screen-attending time: {attended_time:.2f} seconds")

if __name__ == "__main__":
    main()
