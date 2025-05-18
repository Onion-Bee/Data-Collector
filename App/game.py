import pygame
import time
import random
import csv
from datetime import datetime
import cv2
import mediapipe as mp
import numpy as np

# Initialize Pygame
pygame.init()

# Screen settings
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bubble Pop Game with Eye, Head & Blink Tracking (Eye-Socket Normalized)")

# Load assets
BACKGROUND_COLOR = (30, 30, 60)
BUBBLE_COLORS = [(135, 206, 250), (100, 149, 237), (173, 216, 230), (176, 224, 230)]
POP_SOUND = pygame.mixer.Sound(file='pop.mp3')  # load your own sound

# Fonts
pygame.font.init()
font_large = pygame.font.SysFont("Arial", 36, bold=True)

# Game variables
bubbles = []
reaction_data = []
eyetrack_data = []
headtrack_data = []
score = 0
clock = pygame.time.Clock()

game_duration = 35  # seconds
game_start_time = time.time()

BUBBLE_INTERVAL = 1500  # ms
BUBBLE_LIFESPAN = 3     # seconds
MAX_RADIUS = 50
MIN_RADIUS = 20

# Mediapipe setup
mp_face = mp.solutions.face_mesh
mp_drawing = mp.solutions.drawing_utils
drawing_spec = mp_drawing.DrawingSpec(thickness=1, circle_radius=1, color=(0,255,0))
face_mesh = mp_face.FaceMesh(static_image_mode=False,
                             max_num_faces=1,
                             refine_landmarks=True,
                             min_detection_confidence=0.5)

# OpenCV capture
cap = cv2.VideoCapture(0)

# Utility: compute average landmark coords

def avg_landmarks(landmarks, indices, w, h):
    xs, ys = [], []
    for i in indices:
        lm = landmarks[i]
        xs.append(lm.x * w)
        ys.append(lm.y * h)
    return sum(xs)/len(xs), sum(ys)/len(ys)

# EAR for blink detection
def eye_aspect_ratio(landmarks, idxs, w, h):
    pts = [(landmarks[i].x * w, landmarks[i].y * h) for i in idxs]
    C = np.linalg.norm(np.array(pts[0]) - np.array(pts[3]))
    A = np.linalg.norm(np.array(pts[1]) - np.array(pts[5]))
    B = np.linalg.norm(np.array(pts[2]) - np.array(pts[4]))
    return (A + B) / (2.0 * C) if C != 0 else 0

# Eye landmark indices
LEFT_EYE_IDXS  = (33, 133, 160, 158, 153, 144)
RIGHT_EYE_IDXS = (362, 263, 385, 387, 373, 380)
EAR_THRESHOLD = 0.25

class Bubble:
    def __init__(self):
        self.radius = random.randint(MIN_RADIUS, MAX_RADIUS)
        self.color = random.choice(BUBBLE_COLORS)
        self.x = random.randint(self.radius, WIDTH - self.radius)
        self.y = random.randint(self.radius, HEIGHT - self.radius)
        self.appear_time = time.time()

    def draw(self):
        elapsed = time.time() - self.appear_time
        alpha = int(255 * min(elapsed/0.5, 1))
        surf = pygame.Surface((self.radius*2, self.radius*2), pygame.SRCALPHA)
        pygame.draw.circle(surf, (*self.color, alpha), (self.radius, self.radius), self.radius)
        shadow = pygame.Surface((self.radius*2, self.radius*2), pygame.SRCALPHA)
        pygame.draw.circle(shadow, (0,0,0,int(alpha*0.3)), (self.radius+2,self.radius+2), self.radius)
        screen.blit(shadow, (self.x-self.radius, self.y-self.radius))
        screen.blit(surf, (self.x-self.radius, self.y-self.radius))

    def is_clicked(self, pos):
        return ((self.x-pos[0])**2 + (self.y-pos[1])**2)**0.5 <= self.radius

# Main loop
running = True
last_bubble_time = pygame.time.get_ticks()

