from pygame.transform import scale
from pygame.image import load
from pygame.sprite import Sprite


class Mark(Sprite):
    def __init__(self, player: str, pos: tuple[int, int], size: tuple[int, int]) -> None:
        super().__init__()
        if player == "1":
            original_x_surf = load("src/assets/imgs/x.png")
            self.image = scale(original_x_surf, size).convert_alpha()
        else:
            original_o_surf = load("src/assets/imgs/o.png")
            self.image = scale(original_o_surf, size).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = pos

    def __str__(self) -> str:
        return f"POSITION: {self.rect.topleft}"
