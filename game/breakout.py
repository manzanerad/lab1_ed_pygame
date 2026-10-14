import pygame
import time
from telemetry.writer import EventLogWriter


class Breakout:
    def __init__(self, cfg):
        pygame.init()
        self.cfg = cfg
        self.width = cfg["screen_width"]
        self.height = cfg["screen_height"]
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Breakout Telemetry")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("monospace", 20)
        self.writer = EventLogWriter(buffer_size=5)
        self.reset_game()
        self.writer.log("SESSION_START", {
            "player": cfg["player"],
            "difficulty": cfg["difficulty"],
        })
        self.start_time = time.time()

    def reset_game(self):
        diff = self.cfg["difficulty"]
        speed_map = {"easy": 4, "normal": 6, "hard": 8}
        paddle_map = {"easy": 140, "normal": 100, "hard": 70}
        self.ball_speed = speed_map.get(diff, 6)
        self.paddle_w = paddle_map.get(diff, 100)
        self.paddle_h = 15
        self.paddle_x = self.width // 2 - self.paddle_w // 2
        self.paddle_y = self.height - 40
        self.ball_r = 8
        self.reset_ball()
        self.lives = 3
        self.score = 0
        self.level = 1
        self.bricks = []
        self.spawn_bricks()
        self.running = True
        self.result = None

    def reset_ball(self):
        self.ball_x = self.width // 2
        self.ball_y = self.height // 2
        self.ball_vx = self.ball_speed
        self.ball_vy = -self.ball_speed

    def spawn_bricks(self):
        rows = 5 + self.level
        cols = 10
        brick_w = self.width // cols - 4
        brick_h = 20
        for r in range(rows):
            for c in range(cols):
                x = c * (brick_w + 4) + 2
                y = r * (brick_h + 4) + 50
                self.bricks.append(pygame.Rect(x, y, brick_w, brick_h))

    def run(self):
        while self.running:
            dt = self.clock.tick(60)
            self.handle_events()
            self.update()
            self.draw()
        self.writer.close()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.end_session("quit")
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.end_session("quit")
                    self.running = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.paddle_x -= 8
        if keys[pygame.K_RIGHT]:
            self.paddle_x += 8
        self.paddle_x = max(0, min(self.width - self.paddle_w, self.paddle_x))

    def update(self):
        self.ball_x += self.ball_vx
        self.ball_y += self.ball_vy

        # Rebotes paredes
        if self.ball_x <= self.ball_r or self.ball_x >= self.width - self.ball_r:
            self.ball_vx *= -1
        if self.ball_y <= self.ball_r:
            self.ball_vy *= -1

        # Paleta
        paddle = pygame.Rect(self.paddle_x, self.paddle_y, self.paddle_w, self.paddle_h)
        ball = pygame.Rect(self.ball_x - self.ball_r, self.ball_y - self.ball_r,
                           self.ball_r * 2, self.ball_r * 2)
        if ball.colliderect(paddle) and self.ball_vy > 0:
            self.ball_vy *= -1
            offset = (self.ball_x - (self.paddle_x + self.paddle_w / 2)) / (self.paddle_w / 2)
            self.ball_vx = self.ball_speed * offset

        # Ladrillos
        for brick in self.bricks[:]:
            if ball.colliderect(brick):
                self.bricks.remove(brick)
                self.ball_vy *= -1
                self.score += 10
                self.writer.log("ENEMY_KILL", {
                    "type": "brick",
                    "wave": self.level,
                })
                break

        # Bola cae
        if self.ball_y > self.height:
            self.lives -= 1
            self.writer.log("DAMAGE_TAKEN", {
                "amount": 1,
                "source": "fall",
            })
            if self.lives <= 0:
                self.writer.log("PLAYER_DEATH", {
                    "cause": "fall",
                    "level": self.level,
                })
                self.end_session("death")
                self.running = False
            else:
                self.reset_ball()

        # Siguiente nivel
        if not self.bricks:
            self.level += 1
            self.writer.log("LEVEL_UP", {
                "level": self.level,
                "time": round(time.time() - self.start_time, 1),
            })
            self.spawn_bricks()
            self.reset_ball()

    def end_session(self, result):
        if self.result is None:
            self.result = result
            self.writer.log("SESSION_END", {
                "score": self.score,
                "level": self.level,
                "duration": round(time.time() - self.start_time, 1),
                "result": result,
            })
            self.writer.close()

    def draw(self):
        self.screen.fill((20, 20, 30))
        pygame.draw.rect(self.screen, (200, 200, 200),
                         (self.paddle_x, self.paddle_y, self.paddle_w, self.paddle_h))
        pygame.draw.circle(self.screen, (255, 100, 100),
                           (int(self.ball_x), int(self.ball_y)), self.ball_r)
        for brick in self.bricks:
            pygame.draw.rect(self.screen, (100, 200, 255), brick)
        text = self.font.render(
            f"Score: {self.score}  Lives: {self.lives}  Level: {self.level}", True, (255, 255, 255)
        )
        self.screen.blit(text, (10, 10))
        pygame.display.flip()













