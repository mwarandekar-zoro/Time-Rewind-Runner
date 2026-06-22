import pygame
import sys
import random
import json
import os
from enum import Enum

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
GREEN = (100, 255, 100)
PURPLE = (200, 100, 255)
CYAN = (100, 255, 255)
GRAY = (100, 100, 100)

# Difficulty levels
class Difficulty(Enum):
    EASY = {"ghost_delay": 500, "obstacle_freq": 0.01, "speed_cap": 8, "spawn_delay": 1500}
    NORMAL = {"ghost_delay": 300, "obstacle_freq": 0.02, "speed_cap": 12, "spawn_delay": 1000}
    HARD = {"ghost_delay": 150, "obstacle_freq": 0.035, "speed_cap": 15, "spawn_delay": 700}

# Skins
class Skin(Enum):
    PIKACHU = "pikachu"
    CHARMANDER = "charmander"
    SQUIRTLE = "squirtle"

# Power-up types
class PowerUpType(Enum):
    SHIELD = "shield"
    SLOW_MO = "slow_mo"
    SPEED_BOOST = "speed_boost"

# Game variables
difficulty = None
selected_skin = Skin.PIKACHU
score = 0
lives = 3
font = pygame.font.SysFont(None, 40)
small_font = pygame.font.SysFont(None, 30)
clock = pygame.time.Clock()
high_scores_file = "high_scores.json"

# Player
player_size = 50
player_x = WIDTH // 2
player_y = HEIGHT // 2
player_speed = 5
player_angle = 0  # for animation

# Coin
coin_size = 20
coin_x = random.randint(50, WIDTH - 50)
coin_y = random.randint(50, HEIGHT - 50)
coin_angle = 0  # for spinning animation

# Movement history
movement_history = []

# Obstacles
obstacles = []
obstacle_spawn_timer = 0

# Power-ups
power_ups = []
power_up_spawn_timer = 0
active_power_up = None
power_up_timer = 0

# Game state
game_over = False
game_paused = False
speed_thresholds = {5, 10, 15, 20}
speed_increased_at = set()
ghost_x = None
ghost_y = None
show_ghost = False


def load_high_scores():
    """Load high scores from file."""
    if os.path.exists(high_scores_file):
        try:
            with open(high_scores_file, 'r') as f:
                return sorted(json.load(f), reverse=True)[:10]
        except:
            return []
    return []


def save_high_score(score):
    """Save score to high scores file."""
    scores = load_high_scores()
    scores.append(score)
    scores = sorted(scores, reverse=True)[:10]
    with open(high_scores_file, 'w') as f:
        json.dump(scores, f)


