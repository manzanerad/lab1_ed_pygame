import pygame
from game.settings import load_config
from game.breakout import Breakout


def main():
    pygame.init()
    cfg = load_config()
    game = Breakout(cfg)
    game.run()
    pygame.quit()


if __name__ == "__main__":
    main()
