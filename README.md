*This project has been created as part of the 42 curriculum by [gagulhon](https://github.com/Gabinap), [aluslu](https://github.com/Yondemon4266)*

<div align="center">

```
██████╗  █████╗  ██████╗      ███╗   ███╗  █████╗  ███╗   ██╗
██╔══██╗██╔══██╗██╔════╝      ████╗ ████║ ██╔══██╗ ████╗  ██║
██████╔╝███████║██║     ▄████╗██╔████╔██║ ███████║ ██╔██╗ ██║
██╔═══╝ ██╔══██║██║           ██║╚██╔╝██║ ██╔══██║ ██║╚██╗██║
██║     ██║  ██║╚██████╗      ██║ ╚═╝ ██║ ██║  ██║ ██║ ╚████║
╚═╝     ╚═╝  ╚═╝ ╚═════╝      ╚═╝     ╚═╝ ╚═╝  ╚═╝ ╚═╝  ╚═══╝

             ·  ·  ·  ·  C>  ·  ·  ·  ·  ·  ·  👻  ·  ·
```

![Python](https://img.shields.io/badge/Python-3.13-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Ursina](https://img.shields.io/badge/Engine-Ursina-FF6B35?style=for-the-badge)
![Panda3D](https://img.shields.io/badge/Backend-Panda3D-2E86AB?style=for-the-badge)
![flake8](https://img.shields.io/badge/Lint-flake8%20%2B%20mypy-4CAF50?style=for-the-badge)
![42](https://img.shields.io/badge/42-Project-000000?style=for-the-badge)

**Waka-waka.** A full 3-D reimagining of the 1980 arcade classic — 10 levels, 7 ambiances, ghosts that actually chase you, and a cheat code only evaluators deserve.

</div>

---

## 🟡 Description

Complete **3-D Pac-Man** in Python 3.13, rendered with the [Ursina](https://www.ursinaengine.org/) engine (Panda3D backend). Every level is a freshly generated maze from the assigned **A-Maze-ing** package, rendered as a textured procedural mesh.

| Feature | Detail |
|---|---|
| Levels | 10, each larger and harder than the last |
| Ambiances | 7 themed worlds — classic, dungeon, manor, forest, ruins, beach, meme |
| Player states | NORMAL · EMPOWERED · STUNNED · UNTOUCHABLE |
| Ghost AI | Distance-minimising pathfinding, reverses when player is empowered |
| Collectibles | Pacgums (dots) + Super-pacgums (power pellets, 4 corners) |
| Audio | Per-ambiance ambient music + UI sound effects |
| Cheat mode | Secret key sequence for evaluators |
| FPS mode | First-person toggle with mouse look |
| Highscores | Persistent top-10, displayed in main menu |

**Game loop:** Main Menu → Start → Play levels → Win / Lose → Enter name → Highscore saved → Back to menu.

---

## 🕹️ Instructions

```bash
make install   # install dependencies (uv required)
make run       # launch with default config
make run <config.json>  # launch with custom config
make debug     # pdb debug mode
make lint      # flake8 + mypy
make clean     # remove caches
```

| Action | Key |
|---|---|
| Move | `↑ ↓ ← →` or `W A S D` |
| Pause | `Escape` |
| FPS toggle | `F` (configurable in Settings) |
| Cheat mode | *type the secret sequence* |

Cheat commands (once unlocked): `I` invincibility · `G` freeze ghosts · `N` next level · `L` +1 life · `Shift`+move speed boost.

---

## 📚 Resources

- [Ursina Engine documentation](https://www.ursinaengine.org/documentation.html)
- [Panda3D manual](https://docs.panda3d.org/1.10/python/index)
- [The Pac-Man Dossier — ghost AI (Jamey Pittman)](https://www.gamedeveloper.com/design/the-pac-man-dossier)
- [mazegenerator A-Maze-ing package](https://github.com/42-AI/A-Maze-ing) — assigned external maze generator

**AI usage — Claude (Anthropic):** code scaffolding (`AnimatedEntity`, bitmask-to-mesh pipeline), refactoring (splitting game loop into subsystems), PEP 257 docstrings across all 38 source files, project management documents, and debugging GLB rendering artifacts. All output was reviewed and understood by both team members before commit.

---

## ⚙️ Configuration

```bash
python3 pac-man.py data/config.json
```

Lines starting with `#` or `//` are treated as comments. Missing or invalid keys are clamped to defaults.

```jsonc
{
    "highscore_filename": "data/highscores.json",
    "lives": 3,
    "points_per_pacgum": 10,
    "points_per_super_pacgum": 100,
    "points_per_ghost": 200,
    "seed": 42,               // fixed seed for level 1
    "level_max_time": 90,     // seconds; 0 = no timer
    // valid ambiances: classic | dungeon | manor | forest | ruins | beach | meme
    // dimensions must be odd numbers
    "levels": [
        {"width": 5,  "height": 5,  "ghost_count": 2},
        {"width": 7,  "height": 7,  "ambiance": "dungeon", "ghost_count": 3},
        {"width": 9,  "height": 9,  "ambiance": "manor"},
        {"width": 11, "height": 11, "ambiance": "forest",  "ghost_count": 5},
        {"width": 11, "height": 11, "ambiance": "ruins",   "ghost_count": 6},
        {"width": 13, "height": 13, "ambiance": "beach",   "ghost_count": 8},
        {"width": 13, "height": 13, "ambiance": "meme",    "ghost_count": 10},
        {"width": 15, "height": 15, "ambiance": "classic", "ghost_count": 12},
        {"width": 17, "height": 17, "ghost_count": 14, "level_max_time": 120},
        {"width": 19, "height": 19, "ghost_count": 16, "level_max_time": 120}
    ]
}
```

---

## 🏆 Highscore

| Property | Value |
|---|---|
| Storage | `data/highscores.json` (path configurable) |
| Capacity | Top 10, sorted descending |
| Player name | 1–10 chars, alphanumeric + spaces |
| Load / Save | At game start / after every session |
| Resilience | Missing or corrupt file → empty list, no crash |
| Display | Main menu, ranked list |

---

## 🌀 Maze Generation

Mazes are generated by the assigned **A-Maze-ing** `mazegenerator` package (v2.0.1), used **as-is**.

Each cell in the returned grid is a 4-bit bitmask encoding open walls (`NORTH=1 EAST=2 SOUTH=4 WEST=8`; value `15` = solid block). Level 1 uses the fixed `seed` from config; subsequent levels use a random seed each session.

`src/gameplay/maze.py` converts the grid into two batched Panda3D meshes (wall boxes + pattern blocks) — the entire maze renders in **two draw calls** regardless of size.

---

## 🔬 Implementation

| Layer | Technology |
|---|---|
| Language | Python 3.13 |
| Game engine | Ursina 0.9+ |
| 3-D backend | Panda3D 1.10 |
| Maze generation | mazegenerator 2.0.1 (external, assigned) |
| Type checking | mypy — disallow-untyped-defs |
| Linting | flake8 — max 79 chars, PEP 257 |
| Package manager | uv |

Movement is grid-aligned: entities move in continuous 3-D space but check wall bitmask flags at each cell boundary. Ghost AI picks the open corridor with minimum squared distance to the player (or to the opposite corner when the player is EMPOWERED). The player follows a four-state machine: `NORMAL → EMPOWERED → NORMAL` and `NORMAL → STUNNED → UNTOUCHABLE → NORMAL`. Unhandled exceptions are caught at top level, logged to `data/crash.log`, and shown as a clean one-liner — no traceback.

---

## 🏗️ General Software Architecture

```
pac-man.py                  ← entry point: arg parse, config load, crash handler
├── src/config/
│   ├── parser.py           ← JSON + comment stripper → GameConfig
│   ├── game_config.py      ← GameConfig / LevelConfig dataclasses
│   ├── constants.py        ← enums, named tuples, global constants
│   ├── controls.py         ← rebindable key bindings
│   ├── input_manager.py    ← cheat buffer, key events
│   ├── audio_manager.py    ← ambient music + SFX
│   └── camera_effects.py   ← top-down / FPS, barrel distortion, shake
├── src/game_engine.py      ← root entity, drives the Ursina update() loop
├── src/gameplay/
│   ├── maze.py             ← bitmask grid → procedural mesh
│   ├── session.py          ← level lifecycle, score, entity ownership
│   ├── ghost_controller.py ← ghost spawning + AI per frame
│   ├── pacgum_controller.py← dot spawning + collision
│   └── entities/           ← AnimatedEntity, Player, Ghost, Pacgum, Floor…
├── src/ui/
│   ├── hud.py              ← score, lives, timer, empowered bar
│   ├── router.py           ← view registry and transitions
│   └── views/              ← MainMenu, Pause, GameOver, NextLevel, Settings…
├── src/utils/              ← Highscores, Timer, shared UI helpers
├── data/                   ← config.json, highscores.json
├── assets/                 ← GLB models, textures, audio (7 ambiances)
├── shaders/                ← barrel distortion GLSL (FPS mode)
└── pm/                     ← project management documents
```

---

## 📊 Project Management

| Document | Contents |
|---|---|
| [`pm/team.md`](pm/team.md) | Roles, responsibilities, workflow |
| [`pm/timeline.md`](pm/timeline.md) | Day-by-day progress (24 days) |
| [`pm/kanban.md`](pm/kanban.md) | Done / In Progress / Backlog |
| [`pm/risk_analysis.md`](pm/risk_analysis.md) | 8 resolved risks + 4 active |
| [`pm/acceptance_tests.md`](pm/acceptance_tests.md) | 60+ manual tests across 13 sections |

**Team:** Gabin (`gagulhon`) — engine architecture, gameplay, norm. Ali (`aluslu`) — UI/UX, HUD, audio, entity polish.

---

<div align="center">

```
·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·
         W A K A - W A K A !     Made with 🟡 at 42
·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·
```

</div>
