import random
from pathlib import Path
from typing import TYPE_CHECKING

import pygame

from assets import get_flag_sprite, get_temp_tile_sprite, get_tile_sprite
from settings import TILE_SIZE

if TYPE_CHECKING:
    from camera import Camera


class TemporaryTile:
    STAND_THRESHOLD = 30
    GONE_DURATION = 180

    def __init__(self, x: int, y: int) -> None:
        self.rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
        self.state = "idle"
        self.stand_time = 0
        self.gone_timer = 0

    def is_solid(self) -> bool:
        return self.state != "gone"

    def reset(self) -> None:
        self.state = "idle"
        self.stand_time = 0
        self.gone_timer = 0

    def tick(self, player_standing: bool) -> bool:
        if self.state == "gone":
            self.gone_timer -= 1
            if self.gone_timer <= 0:
                self.reset()
            return False
        if player_standing:
            if self.state == "idle":
                self.state = "crumbling"
            self.stand_time += 1
            if self.stand_time >= self.STAND_THRESHOLD:
                self.state = "gone"
                self.gone_timer = self.GONE_DURATION
                return True
        elif self.state == "crumbling":
            self.stand_time -= 1
            if self.stand_time <= 0:
                self.reset()
        return False

    def draw(self, surface: pygame.Surface, camera: "Camera", sprite: pygame.Surface) -> None:
        if self.state == "gone":
            return
        pos = camera.apply(self.rect)
        if self.state == "crumbling":
            dx = random.randint(-2, 2)
            pos = pos.move(dx, 0)
        surface.blit(sprite, pos)


class Level:
    def __init__(self, path: str | Path) -> None:
        self.tiles: list[pygame.Rect] = []
        self.temp_tiles: list[TemporaryTile] = []
        self.player_start: tuple[int, int] = (0, 0)
        self.enemy_starts: list[tuple[int, int]] = []
        self.coin_starts: list[tuple[int, int]] = []
        self.heart_starts: list[tuple[int, int]] = []
        self.finish: pygame.Rect | None = None
        self.width: int = 0
        self.height: int = 0
        self._tile_sprite = get_tile_sprite()
        self._temp_tile_sprite = get_temp_tile_sprite()
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
                elif ch == "H":
                    self.heart_starts.append((px, py))
                elif ch == "F":
                    self.finish = pygame.Rect(px, py, TILE_SIZE, TILE_SIZE)
                elif ch == "T":
                    self.temp_tiles.append(TemporaryTile(px, py))

    @property
    def solid_tiles(self) -> list[pygame.Rect]:
        return self.tiles + [t.rect for t in self.temp_tiles if t.is_solid()]

    def reset_temp_tiles(self) -> None:
        for t in self.temp_tiles:
            t.reset()

    def draw(self, surface: pygame.Surface, camera: "Camera") -> None:
        for rect in self.tiles:
            surface.blit(self._tile_sprite, camera.apply(rect))
        for t in self.temp_tiles:
            t.draw(surface, camera, self._temp_tile_sprite)
        if self.finish is not None:
            surface.blit(self._flag_sprite, camera.apply(self.finish))
