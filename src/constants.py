"""Game-wide constants for the Pac-Man project.

Defines fixed values used across the application such as
movement speeds, grid dimensions, ghost respawn delays,
power-up durations, and default configuration values.
These values are never modified at runtime.
"""

from typing import NamedTuple


class Ambiance(NamedTuple):
    wall: str
    floor: str
    pattern: str


# --- Config validation bounds ---
DEFAULT_HIGHSCORE_FILE: str = "data/highscores.json"
MIN_LIVES: int = 1
MAX_LIVES: int = 9
MIN_POINTS: int = 0
MIN_LEVEL_DIM: int = 5
MAX_LEVEL_DIM: int = 19
DEFAULT_LEVEL_WIDTH: int = 11
DEFAULT_LEVEL_HEIGHT: int = 11
MIN_LEVELS: int = 1

# --- Gameplay ---
GHOST_COUNT: int = 4

# Movement speeds in cells per second
PLAYER_SPEED: float = 4.0
GHOST_SPEED_NORMAL: float = 3.5
GHOST_SPEED_FRIGHTENED: float = 2.0
GHOST_SPEED_DEAD: float = 6.0       # returning to spawn after being eaten

# Durations in seconds
FRIGHTENED_DURATION: float = 8.0    # frightened state after a super-pacgum
GHOST_RESPAWN_DELAY: float = 3.0    # pause at spawn before re-entering maze
PLAYER_RESPAWN_DELAY: float = 2.0   # freeze after death before respawn
PLAYER_INVINCIBILITY_DURATION: float = 2.0  # invincibility after respawn

# --- Assets ---
PLAYER_MODEL: str = "player/calibur_vgdc.glb"
GHOST_MODELS: list[str] = [
    "ghosts/crockie_vgdc.glb",
    "ghosts/crocodile.glb",
    "ghosts/grobbo_alien_hatchling.glb",
    "ghosts/skull_crawler.glb",
    "ghosts/volcano_inferno.glb",
]

# Textures loaded relative to assets/ (Ursina default search path).
# Usage: AMBIANCES["forest"] or random.choice(list(AMBIANCES.values())).
AMBIANCES: dict[str, Ambiance] = {
    "classic": Ambiance(
        wall="textures/wall_brick.png",
        floor="textures/floor_marble.png",
        pattern="textures/pattern_bathroom.png",
    ),
    "dungeon": Ambiance(
        wall="textures/wall_plywood.png",
        floor="textures/floor_rubble.png",
        pattern="textures/pattern_bathroom.png",
    ),
    "manor": Ambiance(
        wall="textures/wall_fabric.png",
        floor="textures/floor_parquet.png",
        pattern="textures/pattern_bathroom.png",
    ),
    "forest": Ambiance(
        wall="textures/wall_wood.png",
        floor="textures/floor_forest.png",
        pattern="textures/pattern_bathroom.png",
    ),
    "ruins": Ambiance(
        wall="textures/wall_brick.png",
        floor="textures/floor_moss.png",
        pattern="textures/pattern_bathroom.png",
    ),
    "beach": Ambiance(
        wall="textures/wall_wood.png",
        floor="textures/floor_sand.png",
        pattern="textures/pattern_bathroom.png",
    ),
    "meme": Ambiance(
        wall="textures/wall_meme.png",
        floor="textures/floor_brick.png",
        pattern="textures/pattern_bathroom.png",
    ),
}