def draw_menu():
    """Draw difficulty selection menu."""
    screen.fill(BLACK)
    title = font.render("Time Rewind Runner", True, WHITE)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 100))

    difficulty_text = small_font.render("Select Difficulty:", True, WHITE)
    screen.blit(difficulty_text, (WIDTH // 2 - difficulty_text.get_width() // 2, 200))

    easy_text = small_font.render("1 - EASY", True, GREEN)
    normal_text = small_font.render("2 - NORMAL", True, GOLD)
    hard_text = small_font.render("3 - HARD", True, RED)

    screen.blit(easy_text, (WIDTH // 2 - easy_text.get_width() // 2, 280))
    screen.blit(normal_text, (WIDTH // 2 - normal_text.get_width() // 2, 340))
    screen.blit(hard_text, (WIDTH // 2 - hard_text.get_width() // 2, 400))

    hint = small_font.render("Press 1, 2, or 3 to start", True, GRAY)
    screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2, 500))

    pygame.display.flip()


def draw_skin_menu():
    """Draw skin selection menu."""
    screen.fill(BLACK)
    title = font.render("Choose Your Skin", True, WHITE)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 100))

    skins_text = [
        small_font.render("1 - Pikachu", True, GOLD),
        small_font.render("2 - Charmander", True, RED),
        small_font.render("3 - Squirtle", True, BLUE),
    ]

    for i, text in enumerate(skins_text):
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, 250 + i * 80))

    pygame.display.flip()


def draw_pikachu(surface, x, y, size, angle=0):
    yellow = (255, 204, 0)
    black = (0, 0, 0)
    red = (255, 100, 100)
    rect = pygame.Rect(x, y, size, size)
    pygame.draw.rect(surface, yellow, rect)

    ear_h = int(size * 0.5)
    left_ear = [(x + int(size * 0.15), y), (x + int(size * 0.05), y - ear_h), (x + int(size * 0.35), y)]
    right_ear = [(x + int(size * 0.85), y), (x + int(size * 0.95), y - ear_h), (x + int(size * 0.65), y)]
    pygame.draw.polygon(surface, yellow, left_ear)
    pygame.draw.polygon(surface, yellow, right_ear)

    eye_r = max(2, size // 10)
    eye_x1 = x + int(size * 0.3)
    eye_x2 = x + int(size * 0.7)
    eye_y = y + int(size * 0.35)
    pygame.draw.circle(surface, black, (eye_x1, eye_y), eye_r)
    pygame.draw.circle(surface, black, (eye_x2, eye_y), eye_r)

    cheek_r = max(4, size // 8)
    pygame.draw.circle(surface, red, (x + int(size * 0.2), y + int(size * 0.65)), cheek_r)
    pygame.draw.circle(surface, red, (x + int(size * 0.8), y + int(size * 0.65)), cheek_r)


def draw_charmander(surface, x, y, size, angle=0):
    orange = (255, 165, 0)
    black = (0, 0, 0)
    red = (255, 100, 100)
    rect = pygame.Rect(x, y, size, size)
    pygame.draw.rect(surface, orange, rect)

    eye_r = max(2, size // 10)
    eye_x1 = x + int(size * 0.3)
    eye_x2 = x + int(size * 0.7)
    eye_y = y + int(size * 0.35)
    pygame.draw.circle(surface, black, (eye_x1, eye_y), eye_r)
    pygame.draw.circle(surface, black, (eye_x2, eye_y), eye_r)

    # Flame on head
    flame_points = [
        (x + size // 2, y - size // 3),
        (x + size // 2 - size // 6, y + size // 4),
        (x + size // 2 + size // 6, y + size // 4),
    ]
    pygame.draw.polygon(surface, red, flame_points)


def draw_squirtle(surface, x, y, size, angle=0):
    blue = (100, 150, 255)
    black = (0, 0, 0)
    rect = pygame.Rect(x, y, size, size)
    pygame.draw.rect(surface, blue, rect)

    # Shell circle
    shell_r = int(size * 0.35)
    pygame.draw.circle(surface, (80, 120, 200), (x + size // 2, y + size // 2), shell_r)

    eye_r = max(2, size // 10)
    eye_x1 = x + int(size * 0.3)
    eye_x2 = x + int(size * 0.7)
    eye_y = y + int(size * 0.35)
    pygame.draw.circle(surface, black, (eye_x1, eye_y), eye_r)
    pygame.draw.circle(surface, black, (eye_x2, eye_y), eye_r)


def draw_ghost(surface, x, y, size):
    body_color = RED
    black = (0, 0, 0)
    head_r = size // 2
    center_x = x + head_r
    center_y = y + head_r

    pygame.draw.circle(surface, body_color, (center_x, center_y), head_r)
    pygame.draw.rect(surface, body_color, (x, y + head_r, size, head_r))

    scallop_r = size // 6
    for i in range(4):
        cx = x + int((i + 0.5) * (size / 4))
        cy = y + size
        pygame.draw.circle(surface, body_color, (cx, cy), scallop_r)

    eye_r = max(2, size // 12)
    pygame.draw.circle(surface, black, (x + int(size * 0.35), y + int(size * 0.4)), eye_r)
    pygame.draw.circle(surface, black, (x + int(size * 0.65), y + int(size * 0.4)), eye_r)


def draw_player(surface, x, y, size, angle):
    """Draw player based on selected skin."""
    if selected_skin == Skin.PIKACHU:
        draw_pikachu(surface, x, y, size, angle)
    elif selected_skin == Skin.CHARMANDER:
        draw_charmander(surface, x, y, size, angle)
    elif selected_skin == Skin.SQUIRTLE:
        draw_squirtle(surface, x, y, size, angle)


def spawn_obstacle():
    """Spawn a random obstacle."""
    width = random.randint(30, 100)
    height = random.randint(30, 100)
    x = random.randint(0, WIDTH - width)
    y = random.randint(0, HEIGHT - height)
    obstacles.append(pygame.Rect(x, y, width, height))


def spawn_power_up():
    """Spawn a random power-up."""
    ptype = random.choice(list(PowerUpType))
    x = random.randint(50, WIDTH - 50)
    y = random.randint(50, HEIGHT - 50)
    power_ups.append({"type": ptype, "x": x, "y": y, "radius": 15})


def draw_power_up(surface, pu):
    """Draw power-up with color based on type."""
    color = PURPLE if pu["type"] == PowerUpType.SHIELD else CYAN if pu["type"] == PowerUpType.SLOW_MO else GREEN
    pygame.draw.circle(surface, color, (pu["x"], pu["y"]), pu["radius"])
    pygame.draw.circle(surface, WHITE, (pu["x"], pu["y"]), pu["radius"], 2)


def apply_power_up(ptype):
    """Apply a power-up effect."""
    global active_power_up, power_up_timer
    active_power_up = ptype
    power_up_timer = 300  # 5 seconds at 60 FPS


# Menu loop - Difficulty selection
while difficulty is None:
    draw_menu()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                difficulty = Difficulty.EASY
            elif event.key == pygame.K_2:
                difficulty = Difficulty.NORMAL
            elif event.key == pygame.K_3:
                difficulty = Difficulty.HARD

# Skin selection
skin_selected = False
while not skin_selected:
    draw_skin_menu()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                selected_skin = Skin.PIKACHU
                skin_selected = True
            elif event.key == pygame.K_2:
                selected_skin = Skin.CHARMANDER
                skin_selected = True
            elif event.key == pygame.K_3:
                selected_skin = Skin.SQUIRTLE
                skin_selected = True

# Get difficulty settings
diff_settings = difficulty.value
max_player_speed = diff_settings["speed_cap"]

# Main game loop
running = True
ghost_spawn_timer = 0

while running:
    clock.tick(60)

    # Events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                game_paused = not game_paused

    if game_paused:
        pause_text = font.render("PAUSED - Press P to Resume", True, WHITE)
        screen.blit(pause_text, (WIDTH // 2 - pause_text.get_width() // 2, HEIGHT // 2))
        pygame.display.flip()
        continue

    # Key presses
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        player_x -= player_speed
    if keys[pygame.K_RIGHT]:
        player_x += player_speed
    if keys[pygame.K_UP]:
        player_y -= player_speed
    if keys[pygame.K_DOWN]:
        player_y += player_speed

    # Animation
    player_angle += 5
    coin_angle += 10

    # Boundaries
    if player_x < 0:
        player_x = 0
    if player_x > WIDTH - player_size:
        player_x = WIDTH - player_size
    if player_y < 0:
        player_y = 0
    if player_y > HEIGHT - player_size:
        player_y = HEIGHT - player_size

    # Record movement
    movement_history.append((player_x, player_y))

    # Collision detection - coin
    player_rect = pygame.Rect(player_x, player_y, player_size, player_size)
    coin_rect = pygame.Rect(coin_x - coin_size, coin_y - coin_size, coin_size * 2, coin_size * 2)

    if player_rect.colliderect(coin_rect):
        score += 1
        coin_x = random.randint(50, WIDTH - 50)
        coin_y = random.randint(50, HEIGHT - 50)

        # Speed increase at thresholds
        if score in speed_thresholds and score not in speed_increased_at:
            player_speed = min(player_speed + 1, max_player_speed)
            speed_increased_at.add(score)

    # Collision detection - power-ups
    for pu in power_ups[:]:
        pu_rect = pygame.Rect(pu["x"] - pu["radius"], pu["y"] - pu["radius"], pu["radius"] * 2, pu["radius"] * 2)
        if player_rect.colliderect(pu_rect):
            apply_power_up(pu["type"])
            power_ups.remove(pu)

    # Collision detection - obstacles
    for obs in obstacles:
        if player_rect.colliderect(obs):
            lives -= 1
            if lives <= 0:
                game_over = True
                running = False
            else:
                # Reset player position
                player_x = WIDTH // 2
                player_y = HEIGHT // 2
                obstacles.clear()
                obstacle_spawn_timer = 0

    # Update power-up timer
    if active_power_up:
        power_up_timer -= 1
        if power_up_timer <= 0:
            active_power_up = None

    # Spawn obstacles
    obstacle_spawn_timer += 1
    if random.random() < diff_settings["obstacle_freq"] and obstacle_spawn_timer > diff_settings["spawn_delay"]:
        spawn_obstacle()
        obstacle_spawn_timer = 0

    # Spawn power-ups
    power_up_spawn_timer += 1
    if power_up_spawn_timer > 1200 and random.random() < 0.3:
        spawn_power_up()
        power_up_spawn_timer = 0

    # Apply power-up effects
    current_speed = player_speed
    if active_power_up == PowerUpType.SPEED_BOOST:
        current_speed = min(player_speed * 1.5, max_player_speed)
    elif active_power_up == PowerUpType.SLOW_MO:
        current_speed = player_speed * 0.5

    # Ghost spawn and collision
    ghost_spawn_timer += 1
    show_ghost = False
    if ghost_spawn_timer > diff_settings["ghost_delay"] and len(movement_history) > 300:
        global ghost_x, ghost_y
        ghost_x, ghost_y = movement_history[0]
        show_ghost = True

        ghost_rect = pygame.Rect(ghost_x, ghost_y, player_size, player_size)
        if player_rect.colliderect(ghost_rect):
            if active_power_up == PowerUpType.SHIELD:
                active_power_up = None
                power_up_timer = 0
            else:
                lives -= 1
                if lives <= 0:
                    game_over = True
                    running = False

        movement_history.pop(0)
        ghost_spawn_timer = 0

    # Draw
    screen.fill(BLACK)

    # Draw player
    draw_player(screen, player_x, player_y, player_size, player_angle)

    # Draw coin with rotation effect
    coin_surf = pygame.Surface((coin_size * 2, coin_size * 2), pygame.SRCALPHA)
    pygame.draw.circle(coin_surf, GOLD, (coin_size, coin_size), coin_size)
    rotated_coin = pygame.transform.rotate(coin_surf, coin_angle)
    screen.blit(rotated_coin, (coin_x - coin_size, coin_y - coin_size))

    # Draw obstacles
    for obs in obstacles:
        pygame.draw.rect(screen, GRAY, obs)
        pygame.draw.rect(screen, WHITE, obs, 2)

    # Draw ghost
    if show_ghost:
        draw_ghost(screen, ghost_x, ghost_y, player_size)

    # Draw power-ups
    for pu in power_ups:
        draw_power_up(screen, pu)

    # Draw active power-up indicator
    if active_power_up:
        pu_text = small_font.render(f"Shield" if active_power_up == PowerUpType.SHIELD else "Slow-Mo" if active_power_up == PowerUpType.SLOW_MO else "Speed Boost", True, GOLD)
        screen.blit(pu_text, (WIDTH - 200, 20))

    # Draw UI
    score_text = font.render(f"Score: {score}", True, WHITE)
    lives_text = font.render(f"Lives: {lives}", True, WHITE if lives > 1 else RED)
    difficulty_text = small_font.render(f"Difficulty: {difficulty.name}", True, WHITE)
    skin_text = small_font.render(f"Skin: {selected_skin.value.capitalize()}", True, WHITE)

    screen.blit(score_text, (20, 20))
    screen.blit(lives_text, (20, 60))
    screen.blit(difficulty_text, (20, 100))
    screen.blit(skin_text, (20, 140))

    pause_hint = small_font.render("Press P to Pause", True, GRAY)
    screen.blit(pause_hint, (WIDTH - 200, HEIGHT - 30))

    pygame.display.flip()

# Game Over screen
if game_over:
    save_high_score(score)
    high_scores = load_high_scores()

    waiting = True
    while waiting:
        screen.fill(BLACK)
        over_text = font.render(f"Game Over! Score: {score}", True, RED)
        screen.blit(over_text, (WIDTH // 2 - over_text.get_width() // 2, 80))

        hs_title = font.render("Top 10 High Scores:", True, GOLD)
        screen.blit(hs_title, (WIDTH // 2 - hs_title.get_width() // 2, 150))

        for i, hs in enumerate(high_scores[:10]):
            hs_text = small_font.render(f"{i + 1}. {hs}", True, WHITE)
            screen.blit(hs_text, (WIDTH // 2 - hs_text.get_width() // 2, 200 + i * 30))

        instr_text = small_font.render("Press any key to exit...", True, GRAY)
        screen.blit(instr_text, (WIDTH // 2 - instr_text.get_width() // 2, HEIGHT - 50))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                waiting = False
            elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                waiting = False

pygame.quit()
sys.exit()
