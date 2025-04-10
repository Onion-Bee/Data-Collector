import pygame
import random
import time
import csv

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bubble Pop Game")

font = pygame.font.SysFont("Arial", 24)
clock = pygame.time.Clock()

bubble_radius = 30
bubble_speed = 2
score = 0
start_time = time.time()
game_duration = 30  # seconds

# Modify the Bubble class to record its spawn time.
class Bubble:
    def __init__(self):
        self.x = random.randint(bubble_radius, WIDTH - bubble_radius)
        self.y = HEIGHT + bubble_radius
        self.color = (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))
        self.spawn_time = time.time()  # Record when this bubble was created.

    def move(self):
        self.y -= bubble_speed

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (self.x, self.y), bubble_radius)

    def is_clicked(self, pos):
        return (self.x - pos[0])**2 + (self.y - pos[1])**2 <= bubble_radius**2

    def off_screen(self):
        return self.y + bubble_radius < 0

bubbles = []
running = True
game_over = False

# Open the CSV file once for appending reaction times.
csv_file = "reaction_times.csv"
# Optionally, write header if file is new. Here we simply open in append mode.
with open(csv_file, "a", newline="") as csvfile:
    writer = csv.writer(csvfile)
    # Uncomment the next line if you want a header every time you run the game
    # writer.writerow(["reaction_time_sec"])

while running:
    screen.fill((255, 255, 255))
    elapsed_time = time.time() - start_time

    if elapsed_time < game_duration:
        if random.random() < 0.02:
            bubbles.append(Bubble())

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN and not game_over:
                # Process bubble clicks and store reaction times.
                for bubble in bubbles[:]:
                    if bubble.is_clicked(event.pos):
                        reaction_time = time.time() - bubble.spawn_time
                        with open(csv_file, "a", newline="") as csvfile:
                            writer = csv.writer(csvfile)
                            writer.writerow([round(reaction_time, 2)])
                        bubbles.remove(bubble)
                        score += 1
                        break

        for bubble in bubbles[:]:
            bubble.move()
            bubble.draw(screen)
            if bubble.off_screen():
                bubbles.remove(bubble)

        timer_text = font.render(f"Time: {int(game_duration - elapsed_time)}", True, (0, 0, 0))
        score_text = font.render(f"Score: {score}", True, (0, 0, 0))
        screen.blit(timer_text, (10, 10))
        screen.blit(score_text, (10, 40))
    else:
        if not game_over:
            game_over = True
            print(f"Final Score: {score}")
        screen.fill((255, 255, 255))
        game_over_text = font.render("Game Over!", True, (255, 0, 0))
        final_score_text = font.render(f"Your Score: {score}", True, (0, 0, 0))
        screen.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//2 - 30))
        screen.blit(final_score_text, (WIDTH//2 - final_score_text.get_width()//2, HEIGHT//2 + 10))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
