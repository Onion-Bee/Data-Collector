import pygame
import random
import time
import csv
import json
from datetime import datetime
import tkinter as tk
from tkinter import ttk

##########################################
# Phase 1: Collect Kid's Information
##########################################

def submit_info():
    name = name_entry.get().strip()
    age = age_entry.get().strip()
    gender = gender_entry.get().strip()
    
    if not name or not age or not gender:
        info_status_label.config(text="Please enter name, age, and gender.", foreground="red")
        return
    
    kid_info = {
        "name": name,
        "age": age,
        "gender": gender,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    info_csv = "kid_info.csv"
    try:
        with open(info_csv, 'x', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=["name", "age", "gender", "timestamp"])
            writer.writeheader()
            writer.writerow(kid_info)
    except FileExistsError:
        with open(info_csv, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=["name", "age", "gender", "timestamp"])
            writer.writerow(kid_info)
    
    info_status_label.config(text="Info saved! Starting M-CHAT-RF...", foreground="green")
    root.after(1000, root.destroy)  # Close after 1 second

root = tk.Tk()
root.title("Enter Kid's Information")
root.geometry("300x250")
root.resizable(False, False)

ttk.Label(root, text="Kid's Name:").pack(pady=(20, 5))
name_entry = ttk.Entry(root, width=25)
name_entry.pack()

ttk.Label(root, text="Kid's Age:").pack(pady=(10, 5))
age_entry = ttk.Entry(root, width=25)
age_entry.pack()

ttk.Label(root, text="Kid's Gender:").pack(pady=(10, 5))
gender_entry = ttk.Entry(root, width=25)
gender_entry.pack()

submit_button = ttk.Button(root, text="Submit", command=submit_info)
submit_button.pack(pady=(20, 10))

info_status_label = ttk.Label(root, text="")
info_status_label.pack()

root.mainloop()

##########################################
# Phase 2: M-CHAT-RF Screening
##########################################

# Define 20 illustrative M-CHAT-RF initial screening questions
initial_questions = [
    "1. Does your child enjoy being read to?",
    "2. Does your child smile at you?",
    "3. Does your child respond when you call their name?",
    "4. Does your child point to objects to show interest?",
    "5. Does your child engage in pretend play?",
    "6. Does your child make eye contact?",
    "7. Does your child use gestures, such as waving?",
    "8. Does your child imitate adult actions?",
    "9. Does your child enjoy social games?",
    "10. Does your child react typically to loud sounds?",
    "11. Does your child have a favorite toy that they seek out?",
    "12. Does your child use their hands to communicate?",
    "13. Does your child show interest in other children?",
    "14. Does your child respond to facial expressions?",
    "15. Does your child try to share enjoyment with you?",
    "16. Does your child show varied facial expressions?",
    "17. Does your child use single words to communicate?",
    "18. Does your child understand simple instructions?",
    "19. Does your child engage in repetitive movements?",
    "20. Does your child show distress with changes in routine?"
]

# Set initial screening threshold (e.g. if 3 or more red flags, follow-up is needed)
initial_threshold = 3

# Define follow-up questions (illustrative examples; you may add more)
followup_questions = [
    "Follow-Up 1: Does your child have difficulty understanding instructions?",
    "Follow-Up 2: Does your child seem unusually withdrawn in social settings?",
    "Follow-Up 3: Does your child repeat phrases or words over and over?"
]
followup_threshold = 1  # If at least one red flag on follow-up, outcome shifts

# Dictionaries to store answers
mchat_initial_answers = {}
mchat_followup_answers = {}

def submit_initial():
    red_flags = 0
    for i in range(len(initial_questions)):
        answer = initial_var_list[i].get()
        mchat_initial_answers[f"Q{i+1}"] = answer
        if answer == "No":
            red_flags += 1
            
    initial_result_label.config(text=f"Red flags: {red_flags}")
    window_initial.destroy()
    
    if red_flags >= initial_threshold:
        show_followup()
    else:
        outcome = "Pass"
        save_mchat_results(red_flags, None, outcome, mchat_initial_answers, None)

def submit_followup():
    red_flags_followup = 0
    for i in range(len(followup_questions)):
        answer = followup_var_list[i].get()
        mchat_followup_answers[f"Followup_Q{i+1}"] = answer
        if answer == "No":
            red_flags_followup += 1
            
    followup_result_label.config(text=f"Follow-up red flags: {red_flags_followup}")
    window_followup.destroy()
    
    # Determine outcome based on follow-up responses.
    if red_flags_followup >= followup_threshold:
        outcome = "High Risk"
    else:
        outcome = "Moderate Risk"
    save_mchat_results(sum(1 for a in mchat_initial_answers.values() if a=="No"),
                       red_flags_followup,
                       outcome,
                       mchat_initial_answers,
                       mchat_followup_answers)

def save_mchat_results(initial_red_flags, followup_red_flags, outcome, initial_ans, followup_ans):
    csv_file = "mchat_results.csv"
    result = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "initial_red_flags": initial_red_flags,
        "followup_red_flags": followup_red_flags if followup_red_flags is not None else "",
        "outcome": outcome,
        "initial_answers": json.dumps(initial_ans),
        "followup_answers": json.dumps(followup_ans) if followup_ans is not None else ""
    }
    try:
        with open(csv_file, 'x', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=["timestamp", "initial_red_flags", "followup_red_flags", "outcome", "initial_answers", "followup_answers"])
            writer.writeheader()
            writer.writerow(result)
    except FileExistsError:
        with open(csv_file, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=["timestamp", "initial_red_flags", "followup_red_flags", "outcome", "initial_answers", "followup_answers"])
            writer.writerow(result)
    print("M-CHAT-RF results saved:", result)

