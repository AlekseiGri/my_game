from typing import TYPE_CHECKING

import pygame

from assets import get_heart_frames
from settings import HEART_ANIM_FRAME_DURATION, HEART_SIZE, TILE_SIZE

if TYPE_CHECKING:
    from camera import Camera


class Heart:
    def __init__(self, x: int, y: int) -> None:
        offset = (TILE_SIZE - HEART_SIZE) // 2
        self.rect = pygame.Rect(x + offset, y + offset, HEART_SIZE, HEART_SIZE)
        self.frames = get_heart_frames()
        self.frame_idx = 0
        self.frame_timer = 0

    def update(self) -> None:
        self.frame_timer += 1
        if self.frame_timer >= HEART_ANIM_FRAME_DURATION:
            self.frame_timer = 0
            self.frame_idx = (self.frame_idx + 1) % len(self.frames)

    def draw(self, surface: pygame.Surface, camera: "Camera") -> None:
        surface.blit(self.frames[self.frame_idx], camera.apply(self.rect))
