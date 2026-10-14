import pygame


class App:
    def __init__(self, cfg):
        pygame.init()
        self.cfg = cfg
        self.width = cfg["screen_width"]
        self.height = cfg["screen_height"]
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Breakout Telemetry")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("monospace", 24)
        self.small_font = pygame.font.SysFont("monospace", 16)

    def run_screen(self, screen_obj):
        return screen_obj.run()
