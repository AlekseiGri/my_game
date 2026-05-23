from typing import TYPE_CHECKING

import pygame

from assets import get_coin_sprite
from settings import COIN_SIZE, TILE_SIZE

if TYPE_CHECKING:
    from camera import Camera


class Coin:
    def __init__(self, x: int, y: int) -> None:
        offset = (TILE_SIZE - COIN_SIZE) // 2
        self.rect = pygame.Rect(x + offset, y + offset, COIN_SIZE, COIN_SIZE)
        self.sprite = get_coin_sprite()

    def draw(self, surface: pygame.Surface, camera: "Camera") -> None:
        surface.blit(self.sprite, camera.apply(self.rect))
