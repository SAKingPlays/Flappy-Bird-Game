import pygame
import random
import sys
import math

# Initialize pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 400, 600
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Bird")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
SKY_BLUE_TOP = (135, 206, 250)
SKY_BLUE_BOTTOM = (70, 130, 180)
GREEN = (60, 180, 75)
DARK_GREEN = (30, 90, 40)
BIRD_BODY = (255, 200, 0)  # Yellow for bird body
BIRD_BEAK = (255, 140, 0)  # Orange for beak
BIRD_EYE = (0, 0, 0)       # Black for eye
GROUND_COLOR = (139, 69, 19)

# Game variables
FPS = 60
GRAVITY = 0.3
BIRD_JUMP_VELOCITY = -8
PIPE_SPEED = 3
PIPE_GAP = 180
PIPE_FREQUENCY = 1500  # milliseconds

# Fonts
FONT = pygame.font.SysFont("Arial", 32, bold=True)
SMALL_FONT = pygame.font.SysFont("Arial", 18)

class Bird:
    def __init__(self):
        self.x = 80
        self.y = HEIGHT // 2
        self.velocity = 0
        self.radius = 15
        self.rotation = 0
        self.flap_counter = 0

    def flap(self):
        self.velocity = BIRD_JUMP_VELOCITY
        self.rotation = -30  # Tilt up on flap

    def update(self):
        self.velocity += GRAVITY
        self.y += self.velocity

        # Clamp bird inside screen vertically
        if self.y < self.radius:
            self.y = self.radius
            self.velocity = 0
        if self.y > HEIGHT - 20 - self.radius:
            self.y = HEIGHT - 20 - self.radius
            self.velocity = 0

        # Smooth rotation based on velocity
        if self.velocity < 0:
            self.rotation = max(-30, self.rotation - 4)
        else:
            self.rotation = min(60, self.rotation + 4)

        self.flap_counter += 1

    def get_rect(self):
        return pygame.Rect(self.x - self.radius, self.y - self.radius,
                           self.radius * 2, self.radius * 2)

    def draw(self, screen):
        # Save current surface to rotate bird
        bird_surface = pygame.Surface((self.radius * 4, self.radius * 4), pygame.SRCALPHA)
        center = (self.radius * 2, self.radius * 2)

        # Draw bird body
        pygame.draw.circle(bird_surface, BIRD_BODY, center, self.radius)

        # Draw wing with flapping animation
        wing_offset = math.sin(self.flap_counter * 0.3) * 5
        wing_points = [
            (center[0] - 10, center[1] - wing_offset),
            (center[0] - 25, center[1] - 5 - wing_offset),
            (center[0] - 15, center[1] + 5 - wing_offset)
        ]
        pygame.draw.polygon(bird_surface, BIRD_BODY, wing_points)

        # Draw beak
        beak_points = [
            (center[0] + self.radius, center[1]),
            (center[0] + self.radius + 8, center[1] - 3),
            (center[0] + self.radius + 8, center[1] + 3)
        ]
        pygame.draw.polygon(bird_surface, BIRD_BEAK, beak_points)

        # Draw eye
        pygame.draw.circle(bird_surface, WHITE, (center[0] + 5, center[1] - 5), 4)
        pygame.draw.circle(bird_surface, BIRD_EYE, (center[0] + 6, center[1] - 5), 2)

        # Rotate bird surface
        rotated_surface = pygame.transform.rotate(bird_surface, self.rotation)
        rotated_rect = rotated_surface.get_rect(center=(self.x, self.y))

        # Blit rotated bird
        screen.blit(rotated_surface, rotated_rect.topleft)

class Pipe:
    def __init__(self, x):
        self.x = x
        self.height = random.randint(100, HEIGHT - PIPE_GAP - 120)
        self.passed = False

        # Rectangles for collision
        self.top_pipe = pygame.Rect(self.x, 0, 60, self.height)
        self.bottom_pipe = pygame.Rect(self.x, self.height + PIPE_GAP, 60, HEIGHT - self.height - PIPE_GAP - 20)

        # Caps for pipes
        self.top_cap = pygame.Rect(self.x - 5, self.height - 20, 70, 20)
        self.bottom_cap = pygame.Rect(self.x - 5, self.height + PIPE_GAP, 70, 20)

    def update(self):
        self.x -= PIPE_SPEED
        self.top_pipe.x = int(self.x)
        self.bottom_pipe.x = int(self.x)
        self.top_cap.x = int(self.x) - 5
        self.bottom_cap.x = int(self.x) - 5

    def draw(self, screen):
        # Draw pipes
        pygame.draw.rect(screen, GREEN, self.top_pipe)
        pygame.draw.rect(screen, DARK_GREEN, self.top_cap)
        pygame.draw.rect(screen, GREEN, self.bottom_pipe)
        pygame.draw.rect(screen, DARK_GREEN, self.bottom_cap)

        # Pipe stripes for detail
        for i in range(0, self.height, 15):
            pygame.draw.rect(screen, DARK_GREEN, (self.x + 5, i, 50, 2))
        for i in range(self.height + PIPE_GAP, HEIGHT - 20, 15):
            pygame.draw.rect(screen, DARK_GREEN, (self.x + 5, i, 50, 2))

    def off_screen(self):
        return self.x < -70

    def collide(self, bird):
        bird_rect = bird.get_rect()
        return (self.top_pipe.colliderect(bird_rect) or
                self.bottom_pipe.colliderect(bird_rect) or
                self.top_cap.colliderect(bird_rect) or
                self.bottom_cap.colliderect(bird_rect))

