from typing import TYPE_CHECKING

import pygame

from assets import get_coin_frames
from settings import COIN_ANIM_FRAME_DURATION, COIN_SIZE, TILE_SIZE

if TYPE_CHECKING:
    from camera import Camera


class CoinPickupEffect:
    LIFETIME = 20
    RISE_SPEED = 2
    GROWTH = 1.6

    def __init__(self, cx: int, cy: int, source: pygame.Surface) -> None:
        self.cx = cx
        self.cy = cy
        self.source = source
        self.timer = 0

    def update(self) -> None:
        self.timer += 1
        self.cy -= self.RISE_SPEED

    @property
    def alive(self) -> bool:
        return self.timer < self.LIFETIME

    def draw(self, surface: pygame.Surface, camera: "Camera") -> None:
        t = self.timer / self.LIFETIME
        scale = 1 + (self.GROWTH - 1) * t
        alpha = int(255 * (1 - t))
        w = max(1, int(self.source.get_width() * scale))
        h = max(1, int(self.source.get_height() * scale))
        sprite = pygame.transform.scale(self.source, (w, h))
        sprite.set_alpha(alpha)
        rect = pygame.Rect(0, 0, w, h)
        rect.center = (self.cx, self.cy)
        surface.blit(sprite, camera.apply(rect))


class Coin:
    def __init__(self, x: int, y: int) -> None:
        offset = (TILE_SIZE - COIN_SIZE) // 2
        self.rect = pygame.Rect(x + offset, y + offset, COIN_SIZE, COIN_SIZE)
        self.frames = get_coin_frames()
        self.frame_idx = 0
        self.frame_timer = 0

    def update(self) -> None:
        self.frame_timer += 1
        if self.frame_timer >= COIN_ANIM_FRAME_DURATION:
            self.frame_timer = 0
            self.frame_idx = (self.frame_idx + 1) % len(self.frames)

    def draw(self, surface: pygame.Surface, camera: "Camera") -> None:
        sprite = self.frames[self.frame_idx]
        screen_pos = camera.apply(self.rect)
        offset_x = (self.rect.width - sprite.get_width()) // 2
        offset_y = (self.rect.height - sprite.get_height()) // 2
        surface.blit(sprite, (screen_pos.x + offset_x, screen_pos.y + offset_y))
