import pygame
import sys
import random

# Initialize pygame
pygame.init()

# Screen settings
WIDTH = 1000
HEIGHT = 700

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Time Rewind Runner")

# Colors
WHITE = (255, 255, 255)
BLACK = (20, 20, 20)
BLUE = (50, 150, 255)
GOLD = (255, 215, 0)
RED = (255, 100, 100)

# Player
player_size = 50
player_x = WIDTH // 2
player_y = HEIGHT // 2
player_speed = 5

# Coin
coin_size = 20
coin_x = random.randint(50, WIDTH - 50)
coin_y = random.randint(50, HEIGHT - 50)

# Score
score = 0

# Font
font = pygame.font.SysFont(None, 40)

# Clock
clock = pygame.time.Clock()

movement_history = []

# Speed increase settings
speed_thresholds = {5, 10, 15}
speed_increased_at = set()
max_player_speed = 12

# Game state
game_over = False


def draw_pikachu(surface, x, y, size):
    yellow = (255, 204, 0)
    black = (0, 0, 0)
    red = (255, 100, 100)
    rect = pygame.Rect(x, y, size, size)
    pygame.draw.rect(surface, yellow, rect)

    # ears
    ear_h = int(size * 0.5)
    left_ear = [(x + int(size * 0.15), y), (x + int(size * 0.05), y - ear_h), (x + int(size * 0.35), y)]
    right_ear = [(x + int(size * 0.85), y), (x + int(size * 0.95), y - ear_h), (x + int(size * 0.65), y)]
    pygame.draw.polygon(surface, yellow, left_ear)
    pygame.draw.polygon(surface, yellow, right_ear)
    pygame.draw.polygon(surface, black, [(left_ear[1][0], left_ear[1][1]), (left_ear[1][0] + 8, left_ear[1][1] + 20), (left_ear[1][0] - 8, left_ear[1][1] + 20)])
    pygame.draw.polygon(surface, black, [(right_ear[1][0], right_ear[1][1]), (right_ear[1][0] + 8, right_ear[1][1] + 20), (right_ear[1][0] - 8, right_ear[1][1] + 20)])

    # eyes
    eye_r = max(2, size // 10)
    eye_x1 = x + int(size * 0.3)
    eye_x2 = x + int(size * 0.7)
    eye_y = y + int(size * 0.35)
    pygame.draw.circle(surface, black, (eye_x1, eye_y), eye_r)
    pygame.draw.circle(surface, black, (eye_x2, eye_y), eye_r)

    # cheeks
    cheek_r = max(4, size // 8)
    pygame.draw.circle(surface, red, (x + int(size * 0.2), y + int(size * 0.65)), cheek_r)
    pygame.draw.circle(surface, red, (x + int(size * 0.8), y + int(size * 0.65)), cheek_r)

    # mouth / nose
    pygame.draw.circle(surface, black, (x + size // 2, y + int(size * 0.55)), max(1, size // 20))


def draw_ghost(surface, x, y, size):
    body_color = RED
    black = (0, 0, 0)
    head_r = size // 2
    center_x = x + head_r
    center_y = y + head_r

    # head
    pygame.draw.circle(surface, body_color, (center_x, center_y), head_r)
    # body rectangle
    pygame.draw.rect(surface, body_color, (x, y + head_r, size, head_r))

    # scallops
    scallop_r = size // 6
    for i in range(4):
        cx = x + int((i + 0.5) * (size / 4))
        cy = y + size
        pygame.draw.circle(surface, body_color, (cx, cy), scallop_r)

    # eyes
    eye_r = max(2, size // 12)
    pygame.draw.circle(surface, black, (x + int(size * 0.35), y + int(size * 0.4)), eye_r)
    pygame.draw.circle(surface, black, (x + int(size * 0.65), y + int(size * 0.4)), eye_r)

# Game Loop
running = True

while running:

    clock.tick(60)

    # Events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Key Presses
    keys = pygame.key.get_pressed()

    if keys[pygame.K_LEFT]:
        player_x -= player_speed

    if keys[pygame.K_RIGHT]:
        player_x += player_speed

    if keys[pygame.K_UP]:
        player_y -= player_speed

    if keys[pygame.K_DOWN]:
        player_y += player_speed

    # Boundaries
    if player_x < 0:
        player_x = 0

    if player_x > WIDTH - player_size:
        player_x = WIDTH - player_size

    if player_y < 0:
        player_y = 0

    if player_y > HEIGHT - player_size:
        player_y = HEIGHT - player_size

    movement_history.append((player_x, player_y))

    # Collision Detection
    player_rect = pygame.Rect(
        player_x,
        player_y,
        player_size,
        player_size
    )

    coin_rect = pygame.Rect(
        coin_x - coin_size,
        coin_y - coin_size,
        coin_size * 2,
        coin_size * 2
    )

    if player_rect.colliderect(coin_rect):

        score += 1

        coin_x = random.randint(50, WIDTH - 50)
        coin_y = random.randint(50, HEIGHT - 50)

    # Draw
    screen.fill(BLACK)

    # Player (draw Pikachu)
    draw_pikachu(screen, player_x, player_y, player_size)

    # Coin
    pygame.draw.circle(
        screen,
        GOLD,
        (coin_x, coin_y),
        coin_size
    )

    if len(movement_history) > 300:
        ghost_x, ghost_y = movement_history[0]

        # draw ghost and check collision
        draw_ghost(screen, ghost_x, ghost_y, player_size)

        ghost_rect = pygame.Rect(ghost_x, ghost_y, player_size, player_size)
        if player_rect.colliderect(ghost_rect):
            game_over = True
            running = False

        movement_history.pop(0)

    # Score
    score_text = font.render(
        f"Score: {score}",
        True,
        WHITE
    )

    # Increase speed once when crossing thresholds
    if score in speed_thresholds and score not in speed_increased_at:
        player_speed = min(player_speed + 1, max_player_speed)
        speed_increased_at.add(score)

    screen.blit(score_text, (20, 20))

    pygame.display.flip()

# If the game ended because of ghost collision, show Game Over briefly
if game_over:
    screen.fill(BLACK)
    over_text = font.render(f"Game Over! Score: {score}", True, WHITE)
    instr_text = font.render("Press any key to exit...", True, WHITE)
    screen.blit(over_text, (WIDTH // 2 - over_text.get_width() // 2, HEIGHT // 2 - 30))
    screen.blit(instr_text, (WIDTH // 2 - instr_text.get_width() // 2, HEIGHT // 2 + 10))
    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                waiting = False
            elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                waiting = False

pygame.quit()
sys.exit()