def draw_clouds(screen):
    # Draw moving clouds
    cloud_color = (255, 255, 255, 180)
    for i in range(3):
        x = (pygame.time.get_ticks() // 50 + i * 200) % (WIDTH + 200) - 100
        y = 80 + i * 60
        pygame.draw.ellipse(screen, WHITE, (x, y, 80, 40))
        pygame.draw.ellipse(screen, WHITE, (x + 20, y - 10, 60, 30))
        pygame.draw.ellipse(screen, WHITE, (x + 40, y + 10, 70, 35))

def draw_ground(screen):
    # Draw ground with texture
    pygame.draw.rect(screen, GROUND_COLOR, (0, HEIGHT - 20, WIDTH, 20))
    for i in range(0, WIDTH, 30):
        pygame.draw.line(screen, (160, 82, 45), (i, HEIGHT - 20), (i, HEIGHT), 2)

def draw_text(text, font, color, surface, x, y):
    textobj = font.render(text, True, color)
    textrect = textobj.get_rect(center=(x, y))
    surface.blit(textobj, textrect)

def main():
    clock = pygame.time.Clock()
    bird = Bird()
    pipes = []
    score = 0
    last_pipe = pygame.time.get_ticks()
    game_active = False

    while True:
        clock.tick(FPS)

        # Gradient background
        for y in range(HEIGHT):
            ratio = y / HEIGHT
            r = SKY_BLUE_TOP[0] * (1 - ratio) + SKY_BLUE_BOTTOM[0] * ratio
            g = SKY_BLUE_TOP[1] * (1 - ratio) + SKY_BLUE_BOTTOM[1] * ratio
            b = SKY_BLUE_TOP[2] * (1 - ratio) + SKY_BLUE_BOTTOM[2] * ratio
            pygame.draw.line(SCREEN, (int(r), int(g), int(b)), (0, y), (WIDTH, y))

        draw_clouds(SCREEN)
        draw_ground(SCREEN)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if not game_active:
                        # Start or restart game
                        game_active = True
                        bird = Bird()
                        pipes.clear()
                        score = 0
                        last_pipe = pygame.time.get_ticks()
                    bird.flap()
                if event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()

        if game_active:
            # Add pipes at intervals
            current_time = pygame.time.get_ticks()
            if current_time - last_pipe > PIPE_FREQUENCY:
                pipes.append(Pipe(WIDTH))
                last_pipe = current_time

            bird.update()

            # Update pipes and check for off-screen pipes and scoring
            for pipe in pipes[:]:
                pipe.update()
                if pipe.off_screen():
                    pipes.remove(pipe)
                # Score when bird passes pipe
                if not pipe.passed and pipe.x + 60 < bird.x:
                    pipe.passed = True
                    score += 1

            # Collision detection
            for pipe in pipes:
                if pipe.collide(bird):
                    game_active = False
                    break

            # Check if bird hits ground or ceiling
            if bird.y >= HEIGHT - 20 - bird.radius or bird.y <= bird.radius:
                game_active = False

        # Draw pipes
        for pipe in pipes:
            pipe.draw(SCREEN)

        # Draw bird
        bird.draw(SCREEN)

        # Draw score
        draw_text(f"Score: {score}", FONT, BLACK, SCREEN, WIDTH // 2, 50)

        if not game_active:
            if score > 0:
                draw_text("Game Over", FONT, BLACK, SCREEN, WIDTH // 2, HEIGHT // 2 - 50)
                draw_text(f"Final Score: {score}", FONT, BLACK, SCREEN, WIDTH // 2, HEIGHT // 2)
                draw_text("Press SPACE to Restart", SMALL_FONT, BLACK, SCREEN, WIDTH // 2, HEIGHT // 2 + 50)
                draw_text("Press Q to Quit", SMALL_FONT, BLACK, SCREEN, WIDTH // 2, HEIGHT // 2 + 80)
            else:
                draw_text("Press SPACE to Start", FONT, BLACK, SCREEN, WIDTH // 2, HEIGHT // 2)

        pygame.display.update()

if __name__ == "__main__":
    main()
