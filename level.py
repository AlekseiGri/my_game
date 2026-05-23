from pathlib import Path
from typing import TYPE_CHECKING

import pygame

from assets import get_flag_sprite, get_tile_sprite
from settings import TILE_SIZE

if TYPE_CHECKING:
    from camera import Camera


class Level:
    def __init__(self, path: str | Path) -> None:
        self.tiles: list[pygame.Rect] = []
        self.player_start: tuple[int, int] = (0, 0)
        self.enemy_starts: list[tuple[int, int]] = []
        self.coin_starts: list[tuple[int, int]] = []
        self.finish: pygame.Rect | None = None
        self.width: int = 0
        self.height: int = 0
        self._tile_sprite = get_tile_sprite()
        self._flag_sprite = get_flag_sprite()
        self._load(Path(path))

    def _load(self, path: Path) -> None:
        with path.open(encoding="utf-8") as f:
            rows = [line.rstrip("\n") for line in f]

        self.width = (max(len(r) for r in rows) if rows else 0) * TILE_SIZE
        self.height = len(rows) * TILE_SIZE

        for y, row in enumerate(rows):
            for x, ch in enumerate(row):
                px = x * TILE_SIZE
                py = y * TILE_SIZE
                if ch == "#":
                    self.tiles.append(pygame.Rect(px, py, TILE_SIZE, TILE_SIZE))
                elif ch == "P":
                    self.player_start = (px, py)
                elif ch == "E":
                    self.enemy_starts.append((px, py))
                elif ch == "C":
                    self.coin_starts.append((px, py))
                elif ch == "F":
                    self.finish = pygame.Rect(px, py, TILE_SIZE, TILE_SIZE)

    def draw(self, surface: pygame.Surface, camera: "Camera") -> None:
        for rect in self.tiles:
            surface.blit(self._tile_sprite, camera.apply(rect))
        if self.finish is not None:
            surface.blit(self._flag_sprite, camera.apply(self.finish))
