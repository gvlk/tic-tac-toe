# https://github.com/gvlk
# leia o README.md

import pygame as pg
from pygame import freetype
from argparse import ArgumentParser, Namespace

from settings import Settings
from src.game_controller import GameController
from src.modules.mouse import Mouse
from src.modules.debugger import Debugger


def main() -> None:
    args = parse_command_line_arguments()
    debug_mode = args.debug

    settings = Settings()
    screen, font = initialize_pygame(settings.WIDTH, settings.HEIGHT, settings.UI_FONT, settings.UI_FONT_SIZE)

    mouse = Mouse(settings.MOUSE_SPRITE)
    debugger = Debugger(settings.DEBUG_POS, settings.DEBUG_FONT, settings.DEBUG_FONT_SIZE)

    game_controller = GameController(screen, settings.FPS, mouse, font, debugger, debug_mode)
    game_controller.run_game()


def parse_command_line_arguments() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument('-d', '--debug', action='store_true', help='Activate debug mode')
    return parser.parse_args()


def initialize_pygame(width: int, height: int, font_path: str, font_size: int) -> tuple[pg.Surface, pg.freetype.Font]:
    pg.init()
    freetype.init()

    pg.display.set_caption("Tic Tac Toe")
    screen = pg.display.set_mode((width, height))

    font = pg.freetype.Font(font_path, font_size)

    pg.event.set_grab(False)
    pg.mouse.set_visible(False)

    return screen, font


if __name__ == "__main__":
    main()
