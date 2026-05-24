import sys
from pathlib import Path

import pygame

from assets import (
    get_background_sprite,
    get_game_over_sprite,
    get_win_sprite,
    load_sound,
    play_sound,
)
from camera import Camera
from coin import Coin, CoinPickupEffect
from enemy import Enemy
from gravestone import Gravestone
from heart import Heart
from level import Level
from player import (
    DustParticle,
    Player,
    spawn_head_bump_burst,
    spawn_hit_burst,
    spawn_jump_dust,
)
from title import Cloud, make_title_clouds, make_title_sky
from settings import (
    BG_COLOR,
    FPS,
    HEIGHT,
    HUD_COLOR,
    HUD_FONT_SIZE,
    LIVES_START,
    SKY_COLOR,
    TITLE,
    TITLE_FONT_SIZE,
    WIDTH,
)

LEVEL_FILES = ["level1.txt", "level2.txt"]

STATE_TITLE = "title"
STATE_PLAYING = "playing"
STATE_GAME_OVER = "game_over"
STATE_WIN = "win"


def load_level(
    index: int,
) -> tuple[Level, Player, list[Enemy], list[Coin], list[Heart], Camera]:
    path = Path(__file__).parent / "levels" / LEVEL_FILES[index]
    level = Level(path)
    player = Player(*level.player_start)
    enemies = [Enemy(x, y) for x, y in level.enemy_starts]
    coins = [Coin(x, y) for x, y in level.coin_starts]
    hearts = [Heart(x, y) for x, y in level.heart_starts]
    camera = Camera(level.width, level.height)
    return level, player, enemies, coins, hearts, camera


