from typing import TYPE_CHECKING

import pygame

from assets import get_enemy_sprite
from settings import ENEMY_SIZE, ENEMY_SPEED, GRAVITY

if TYPE_CHECKING:
    from camera import Camera


class Enemy:
    def __init__(self, x: int, y: int) -> None:
        self.rect = pygame.Rect(x, y, ENEMY_SIZE, ENEMY_SIZE)
        self.vel_x: int = ENEMY_SPEED
        self.vel_y: int = 0
        self.sprite = get_enemy_sprite()

    def update(self, tiles: list[pygame.Rect]) -> None:
        self.vel_y += GRAVITY

        self.rect.x += self.vel_x
        for tile in tiles:
            if not self.rect.colliderect(tile):
                continue
            if self.vel_x > 0:
                self.rect.right = tile.left
            elif self.vel_x < 0:
                self.rect.left = tile.right
            self.vel_x = -self.vel_x
            break

        on_ground = False
        self.rect.y += self.vel_y
        for tile in tiles:
            if not self.rect.colliderect(tile):
                continue
            if self.vel_y > 0:
                self.rect.bottom = tile.top
                on_ground = True
            elif self.vel_y < 0:
                self.rect.top = tile.bottom
            self.vel_y = 0

        if on_ground:
            probe_x = self.rect.right + 1 if self.vel_x > 0 else self.rect.left - 1
            probe = pygame.Rect(probe_x, self.rect.bottom + 1, 1, 1)
            if not any(probe.colliderect(t) for t in tiles):
                self.vel_x = -self.vel_x

    def draw(self, surface: pygame.Surface, camera: "Camera") -> None:
        surface.blit(self.sprite, camera.apply(self.rect))
