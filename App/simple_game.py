import pygame

class SimpleGame:
    def start(self):
        pygame.init()
        screen = pygame.display.set_mode((400, 400))
        pygame.display.set_caption("Simple Game")
        clock = pygame.time.Clock()
        color = (0, 0, 255)
        pos = [200, 200]
        running = True

        while running:
            screen.fill((255, 255, 255))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        pos[1] -= 10
                    elif event.key == pygame.K_DOWN:
                        pos[1] += 10
                    elif event.key == pygame.K_LEFT:
                        pos[0] -= 10
                    elif event.key == pygame.K_RIGHT:
                        pos[0] += 10

            pygame.draw.circle(screen, color, pos, 20)
            pygame.display.flip()
            clock.tick(30)

        pygame.quit()
