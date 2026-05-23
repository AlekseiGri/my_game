"""Asset loading with graceful fallback to generated surfaces and silent sounds.

Drop your own files into these locations to override the fallbacks
(any size — sprites are scaled to the target size):

    assets/sprites/player.png
    assets/sprites/enemy.png
    assets/sprites/tile.png
    assets/sprites/coin.png
    assets/sprites/flag.png

    assets/sounds/jump.wav
    assets/sounds/coin.wav
    assets/sounds/death.wav
    assets/sounds/win.wav
"""

from functools import lru_cache
from pathlib import Path
from typing import Callable

import pygame

from settings import (
    COIN_COLOR,
    COIN_SIZE,
    ENEMY_COLOR,
    ENEMY_SIZE,
    PLAYER_COLOR,
    PLAYER_SIZE,
    TILE_COLOR,
    TILE_SIZE,
)

ASSETS_DIR = Path(__file__).parent / "assets"
SPRITES_DIR = ASSETS_DIR / "sprites"
SOUNDS_DIR = ASSETS_DIR / "sounds"


def _load_image_or_fallback(
    filename: str,
    size: tuple[int, int],
    fallback: Callable[[], pygame.Surface],
) -> pygame.Surface:
    path = SPRITES_DIR / filename
    if path.exists():
        try:
            img = pygame.image.load(str(path)).convert_alpha()
            return pygame.transform.scale(img, size)
        except pygame.error:
            pass
    return fallback()


def _make_player_fallback() -> pygame.Surface:
    s = pygame.Surface((PLAYER_SIZE, PLAYER_SIZE), pygame.SRCALPHA)
    s.fill(PLAYER_COLOR)
    pygame.draw.rect(s, (0, 0, 0), s.get_rect(), 1)
    eye_y = PLAYER_SIZE // 3
    pygame.draw.circle(s, (255, 255, 255), (PLAYER_SIZE * 2 // 3, eye_y), 4)
    pygame.draw.circle(s, (0, 0, 0), (PLAYER_SIZE * 2 // 3, eye_y), 2)
    return s


def _make_enemy_fallback() -> pygame.Surface:
    s = pygame.Surface((ENEMY_SIZE, ENEMY_SIZE), pygame.SRCALPHA)
    s.fill(ENEMY_COLOR)
    pygame.draw.rect(s, (0, 0, 0), s.get_rect(), 1)
    pygame.draw.circle(s, (255, 255, 255), (ENEMY_SIZE // 3, ENEMY_SIZE // 2), 4)
    pygame.draw.circle(s, (255, 255, 255), (ENEMY_SIZE * 2 // 3, ENEMY_SIZE // 2), 4)
    pygame.draw.circle(s, (0, 0, 0), (ENEMY_SIZE // 3, ENEMY_SIZE // 2), 2)
    pygame.draw.circle(s, (0, 0, 0), (ENEMY_SIZE * 2 // 3, ENEMY_SIZE // 2), 2)
    return s


def _make_tile_fallback() -> pygame.Surface:
    s = pygame.Surface((TILE_SIZE, TILE_SIZE))
    s.fill(TILE_COLOR)
    pygame.draw.rect(s, (60, 140, 60), (0, TILE_SIZE * 3 // 4, TILE_SIZE, TILE_SIZE // 4))
    pygame.draw.rect(s, (0, 0, 0), s.get_rect(), 1)
    return s


def _make_coin_fallback() -> pygame.Surface:
    s = pygame.Surface((COIN_SIZE, COIN_SIZE), pygame.SRCALPHA)
    pygame.draw.ellipse(s, COIN_COLOR, s.get_rect())
    pygame.draw.ellipse(s, (200, 150, 0), s.get_rect(), 1)
    return s


def _make_flag_fallback() -> pygame.Surface:
    s = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
    pole_x = TILE_SIZE // 4
    pygame.draw.rect(s, (200, 200, 200), (pole_x, 0, 3, TILE_SIZE))
    points = [
        (pole_x + 3, TILE_SIZE // 8),
        (pole_x + 3 + TILE_SIZE // 2, TILE_SIZE // 4),
        (pole_x + 3, TILE_SIZE * 3 // 8),
    ]
    pygame.draw.polygon(s, (220, 50, 50), points)
    return s


@lru_cache(maxsize=None)
def get_player_sprite() -> pygame.Surface:
    return _load_image_or_fallback("player.png", (PLAYER_SIZE, PLAYER_SIZE), _make_player_fallback)


@lru_cache(maxsize=None)
def get_enemy_sprite() -> pygame.Surface:
    return _load_image_or_fallback("enemy.png", (ENEMY_SIZE, ENEMY_SIZE), _make_enemy_fallback)


@lru_cache(maxsize=None)
def get_tile_sprite() -> pygame.Surface:
    return _load_image_or_fallback("tile.png", (TILE_SIZE, TILE_SIZE), _make_tile_fallback)


@lru_cache(maxsize=None)
def get_coin_sprite() -> pygame.Surface:
    return _load_image_or_fallback("coin.png", (COIN_SIZE, COIN_SIZE), _make_coin_fallback)


@lru_cache(maxsize=None)
def get_flag_sprite() -> pygame.Surface:
    return _load_image_or_fallback("flag.png", (TILE_SIZE, TILE_SIZE), _make_flag_fallback)


def load_sound(filename: str) -> pygame.mixer.Sound | None:
    path = SOUNDS_DIR / filename
    if not path.exists():
        return None
    try:
        return pygame.mixer.Sound(str(path))
    except pygame.error:
        return None


def play_sound(sound: pygame.mixer.Sound | None) -> None:
    if sound is not None:
        sound.play()
