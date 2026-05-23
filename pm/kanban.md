# Kanban Board

## Done

### Architecture and Engine
- [x] Project structure, Makefile, uv environment
- [x] Config parsing (JSON with comments, clamped defaults)
- [x] Constants module (`EGameState`, `EGameView`, `EDifficulty`, `ModelSpec`, `Ambiance`)
- [x] `GameEngine` split into `GameSession`, `GhostController`, `PacgumController`
- [x] Entry point with crash logger (`data/crash.log`)

### Maze
- [x] Procedural maze generation (recursive backtracking, configurable size)
- [x] 3D rendering (walls, floor, pattern blocks) with Ursina
- [x] Ambiance system (7 themes: classic, dungeon, manor, forest, ruins, beach, meme)
- [x] Reproducible seed for level 1, random seed for subsequent levels

### Player
- [x] Grid-aligned movement (top-down and FPS mode)
- [x] Spawn animation, idle/walk animation
- [x] Taunt animation (random, periodic)
- [x] NORMAL / UNTOUCHABLE / EMPOWERED / STUNNED states
- [x] Blink on UNTOUCHABLE, teleport to spawn on death
- [x] Cheat mode (invincible + speed boost on Shift)
- [x] FPS camera mode (mouse look)

### Ghosts
- [x] 4 ghost models (Crockie, Grobbo, Halloween Bat, Ophanim Angel, Tuna Fish, Calibur)
- [x] Per-model speed multiplier
- [x] BFS pathfinding
- [x] Ring-based random targeting (8 / 12 / 16 cells by ghost count)
- [x] Flee to home corner when player is EMPOWERED
- [x] Blink and teleport to spawn on stun
- [x] Attack animation on player hit

### Pacgums
- [x] Regular pacgums on every open cell (per-ambiance 3D models)
- [x] 4 super-pacgums near corners
- [x] Player empower on super-pacgum pickup
- [x] Level complete when all pacgums collected

### HUD
- [x] Score display
- [x] Lives display (or infinity symbol)
- [x] Timer bar
- [x] Empowered progress bar
- [x] Pacgum / super-pacgum counters
- [x] HUD hide/show with `h`

### UI Views
- [x] Main menu (difficulty, highscores, start)
- [x] Instructions view
- [x] Settings view (controls, sound volume)
- [x] Pause overlay (Resume, Main menu)
- [x] Next level screen
- [x] Game over / Victory screen (name input, score, register, replay, menu)
- [x] Loading screen with progress bar and images

### Audio
- [x] Audio manager (`src/config/audio_manager.py`)
- [x] Ambient music per ambiance
- [x] Menu button click sounds
- [x] Sound settings in settings view

### Game Loop
- [x] Level progression (1 → 10)
- [x] Per-level ghost count, ambiance, timer, dimensions
- [x] Difficulty (Easy = infinite lives, Medium = config lives, Hard = 1 life)
- [x] Highscore save/load (`data/highscores.json`)
- [x] Timer per level → GAME OVER on expiry
- [x] Score accumulates across levels

### Code Quality
- [x] PEP 8 compliance (`make lint`)
- [x] Strict lint (`make lint-strict`)
- [x] PEP 257 docstrings (English) on all public methods
- [x] French comments translated to English

## In Progress

- [ ] README.md (required sections, 42 header)
- [ ] Game deployment / packaging script
- [ ] Upload to Itch.io or Steam

## Backlog

- [ ] Link sound documentation to instructions view
- [ ] Sound effects for pacgum pickup and ghost eat
