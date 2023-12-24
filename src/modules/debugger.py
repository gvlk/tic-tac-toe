from pygame import display, Color
from pygame.font import Font

from typing import Any


class Debugger:
    def __init__(self, pos: tuple, font: str, font_size: int) -> None:
        self.display_surf = display.get_surface()
        self.x, self.y = pos
        self.font = Font(font, font_size)

    def display_information(self, *infos: Any) -> None:
        for y, info in enumerate(infos):
            str_info = str(info)
            debug_surf = self.font.render(str_info, True, Color("White"), Color("Black"))
            debug_rect = debug_surf.get_rect(topleft=(self.x, self.y + (y * 20)))
            self.display_surf.blit(debug_surf, debug_rect)
