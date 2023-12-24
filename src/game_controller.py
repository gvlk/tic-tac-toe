import pygame as pg
from src.modules.mouse import Mouse
from src.modules.debugger import Debugger


class GameController:

    def __init__(self, screen: pg.Surface, fps: int, mouse: Mouse, debugger: Debugger, debug_mode: bool) -> None:
        self.screen = screen
        self.mouse = mouse
        # noinspection PyTypeChecker
        self.mouse_group = pg.sprite.GroupSingle(self.mouse)

        self.clock = pg.time.Clock()
        self.fps = fps
        self.debugger = debugger
        self.debug_mode = debug_mode
        self.run = True

    def run_game(self) -> None:
        while self.run:
            self.handle_events()
            self.update_game_state()
            self.draw()
            if self.debug_mode:
                self.draw_debug_info()
            self.clock.tick(self.fps)
        pg.quit()

    def handle_events(self) -> None:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.run = False
            elif event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                self.run = False
            elif event.type == pg.MOUSEMOTION:
                self.handle_mouse_motion()

    def handle_mouse_motion(self) -> None:
        self.mouse.pos = pg.mouse.get_pos()
        self.mouse_group.update()

    def update_game_state(self) -> None:
        pg.display.update()

    def draw(self) -> None:
        self.screen.fill(pg.Color('white'))
        self.mouse_group.draw(self.screen)

    def draw_debug_info(self) -> None:
        self.debugger.display_information(
            f"WINDOW: {pg.display.get_window_size()}",
            f"FPS: {int(self.clock.get_fps())}",
            f"MOUSE: {self.mouse}"
        )
