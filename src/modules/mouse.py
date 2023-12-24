from pygame.sprite import Sprite
from pygame.image import load
from pygame.math import Vector2


class Mouse(Sprite):
    def __init__(self, image: str) -> None:
        super().__init__()
        self.image = load(image).convert_alpha()
        self.rect = self.image.get_rect()
        self.pos = Vector2()

    def __str__(self) -> str:
        return f"POSITION: {self.rect.center}"

    def update(self) -> None:
        self.rect.center = Vector2(self.pos)
