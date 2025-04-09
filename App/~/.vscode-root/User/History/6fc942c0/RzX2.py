import pygame
import random
import time
import csv
from datetime import datetime
import tkinter as tk
from tkinter import ttk

#############################
# Part 1: Collect Kid's Info
#############################

def submit_info():
    name = name_entry.get().strip()
    age = age_entry.get().strip()
    gender = gender_entry.get().strip()
    
    if not name or not age or not gender:
        status_label.config(text="Please enter name, age, and gender.", foreground="red")
        return
    
    # Save info to CSV file
    kid_info = {
        "name": name,
        "age": age,
        "gender": gender,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    csv_file = "kid_info.csv"
    try:
        with open(csv_file, 'x', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=["name", "age", "gender", "timestamp"])
            writer.writeheader()
            writer.writerow(kid_info)
    except FileExistsError:
        with open(csv_file, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=["name", "age", "gender", "timestamp"])
            writer.writerow(kid_info)
    
    status_label.config(text="Info saved! Starting game...", foreground="green")
    root.after(1000, root.destroy)  # Close the window after 1 second

# Setup Tkinter window
root = tk.Tk()
root.title("Enter Kid's Information")
root.geometry("300x250")
root.resizable(False, False)

# Widgets for Name, Age, and Gender
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

status_label = ttk.Label(root, text="")
status_label.pack()

root.mainloop()

##########################################
# Part 2: Bubble Game using Pygame
##########################################

# Initialize Pygame
pygame.init()

# Screen settings
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bubble Pop Game")

# Colors
WHITE = (255, 255, 255)
BLUE = (0, 100, 255)
BLACK = (0, 0, 0)

# Font setup for score display
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

    # Draw and update all bubbles, checking for missed ones
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

    # Handle mouse and touch input
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

# Save game reaction data to CSV
csv_file = "reaction_times.csv"
with open(csv_file, mode='w', newline='') as file:
    writer = csv.DictWriter(file, fieldnames=["x", "y", "reaction_time_sec", "timestamp", "status"])
    writer.writeheader()
    writer.writerows(reaction_data)

print(f"\nSaved {len(reaction_data)} records to {csv_file}")
