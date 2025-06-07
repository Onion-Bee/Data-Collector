import cv2
import os
import sys
import subprocess
import numpy as np
from moviepy.video.io.VideoFileClip import VideoFileClip
import pygame
import time
import math

VIDEO_FOLDER = "videos"
VIDEO_EXTENSIONS = ('.mp4', '.avi', '.mov', '.mkv')
TEMP_AUDIO_DIR = "temp_audio_files"
TRANSITION_DURATION = 1.0
SKIP_OVERLAY_DURATION = 1.5

arrow_trail = []

def get_video_files(folder):
    return [
        os.path.join(folder, f)
        for f in os.listdir(folder)
        if f.lower().endswith(VIDEO_EXTENSIONS)
    ]

def apply_fade(frame, frame_index, total_frames, fps, fade_in, fade_out):
    fade_frames = int(TRANSITION_DURATION * fps)
    alpha = 1.0
    if fade_in and frame_index < fade_frames:
        alpha = frame_index / fade_frames
    elif fade_out and frame_index >= total_frames - fade_frames:
        alpha = (total_frames - frame_index - 1) / fade_frames
    return (frame.astype(np.float32) * alpha).clip(0, 255).astype(np.uint8)

arrow_trail = []  # Keep this global or accessible for tracking

def draw_arrow(img, pos_x, pos_y, size=100, color=(255, 105, 180), thickness=18):
    global arrow_trail

    current_time = time.time()
    arrow_trail.append((pos_x, pos_y, current_time))
    arrow_trail = [
        (x, y, t) for (x, y, t) in arrow_trail if current_time - t < 0.6
    ]

    # Draw fading trail
    for tx, ty, t in arrow_trail:
        alpha = 1.0 - ((current_time - t) / 0.6)
        trail_color = tuple(int(c * alpha) for c in color)
        trail_thickness = max(2, int(thickness * alpha))

        cv2.line(
            img,
            (tx, ty),
            (tx + size, ty),
            trail_color,
            trail_thickness,
            lineType=cv2.LINE_AA,
        )

        head_len = 40
        head_width = 40
        tip = (tx + size + head_len, ty)
        left = (tx + size, ty - head_width // 2)
        right = (tx + size, ty + head_width // 2)
        points = np.array([tip, left, right], np.int32)
        cv2.fillPoly(img, [points], trail_color)

    arrow_color = color
    glow_color = (255, 182, 193)
    black_outline = (0, 0, 0)

    start_point = (pos_x, pos_y)
    end_point = (pos_x + size, pos_y)
    cv2.line(
        img, start_point, end_point, arrow_color, thickness, lineType=cv2.LINE_AA
    )

    head_len = 40
    head_width = 40
    tip = (pos_x + size + head_len, pos_y)
    left = (pos_x + size, pos_y - head_width // 2)
    right = (pos_x + size, pos_y + head_width // 2)
    points = np.array([tip, left, right], np.int32)
    cv2.fillPoly(img, [points], arrow_color)
    cv2.polylines(img, [points], isClosed=True, color=black_outline, thickness=4, lineType=cv2.LINE_AA)

    # Pulsating effect parameters
    pulse_speed = 2.5  # Pulses per second
    pulse = (math.sin(current_time * pulse_speed * 2 * math.pi) + 1) / 2  # 0 to 1 smoothly

    # Pulsating radii and thickness
    base_radius_small = 18
    base_radius_large = 30
    radius_small = int(base_radius_small + pulse * 6)   # small circle radius pulsates between 18 and 24
    radius_large = int(base_radius_large + pulse * 8)   # large circle radius pulsates between 30 and 38
    thickness_large = int(6 + pulse * 3)                # thickness pulsates between 6 and 9

    # Draw pulsating glowing circles
    cv2.circle(img, start_point, radius_small, glow_color, -1, lineType=cv2.LINE_AA)
    cv2.circle(img, start_point, radius_large, arrow_color, thickness_large, lineType=cv2.LINE_AA)

    sparkle_positions = [
        (pos_x - 40, pos_y - 30),
        (pos_x + size // 2, pos_y - 50),
        (pos_x + size // 2, pos_y + 50),
        (pos_x + size + 30, pos_y + 30),
    ]
    for sx, sy in sparkle_positions:
        cv2.circle(img, (sx, sy), 6, (255, 255, 255), -1, lineType=cv2.LINE_AA)
        cv2.circle(img, (sx, sy), 10, arrow_color, 2, lineType=cv2.LINE_AA)

def slide_to_next_interaction(window_name, window_width, window_height):
    dragging = {'active': False}
    arrow_x = [50]
    arrow_y = window_height // 2

    def on_mouse(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            if arrow_x[0] <= x <= arrow_x[0] + 50 and arrow_y - 15 <= y <= arrow_y + 15:
                dragging['active'] = True
                dragging['offset'] = x - arrow_x[0]
        elif event == cv2.EVENT_MOUSEMOVE and dragging['active']:
            new_x = x - dragging['offset']
            arrow_x[0] = max(50, min(new_x, window_width - 60))
        elif event == cv2.EVENT_LBUTTONUP:
            dragging['active'] = False
            if arrow_x[0] < int(window_width * 0.8):
                arrow_x[0] = 50

    cv2.setMouseCallback(window_name, on_mouse)
    black_bg = np.zeros((window_height, window_width, 3), dtype=np.uint8)

    while True:
        frame = black_bg.copy()
        draw_arrow(frame, arrow_x[0], arrow_y)
        text = "Drag the arrow to the right to play next video"
        font = cv2.FONT_HERSHEY_DUPLEX
        font_scale = 1.2
        thickness = 3
        text_size, _ = cv2.getTextSize(text, font, font_scale, thickness)
        text_x = 50
        text_y = 70

        # Draw shadow (black) slightly offset for better readability
        cv2.putText(
            frame,
            text,
            (text_x + 2, text_y + 2),
            font,
            font_scale,
            (0, 0, 0),
            thickness + 2,
            lineType=cv2.LINE_AA,
        )

        # Draw main white text on top
        cv2.putText(
            frame,
            text,
            (text_x, text_y),
            font,
            font_scale,
            (255, 255, 255),
            thickness,
            lineType=cv2.LINE_AA,
        )

        cv2.imshow(window_name, frame)

        key = cv2.waitKey(20) & 0xFF
        if key == ord('q'):
            return False
        if arrow_x[0] > int(window_width * 0.8):
            return True

def thanks_for_watching_screen(window_name, window_width, window_height, duration=3.0, fade_out_duration=2.0):
    """
    Show a 'Thanks for watching' message centered on screen.
    Fade it out gradually over fade_out_duration seconds.
    Total duration before exit = duration + fade_out_duration.
    """
    start_time = time.time()
    font = cv2.FONT_HERSHEY_SIMPLEX
    message = "Thanks for watching!"
    font_scale = 2.5
    thickness = 5
    text_size, _ = cv2.getTextSize(message, font, font_scale, thickness)
    text_x = (window_width - text_size[0]) // 2
    text_y = (window_height + text_size[1]) // 2

    while True:
        elapsed = time.time() - start_time
        img = np.zeros((window_height, window_width, 3), dtype=np.uint8)

        if elapsed < duration:
            alpha = 1.0  # fully visible
        elif elapsed < duration + fade_out_duration:
            alpha = 1.0 - (elapsed - duration) / fade_out_duration
        else:
            break

        # Create transparent overlay
        overlay = img.copy()
        cv2.putText(
            overlay,
            message,
            (text_x, text_y),
            font,
            font_scale,
            (255, 255, 255),
            thickness,
            lineType=cv2.LINE_AA,
        )

        # Blend with alpha for fade out effect
        cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0, img)

        cv2.imshow(window_name, img)
        if cv2.waitKey(30) & 0xFF == ord('q'):
            break

def play_video(video_path, fade_in=True, fade_out=True):
    clip = VideoFileClip(video_path)
    fps = clip.fps
    total_frames = int(clip.duration * fps)
    width, height = map(int, clip.size)

    base_name = os.path.splitext(os.path.basename(video_path))[0]
    if not os.path.exists(TEMP_AUDIO_DIR):
        os.makedirs(TEMP_AUDIO_DIR)
    audio_path = os.path.join(TEMP_AUDIO_DIR, f"{base_name}.wav")

    audio_available = clip.audio is not None
    if audio_available:
        if not os.path.exists(audio_path):
            clip.audio.write_audiofile(audio_path, logger=None)
        pygame.mixer.init()
        pygame.mixer.music.load(audio_path)

    cv2.namedWindow("Video Player", cv2.WINDOW_NORMAL)
    cv2.setWindowProperty("Video Player", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    playback_time = 0.0
    last_time = time.time()

    if audio_available:
        pygame.mixer.music.play()

    speed = 1.0
    paused = False
    skip_overlay = None
    skip_overlay_start = 0

    while True:
        if not paused:
            current_time = time.time()
            elapsed = current_time - last_time
            playback_time += elapsed * speed
            last_time = current_time

        current_frame_idx = int(playback_time * fps)
        current_frame_idx = min(max(current_frame_idx, 0), total_frames - 1)

        try:
            frame = clip.get_frame(current_frame_idx / fps)
        except Exception as e:
            print(f"Error reading frame {current_frame_idx}: {e}")
            break

        if frame is None:
            print("Error: Could not read frame.")
            break

        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        frame = apply_fade(frame, current_frame_idx, total_frames, fps, fade_in, fade_out)

        window_rect = cv2.getWindowImageRect("Video Player")
        window_width, window_height = window_rect[2], window_rect[3]
        aspect_ratio = width / height

        if window_width / window_height > aspect_ratio:
            new_width = int(window_height * aspect_ratio)
            new_height = window_height
        else:
            new_width = window_width
            new_height = int(window_width / aspect_ratio)

        resized_frame = cv2.resize(frame, (new_width, new_height))
        background = np.zeros((window_height, window_width, 3), dtype=np.uint8)
        y_offset = (window_height - new_height) // 2
        x_offset = (window_width - new_width) // 2
        background[y_offset : y_offset + new_height, x_offset : x_offset + new_width] = resized_frame

        if skip_overlay and (time.time() - skip_overlay_start) < SKIP_OVERLAY_DURATION:
            overlay_text = skip_overlay
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 1.5
            thickness = 3
            text_size, _ = cv2.getTextSize(overlay_text, font, font_scale, thickness)
            text_x = (window_width - text_size[0]) // 2
            text_y = window_height // 5
            cv2.rectangle(
                background,
                (text_x - 10, text_y - text_size[1] - 10),
                (text_x + text_size[0] + 10, text_y + 10),
                (0, 0, 0),
                cv2.FILLED,
            )
            cv2.putText(
                background,
                overlay_text,
                (text_x, text_y),
                font,
                font_scale,
                (255, 255, 255),
                thickness,
            )

        cv2.imshow("Video Player", background)

        key = cv2.waitKey(1) & 0xFF

        if key == ord('q'):
            if audio_available:
                pygame.mixer.music.stop()
                pygame.mixer.quit()
            cv2.destroyAllWindows()
            return False

        elif key == ord('p'):
            paused = not paused
            if paused:
                if audio_available:
                    pygame.mixer.music.pause()
                pause_time = time.time()
            else:
                if audio_available:
                    pygame.mixer.music.unpause()
                else:
                    last_time += time.time() - pause_time

        elif key == ord('n'):
            if audio_available:
                pygame.mixer.music.stop()
                pygame.mixer.quit()
            cv2.destroyAllWindows()
            return "next"

        elif key == ord('b'):
            if audio_available:
                pygame.mixer.music.stop()
                pygame.mixer.quit()
            cv2.destroyAllWindows()
            return "prev"

        elif key == ord('+'):
            speed = min(speed + 0.25, 2.0)

        elif key == ord('-'):
            speed = max(speed - 0.25, 0.5)

        elif key == ord('f') or key == 83:
            playback_time += 5
            if playback_time >= clip.duration:
                playback_time = clip.duration - 0.01
            skip_overlay = "5s skipped forward"
            skip_overlay_start = time.time()
            if audio_available:
                pygame.mixer.music.pause()
                pygame.mixer.music.set_pos(playback_time)
                pygame.mixer.music.unpause()
            last_time = time.time()

        elif key == ord('d') or key == 81:
            playback_time -= 5
            if playback_time < 0:
                playback_time = 0
            skip_overlay = "5s skipped backward"
            skip_overlay_start = time.time()
            if audio_available:
                pygame.mixer.music.pause()
                pygame.mixer.music.set_pos(playback_time)
                pygame.mixer.music.unpause()
            last_time = time.time()

        if not paused and current_frame_idx >= total_frames - 1:
            if audio_available and pygame.mixer.music.get_busy():
                continue
            else:
                if audio_available:
                    pygame.mixer.music.stop()
                    pygame.mixer.quit()
                window_rect = cv2.getWindowImageRect("Video Player")
                w_width, w_height = window_rect[2], window_rect[3]
                proceed = slide_to_next_interaction("Video Player", w_width, w_height)
                cv2.destroyAllWindows()
                return "next" if proceed else False

    if audio_available and pygame.mixer.get_init():
        pygame.mixer.music.stop()
        pygame.mixer.quit()

    cv2.destroyAllWindows()
    return True

def main():
    # Gather all video files in the playlist
    videos = get_video_files(VIDEO_FOLDER)
    if not videos:
        print("No videos found in the folder.")
        return

    current_video_idx = 0

    while current_video_idx < len(videos):
        video = videos[current_video_idx]
        print(f"Playing: {os.path.basename(video)}")

        # 1) Launch head_monitor.py before starting playback
        head_proc = subprocess.Popen([sys.executable, "head_monitor.py"])
        print(f"[HEAD MONITOR] Started for '{video}' → PID={head_proc.pid}")

        # 2) Play the video (blocks until video ends or user exits/next/prev)
        action = play_video(video, fade_in=True, fade_out=True)

        # 3) As soon as playback returns, terminate head_monitor.py
        head_proc.terminate()
        head_proc.wait()
        print(f"[HEAD MONITOR] Terminated for '{video}' → PID={head_proc.pid}")
        time.sleep(0.5)  # Small buffer to ensure unique filenames

        # 4) Handle user action/playlist logic
        if action == "next":
            current_video_idx += 1
            # If this was the last video, show a “Thanks for watching” screen
            if current_video_idx >= len(videos):
                cv2.namedWindow("Video Player", cv2.WINDOW_NORMAL)
                cv2.setWindowProperty("Video Player", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
                window_rect = cv2.getWindowImageRect("Video Player")
                w_width, w_height = window_rect[2], window_rect[3]
                thanks_for_watching_screen("Video Player", w_width, w_height)
                cv2.destroyAllWindows()
                break

        elif action == "prev":
            current_video_idx = max(0, current_video_idx - 1)

        elif action is False:
            # User pressed 'q' or closed window; exit completely
            break

        else:
            # If play_video returned True (natural end without “next/prev”), move forward
            current_video_idx += 1

    print("All videos played once. Exiting.")

if __name__ == "__main__":
    main()
