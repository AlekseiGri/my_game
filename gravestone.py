from typing import TYPE_CHECKING

import pygame

from assets import get_gravestone_sprite

if TYPE_CHECKING:
    from camera import Camera


class Gravestone:
    def __init__(self, x: int, y: int) -> None:
        self.sprite = get_gravestone_sprite()
        w, h = self.sprite.get_size()
        self.rect = pygame.Rect(x - w // 2, y - h, w, h)

    def draw(self, surface: pygame.Surface, camera: "Camera") -> None:
        surface.blit(self.sprite, camera.apply(self.rect))
