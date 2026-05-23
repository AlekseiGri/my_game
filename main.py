import sys
from pathlib import Path

import pygame

from assets import load_sound, play_sound
from camera import Camera
from coin import Coin
from enemy import Enemy
from level import Level
from player import Player
from settings import (
    BG_COLOR,
    FPS,
    HEIGHT,
    HUD_COLOR,
    HUD_FONT_SIZE,
    LIVES_START,
    TITLE,
    TITLE_FONT_SIZE,
    WIDTH,
)

LEVEL_FILES = ["level1.txt", "level2.txt"]

STATE_TITLE = "title"
STATE_PLAYING = "playing"
STATE_GAME_OVER = "game_over"
STATE_WIN = "win"


def load_level(index: int) -> tuple[Level, Player, list[Enemy], list[Coin], Camera]:
    path = Path(__file__).parent / "levels" / LEVEL_FILES[index]
    level = Level(path)
    player = Player(*level.player_start)
    enemies = [Enemy(x, y) for x, y in level.enemy_starts]
    coins = [Coin(x, y) for x, y in level.coin_starts]
    camera = Camera(level.width, level.height)
    return level, player, enemies, coins, camera


def draw_centered(
    surface: pygame.Surface,
    font: pygame.font.Font,
    text: str,
    y: int,
    color: tuple[int, int, int],
) -> None:
    rendered = font.render(text, True, color)
    rect = rendered.get_rect(center=(WIDTH // 2, y))
    surface.blit(rendered, rect)


def main() -> None:
    pygame.init()
    try:
        pygame.mixer.init()
    except pygame.error:
        pass

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption(TITLE)
    clock = pygame.time.Clock()

    hud_font = pygame.font.Font(None, HUD_FONT_SIZE)
    title_font = pygame.font.Font(None, TITLE_FONT_SIZE)

    sounds = {
        "jump": load_sound("jump.wav"),
        "coin": load_sound("coin.wav"),
        "death": load_sound("death.wav"),
        "win": load_sound("win.wav"),
    }

    state = STATE_TITLE
    level_index = 0
    score = 0
    lives = LIVES_START
    level, player, enemies, coins, camera = load_level(level_index)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    if state == STATE_TITLE:
                        level_index = 0
                        score = 0
                        lives = LIVES_START
                        level, player, enemies, coins, camera = load_level(level_index)
                        state = STATE_PLAYING
                    elif state == STATE_PLAYING:
                        if player.jump():
                            play_sound(sounds["jump"])
                    elif state in (STATE_GAME_OVER, STATE_WIN):
                        state = STATE_TITLE
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE and state == STATE_PLAYING:
                    player.cut_jump()

        if state == STATE_PLAYING:
            keys = pygame.key.get_pressed()
            player.handle_input(keys)
            player.update(level.tiles)

            for enemy in enemies:
                enemy.update(level.tiles)

            remaining: list[Coin] = []
            for coin in coins:
                if player.rect.colliderect(coin.rect):
                    score += 1
                    play_sound(sounds["coin"])
                else:
                    remaining.append(coin)
            coins = remaining

            died = player.rect.top > level.height or any(
                player.rect.colliderect(e.rect) for e in enemies
            )
            if died:
                lives -= 1
                play_sound(sounds["death"])
                if lives <= 0:
                    state = STATE_GAME_OVER
                else:
                    player.respawn(*level.player_start)

            if (
                state == STATE_PLAYING
                and level.finish is not None
                and player.rect.colliderect(level.finish)
            ):
                play_sound(sounds["win"])
                level_index += 1
                if level_index >= len(LEVEL_FILES):
                    state = STATE_WIN
                else:
                    level, player, enemies, coins, camera = load_level(level_index)

            camera.update(player.rect)

        screen.fill(BG_COLOR)

        if state == STATE_TITLE:
            draw_centered(screen, title_font, "PLATFORMER", HEIGHT // 2 - 80, HUD_COLOR)
            draw_centered(screen, hud_font, "Press SPACE to start", HEIGHT // 2, HUD_COLOR)
            draw_centered(screen, hud_font, "Arrows to move, SPACE to jump, ESC to quit", HEIGHT // 2 + 40, HUD_COLOR)
        elif state == STATE_PLAYING:
            level.draw(screen, camera)
            for coin in coins:
                coin.draw(screen, camera)
            for enemy in enemies:
                enemy.draw(screen, camera)
            player.draw(screen, camera)
            hud = hud_font.render(
                f"Score: {score}   Lives: {lives}   Level: {level_index + 1}/{len(LEVEL_FILES)}",
                True,
                HUD_COLOR,
            )
            screen.blit(hud, (10, 10))
        elif state == STATE_GAME_OVER:
            draw_centered(screen, title_font, "GAME OVER", HEIGHT // 2 - 60, HUD_COLOR)
            draw_centered(screen, hud_font, f"Score: {score}", HEIGHT // 2 + 20, HUD_COLOR)
            draw_centered(screen, hud_font, "Press SPACE for title", HEIGHT // 2 + 60, HUD_COLOR)
        elif state == STATE_WIN:
            draw_centered(screen, title_font, "YOU WIN!", HEIGHT // 2 - 60, HUD_COLOR)
            draw_centered(screen, hud_font, f"Final score: {score}", HEIGHT // 2 + 20, HUD_COLOR)
            draw_centered(screen, hud_font, "Press SPACE for title", HEIGHT // 2 + 60, HUD_COLOR)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