def show_initial():
    global window_initial, initial_var_list, initial_result_label
    window_initial = tk.Tk()
    window_initial.title("M-CHAT-RF Screening (Initial)")
    window_initial.geometry("500x600")
    
    # Create a canvas and scrollbar for scrolling the questions
    canvas = tk.Canvas(window_initial, width=480, height=550)
    canvas.pack(side="left", fill="both", expand=True)
    
    scrollbar = ttk.Scrollbar(window_initial, orient="vertical", command=canvas.yview)
    scrollbar.pack(side="right", fill="y")
    
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    
    # Create a frame to hold the questions inside the canvas
    frame = ttk.Frame(canvas)
    canvas.create_window((0,0), window=frame, anchor="nw")
    
    ttk.Label(frame, text="Answer the following questions (Yes/No):", wraplength=460).pack(pady=10)
    initial_var_list = []
    for i, question in enumerate(initial_questions):
        q_frame = ttk.Frame(frame)
        q_frame.pack(fill="x", padx=10, pady=3)
        ttk.Label(q_frame, text=question, wraplength=450).pack(side="top", anchor="w")
        var = tk.StringVar(value="Yes")
        initial_var_list.append(var)
        options_frame = ttk.Frame(q_frame)
        options_frame.pack(side="top", anchor="w", padx=20)
        ttk.Radiobutton(options_frame, text="Yes", variable=var, value="Yes").pack(side="left")
        ttk.Radiobutton(options_frame, text="No", variable=var, value="No").pack(side="left")
    
    initial_result_label = ttk.Label(frame, text="Red flags: 0")
    initial_result_label.pack(pady=5)
    
    submit_initial_button = ttk.Button(frame, text="Submit Answers", command=submit_initial)
    submit_initial_button.pack(pady=15)
    
    window_initial.mainloop()

