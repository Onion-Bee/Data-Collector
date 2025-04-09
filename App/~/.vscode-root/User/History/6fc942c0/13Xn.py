import pygame
import random
import time
import csv
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
    
    # Save info to CSV file
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
    root.after(1000, root.destroy)  # Close the window after a second

# Create Tkinter window for kid's info
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

# We define a list of initial screening questions.
# For simplicity, we assume the expected answer is "Yes".
# A "No" answer counts as a risk (red flag).
initial_questions = [
    "Does your child enjoy social games?",
    "Does your child make eye contact with you?",
    "Does your child imitate adults?",
    "Does your child engage in pretend play?",
    "Does your child respond when you call their name?"
]

# Threshold: if red flags (i.e. "No" answers) are >= threshold, then follow-up screening is needed.
initial_threshold = 2

# We'll also define a list for follow-up screening questions.
followup_questions = [
    "Does your child have difficulty understanding simple instructions?",
    "Does your child show limited interest in social interactions?"
]
followup_threshold = 1  # if at least one "No" on follow-up

# We'll store answers in dictionaries.
mchat_initial_answers = {}
mchat_followup_answers = {}

def submit_initial():
    # Count red flag responses in the initial screening.
    red_flags = 0
    for i in range(len(initial_questions)):
        answer = var_list[i].get()
        mchat_initial_answers[f"Q{i+1}"] = answer
        if answer == "No":
            red_flags += 1
            
    initial_score_label.config(text=f"Red flags: {red_flags}")
    # Save initial answers temporarily (could be saved later along with followup below)
    window_initial.destroy()
    
    # If red flags meet threshold, start followup screening; otherwise, record result.
    if red_flags >= initial_threshold:
        show_followup()
    else:
        # Save M-CHAT results
        outcome = "Pass"
        save_mchat_results(red_flags, None, outcome)
        window_initial.quit()  # close loop if needed

def submit_followup():
    red_flags_followup = 0
    for i in range(len(followup_questions)):
        answer = followup_vars[i].get()
        mchat_followup_answers[f"Followup_Q{i+1}"] = answer
        if answer == "No":
            red_flags_followup += 1
    followup_score_label.config(text=f"Follow-up red flags: {red_flags_followup}")
    window_followup.destroy()
    
    # Determine final outcome based on follow-up:
    if red_flags_followup >= followup_threshold:
        outcome = "High Risk"
    else:
        outcome = "Moderate Risk"
    # Save M-CHAT results: combine initial and followup
    save_mchat_results(sum(1 for a in mchat_initial_answers.values() if a=="No"),
                       red_flags_followup,
                       outcome)

def save_mchat_results(initial_red_flags, followup_red_flags, outcome):
    # Save results to CSV
    csv_file = "mchat_results.csv"
    result = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "initial_red_flags": initial_red_flags,
        "followup_red_flags": followup_red_flags if followup_red_flags is not None else "",
        "outcome": outcome
    }
    try:
        with open(csv_file, 'x', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=["timestamp", "initial_red_flags", "followup_red_flags", "outcome"])
            writer.writeheader()
            writer.writerow(result)
    except FileExistsError:
        with open(csv_file, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=["timestamp", "initial_red_flags", "followup_red_flags", "outcome"])
            writer.writerow(result)
    print(f"M-CHAT results saved: {result}")

