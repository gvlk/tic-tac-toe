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

        self.grid_rects = self.generate_grid_rects()

        # TODO: Make a module to deal with image files like the background. The other parts should request the file
        #  to this module to get it.

        # original_bg_surf = pg.image.load("src/assets/imgs/grid.png")
        # self.bg_surf = pg.transform.scale(original_bg_surf, (screen.get_width(), screen.get_height()))
        # self.bg_rect = self.bg_surf.get_rect()
        original_x_surf = pg.image.load("src/assets/imgs/x.png")
        original_o_surf = pg.image.load("src/assets/imgs/o.png")
        self.x_surf = pg.transform.scale(original_x_surf, self.grid_rects[0].size)
        self.o_surf = pg.transform.scale(original_o_surf, self.grid_rects[0].size)
        self.x_rect = self.x_surf.get_rect()
        self.o_rect = self.o_surf.get_rect()

        self.turn_player = "1"
        self.game_state = "000000000"

        self.run = True

    def run_game(self) -> None:
        while self.run:
            self.handle_events()
            self.update_game_state()
            self.draw()
            if self.debug_mode:
                self.draw_debug()
            self.clock.tick(self.fps)
        pg.quit()

    def handle_events(self) -> None:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.run = False

            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.run = False

            elif event.type == pg.MOUSEMOTION:
                self.handle_mouse_motion()

            elif event.type == pg.MOUSEBUTTONDOWN:
                mouse_buttons = pg.mouse.get_pressed(3)
                if mouse_buttons[0]:
                    self.handle_mouse_press()

    def handle_mouse_motion(self) -> None:
        self.mouse.pos = pg.mouse.get_pos()
        self.mouse_group.update()

    def handle_mouse_press(self) -> None:
        for i, grid_rect in enumerate(self.grid_rects):
            if grid_rect.collidepoint(self.mouse.pos[0], self.mouse.pos[1]) and self.game_state[i] == "0":
                self.game_state = self.game_state[:i] + self.turn_player + self.game_state[i + 1:]
                self.turn_player = "2" if self.turn_player == "1" else "1"

    def update_game_state(self) -> None:
        pg.display.update()

    def draw(self) -> None:
        # self.screen.blit(self.bg_surf, self.bg_rect)
        self.screen.fill("white")
        for grid_rect in self.grid_rects:
            pg.draw.rect(self.screen, pg.Color("green"), grid_rect)
        for i, grid_pos in enumerate(self.game_state):
            if grid_pos == "1":
                self.screen.blit(self.x_surf, self.grid_rects[i])
            elif grid_pos == "2":
                self.screen.blit(self.o_surf, self.grid_rects[i])

        self.mouse_group.draw(self.screen)

    def draw_debug(self) -> None:
        self.debugger.display_information(
            f"WINDOW: {pg.display.get_window_size()}",
            f"FPS: {int(self.clock.get_fps())}",
            f"MOUSE: {self.mouse}",
            f"GAME_STATE: {self.game_state}",
            f"TURN_PLAYER: {self.turn_player}"
        )

    def generate_grid_rects(self) -> list[pg.Rect]:
        screen_width = self.screen.get_width()
        screen_height = self.screen.get_height()

        rects = list()
        square_size = screen_height // 8
        margin = square_size // 5

        grid_width = 3 * (square_size + margin) - margin
        grid_height = 3 * (square_size + margin) - margin

        start_x = (screen_width - grid_width) // 2
        start_y = (screen_height - grid_height) // 2

        for row in range(3):
            for col in range(3):
                x = start_x + col * (square_size + margin)
                y = start_y + row * (square_size + margin)
                rects.append(pg.Rect(x, y, square_size, square_size))

        return rects
