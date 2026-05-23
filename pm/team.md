# Team Organization

## Members

| Name | Login | Role |
|------|-------|------|
| Gabin Agulhon--Pavageau | gagulhon | Lead architecture, engine, gameplay systems |
| Ali Uslu | aluslu | UI/UX, HUD, game loop, audio |

## Responsibilities

### Gabin
- Project architecture and configuration system (`src/config/`)
- 3D maze generation and rendering (`src/gameplay/maze.py`)
- Player entity, FPS mode, animation system (`src/gameplay/entities/`)
- Ghost AI, pathfinding, BFS routing (`src/gameplay/ghost_controller.py`)
- Pacgum system and 3D pickup models
- Settings view
- Asset pipeline and optimization (`tools/`)
- Norm compliance and code quality (`make lint`, `make lint-strict`)

### Ali
- Main menu and all UI views (`src/ui/views/`)
- HUD (score, lives, timer, empowered bar)
- Highscore system (save/load, name entry)
- Game Over, Victory, Next Level, Instructions screens
- Player/ghost collision and untouchable/blink states
- Loading screen and animations
- Audio manager, sound effects, ambient music (`src/config/audio_manager.py`)
- Entity refactoring (one file per class)
- Difficulty system integration

## Workflow

- Main development on `main` branch
- Feature work on `ali` branch, merged via pull requests
- 3 pull requests merged over the project lifetime (#1, #2, #3)
- Code review done at merge time; norm checked via `make lint`
