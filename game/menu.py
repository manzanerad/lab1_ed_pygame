import pygame


class MenuScreen:
    def __init__(self, app):
        self.app = app
        self.screen = app.screen
        self.font = app.font
        self.options = ["Start Game", "Statistics", "Settings", "Quit"]
        self.selected = 0

    def run(self):
        while True:
            dt = self.app.clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "quit"
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.selected = (self.selected - 1) % len(self.options)
                    elif event.key == pygame.K_DOWN:
                        self.selected = (self.selected + 1) % len(self.options)
                    elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        return self._select()

            self.draw()

    def _select(self):
        opt = self.options[self.selected]
        if opt == "Start Game":
            return "game"
        elif opt == "Statistics":
            return "stats"
        elif opt == "Settings":
            return "settings"
        elif opt == "Quit":
            return "quit"
        return "menu"

    def draw(self):
        self.screen.fill((20, 20, 30))
        title = self.font.render("BREAKOUT TELEMETRY", True, (255, 255, 255))
        self.screen.blit(title, (self.app.width // 2 - title.get_width() // 2, 80))

        for i, opt in enumerate(self.options):
            color = (255, 255, 0) if i == self.selected else (200, 200, 200)
            text = self.font.render(opt, True, color)
            y = 200 + i * 50
            self.screen.blit(text, (self.app.width // 2 - text.get_width() // 2, y))

        hint = self.app.small_font.render("Use UP/DOWN + ENTER", True, (150, 150, 150))
        self.screen.blit(hint, (self.app.width // 2 - hint.get_width() // 2, self.app.height - 60))
        pygame.display.flip()
