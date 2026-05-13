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
GHOST_SPEED_NORMAL: float = 2.6
GHOST_SPEED_FRIGHTENED: float = 2.0
GHOST_SPEED_DEAD: float = 6.0  # returning to spawn after being eaten

# Durations in seconds
FRIGHTENED_DURATION: float = 8.0  # frightened state after a super-pacgum
GHOST_RESPAWN_DELAY: float = 3.0  # pause at spawn before re-entering maze
PLAYER_RESPAWN_DELAY: float = 2.0  # freeze after death before respawn
PLAYER_INVINCIBILITY_DURATION: float = 2.0  # invincibility after respawn


# --- Assets ---
class ModelSpec(NamedTuple):
    path: str
    scale: float
    rotation_x: float
    anim_idle: int
    anim_idle_rate: float
    anim_walk: int
    anim_walk_rate: float
    anim_attack: int
    anim_attack_rate: float
    attack_scale: float
    supported: bool = True


# Animations: ['Idle_g', 'Run1_g', 'Run2_g', 'Lunge_g', 'Default_g']
_CROCKIE = ModelSpec(
    path="ghosts/crockie_vgdc.glb",
    scale=1.0,
    rotation_x=0,
    anim_idle=0,
    anim_idle_rate=1.0,
    anim_walk=1,
    anim_walk_rate=1.0,
    anim_attack=3,
    anim_attack_rate=1.0,
    attack_scale=0.9,
)

# Animations: ['Moving Idle', 'Tail Swipe']
_GROBBO = ModelSpec(
    path="ghosts/grobbo_alien_hatchling.glb",
    scale=0.00175,
    rotation_x=-90,
    anim_idle=0,
    anim_idle_rate=0.05,
    anim_walk=0,
    anim_walk_rate=0.2,
    anim_attack=1,
    anim_attack_rate=1.0,
    attack_scale=0.001,
)

GHOST_SPECS: list[ModelSpec] = [
    _GROBBO,  # 0
    ModelSpec(
        "ghosts/crocodile.glb", 1.0, 0, 0, 1.0, 0, 1.0, 0, 1.0, 0.9, False
    ),  # 1
    _GROBBO,  # 2
    ModelSpec(
        "ghosts/skull_crawler.glb", 1.0, 0, 0, 1.0, 0, 1.0, 0, 1.0, 0.9, False
    ),  # 3
    ModelSpec(
        "ghosts/volcano_inferno.glb",
        1.0,
        0,
        0,
        1.0,
        0,
        1.0,
        0,
        1.0,
        0.9,
        False,
    ),  # 4
]

PLAYER_SPEC: ModelSpec = _CROCKIE

# Textures loaded relative to assets/ (Ursina default search path).
# Usage: AMBIANCES["forest"] or random.choice(list(AMBIANCES.values())).
AMBIANCES: dict[str, Ambiance] = {
    "classic": Ambiance(
        wall="textures/wall_brick.jpg",
        floor="textures/floor_marble.jpg",
        pattern="textures/pattern_bathroom.jpg",
    ),
    "dungeon": Ambiance(
        wall="textures/wall_plywood.jpg",
        floor="textures/floor_rubble.jpg",
        pattern="textures/pattern_bathroom.jpg",
    ),
    "manor": Ambiance(
        wall="textures/wall_fabric.jpg",
        floor="textures/floor_parquet.jpg",
        pattern="textures/pattern_bathroom.jpg",
    ),
    "forest": Ambiance(
        wall="textures/wall_wood.jpg",
        floor="textures/floor_forest.jpg",
        pattern="textures/pattern_bathroom.jpg",
    ),
    "ruins": Ambiance(
        wall="textures/wall_brick.jpg",
        floor="textures/floor_moss.jpg",
        pattern="textures/pattern_bathroom.jpg",
    ),
    "beach": Ambiance(
        wall="textures/wall_wood.jpg",
        floor="textures/floor_sand.jpg",
        pattern="textures/pattern_bathroom.jpg",
    ),
    "meme": Ambiance(
        wall="textures/wall_meme.jpg",
        floor="textures/floor_brick.png",
        pattern="textures/pattern_bathroom.jpg",
    ),
}
