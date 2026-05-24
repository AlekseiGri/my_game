import math
import random
from typing import TYPE_CHECKING

import pygame

from assets import get_player_animations
from settings import (
    GRAVITY,
    JUMP_CUT_VELOCITY,
    JUMP_VELOCITY,
    PLAYER_SIZE,
    PLAYER_SPEED,
    PLAYER_STUN_FRAMES,
)

if TYPE_CHECKING:
    from camera import Camera


class DustParticle:
    LIFETIME = 20
    RADIUS_START = 3.0
    RADIUS_END = 9.0
    DEFAULT_COLOR = (220, 200, 175)
    DEFAULT_GRAVITY = 0.15

    def __init__(
        self,
        x: int,
        y: int,
        vx: float,
        vy: float,
        color: tuple[int, int, int] = DEFAULT_COLOR,
        gravity: float = DEFAULT_GRAVITY,
    ) -> None:
        self.x = float(x)
        self.y = float(y)
        self.vx = vx
        self.vy = vy
        self.color = color
        self.gravity = gravity
        self.timer = 0

    def update(self) -> None:
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity
        self.timer += 1

    @property
    def alive(self) -> bool:
        return self.timer < self.LIFETIME

    def draw(self, surface: pygame.Surface, camera: "Camera") -> None:
        t = self.timer / self.LIFETIME
        radius = self.RADIUS_START + (self.RADIUS_END - self.RADIUS_START) * t
        alpha = int(200 * (1 - t))
        sz = int(radius * 2) + 2
        surf = pygame.Surface((sz, sz), pygame.SRCALPHA)
        pygame.draw.circle(surf, (*self.color, alpha), (sz // 2, sz // 2), int(radius))
        rect = pygame.Rect(0, 0, sz, sz)
        rect.center = (int(self.x), int(self.y))
        surface.blit(surf, camera.apply(rect))


def spawn_jump_dust(x: int, y: int) -> list[DustParticle]:
    particles: list[DustParticle] = []
    for _ in range(6):
        vx = random.uniform(-2.0, 2.0)
        vy = random.uniform(-2.0, -0.5)
        particles.append(DustParticle(x, y, vx, vy))
    return particles


def spawn_hit_burst(x: int, y: int) -> list[DustParticle]:
    particles: list[DustParticle] = []
    for _ in range(12):
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(2.0, 4.0)
        vx = math.cos(angle) * speed
        vy = math.sin(angle) * speed
        particles.append(
            DustParticle(x, y, vx, vy, color=(220, 80, 60), gravity=0.05)
        )
    return particles


def spawn_head_bump_burst(x: int, y: int) -> list[DustParticle]:
    particles: list[DustParticle] = []
    for _ in range(8):
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(1.5, 3.0)
        vx = math.cos(angle) * speed
        vy = math.sin(angle) * speed
        particles.append(
            DustParticle(x, y, vx, vy, color=(255, 230, 100), gravity=0.1)
        )
    return particles


class Player:
    FRAME_DURATION = 5

    def __init__(self, x: int, y: int) -> None:
        self.rect = pygame.Rect(x, y, PLAYER_SIZE, PLAYER_SIZE)
        self.vel_x: int = 0
        self.vel_y: int = 0
        self.on_ground: bool = False
        self.anims = get_player_animations()
        self.facing: str = "right"
        self.current_anim: str = "idle_right"
        self.frame_idx: int = 0
        self.frame_timer: int = 0
        self.stunned_timer: int = 0
        self.head_bumped_this_frame: bool = False

    def is_stunned(self) -> bool:
        return self.stunned_timer > 0

    def handle_input(self, keys) -> None:
        if self.is_stunned():
            return
        self.vel_x = 0
        if keys[pygame.K_LEFT]:
            self.vel_x = -PLAYER_SPEED
            self.facing = "left"
        if keys[pygame.K_RIGHT]:
            self.vel_x = PLAYER_SPEED
            self.facing = "right"

    def respawn(self, x: int, y: int) -> None:
        self.rect.topleft = (x, y)
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False
        self.facing = "right"
        self.current_anim = "idle_right"
        self.frame_idx = 0
        self.frame_timer = 0
        self.stunned_timer = 0
        self.head_bumped_this_frame = False

    def jump(self) -> bool:
        if self.is_stunned():
            return False
        if self.on_ground:
            self.vel_y = JUMP_VELOCITY
            self.on_ground = False
            return True
        return False

    def cut_jump(self) -> None:
        if self.is_stunned():
            return
        if self.vel_y < JUMP_CUT_VELOCITY:
            self.vel_y = JUMP_CUT_VELOCITY

    def update(self, tiles: list[pygame.Rect]) -> None:
        self.head_bumped_this_frame = False
        if self.stunned_timer > 0:
            self.stunned_timer -= 1
            self.vel_x = 0

        self.vel_y += GRAVITY

        self.rect.x += self.vel_x
        self._collide_x(tiles)

        self.on_ground = False
        self.rect.y += self.vel_y
        self._collide_y(tiles)

        self._update_anim()

    def _pick_anim(self) -> str:
        if self.is_stunned():
            return f"stunned_{self.facing}"
        if not self.on_ground:
            return f"jump_{self.facing}"
        if self.vel_x != 0:
            return f"run_{self.facing}"
        return f"idle_{self.facing}"

    def _update_anim(self) -> None:
        new_anim = self._pick_anim()
        if new_anim != self.current_anim:
            self.current_anim = new_anim
            self.frame_idx = 0
            self.frame_timer = 0
        self.frame_timer += 1
        if self.frame_timer >= self.FRAME_DURATION:
            self.frame_timer = 0
            self.frame_idx = (self.frame_idx + 1) % len(self.anims[self.current_anim])

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
                if not self.is_stunned():
                    self.head_bumped_this_frame = True
                    self.stunned_timer = PLAYER_STUN_FRAMES
            self.vel_y = 0

    def draw(self, surface: pygame.Surface, camera: "Camera") -> None:
        sprite = self.anims[self.current_anim][self.frame_idx]
        bbox = sprite.get_bounding_rect()
        screen_rect = camera.apply(self.rect)
        offset_x = (self.rect.width - bbox.width) // 2 - bbox.x
        offset_y = self.rect.height - bbox.bottom
        surface.blit(sprite, (screen_rect.x + offset_x, screen_rect.y + offset_y))
        if self.is_stunned():
            cx = screen_rect.centerx
            cy = screen_rect.top + offset_y + max(0, bbox.y) - 6
            phase = (PLAYER_STUN_FRAMES - self.stunned_timer) * 0.18
            for i in range(3):
                angle = phase + i * (2 * math.pi / 3)
                sx = cx + int(14 * math.cos(angle))
                sy = cy + int(5 * math.sin(angle))
                pygame.draw.circle(surface, (255, 220, 80), (sx, sy), 3)
                pygame.draw.circle(surface, (140, 90, 0), (sx, sy), 3, 1)