while running:
    if time.time() - game_start_time > game_duration:
        break

    ret, frame = cap.read()
    if ret:
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(frame_rgb)
        annotated = frame.copy()
        h_f, w_f, _ = frame.shape
        now_ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")

        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                lm = face_landmarks.landmark
                mp_drawing.draw_landmarks(
                    image=annotated,
                    landmark_list=face_landmarks,
                    connections=mp_face.FACEMESH_TESSELATION,
                    landmark_drawing_spec=drawing_spec,
                    connection_drawing_spec=drawing_spec)

                # Raw pixel centers
                left_pix  = avg_landmarks(lm, LEFT_EYE_IDXS,  w_f, h_f)
                right_pix = avg_landmarks(lm, RIGHT_EYE_IDXS, w_f, h_f)

                # Compute blink
                ear = (eye_aspect_ratio(lm, LEFT_EYE_IDXS,  w_f, h_f) +
                       eye_aspect_ratio(lm, RIGHT_EYE_IDXS, w_f, h_f)) / 2
                blink = ear < EAR_THRESHOLD

                if left_pix and right_pix:
                    # Eye-socket normalization
                    # Compute bounding box of eye landmarks
                    left_pts = [(lm[i].x*w_f, lm[i].y*h_f) for i in LEFT_EYE_IDXS]
                    xs, ys = zip(*left_pts)
                    lx_min, lx_max = min(xs), max(xs)
                    ly_min, ly_max = min(ys), max(ys)
                    rx_pts = [(lm[i].x*w_f, lm[i].y*h_f) for i in RIGHT_EYE_IDXS]
                    xs2, ys2 = zip(*rx_pts)
                    rx_min, rx_max = min(xs2), max(xs2)
                    ry_min, ry_max = min(ys2), max(ys2)

                    # Normalize relative to socket
                    left_norm  = ((left_pix[0] - lx_min) / (lx_max - lx_min),
                                  (left_pix[1] - ly_min) / (ly_max - ly_min))
                    right_norm = ((right_pix[0] - rx_min) / (rx_max - rx_min),
                                  (right_pix[1] - ry_min) / (ry_max - ry_min))

                    eyetrack_data.append({
                        "timestamp": now_ts,
                        "left_x": round(left_norm[0], 5),
                        "left_y": round(left_norm[1], 5),
                        "right_x": round(right_norm[0], 5),
                        "right_y": round(right_norm[1], 5),
                        "blink": blink
                    })

                    # Draw raw gaze points
                    cv2.circle(annotated, (int(left_pix[0]), int(left_pix[1])), 5, (0,0,255), -1)
                    cv2.circle(annotated, (int(right_pix[0]), int(right_pix[1])), 5, (0,0,255), -1)

                # Head tracking
                nose = lm[1]
                nx, ny = int(nose.x*w_f), int(nose.y*h_f)
                headtrack_data.append({"timestamp": now_ts, "nose_x": nx, "nose_y": ny})
                cv2.circle(annotated, (nx, ny), 5, (255,0,0), -1)

        cv2.imshow('Eye & Head Tracking', annotated)

    # Rest of game loop unchanged...
    # (pygame events, bubble management, drawing, cleanup, CSV saving)

    # Pygame events & drawing
    screen.fill(BACKGROUND_COLOR)
    now_sec = time.time()
    if pygame.time.get_ticks() - last_bubble_time > BUBBLE_INTERVAL:
        bubbles.append(Bubble())
        last_bubble_time = pygame.time.get_ticks()

    for bubble in bubbles[:]:
        bubble.draw()
        if now_sec - bubble.appear_time > BUBBLE_LIFESPAN:
            reaction_data.append({
                "x": bubble.x, "y": bubble.y,
                "reaction_time_sec": None,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "status": "missed"
            })
            bubbles.remove(bubble)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type in (pygame.MOUSEBUTTONDOWN, pygame.FINGERDOWN):
            pos = pygame.mouse.get_pos() if event.type==pygame.MOUSEBUTTONDOWN else (int(event.x*WIDTH), int(event.y*HEIGHT))
            for bubble in bubbles[:]:
                if bubble.is_clicked(pos):
                    rt = now_sec - bubble.appear_time
                    reaction_data.append({
                        "x": bubble.x, "y": bubble.y,
                        "reaction_time_sec": round(rt,2),
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "status": "popped"
                    })
                    score += 1
                    try: POP_SOUND.play()
                    except: pass
                    bubbles.remove(bubble)
                    break

    # Draw score
    score_surf = font_large.render(f"Score: {score}", True, (255,255,255))
    box = pygame.Surface((score_surf.get_width()+20, score_surf.get_height()+10), pygame.SRCALPHA)
    pygame.draw.rect(box, (0,0,0,150), box.get_rect(), border_radius=10)
    box.blit(score_surf, (10,5))
    screen.blit(box, (10,10))
    pygame.display.flip()
    clock.tick(60)
    if cv2.waitKey(1) & 0xFF == 27:
        break

# Cleanup
cap.release()
face_mesh.close()
cv2.destroyAllWindows()

# End screen
screen.fill(BACKGROUND_COLOR)
end_msg = font_large.render("Time's up!", True, (255,255,255))
score_msg = font_large.render(f"Final Score: {score}", True, (255,255,255))
pad=20
bw = max(end_msg.get_width(), score_msg.get_width()) + pad*2
bh = end_msg.get_height() + score_msg.get_height() + pad*3
bx, by = (WIDTH-bw)//2, (HEIGHT-bh)//2
box_e = pygame.Surface((bw,bh), pygame.SRCALPHA)
pygame.draw.rect(box_e, (0,0,0,200), (0,0,bw,bh), border_radius=15)
box_e.blit(end_msg, ((bw-end_msg.get_width())//2, pad))
box_e.blit(score_msg, ((bw-score_msg.get_width())//2, pad*2+end_msg.get_height()))
screen.blit(box_e, (bx,by))
pygame.display.flip()
pygame.time.delay(3000)
pygame.quit()

# Save CSVs
ts = datetime.now().strftime("%Y%m%d_%H%M%S")
with open(f"reaction_times_{ts}.csv", "w", newline='') as f:
    w = csv.DictWriter(f, ["x","y","reaction_time_sec","timestamp","status"])
    w.writeheader(); w.writerows(reaction_data)
with open(f"game_eye_track_{ts}.csv", "w", newline='') as f:
    w = csv.DictWriter(f, ["timestamp","left_x","left_y","right_x","right_y","blink"])
    w.writeheader(); w.writerows(eyetrack_data)
with open(f"game_head_track_{ts}.csv", "w", newline='') as f:
    w = csv.DictWriter(f, ["timestamp","nose_x","nose_y"])
    w.writeheader(); w.writerows(headtrack_data)

print(f"Saved {len(reaction_data)} reactions, {len(eyetrack_data)} eye records, {len(headtrack_data)} head records.")
