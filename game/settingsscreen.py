import pygame
from game.settings import save_config


class SettingsScreen:
    OPTIONS = ["player", "volume", "difficulty"]
    DIFFICULTIES = ["easy", "normal", "hard"]

    def __init__(self, app):
        self.app = app
        self.screen = app.screen
        self.font = app.font
        self.selected = 0
        self.editing = False
        self.temp_value = ""

    def run(self):
        while True:
            self.app.clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    save_config(self.app.cfg)
                    return "quit"
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        save_config(self.app.cfg)
                        return "menu"
                    elif event.key == pygame.K_UP and not self.editing:
                        self.selected = (self.selected - 1) % len(self.OPTIONS)
                    elif event.key == pygame.K_DOWN and not self.editing:
                        self.selected = (self.selected + 1) % len(self.OPTIONS)
                    elif event.key == pygame.K_RETURN:
                        self._toggle_edit()
                    elif event.key == pygame.K_BACKSPACE and self.editing:
                        self.temp_value = self.temp_value[:-1]
                    elif self.editing and event.unicode.isprintable():
                        self.temp_value += event.unicode
                    elif event.key == pygame.K_LEFT and not self.editing:
                        self._cycle_difficulty(-1)
                    elif event.key == pygame.K_RIGHT and not self.editing:
                        self._cycle_difficulty(1)

            self.draw()

    def _toggle_edit(self):
        key = self.OPTIONS[self.selected]
        if key == "difficulty":
            return

        if not self.editing:
            self.editing = True
            self.temp_value = str(self.app.cfg[key])
        else:
            try:
                if key == "volume":
                    self.app.cfg[key] = max(0, min(100, int(self.temp_value)))
                elif key == "player":
                    self.app.cfg[key] = self.temp_value.strip() or "player"
            except ValueError:
                pass
            self.editing = False
            self.temp_value = ""

    def _cycle_difficulty(self, direction):
        if self.OPTIONS[self.selected] != "difficulty":
            return
        current = self.app.cfg["difficulty"]
        idx = self.DIFFICULTIES.index(current)
        new_idx = (idx + direction) % len(self.DIFFICULTIES)
        self.app.cfg["difficulty"] = self.DIFFICULTIES[new_idx]

    def draw(self):
        self.screen.fill((20, 20, 30))
        title = self.font.render("SETTINGS", True, (255, 255, 255))
        self.screen.blit(title, (self.app.width // 2 - title.get_width() // 2, 80))

        for i, key in enumerate(self.OPTIONS):
            label = key.capitalize()
            value = str(self.app.cfg[key])
            if self.editing and i == self.selected:
                value = self.temp_value + "_"
            color = (255, 255, 0) if i == self.selected else (200, 200, 200)
            line = f"{label}: {value}"
            text = self.font.render(line, True, color)
            y = 180 + i * 50
            self.screen.blit(text, (self.app.width // 2 - text.get_width() // 2, y))

        hint = self.app.small_font.render(
            "UP/DOWN select | ENTER edit | ESC save & back", True, (150, 150, 150)
        )
        self.screen.blit(hint, (self.app.width // 2 - hint.get_width() // 2, self.app.height - 60))
        pygame.display.flip()
