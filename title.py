import random

import pygame

from settings import HEIGHT, WIDTH


class Cloud:
    def __init__(self, x: float, y: int, speed: float, sprite: pygame.Surface) -> None:
        self.x = x
        self.y = y
        self.speed = speed
        self.sprite = sprite

    def update(self) -> None:
        self.x += self.speed
        if self.x > WIDTH:
            self.x = -self.sprite.get_width()

    def draw(self, surface: pygame.Surface) -> None:
        surface.blit(self.sprite, (int(self.x), self.y))


def make_title_sky() -> pygame.Surface:
    surface = pygame.Surface((WIDTH, HEIGHT))
    top = (80, 150, 220)
    bottom = (200, 230, 250)
    for y in range(HEIGHT):
        t = y / max(HEIGHT - 1, 1)
        color = (
            int(top[0] + (bottom[0] - top[0]) * t),
            int(top[1] + (bottom[1] - top[1]) * t),
            int(top[2] + (bottom[2] - top[2]) * t),
        )
        pygame.draw.line(surface, color, (0, y), (WIDTH, y))
    return surface


def _make_cloud_sprite(scale: float) -> pygame.Surface:
    w = int(140 * scale)
    h = int(64 * scale)
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    color = (255, 255, 255, 235)
    blobs = [
        (0, h * 1 // 3, w * 5 // 8, h * 2 // 3),
        (w * 1 // 4, 0, w * 1 // 2, h * 2 // 3),
        (w * 2 // 5, h * 1 // 4, w * 3 // 5, h * 3 // 4),
        (w * 1 // 8, h * 1 // 3, w * 5 // 8, h * 2 // 3),
    ]
    for x, y, ew, eh in blobs:
        pygame.draw.ellipse(surf, color, (x, y, ew, eh))
    return surf


def make_title_clouds() -> list[Cloud]:
    configs = [
        (0.7, 0.35),
        (1.0, 0.55),
        (1.4, 0.30),
        (0.8, 0.50),
        (1.2, 0.40),
    ]
    clouds: list[Cloud] = []
    for scale, speed in configs:
        sprite = _make_cloud_sprite(scale)
        x = random.uniform(0, WIDTH)
        y = random.randint(40, HEIGHT // 2 - 20)
        clouds.append(Cloud(x, y, speed, sprite))
    return clouds