def show_followup():
    global window_followup, followup_var_list, followup_result_label
    window_followup = tk.Tk()
    window_followup.title("M-CHAT-RF Screening (Follow-Up)")
    window_followup.geometry("500x400")
    
    ttk.Label(window_followup, text="Follow-Up Questions (Yes/No):", wraplength=480).pack(pady=10)
    followup_var_list = []
    for i, question in enumerate(followup_questions):
        frame = ttk.Frame(window_followup)
        frame.pack(fill="x", padx=10, pady=5)
        ttk.Label(frame, text=question, wraplength=450).pack(side="top", anchor="w")
        var = tk.StringVar(value="Yes")
        followup_var_list.append(var)
        options_frame = ttk.Frame(frame)
        options_frame.pack(side="top", anchor="w", padx=20)
        ttk.Radiobutton(options_frame, text="Yes", variable=var, value="Yes").pack(side="left")
        ttk.Radiobutton(options_frame, text="No", variable=var, value="No").pack(side="left")
    
    followup_result_label = ttk.Label(window_followup, text="Follow-up red flags: 0")
    followup_result_label.pack(pady=5)
    
    submit_followup_button = ttk.Button(window_followup, text="Submit Follow-Up Answers", command=submit_followup)
    submit_followup_button.pack(pady=15)
    
    window_followup.mainloop()

# Launch the initial M-CHAT-RF screening window.
show_initial()

##########################################
# Phase 3: Bubble Pop Game using Pygame
##########################################

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bubble Pop Game")

WHITE = (255, 255, 255)
BLUE = (0, 100, 255)
BLACK = (0, 0, 0)

pygame.font.init()
font = pygame.font.SysFont("Arial", 28)

bubbles = []
reaction_data = []
score = 0
clock = pygame.time.Clock()

BUBBLE_INTERVAL = 1500  # milliseconds
BUBBLE_LIFESPAN = 3     # seconds

class Bubble:
    def __init__(self):
        self.radius = 30
        self.x = random.randint(self.radius, WIDTH - self.radius)
        self.y = random.randint(self.radius, HEIGHT - self.radius)
        self.appear_time = time.time()
        self.is_popped = False

    def draw(self):
        pygame.draw.circle(screen, BLUE, (self.x, self.y), self.radius)

    def is_clicked(self, pos):
        dist = ((self.x - pos[0]) ** 2 + (self.y - pos[1]) ** 2) ** 0.5
        return dist <= self.radius

running = True
last_bubble_time = pygame.time.get_ticks()

while running:
    screen.fill(WHITE)
    current_time = pygame.time.get_ticks()
    now = time.time()
    
    if current_time - last_bubble_time > BUBBLE_INTERVAL:
        bubbles.append(Bubble())
        last_bubble_time = current_time

    for bubble in bubbles[:]:
        bubble.draw()
        if not bubble.is_popped and now - bubble.appear_time > BUBBLE_LIFESPAN:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            reaction_data.append({
                "x": bubble.x,
                "y": bubble.y,
                "reaction_time_sec": None,
                "timestamp": timestamp,
                "status": "missed"
            })
            print(f"Missed bubble at ({bubble.x}, {bubble.y})")
            bubbles.remove(bubble)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        mouse_pos = None
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
        elif event.type == pygame.FINGERDOWN:
            mouse_pos = (int(event.x * WIDTH), int(event.y * HEIGHT))

        if mouse_pos is not None:
            for bubble in bubbles[:]:
                if bubble.is_clicked(mouse_pos):
                    reaction_time = now - bubble.appear_time
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    reaction_data.append({
                        "x": bubble.x,
                        "y": bubble.y,
                        "reaction_time_sec": round(reaction_time, 2),
                        "timestamp": timestamp,
                        "status": "popped"
                    })
                    score += 1
                    print(f"Popped bubble at ({bubble.x}, {bubble.y}) - Reaction: {reaction_time:.2f}s")
                    bubble.is_popped = True
                    bubbles.remove(bubble)

    score_text = font.render(f"Score: {score}", True, BLACK)
    screen.blit(score_text, (10, 10))
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()

csv_file = "reaction_times.csv"
with open(csv_file, mode='w', newline='') as file:
    writer = csv.DictWriter(file, fieldnames=["x", "y", "reaction_time_sec", "timestamp", "status"])
    writer.writeheader()
    writer.writerows(reaction_data)

print(f"\nSaved {len(reaction_data)} records to {csv_file}")