def show_initial():
    global window_initial, var_list, initial_score_label
    window_initial = tk.Tk()
    window_initial.title("M-CHAT-RF Screening (Initial)")
    window_initial.geometry("400x400")
    
    ttk.Label(window_initial, text="Please answer the questions below (Yes/No):", wraplength=380).pack(pady=10)
    var_list = []
    for i, question in enumerate(initial_questions):
        frame = ttk.Frame(window_initial)
        frame.pack(fill="x", padx=10, pady=5)
        ttk.Label(frame, text=f"{i+1}. {question}", wraplength=350).pack(side="top", anchor="w")
        # Variable for the answer of question i
        var = tk.StringVar(value="Yes")
        var_list.append(var)
        # Options: Yes and No using Radiobuttons
        options_frame = ttk.Frame(frame)
        options_frame.pack(side="top", anchor="w", padx=20)
        ttk.Radiobutton(options_frame, text="Yes", variable=var, value="Yes").pack(side="left")
        ttk.Radiobutton(options_frame, text="No", variable=var, value="No").pack(side="left")
    
    initial_score_label = ttk.Label(window_initial, text="Red flags: 0")
    initial_score_label.pack(pady=5)
    
    submit_initial_button = ttk.Button(window_initial, text="Submit Answers", command=submit_initial)
    submit_initial_button.pack(pady=20)
    
    window_initial.mainloop()

def show_followup():
    global window_followup, followup_vars, followup_score_label
    window_followup = tk.Tk()
    window_followup.title("M-CHAT-RF Screening (Follow-Up)")
    window_followup.geometry("400x300")
    
    ttk.Label(window_followup, text="Follow-Up Questions (Yes/No):", wraplength=380).pack(pady=10)
    followup_vars = []
    for i, question in enumerate(followup_questions):
        frame = ttk.Frame(window_followup)
        frame.pack(fill="x", padx=10, pady=5)
        ttk.Label(frame, text=f"{i+1}. {question}", wraplength=350).pack(side="top", anchor="w")
        var = tk.StringVar(value="Yes")
        followup_vars.append(var)
        options_frame = ttk.Frame(frame)
        options_frame.pack(side="top", anchor="w", padx=20)
        ttk.Radiobutton(options_frame, text="Yes", variable=var, value="Yes").pack(side="left")
        ttk.Radiobutton(options_frame, text="No", variable=var, value="No").pack(side="left")
        
    followup_score_label = ttk.Label(window_followup, text="Follow-up red flags: 0")
    followup_score_label.pack(pady=5)
    
    submit_followup_button = ttk.Button(window_followup, text="Submit Follow-Up Answers", command=submit_followup)
    submit_followup_button.pack(pady=20)
    
    window_followup.mainloop()

# First, show the initial M-CHAT screening window.
show_initial()

##########################################
# Phase 3: Bubble Pop Game using Pygame
##########################################

# Initialize Pygame
pygame.init()

# Screen settings
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bubble Pop Game")

# Colors for the game
WHITE = (255, 255, 255)
BLUE = (0, 100, 255)
BLACK = (0, 0, 0)

# Font setup for score
pygame.font.init()
font = pygame.font.SysFont("Arial", 28)

# Bubble list and logs for reaction times
bubbles = []
reaction_data = []

# Score variable
score = 0

# Clock for controlling the game's framerate
clock = pygame.time.Clock()

# Constants for bubble generation and lifespan
BUBBLE_INTERVAL = 1500  # milliseconds between bubbles
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

# Game loop
running = True
last_bubble_time = pygame.time.get_ticks()

while running:
    screen.fill(WHITE)
    current_time = pygame.time.get_ticks()
    now = time.time()

    # Generate new bubble periodically
    if current_time - last_bubble_time > BUBBLE_INTERVAL:
        bubbles.append(Bubble())
        last_bubble_time = current_time

    # Draw and update bubbles; check for missed bubbles
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

    # Handle input for mouse and touch
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

    # Render score on screen
    score_text = font.render(f"Score: {score}", True, BLACK)
    screen.blit(score_text, (10, 10))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()

# Save game reaction data to CSV after the game ends
csv_file = "reaction_times.csv"
with open(csv_file, mode='w', newline='') as file:
    writer = csv.DictWriter(file, fieldnames=["x", "y", "reaction_time_sec", "timestamp", "status"])
    writer.writeheader()
    writer.writerows(reaction_data)

print(f"\nSaved {len(reaction_data)} records to {csv_file}")
