import pygame
import random
import time
import config_manager as cfg_mgr
from telemetry import LogWriter

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Breakout - semana 1")
clock = pygame.time.Clock()

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (220, 80, 80)
GREEN = (80, 220, 100)
BLUE = (80, 150, 220)

config = cfg_mgr.load_config()

paddle = pygame.Rect(WIDTH // 2 - 50, HEIGHT - 40, 100, 12)
ball = pygame.Rect(WIDTH // 2, HEIGHT // 2, 12, 12)
ball_vel = [random.choice([-4, 4]), -4]

bricks = []
rows, cols = 5, 8
bw, bh = 80, 22
gap = 6
off_x = (WIDTH - (cols * (bw + gap) - gap)) // 2
off_y = 60

for r in range(rows):
    for c in range(cols):
        rect = pygame.Rect(off_x + c * (bw + gap), off_y + r * (bh + gap), bw, bh)
        color = [RED, GREEN, BLUE][r % 3]
        bricks.append({"rect": rect, "color": color, "type": f"color_{r}"})

score = 0
lives = 3
level = 1
session_start = time.time()

log = LogWriter(buffer_size=10)
log.log("SESSION_START", {
    "player": config["player"],
    "difficulty": config["difficulty"]
})

font = pygame.font.SysFont("consolas", 22)
running = True

def end_session(result):
    log.log("SESSION_END", {
        "score": score,
        "level": level,
        "duration": round(time.time() - session_start, 3),
        "result": result
    })
    log.close()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        paddle.x -= 8
    if keys[pygame.K_RIGHT]:
        paddle.x += 8
    paddle.clamp_ip(screen.get_rect())

    ball.x += ball_vel[0]
    ball.y += ball_vel[1]

    if ball.left <= 0 or ball.right >= WIDTH:
        ball_vel[0] *= -1
    if ball.top <= 0:
        ball_vel[1] *= -1

    if ball.colliderect(paddle) and ball_vel[1] > 0:
        ball_vel[1] *= -1
        offset = (ball.centerx - paddle.centerx) / (paddle.width / 2)
        ball_vel[0] = offset * 4

    for brick in bricks[:]:
        if ball.colliderect(brick["rect"]):
            ball_vel[1] *= -1
            bricks.remove(brick)
            score += 10
            log.log("ENEMY_KILL", {"type": brick["type"], "wave": level})
            break

    if ball.top > HEIGHT:
        lives -= 1
        log.log("DAMAGE_TAKEN", {"amount": 1, "source": "missed_ball"})
        if lives <= 0:
            log.log("PLAYER_DEATH", {"cause": "missed_ball", "level": level})
            end_session("death")
            running = False
        else:
            ball.center = (WIDTH // 2, HEIGHT // 2)
            ball_vel = [random.choice([-4, 4]), -4]

    if not bricks:
        level += 1
        log.log("LEVEL_UP", {"level": level, "time": round(time.time() - session_start, 3)})
        bricks.clear()
        for r in range(rows + level - 1):
            for c in range(cols):
                rect = pygame.Rect(off_x + c * (bw + gap), off_y + r * (bh + gap), bw, bh)
                color = [RED, GREEN, BLUE][r % 3]
                bricks.append({"rect": rect, "color": color, "type": f"color_{r}"})
        ball.center = (WIDTH // 2, HEIGHT // 2)
        ball_vel = [random.choice([-4, 4]), -4]

    screen.fill(BLACK)
    pygame.draw.rect(screen, WHITE, paddle, border_radius=4)
    pygame.draw.ellipse(screen, WHITE, ball)
    for brick in bricks:
        pygame.draw.rect(screen, brick["color"], brick["rect"], border_radius=3)

    hud = font.render(f"Score: {score}  Level: {level}  Lives: {lives}", True, WHITE)
    screen.blit(hud, (10, 10))

    pygame.display.flip()
    clock.tick(60)

end_session("quit")
pygame.quit()
