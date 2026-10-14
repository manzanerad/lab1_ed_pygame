import pygame
from game.app import App
from game.menu import MenuScreen
from game.breakout import Breakout
from game.statsscreen import StatsScreen
from game.settingsscreen import SettingsScreen
from game.settings import load_config


def main():
    cfg = load_config()
    app = App(cfg)

    screen_map = {
        "menu": lambda: MenuScreen(app),
        "game": lambda: Breakout(app.screen, app.clock, cfg),
        "stats": lambda: StatsScreen(app),
        "settings": lambda: SettingsScreen(app),
    }

    current = "menu"
    while current != "quit":
        screen = screen_map[current]()
        current = screen.run()

    pygame.quit()


if __name__ == "__main__":
    main()
