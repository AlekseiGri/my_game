"""Asset loading with graceful fallback to generated surfaces and silent sounds.

Drop your own files into these locations to override the fallbacks
(any size — sprites are scaled to the target size):

    assets/sprites/player.png
    assets/sprites/enemy_right.png
    assets/sprites/enemy_left.png
    assets/sprites/tile.png
    assets/sprites/temp_tile.png    (crumbling tile used for 'T' in level files)
    assets/sprites/coin_0.png ... coin_N.png   (animation frames; loops)
    assets/sprites/flag.png
    assets/sprites/gravestone.png   (marker placed where player died to an enemy)
    assets/sprites/heart.png        (life pickup; placed with 'H' in level files)
    assets/sprites/heart_spritesheet.png   (optional animated heart; horizontal strip of square frames)
    assets/sprites/background.png   (sized to window, scaled if not)
    assets/sprites/game_over.png    (optional; shown on GAME OVER screen)
    assets/sprites/win.png          (optional; shown on YOU WIN screen)

    assets/sounds/jump.wav
    assets/sounds/coin.wav
    assets/sounds/death.wav
    assets/sounds/win.wav
    assets/sounds/head_bump.wav     (one-shot on head hit)
    assets/sounds/stun.wav          (looped while player is stunned)
    assets/sounds/run.wav           (looped while player runs on ground)
    assets/sounds/crumble.wav       (one-shot when a 'T' tile collapses)
    assets/sounds/rattle.wav        (looped while any 'T' tile is shaking)
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
    HEART_SIZE,
    HEIGHT,
    PLAYER_COLOR,
    PLAYER_SIZE,
    PLAYER_SPRITE_SIZE,
    TILE_COLOR,
    TILE_SIZE,
    WIDTH,
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


def _make_temp_tile_fallback() -> pygame.Surface:
    s = pygame.Surface((TILE_SIZE, TILE_SIZE))
    s.fill((230, 180, 80))
    pygame.draw.rect(s, (180, 130, 50), (0, TILE_SIZE * 3 // 4, TILE_SIZE, TILE_SIZE // 4))
    pygame.draw.line(s, (130, 80, 30), (5, 5), (15, 22), 1)
    pygame.draw.line(s, (130, 80, 30), (20, 8), (28, 26), 1)
    pygame.draw.rect(s, (0, 0, 0), s.get_rect(), 1)
    return s


def _make_coin_fallback() -> pygame.Surface:
    s = pygame.Surface((COIN_SIZE, COIN_SIZE), pygame.SRCALPHA)
    pygame.draw.ellipse(s, COIN_COLOR, s.get_rect())
    pygame.draw.ellipse(s, (200, 150, 0), s.get_rect(), 1)
    return s


def _make_heart_fallback() -> pygame.Surface:
    s = pygame.Surface((HEART_SIZE, HEART_SIZE), pygame.SRCALPHA)
    red = (220, 50, 50)
    dark = (140, 25, 25)
    r = HEART_SIZE // 4 + 1
    cx_left = r
    cx_right = HEART_SIZE - r
    cy = r
    pygame.draw.circle(s, red, (cx_left, cy), r)
    pygame.draw.circle(s, red, (cx_right, cy), r)
    pts = [(0, cy), (HEART_SIZE, cy), (HEART_SIZE // 2, HEART_SIZE - 1)]
    pygame.draw.polygon(s, red, pts)
    pygame.draw.polygon(s, dark, pts, 1)
    pygame.draw.circle(s, dark, (cx_left, cy), r, 1)
    pygame.draw.circle(s, dark, (cx_right, cy), r, 1)
    return s


def _make_gravestone_fallback() -> pygame.Surface:
    s = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
    body = (110, 70, 35)
    edge = (60, 35, 10)
    cross = (245, 235, 200)
    pts = [(16, 4), (26, 9), (26, 27), (16, 30), (6, 27), (6, 9)]
    pygame.draw.polygon(s, body, pts)
    pygame.draw.polygon(s, edge, pts, 2)
    pygame.draw.rect(s, cross, (15, 13, 2, 10))
    pygame.draw.rect(s, cross, (12, 16, 8, 2))
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
def get_player_animations() -> dict[str, tuple[pygame.Surface, ...]]:
    path = SPRITES_DIR / "player_spritesheet.png"
    if not path.exists():
        fb = pygame.transform.scale(_make_player_fallback(), (PLAYER_SPRITE_SIZE, PLAYER_SPRITE_SIZE))
        return {
            "idle_left": (fb,),
            "idle_right": (fb,),
            "run_left": (fb,),
            "run_right": (fb,),
            "jump_left": (fb,),
            "jump_right": (fb,),
            "stunned_left": (fb,),
            "stunned_right": (fb,),
        }
    sheet = pygame.image.load(str(path)).convert_alpha()
    frame_size = 128

    def cell(col: int, row: int) -> pygame.Surface:
        raw = sheet.subsurface((col * frame_size, row * frame_size, frame_size, frame_size))
        return pygame.transform.smoothscale(raw, (PLAYER_SPRITE_SIZE, PLAYER_SPRITE_SIZE))

    jump_left = tuple(cell(c, 0) for c in range(5))
    run_left = tuple(cell(c, 1) for c in range(8))
    jump_right = tuple(pygame.transform.flip(s, True, False) for s in jump_left)
    run_right = tuple(pygame.transform.flip(s, True, False) for s in run_left)

    return {
        "idle_left": (jump_left[0],),
        "idle_right": (jump_right[0],),
        "run_left": run_left,
        "run_right": run_right,
        "jump_left": jump_left,
        "jump_right": jump_right,
        "stunned_left": (jump_left[2],),
        "stunned_right": (jump_right[2],),
    }


@lru_cache(maxsize=None)
def get_enemy_right_sprite() -> pygame.Surface:
    return _load_image_or_fallback("enemy_right.png", (ENEMY_SIZE, ENEMY_SIZE), _make_enemy_fallback)


@lru_cache(maxsize=None)
def get_enemy_left_sprite() -> pygame.Surface:
    return _load_image_or_fallback("enemy_left.png", (ENEMY_SIZE, ENEMY_SIZE), _make_enemy_fallback)


@lru_cache(maxsize=None)
def get_tile_sprite() -> pygame.Surface:
    return _load_image_or_fallback("tile.png", (TILE_SIZE, TILE_SIZE), _make_tile_fallback)


@lru_cache(maxsize=None)
def get_temp_tile_sprite() -> pygame.Surface:
    return _load_image_or_fallback("temp_tile.png", (TILE_SIZE, TILE_SIZE), _make_temp_tile_fallback)


@lru_cache(maxsize=None)
def get_coin_frames() -> tuple[pygame.Surface, ...]:
    raw: list[pygame.Surface] = []
    for i in range(20):
        path = SPRITES_DIR / f"coin_{i}.png"
        if not path.exists():
            continue
        try:
            raw.append(pygame.image.load(str(path)).convert_alpha())
        except pygame.error:
            continue
    if not raw:
        return (_make_coin_fallback(),)
    max_dim = max(max(s.get_width(), s.get_height()) for s in raw)
    factor = COIN_SIZE / max_dim if max_dim else 1.0
    return tuple(
        pygame.transform.smoothscale(
            s,
            (max(1, int(s.get_width() * factor)), max(1, int(s.get_height() * factor))),
        )
        for s in raw
    )


@lru_cache(maxsize=None)
def get_flag_sprite() -> pygame.Surface:
    return _load_image_or_fallback("flag.png", (TILE_SIZE, TILE_SIZE), _make_flag_fallback)


@lru_cache(maxsize=None)
def get_gravestone_sprite() -> pygame.Surface:
    return _load_image_or_fallback("gravestone.png", (TILE_SIZE, TILE_SIZE), _make_gravestone_fallback)


@lru_cache(maxsize=None)
def get_heart_sprite() -> pygame.Surface:
    return _load_image_or_fallback("heart.png", (HEART_SIZE, HEART_SIZE), _make_heart_fallback)


@lru_cache(maxsize=None)
def get_heart_frames() -> tuple[pygame.Surface, ...]:
    path = SPRITES_DIR / "heart_spritesheet.png"
    if not path.exists():
        return (get_heart_sprite(),)
    try:
        sheet = pygame.image.load(str(path)).convert_alpha()
    except pygame.error:
        return (get_heart_sprite(),)
    frame_h = sheet.get_height()
    frame_w = frame_h
    n = sheet.get_width() // frame_w
    if n <= 0:
        return (get_heart_sprite(),)
    return tuple(
        pygame.transform.smoothscale(
            sheet.subsurface((i * frame_w, 0, frame_w, frame_h)),
            (HEART_SIZE, HEART_SIZE),
        )
        for i in range(n)
    )


def _make_background_fallback() -> pygame.Surface:
    surface = pygame.Surface((WIDTH, HEIGHT))
    top = (100, 170, 230)
    bottom = (200, 225, 245)
    for y in range(HEIGHT):
        t = y / max(HEIGHT - 1, 1)
        color = (
            int(top[0] + (bottom[0] - top[0]) * t),
            int(top[1] + (bottom[1] - top[1]) * t),
            int(top[2] + (bottom[2] - top[2]) * t),
        )
        pygame.draw.line(surface, color, (0, y), (WIDTH, y))
    clouds = [(80, 90), (320, 60), (560, 130), (170, 220), (470, 240), (680, 80)]
    for cx, cy in clouds:
        for dx, dy, w, h in [(0, 10, 70, 28), (25, 0, 60, 32), (50, 8, 65, 26)]:
            pygame.draw.ellipse(surface, (255, 255, 255), (cx + dx, cy + dy, w, h))
    return surface


@lru_cache(maxsize=None)
def get_background_sprite() -> pygame.Surface:
    return _load_image_or_fallback("background.svg", (WIDTH, HEIGHT), _make_background_fallback)


@lru_cache(maxsize=None)
def get_game_over_sprite() -> pygame.Surface | None:
    return _try_load_screen_image("game_over")


@lru_cache(maxsize=None)
def get_win_sprite() -> pygame.Surface | None:
    return _try_load_screen_image("win")


def _try_load_screen_image(stem: str) -> pygame.Surface | None:
    for ext in (".png", ".jpg", ".jpeg", ".bmp", ".gif", ".svg"):
        path = SPRITES_DIR / f"{stem}{ext}"
        if path.exists():
            try:
                img = pygame.image.load(str(path)).convert_alpha()
                return pygame.transform.scale(img, (WIDTH, HEIGHT))
            except pygame.error:
                continue
    return None


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
