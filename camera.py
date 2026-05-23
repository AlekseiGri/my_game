import pygame

from settings import HEIGHT, WIDTH


class Camera:
    def __init__(self, level_width: int, level_height: int) -> None:
        self.offset = pygame.Vector2(0, 0)
        self.level_width = level_width
        self.level_height = level_height

    def update(self, target: pygame.Rect) -> None:
        self.offset.x = target.centerx - WIDTH // 2
        self.offset.y = target.centery - HEIGHT // 2

        max_x = max(0, self.level_width - WIDTH)
        max_y = max(0, self.level_height - HEIGHT)
        self.offset.x = max(0, min(self.offset.x, max_x))
        self.offset.y = max(0, min(self.offset.y, max_y))

    def apply(self, rect: pygame.Rect) -> pygame.Rect:
        return rect.move(-self.offset.x, -self.offset.y)
