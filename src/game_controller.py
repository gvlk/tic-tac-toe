from typing import Optional, List, Set, Tuple

import pygame as pg
import pygame.freetype

from src.modules.debugger import Debugger
from src.modules.mouse import Mouse
from src.modules.mark import Mark


class GameController:
    EMPTY_CELL: str = "0"
    TIE_CONDITION: str = "3"
    P1_MARK: str = "1"
    P2_MARK: str = "2"
    P1_WIN_CONDITIONS: Set[str] = {
        "111000000",
        "000111000",
        "000000111",
        "100100100",
        "010010010",
        "001001001",
        "100010001",
        "001010100"
    }
    P2_WIN_CONDITIONS: Set[str] = set((condition.replace("1", "2") for condition in P1_WIN_CONDITIONS))

    def __init__(
            self,
            screen: pg.Surface,
            fps: int,
            mouse: Mouse,
            font: pg.freetype.Font,
            debugger: Debugger,
            debug_mode: bool
    ) -> None:
        self.screen: pg.Surface = screen
        self.mouse: Mouse = mouse
        # noinspection PyTypeChecker
        self.mouse_group: pg.sprite.GroupSingle[Mouse] = pg.sprite.GroupSingle(self.mouse)
        self.font: pg.freetype.Font = font

        self.clock: pg.time.Clock = pg.time.Clock()
        self.fps: int = fps
        self.debugger: Debugger = debugger
        self.debug_mode: bool = debug_mode

        self.grid_rects: List[pg.Rect] = self.generate_grid_rects()

        # TODO: Make a module to deal with image files like the background. The other parts should request the file
        #  to this module to get it.

        self.bg_surf, self.bg_rect = self.generate_background()
        self.marks = pg.sprite.Group()

        self.p1_win_conditions: Set[str] = self.P1_WIN_CONDITIONS.copy()
        self.p2_win_conditions: Set[str] = self.P2_WIN_CONDITIONS.copy()
        self.impossible_conditions: Set[str] = set()
        self.turn: int = 1
        self.turn_player: str = self.P1_MARK
        self.game_state: str = self.EMPTY_CELL * 9
        self.finished: bool = False
        self.winner: str = self.EMPTY_CELL

        self.turn_text, self.turn_text_rect = self.generate_turn_message()
        (
            self.finished_text,
            self.finished_text_rect,
            self.reset_text,
            self.reset_text_rect
        ) = self.generate_winner_message()

        self.run: bool = True

    def run_game(self) -> None:
        """
        Main game loop. Runs until the game is closed or exited.
        """
        while self.run:
            self.handle_events()
            self.update_game_state()
            self.draw()
            if self.debug_mode:
                self.draw_debug()
            self.clock.tick(self.fps)
        pg.quit()

    def handle_events(self) -> None:
        """
        Handle pygame events, such as key presses and mouse movements.
        """
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.run = False

            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.run = False
                elif event.key == pg.K_r:
                    self.reset_game()
                elif event.key == pg.K_d:
                    self.debug_mode = not self.debug_mode

            elif event.type == pg.MOUSEMOTION:
                self.handle_mouse_motion()

            elif event.type == pg.MOUSEBUTTONDOWN:
                if pg.mouse.get_pressed(3)[0]:
                    self.handle_mouse_press()

    def handle_mouse_motion(self) -> None:
        """
        Update the mouse position and mouse sprite during mouse motion.
        """
        self.mouse.pos = pg.mouse.get_pos()
        self.mouse_group.update()

    def handle_mouse_press(self) -> None:
        """
        Handle mouse clicks and update game state accordingly.
        """
        if not self.finished:
            clicked_cell = self.get_clicked_cell()
            if clicked_cell is not None:
                self.turn += 1
                self.game_state = self.game_state[:clicked_cell] + self.turn_player + self.game_state[clicked_cell + 1:]
                self.add_mark_sprite(clicked_cell)
                self.switch_turn()
                self.winner = self.check_win()
                if self.winner != self.EMPTY_CELL:
                    self.finish_game()

    def add_mark_sprite(self, clicked_cell: int) -> None:
        """
        Add a mark sprite to the group based on the clicked cell.
        :param clicked_cell: The index of the clicked cell.
        """
        mark_position = self.grid_rects[clicked_cell].center
        mark_size = tuple((int(x * 0.8) for x in self.grid_rects[clicked_cell].size))
        # noinspection PyTypeChecker
        self.marks.add(Mark(self.turn_player, mark_position, mark_size))

    def finish_game(self) -> None:
        """
        Update the finished state and messages when there is a winner.
        """
        self.finished = True
        (
            self.finished_text,
            self.finished_text_rect,
            self.reset_text,
            self.reset_text_rect
        ) = self.generate_winner_message()

    def get_clicked_cell(self) -> Optional[int]:
        """
        Determine the index of the clicked cell on the game grid.
        :return: Optional[int]: Index of the clicked cell or None if no cell is clicked.
        """
        for i, grid_rect in enumerate(self.grid_rects):
            if grid_rect.collidepoint(self.mouse.pos[0], self.mouse.pos[1]) and self.game_state[i] == self.EMPTY_CELL:
                return i
        return None

    def switch_turn(self) -> None:
        """
        Switch the turn between players.
        """
        self.turn_player = self.P2_MARK if self.turn_player == self.P1_MARK else self.P1_MARK
        self.turn_text, self.turn_text_rect = self.generate_turn_message()

    @staticmethod
    def update_game_state() -> None:
        """
        Update the game state and display.
        """
        pg.display.update()

    def draw(self) -> None:
        """
        Draw the game grid, player marks, and additional messages on the screen.
        """
        self.screen.blit(self.bg_surf, self.bg_rect)

        # # Create a transparent surface with the same size as the screen
        # transparent_surface = pg.Surface(self.screen.get_size(), pg.SRCALPHA)
        # transparent_surface.fill((0, 0, 0, 0))  # Fills the surface with transparent black
        # for grid_rect in self.grid_rects:
        #     pg.draw.rect(transparent_surface, pg.Color(0, 255, 0, 128),
        #                  grid_rect)  # 128 is the alpha value for 50% transparency
        # self.screen.blit(transparent_surface, (0, 0))  # Blit the transparent surface onto the screen

        self.marks.draw(self.screen)

        if self.finished:
            self.screen.blit(self.finished_text, self.finished_text_rect)
            self.screen.blit(self.reset_text, self.reset_text_rect)
        else:
            self.screen.blit(self.turn_text, self.turn_text_rect)

        self.mouse_group.draw(self.screen)

    def draw_debug(self) -> None:
        """
        Draw debugging information on the screen during debug mode.
        """
        self.debugger.display_information(
            f"WINDOW: {pg.display.get_window_size()}",
            f"FPS: {int(self.clock.get_fps())}",
            f"MOUSE: {self.mouse}",
            f"GAME_STATE: {self.game_state}",
            f"TURN: {self.turn}",
            f"TURN_PLAYER: {self.turn_player}",
            f"P1_WIN_CONDITIONS: {self.p1_win_conditions}",
            f"P2_WIN_CONDITIONS: {self.p2_win_conditions}",
            f"IMPOSSIBLE_CONDITIONS: {self.impossible_conditions}",
            f"SELF.WINNER: {self.winner}"
        )

    def check_win(self) -> str:
        """
        Check if the current game state results in a win for player 1, player 2, or if it's a tie.
        :return: str: "1" if player 1 wins, "2" if player 2 wins, "3" for a tie, "0" if the game continues.
        """

        def check_player_win(win_conditions: set, p1_mark: str, p2_mark: str) -> bool:
            for condition in win_conditions:
                p_win = True
                for i, cell in enumerate(self.game_state):
                    if condition[i] == p1_mark:
                        if cell == p2_mark:
                            p_win = False
                            self.impossible_conditions.add(condition)
                            break
                        elif cell == self.EMPTY_CELL:
                            p_win = False
                if p_win:
                    return True
            win_conditions -= self.impossible_conditions
            return False

        if check_player_win(self.p1_win_conditions, self.P1_MARK, self.P2_MARK):
            return self.P1_MARK
        elif check_player_win(self.p2_win_conditions, self.P2_MARK, self.P1_MARK):
            return self.P2_MARK
        elif self.turn == 10:
            return self.TIE_CONDITION
        return self.EMPTY_CELL

    def reset_game(self) -> None:
        """
        Reset the game state and conditions for a new game.
        """
        self.marks.empty()
        self.p1_win_conditions = self.P1_WIN_CONDITIONS.copy()
        self.p2_win_conditions = self.P2_WIN_CONDITIONS.copy()
        self.impossible_conditions = set()
        self.turn = 1
        self.turn_player = self.P1_MARK
        self.game_state = self.EMPTY_CELL * 9
        self.finished = False
        self.winner = self.EMPTY_CELL

    def generate_grid_rects(self) -> List[pg.Rect]:
        """
        Generate and return the list of Rect objects representing the game grid cells.
        :return: List[pg.Rect]: List of Rect objects.
        """
        screen_width = self.screen.get_width()
        screen_height = self.screen.get_height()

        rects = list()
        square_size = screen_width // 8
        margin = square_size // 15

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

    def generate_background(self) -> Tuple[pg.Surface, pg.Rect]:
        """
        Load and resize the background image to maintain its aspect ratio and fill the screen.
        :return: Tuple[pg.Surface, pg.Rect]: A tuple containing the resized background surface and its rectangle.
        """
        original_bg_surf = pg.image.load("src/assets/imgs/bg.png")
        aspect_ratio = original_bg_surf.get_width() / original_bg_surf.get_height()

        new_width = self.screen.get_width()
        new_height = int(new_width / aspect_ratio)

        bg_surf = pg.transform.scale(original_bg_surf, (new_width, new_height))
        bg_rect = bg_surf.get_rect()
        bg_rect.center = (self.screen.get_width() // 2, self.screen.get_height() // 2)

        return bg_surf, bg_rect

    def generate_turn_message(self) -> Tuple[pg.Surface, pg.Rect]:
        turn_message_pos = (self.screen.get_width() // 2, self.screen.get_height() // 7)
        turn_text = self.font.render(f"Player {self.turn_player}'s Turn", pg.Color("black"), size=24)[0]
        turn_text_rect = turn_text.get_rect(midbottom=turn_message_pos)

        return turn_text, turn_text_rect

    def generate_winner_message(self) -> Tuple[pg.Surface, pg.Rect, pg.Surface, pg.Rect]:
        """
        Generate surfaces and rectangles for the winner and reset messages.
        :return Tuple[pg.Surface, pg.Rect, pg.Surface, pg.Rect]: A tuple containing the background surface, text rect...
        The winner message is displayed in the center of the screen, and the reset message is positioned below it.
        Both messages have a white background for better readability.
        """
        def generate_message_surface(message: str) -> Tuple[pg.Surface, pg.Rect]:
            """
            Generate a surface and rectangle for a given message.
            :param message: The message to be displayed.
            :return Tuple[pg.Surface, pg.Rect]: A tuple containing the background surface and text rectangle.
            The message surface has a white background for better readability.
            """
            text_surface, text_rect = self.font.render(message, pg.Color("black"))
            message_surface = pg.Surface((text_rect.width + 30, text_rect.height + 30))
            message_surface.fill(pg.Color("white"))
            text_position = ((message_surface.get_width() - text_surface.get_width()) // 2,
                             (message_surface.get_height() - text_surface.get_height()) // 2)
            message_surface.blit(text_surface, text_position)
            message_rect = message_surface.get_rect()

            return message_surface, message_rect

        if self.winner in (self.P1_MARK, self.P2_MARK):
            text = f"Player {self.winner} wins!"
        else:
            text = "It's a tie!"

        finished_background_surface, finished_text_rect = generate_message_surface(text)
        finished_text_rect.center = (self.screen.get_width() // 2, self.screen.get_height() // 2)

        reset_background_surface, reset_text_rect = generate_message_surface("Press 'r' to reset")
        reset_text_rect.center = (self.screen.get_width() // 2, finished_text_rect.bottom + 20)

        return finished_background_surface, finished_text_rect, reset_background_surface, reset_text_rect
