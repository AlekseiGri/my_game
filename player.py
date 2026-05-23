from typing import TYPE_CHECKING

import pygame

from assets import get_player_sprite
from settings import (
    GRAVITY,
    JUMP_CUT_VELOCITY,
    JUMP_VELOCITY,
    PLAYER_SIZE,
    PLAYER_SPEED,
)

if TYPE_CHECKING:
    from camera import Camera


class Player:
    def __init__(self, x: int, y: int) -> None:
        self.rect = pygame.Rect(x, y, PLAYER_SIZE, PLAYER_SIZE)
        self.vel_x: int = 0
        self.vel_y: int = 0
        self.on_ground: bool = False
        self.sprite = get_player_sprite()

    def handle_input(self, keys) -> None:
        self.vel_x = 0
        if keys[pygame.K_LEFT]:
            self.vel_x = -PLAYER_SPEED
        if keys[pygame.K_RIGHT]:
            self.vel_x = PLAYER_SPEED

    def respawn(self, x: int, y: int) -> None:
        self.rect.topleft = (x, y)
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False

    def jump(self) -> bool:
        if self.on_ground:
            self.vel_y = JUMP_VELOCITY
            self.on_ground = False
            return True
        return False

    def cut_jump(self) -> None:
        if self.vel_y < JUMP_CUT_VELOCITY:
            self.vel_y = JUMP_CUT_VELOCITY

    def update(self, tiles: list[pygame.Rect]) -> None:
        self.vel_y += GRAVITY

        self.rect.x += self.vel_x
        self._collide_x(tiles)

        self.on_ground = False
        self.rect.y += self.vel_y
        self._collide_y(tiles)

    def _collide_x(self, tiles: list[pygame.Rect]) -> None:
        for tile in tiles:
            if not self.rect.colliderect(tile):
                continue
            if self.vel_x > 0:
                self.rect.right = tile.left
            elif self.vel_x < 0:
                self.rect.left = tile.right

    def _collide_y(self, tiles: list[pygame.Rect]) -> None:
        for tile in tiles:
            if not self.rect.colliderect(tile):
                continue
            if self.vel_y > 0:
                self.rect.bottom = tile.top
                self.on_ground = True
            elif self.vel_y < 0:
                self.rect.top = tile.bottom
            self.vel_y = 0

    def draw(self, surface: pygame.Surface, camera: "Camera") -> None:
        surface.blit(self.sprite, camera.apply(self.rect))
