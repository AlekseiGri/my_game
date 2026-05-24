# Platformer

A 2D side-scrolling platformer built with Pygame. Features a tile-based level format, animated sprites, sound effects and music, variable-height jumps, crumbling platforms, patrolling enemies, collectible coins and hearts, and a full state machine (title → playing → game over / win).

![Python](https://img.shields.io/badge/python-3.12-blue.svg)
![Pygame](https://img.shields.io/badge/pygame-2.6-green.svg)
![License](https://img.shields.io/badge/license-MIT-lightgrey.svg)

## Table of contents

- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Running the game](#running-the-game)
- [Controls](#controls)
- [Gameplay](#gameplay)
- [Level file format](#level-file-format)
- [Project structure](#project-structure)
- [Custom assets](#custom-assets)
- [Configuration](#configuration)
- [Building your own level](#building-your-own-level)
- [License](#license)

## Features

- **Tile-based levels** authored as plain `.txt` files; one character per tile.
- **State machine**: title screen → gameplay → game over / win, all driven by keyboard input.
- **Animated title screen** with a procedural sky gradient and drifting parallax clouds.
- **Player**: directional sprite-sheet animations (idle / run / jump / stunned), variable-height jump (hold SPACE for higher), axis-separated tile collisions, respawn on death.
- **Enemies**: gravity-driven patrol with wall-and-edge detection so they stay on their platforms; flip sprite to face direction of travel.
- **Coins** with rotating-frame animation and a "pickup pop" effect when collected.
- **Hearts** with sprite-sheet animation; each one grants +1 life.
- **Crumbling tiles** (`T`): countdown while the player stands on them, vanish after a threshold, respawn after a cooldown; rattle and crumble sound cues.
- **Gravestones** spawn where the player dies to an enemy and remain on that level for the rest of the run; no collision, never block movement.
- **Particle effects**: jump dust, hit-burst on enemy collision, head-bump sparkles when the player hits the underside of a block.
- **Stun mechanic**: hitting the head on a ceiling tile freezes player input for two seconds; orbiting "stars" overlay shows the state.
- **Death pause**: half-second freeze and player blink on enemy hits.
- **Camera** follows the player and clamps to level bounds.
- **Audio**: one-shot sound effects (jump, coin, hit, head bump, heart pickup, crumble, win, lose) and looped tracks (run, stun, rattle); per-state music for title / playing / game over.
- **Multi-level flow**: touch the finish flag `F` to advance to the next level; finishing the last level shows the win screen.
- **Graceful fallbacks**: every sprite and sound has a built-in procedural placeholder, so the game runs even with empty `assets/` folders.

## Requirements

- Python 3.12 (3.10+ should work, but 3.12 is what was tested)
- [pygame](https://www.pygame.org/) 2.5 or newer

## Installation

```sh
git clone <repo-url>
cd my_game
pip install pygame
```

No additional dependencies. All other code is pure standard library.

## Running the game

```sh
python main.py
```

The game starts on the title screen. Press SPACE to begin.

## Controls

| Key | Action |
|---|---|
| ← / → | Move left / right |
| SPACE (hold) | Jump (longer hold = higher jump) |
| SPACE (release while rising) | Cut the jump short |
| SPACE (on screens) | Confirm — start game / return to title |
| ESC | Quit |

## Gameplay

You start with 3 lives. Reach the flag `F` to clear a level; clear all levels to win. You lose a life when you touch an enemy or fall off the bottom of the level. Running out of lives shows the GAME OVER screen.

Coins give +1 to your score. Hearts give +1 to your lives (no cap). Some platforms are crumbling — they shake while you stand on them and vanish after about half a second of total standing time; they reappear after a few seconds. Jumping into the underside of a solid block stuns the player for two seconds, freezing input.

When you die to an enemy a gravestone is placed where you fell. It stays on that level for the rest of the run as a visual marker — it never blocks movement.

## Level file format

Levels are plain text files in `levels/`. Each character represents one tile (`TILE_SIZE = 32` pixels by default). All rows must be the same length.

| Char | Meaning |
|---|---|
| `.` | Empty |
| `#` | Solid tile (permanent platform / wall / floor) |
| `T` | Crumbling tile (vanishes while you stand on it, then respawns) |
| `P` | Player spawn (place exactly one) |
| `E` | Enemy spawn |
| `C` | Coin pickup |
| `H` | Heart pickup (grants +1 life) |
| `F` | Finish flag (touch to advance to the next level) |

Example fragment:

```
............................................................
......................C.....................................
.......C.............TTT....................................
......###.............###....................................
..P.............................................########.###
.......E................E...............E...############....
##############...###############...#########################
```

Add new levels by creating `levels/levelN.txt` and adding its filename to `LEVEL_FILES` in `main.py`.

## Project structure

```
my_game/
├── main.py              # Entry point; game loop, state machine, integration
├── settings.py          # All tunable constants (sizes, colours, timings, etc.)
├── assets.py            # Asset loading with procedural fallbacks
├── camera.py            # Follow-player camera with level-bound clamping
├── level.py             # Level parser + Level and TemporaryTile classes
├── player.py            # Player physics, animation, stun, particle helpers
├── enemy.py             # Patrolling enemy with edge detection
├── coin.py              # Coin (animated) and CoinPickupEffect
├── heart.py             # Heart pickup (sprite-sheet animated)
├── gravestone.py        # Visual-only death marker
├── title.py             # Title-screen sky + animated clouds
├── levels/
│   ├── level1.txt
│   └── level2.txt
└── assets/
    ├── sprites/         # Drop your .png/.jpg/.svg files here
    └── sounds/          # Drop your .wav/.mp3/.ogg files here
```

## Custom assets

Every asset has a procedural fallback drawn from primitive shapes. The game runs with empty `assets/sprites/` and `assets/sounds/` folders. To upgrade visuals/audio, place files with the expected names below.

### Sprites (any common image format; auto-scaled to target size)

| Filename | Used for |
|---|---|
| `player.png` | Static player fallback |
| `player_spritesheet.png` | Animated player (row 0: 5-frame jump-left, row 1: 8-frame run-left; right-facing is auto-flipped) |
| `enemy_right.png`, `enemy_left.png` | Directional enemy sprites |
| `tile.png` | Solid platform tile |
| `temp_tile.png` | Crumbling tile (`T` in levels) |
| `coin_0.png` … `coin_N.png` | Coin animation frames (loops automatically; any count up to 20) |
| `heart.png` | Static heart fallback |
| `heart_spritesheet.png` | Animated heart (horizontal strip of square frames) |
| `flag.png` | Finish flag (`F`) |
| `gravestone.png` | Marker placed on death |
| `background.png` | In-game backdrop (sized to window) |
| `game_over.png` | GAME OVER backdrop |
| `win.png` | YOU WIN backdrop |

### Sounds (`.wav` recommended; `.ogg` works; `.mp3` works for music)

| Filename | Trigger |
|---|---|
| `jump.wav` | Player jumps |
| `coin.wav` | Coin collected |
| `heart.wav` | Heart collected |
| `death.wav` | Player dies (one-shot) |
| `win.wav` | Finish flag reached |
| `head_bump.wav` | Player hits head on a tile |
| `crumble.wav` | A `T` tile collapses |
| `run.wav` | **Looped** while player is running on the ground |
| `stun.wav` (or `.mp3`) | **Looped** while player is stunned |
| `rattle.wav` | **Looped** while any `T` tile is shaking |
| `main_menu.wav` (or `.mp3`) | **Music**, looped on the title screen |
| `game_during.mp3` | **Music**, looped during gameplay |
| `lose.ogg` | **Music**, looped on the GAME OVER screen |

Missing files are silently ignored — no crashes.

## Configuration

Tweak [`settings.py`](settings.py) to change feel and look without touching gameplay code. Some notable knobs:

| Constant | What it controls |
|---|---|
| `WIDTH`, `HEIGHT`, `FPS` | Window size and frame rate |
| `TILE_SIZE` | Pixel size of one tile (default 32) |
| `PLAYER_SPEED` | Horizontal movement speed |
| `JUMP_VELOCITY` | Initial upward velocity on jump |
| `JUMP_CUT_VELOCITY` | Cap on remaining upward velocity when SPACE is released |
| `GRAVITY` | Falling acceleration |
| `PLAYER_STUN_FRAMES` | Stun duration after head bump (frames) |
| `PLAYER_SPRITE_SIZE` | Rendered sprite size (independent of the 32-px hitbox) |
| `ENEMY_SPEED` | Patrol speed |
| `COIN_ANIM_FRAME_DURATION`, `HEART_ANIM_FRAME_DURATION` | Animation pacing |
| `LIVES_START` | Initial life count |
| `SKY_COLOR`, `BG_COLOR`, `HUD_COLOR` | Default colours |

## Building your own level

1. Copy `levels/level1.txt` to `levels/level3.txt`.
2. Edit the file in any text editor — each character is one tile (see the [Level file format](#level-file-format) table).
3. Make sure exactly one `P` exists and every row has the same width.
4. Open `main.py` and append `"level3.txt"` to the `LEVEL_FILES` list.
5. Run the game; you'll progress through your new level after the existing ones.

## License

MIT.