def draw_centered(
    surface: pygame.Surface,
    font: pygame.font.Font,
    text: str,
    y: int,
    color: tuple[int, int, int],
    outline: tuple[int, int, int] | None = None,
) -> None:
    rendered = font.render(text, True, color)
    rect = rendered.get_rect(center=(WIDTH // 2, y))
    if outline is not None:
        outlined = font.render(text, True, outline)
        for dx, dy in ((-2, -2), (0, -2), (2, -2), (-2, 0), (2, 0), (-2, 2), (0, 2), (2, 2)):
            surface.blit(outlined, rect.move(dx, dy))
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

    background = get_background_sprite()
    game_over_image = get_game_over_sprite()
    win_image = get_win_sprite()
    title_sky = make_title_sky()
    title_clouds = make_title_clouds()

    sounds = {
        "jump": load_sound("jump.wav"),
        "coin": load_sound("coin.wav"),
        "death": load_sound("death.wav"),
        "win": load_sound("win.wav"),
        "lose": load_sound("Lose.ogg"),
        "head_bump": load_sound("head_bump.wav"),
        "stun": load_sound("stun.mp3"),
        "run": load_sound("run.wav"),
        "crumble": load_sound("crumble.wav"),
        "rattle": load_sound("rattle.wav"),
        "heart": load_sound("heart.wav"),
    }

    music_paths: dict[str, Path] = {}
    if pygame.mixer.get_init() is not None:
        sounds_dir = Path(__file__).parent / "assets" / "sounds"
        for state_name, filename in [
            (STATE_TITLE, "main_menu.wav"),
            (STATE_GAME_OVER, "lose.ogg"),
            (STATE_PLAYING, "game_during.mp3"),
        ]:
            p = sounds_dir / filename
            if p.exists():
                music_paths[state_name] = p
    current_music_state: str | None = None

    state = STATE_TITLE
    level_index = 0
    score = 0
    lives = LIVES_START
    level, player, enemies, coins, hearts, camera = load_level(level_index)
    pickup_effects: list[CoinPickupEffect] = []
    dust_particles: list[DustParticle] = []
    gravestones_by_level: dict[int, list[Gravestone]] = {}
    death_pause_timer = 0
    stun_sound_active = False
    run_sound_active = False
    rattle_sound_active = False

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
                        level, player, enemies, coins, hearts, camera = load_level(level_index)
                        pickup_effects = []
                        dust_particles = []
                        gravestones_by_level = {}
                        death_pause_timer = 0
                        state = STATE_PLAYING
                    elif state == STATE_PLAYING and death_pause_timer == 0:
                        if player.jump():
                            play_sound(sounds["jump"])
                            dust_particles.extend(
                                spawn_jump_dust(player.rect.centerx, player.rect.bottom)
                            )
                    elif state in (STATE_GAME_OVER, STATE_WIN):
                        state = STATE_TITLE
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE and state == STATE_PLAYING and death_pause_timer == 0:
                    player.cut_jump()

        if state == STATE_TITLE:
            for cloud in title_clouds:
                cloud.update()

        if state == STATE_PLAYING:
            for coin in coins:
                coin.update()
            for heart in hearts:
                heart.update()
            for fx in pickup_effects:
                fx.update()
            pickup_effects = [fx for fx in pickup_effects if fx.alive]
            for p in dust_particles:
                p.update()
            dust_particles = [p for p in dust_particles if p.alive]

        if state == STATE_PLAYING and death_pause_timer > 0:
            death_pause_timer -= 1
        elif state == STATE_PLAYING:
            keys = pygame.key.get_pressed()
            player.handle_input(keys)
            player.update(level.solid_tiles)

            if player.head_bumped_this_frame:
                play_sound(sounds["head_bump"])
                dust_particles.extend(
                    spawn_head_bump_burst(player.rect.centerx, player.rect.top)
                )

            for enemy in enemies:
                enemy.update(level.solid_tiles)

            for tt in level.temp_tiles:
                standing = (
                    player.on_ground
                    and player.rect.bottom == tt.rect.top
                    and player.rect.right > tt.rect.left
                    and player.rect.left < tt.rect.right
                )
                if tt.tick(standing):
                    play_sound(sounds["crumble"])

            remaining: list[Coin] = []
            for coin in coins:
                if player.rect.colliderect(coin.rect):
                    score += 1
                    play_sound(sounds["coin"])
                    pickup_effects.append(
                        CoinPickupEffect(coin.rect.centerx, coin.rect.centery, coin.frames[0])
                    )
                else:
                    remaining.append(coin)
            coins = remaining

            remaining_hearts: list[Heart] = []
            for heart in hearts:
                if player.rect.colliderect(heart.rect):
                    lives += 1
                    play_sound(sounds["heart"])
                else:
                    remaining_hearts.append(heart)
            hearts = remaining_hearts

            hit_enemy = next(
                (e for e in enemies if player.rect.colliderect(e.rect)), None
            )
            died = player.rect.top > level.height or hit_enemy is not None
            if died:
                lives -= 1
                play_sound(sounds["death"])
                if hit_enemy is not None:
                    dust_particles.extend(
                        spawn_hit_burst(player.rect.centerx, player.rect.centery)
                    )
                    gravestones_by_level.setdefault(level_index, []).append(
                        Gravestone(player.rect.centerx, player.rect.bottom)
                    )
                if lives <= 0:
                    state = STATE_GAME_OVER
                else:
                    player.respawn(*level.player_start)
                    level.reset_temp_tiles()
                    death_pause_timer = FPS / 2

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
                    level, player, enemies, coins, hearts, camera = load_level(level_index)

            if death_pause_timer == 0:
                camera.update(player.rect)

        should_stun_loop = state == STATE_PLAYING and player.is_stunned()
        stun_sound = sounds["stun"]
        if should_stun_loop and not stun_sound_active and stun_sound is not None:
            stun_sound.play(loops=-1)
            stun_sound_active = True
        elif not should_stun_loop and stun_sound_active and stun_sound is not None:
            stun_sound.stop()
            stun_sound_active = False

        should_run_loop = (
            state == STATE_PLAYING
            and not player.is_stunned()
            and player.on_ground
            and player.vel_x != 0
        )
        run_sound = sounds["run"]
        if should_run_loop and not run_sound_active and run_sound is not None:
            run_sound.play(loops=-1)
            run_sound_active = True
        elif not should_run_loop and run_sound_active and run_sound is not None:
            run_sound.stop()
            run_sound_active = False

        should_rattle_loop = state == STATE_PLAYING and any(
            tt.state == "crumbling" for tt in level.temp_tiles
        )
        rattle_sound = sounds["rattle"]
        if should_rattle_loop and not rattle_sound_active and rattle_sound is not None:
            rattle_sound.play(loops=-1)
            rattle_sound_active = True
        elif not should_rattle_loop and rattle_sound_active and rattle_sound is not None:
            rattle_sound.stop()
            rattle_sound_active = False

        desired_music_state = state if state in music_paths else None
        if desired_music_state != current_music_state:
            if desired_music_state is None:
                pygame.mixer.music.stop()
            else:
                try:
                    pygame.mixer.music.load(str(music_paths[desired_music_state]))
                    pygame.mixer.music.set_volume(0.5)
                    pygame.mixer.music.play(loops=-1)
                except pygame.error:
                    pass
            current_music_state = desired_music_state

        if state == STATE_PLAYING:
            screen.fill(SKY_COLOR)
            screen.blit(background, (0, 0))
        elif state == STATE_TITLE:
            screen.blit(title_sky, (0, 0))
            for cloud in title_clouds:
                cloud.draw(screen)
        else:
            screen.fill(BG_COLOR)

        if state == STATE_TITLE:
            draw_centered(screen, title_font, "PLATFORMER", HEIGHT // 2 - 80, HUD_COLOR, outline=(0, 0, 0))
            draw_centered(screen, hud_font, "Press SPACE to start", HEIGHT // 2, HUD_COLOR, outline=(0, 0, 0))
            draw_centered(screen, hud_font, "Arrows to move, SPACE to jump, ESC to quit", HEIGHT // 2 + 40, HUD_COLOR, outline=(0, 0, 0))
        elif state == STATE_PLAYING:
            level.draw(screen, camera)
            for grave in gravestones_by_level.get(level_index, []):
                grave.draw(screen, camera)
            for coin in coins:
                coin.draw(screen, camera)
            for heart in hearts:
                heart.draw(screen, camera)
            for enemy in enemies:
                enemy.draw(screen, camera)
            for p in dust_particles:
                p.draw(screen, camera)
            if death_pause_timer == 0 or (int(death_pause_timer) // 4) % 2 == 0:
                player.draw(screen, camera)
            for fx in pickup_effects:
                fx.draw(screen, camera)
            hud = hud_font.render(
                f"Score: {score}   Lives: {lives}   Level: {level_index + 1}/{len(LEVEL_FILES)}",
                True,
                HUD_COLOR,
            )
            screen.blit(hud, (10, 10))
        elif state == STATE_GAME_OVER:
            if game_over_image is not None:
                screen.blit(game_over_image, (0, 0))
            else:
                draw_centered(screen, title_font, "GAME OVER", HEIGHT // 2 - 40, HUD_COLOR)
            strip = pygame.Surface((WIDTH, 80), pygame.SRCALPHA)
            strip.fill((0, 0, 0, 160))
            screen.blit(strip, (0, HEIGHT - 80))
            draw_centered(screen, hud_font, f"Score: {score}", HEIGHT - 52, HUD_COLOR, outline=(0, 0, 0))
            draw_centered(screen, hud_font, "Press SPACE for title", HEIGHT - 22, HUD_COLOR, outline=(0, 0, 0))
        elif state == STATE_WIN:
            if win_image is not None:
                screen.blit(win_image, (0, 0))
            else:
                draw_centered(screen, title_font, "YOU WIN!", HEIGHT // 2 - 40, HUD_COLOR)
            strip = pygame.Surface((WIDTH, 80), pygame.SRCALPHA)
            strip.fill((0, 0, 0, 160))
            screen.blit(strip, (0, HEIGHT - 80))
            draw_centered(screen, hud_font, f"Final score: {score}", HEIGHT - 52, HUD_COLOR, outline=(0, 0, 0))
            draw_centered(screen, hud_font, "Press SPACE for title", HEIGHT - 22, HUD_COLOR, outline=(0, 0, 0))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
