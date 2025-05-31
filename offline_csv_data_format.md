# Dataset Column Description

This document describes each column present in the dataset related to facial landmark tracking, gaze estimation, and facial action units.

---

## General Columns

| Column         | Description                                                                                 |
|----------------|---------------------------------------------------------------------------------------------|
| frame          | Frame number in the video sequence                                                         |
| face_id        | Unique identifier for the detected face                                                    |
| timestamp      | Timestamp of the frame (in milliseconds or seconds)                                       |
| confidence     | Confidence score of face detection or tracking                                            |
| success        | Boolean indicating successful detection or tracking (1 = success, 0 = failure)             |

---

## Gaze Data

| Column          | Description                                                                          |
|-----------------|--------------------------------------------------------------------------------------|
| gaze_0_x, y, z  | 3D coordinates of the first gaze vector (eye gaze direction or origin)              |
| gaze_1_x, y, z  | 3D coordinates of the second gaze vector                                           |
| gaze_angle_x    | Horizontal gaze angle (degrees or radians)                                         |
| gaze_angle_y    | Vertical gaze angle                                                                |

---

## Eye Landmarks (2D)

| Columns                     | Description                                                   |
|-----------------------------|---------------------------------------------------------------|
| eye_lmk_x_0 to eye_lmk_x_55 | X-coordinates of 56 eye landmark points (2D image plane)      |
| eye_lmk_y_0 to eye_lmk_y_55 | Y-coordinates of 56 eye landmark points                        |

---

## Eye Landmarks (3D)

| Columns                     | Description                                                   |
|-----------------------------|---------------------------------------------------------------|
| eye_lmk_X_0 to eye_lmk_X_55 | X-coordinates of 56 eye landmark points in 3D space           |
| eye_lmk_Y_0 to eye_lmk_Y_55 | Y-coordinates of 56 eye landmark points in 3D space           |
| eye_lmk_Z_0 to eye_lmk_Z_55 | Z-coordinates of 56 eye landmark points in 3D space           |

---

## Head Pose

| Column   | Description                                                                 |
|----------|-----------------------------------------------------------------------------|
| pose_Tx  | Head translation along X-axis                                               |
| pose_Ty  | Head translation along Y-axis                                               |
| pose_Tz  | Head translation along Z-axis                                               |
| pose_Rx  | Head rotation around X-axis (pitch)                                         |
| pose_Ry  | Head rotation around Y-axis (yaw)                                           |
| pose_Rz  | Head rotation around Z-axis (roll)                                          |

---

## Face Landmarks (2D)

| Columns          | Description                                                        |
|------------------|--------------------------------------------------------------------|
| x_0 to x_67      | X-coordinates of 68 facial landmarks (2D image plane)              |
| y_0 to y_67      | Y-coordinates of 68 facial landmarks (2D image plane)              |

---

## Face Landmarks (3D)

| Columns          | Description                                                        |
|------------------|--------------------------------------------------------------------|
| X_0 to X_67      | X-coordinates of 68 facial landmarks in 3D space                   |
| Y_0 to Y_67      | Y-coordinates of 68 facial landmarks in 3D space                   |
| Z_0 to Z_67      | Z-coordinates of 68 facial landmarks in 3D space                   |

---

## Projection Parameters

| Column    | Description                                                           |
|-----------|-----------------------------------------------------------------------|
| p_scale   | Scale parameter of the projection                                     |
| p_rx      | Rotation around X-axis (projection)                                  |
| p_ry      | Rotation around Y-axis (projection)                                  |
| p_rz      | Rotation around Z-axis (projection)                                  |
| p_tx      | Translation along X-axis (projection)                               |
| p_ty      | Translation along Y-axis (projection)                               |
| p_0 to p_33| Projection matrix or model parameters (various)                      |

---

## Facial Action Units (Intensity and Presence)

| Column     | Description                                                                                      |
|------------|------------------------------------------------------------------------------------------------|
| AU01_r to AU45_r | Intensity of specific Facial Action Units (AUs) — how strongly the muscle movement is present (r = regression value) |
| AU01_c to AU45_c | Presence of specific Facial Action Units — binary or classification label (c = classification)                        |
| AU28_c       | Presence of AU28 (Lip Suck)                                                                     |

---

# Notes

- Eye and face landmarks correspond to key points detected on the eyes and face used for detailed analysis.
- Gaze vectors indicate the direction of gaze for each eye.
- Head pose parameters indicate the estimated 3D position and orientation of the head.
- Facial Action Units are based on the Facial Action Coding System (FACS) used to quantify facial muscle activations.

---

This dataset can be used for tasks such as:

- Gaze estimation
- Blink and eye movement detection
- Facial expression recognition
- Head pose estimation
- Behavioral analysis

---
