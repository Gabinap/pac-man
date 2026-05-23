# Project Timeline

Project duration: 2026-04-30 → 2026-05-23 (24 days)

## Week 1 — 2026-04-30 to 2026-05-06: Foundation

| Date | Author | Work |
|------|--------|------|
| 04-30 | Gabin | Initial commit, project structure |
| 05-02 | Gabin | Entry point (`pac-man.py`), Makefile, config parsing, constants |
| 05-02 | Gabin | Ursina visualization bootstrap — first squares on screen |
| 05-04 | Gabin | Norm pass |
| 05-06 | Ali | Main menu skeleton, `MainMenu` class |
| 05-06 | Ali | Menu skeleton complete |
| 05-06 | Gabin | Maze generation with walls and OpenGL rendering |
| 05-06 | Gabin | Floor and correct wall geometry |
| 05-06 | Gabin | Add maze lib via uv, Makefile target |

## Week 2 — 2026-05-07 to 2026-05-13: Entities and Gameplay

| Date | Author | Work |
|------|--------|------|
| 05-07 | Gabin | Player entity |
| 05-07 | Gabin | Assets: ambiances (wall/floor/pattern textures), asset library |
| 05-07 | Gabin | floor_brick.png resized (was 108 MB) |
| 05-11 | Gabin | First ghost AI (ghost[2] working) |
| 05-11 | Ali | Player movement implementation |
| 05-13 | Gabin | 3D model visualization fixes |
| 05-13 | Ali | Player movement working |
| 05-13 | Ali | Ghost movement — Blinky/Pinky working |
| 05-13 | Gabin | Random animation selection, spawn_y positioning |
| 05-13 | Ali | Added Clyde and Inky movement calculations |
| 05-13 | Ali | Collision system initial implementation |
| 05-13 | Ali | Collision system upgrade |

## Week 3 — 2026-05-14 to 2026-05-17: Game Loop and HUD

| Date | Author | Work |
|------|--------|------|
| 05-14 | Gabin | Entity movement refactor, ghost AI logic |
| 05-14 | Ali | Player lives on collision, untouchable state |
| 05-14 | Ali | Highscores in main menu |
| 05-14 | Gabin | Merge enemy/logic branches |
| 05-14 | Ali | Difficulty selection |
| 05-14 | Gabin | Pacgum models organized (`pacgums/`, `models/`) |
| 05-15 | Gabin | Pacgum gameplay — pickup detection, scoring |
| 05-15 | Gabin | Ambiance system refactor, pacgums per ambiance |
| 05-15 | Ali | Game over view: name input, score display, error handling |
| 05-15 | Ali | Highscore add on game over working |
| 05-15 | Ali | `current_anim` attribute, idle-on-stop fix |
| 05-16 | Ali | Score HUD, lives HUD |
| 05-16 | Ali | Score fixed, replay working |
| 05-16 | Gabin | Menu: glassmorphism style, animation one-shot system, name clarification |
| 05-17 | Ali | Architecture refactor: `GameRender` split into components |
| 05-17 | Ali | HUD computation optimization |
| 05-17 | Ali | Ghost/player blink on stun, teleport to spawn |
| 05-17 | Gabin | Pause system, HUD, level progression, empower, cheat mode |
| 05-17 | Gabin | Post-refactor crash fixes (pause, cheat code) |
| 05-17 | Gabin | 5 gameplay/UI bug fixes |
| 05-17 | Gabin | EASY mode game-over fix, ghosts stuck idle level 2+ fix |

## Week 4 — 2026-05-18 to 2026-05-23: Polish and Features

| Date | Author | Work |
|------|--------|------|
| 05-18 | Gabin | Ghost score value, miscellaneous bug fixes |
| 05-18 | Gabin | Difficulty change updates player lives immediately |
| 05-18 | Gabin | Restore 4 ghost models, introduce `PLAYER_SPEC` |
| 05-18 | Gabin | Remove crashing models (crocodile, volcano inferno) |
| 05-18 | Gabin | Translate French comments to English |
| 05-18 | Gabin | uv dependency lock (`uv sync --frozen`) |
| 05-18 | Ali | Ghost routines work in progress |
| 05-19 | Ali | Loading screen, ghost flee when EMPOWERED, HUD hide with `h` |
| 05-19 | Gabin | FPS mode |
| 05-19 | Gabin | Asset downscale for performance (30+ FPS, fast load) |
| 05-19 | Gabin | Restore high-res textures after downscale revert |
| 05-20 | Gabin | Settings view, better UI panel shapes, HUD polish |
| 05-21 | Ali | Empower progress bar |
| 05-21 | Ali | Player blink on UNTOUCHABLE fixed |
| 05-21 | Ali | Next level view |
| 05-21 | Ali | Score and timeout → GAME OVER |
| 05-22 | Ali | Loading animation fix |
| 05-22 | Ali | Fix WIN → menu transition, level reset |
| 05-22 | Ali | Empowered → NORMAL latency fix |
| 05-22 | Ali | Audio manager + ambient music + button sounds |
| 05-22 | Ali | Sound manager linked to settings view |
| 05-22 | Gabin | UI palette fix, panel shape, camera shake in menu |
| 05-22 | Ali | Instructions view complete |
| 05-23 | Gabin | Ghost AI ring targeting, per-model velocity, norm |
