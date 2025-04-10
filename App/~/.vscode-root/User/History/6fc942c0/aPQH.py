import pygame
import time
import random
import csv         # Added CSV module import
from datetime import datetime

pygame.init()

# Screen settings
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bubble Pop Game")

# Colors and font
WHITE = (255, 255, 255)import pygame
import time
import random
import csv         # Added CSV module import
from datetime import datetime

pygame.init()

# Screen settings
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bubble Pop Game")

# Colors and font
WHITE = (255, 255, 255)
BLUE = (0, 100, 255)
BLACK = (0, 0, 0)
pygame.font.init()
font = pygame.font.SysFont("Arial", 28)

# Game variables
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
        self.appear_time = time.time()  # Record the time when bubble appears
        self.is_popped = False

    def draw(self):
        pygame.draw.circle(screen, BLUE, (self.x, self.y), self.radius)

    def is_clicked(self, pos):
        # Euclidean distance to check if point is within the bubble circle.
        dist = ((self.x - pos[0]) ** 2 + (self.y - pos[1]) ** 2) ** 0.5
        return dist <= self.radius

running = True
last_bubble_time = pygame.time.get_ticks()

while running:
    screen.fill(WHITE)
    current_time = pygame.time.get_ticks()
    now = time.time()
    
    # Generate a new bubble at regular intervals
    if current_time - last_bubble_time > BUBBLE_INTERVAL:
        bubbles.append(Bubble())
        last_bubble_time = current_time

    # Draw bubbles and check for missed bubbles (i.e. those that haven't been popped in time)
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

    # Process events for mouse and touch input
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        mouse_pos = None
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
        elif event.type == pygame.FINGERDOWN:
            # Convert normalized touch coordinates to screen pixel coordinates.
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
                    # Process one bubble per click; break out of the loop.
                    break

    # Display score on the screen
    score_text = font.render(f"Score: {score}", True, BLACK)
    screen.blit(score_text, (10, 10))
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()

# Save the reaction data into a CSV file after the game ends.
csv_file = "reaction_times.csv"
with open(csv_file, mode='w', newline='') as file:
    fieldnames = ["x", "y", "reaction_time_sec", "timestamp", "status"]
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(reaction_data)

print(f"\nSaved {len(reaction_data)} records to {csv_file}")

BLUE = (0, 100, 255)
BLACK = (0, 0, 0)
pygame.font.init()
font = pygame.font.SysFont("Arial", 28)

# Game variables
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
        self.appear_time = time.time()  # Record the time when bubble appears
        self.is_popped = False

    def draw(self):
        pygame.draw.circle(screen, BLUE, (self.x, self.y), self.radius)

    def is_clicked(self, pos):
        # Euclidean distance to check if point is within the bubble circle.
        dist = ((self.x - pos[0]) ** 2 + (self.y - pos[1]) ** 2) ** 0.5
        return dist <= self.radius

running = True
last_bubble_time = pygame.time.get_ticks()

while running:
    screen.fill(WHITE)
    current_time = pygame.time.get_ticks()
    now = time.time()
    
    # Generate a new bubble at regular intervals
    if current_time - last_bubble_time > BUBBLE_INTERVAL:
        bubbles.append(Bubble())
        last_bubble_time = current_time

    # Draw bubbles and check for missed bubbles (i.e. those that haven't been popped in time)
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

    # Process events for mouse and touch input
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        mouse_pos = None
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
        elif event.type == pygame.FINGERDOWN:
            # Convert normalized touch coordinates to screen pixel coordinates.
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
                    # Process one bubble per click; break out of the loop.
                    break

    # Display score on the screen
    score_text = font.render(f"Score: {score}", True, BLACK)
    screen.blit(score_text, (10, 10))
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()

# Save the reaction data into a CSV file after the game ends.
csv_file = "reaction_times.csv"
with open(csv_file, mode='w', newline='') as file:
    fieldnames = ["x", "y", "reaction_time_sec", "timestamp", "status"]
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(reaction_data)

print(f"\nSaved {len(reaction_data)} records to {csv_file}")
