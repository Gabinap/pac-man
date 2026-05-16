"""Game-wide constants for the Pac-Man project.

Defines fixed values used across the application such as
movement speeds, grid dimensions, ghost respawn delays,
power-up durations, and default configuration values.
These values are never modified at runtime.
"""

from enum import Enum, auto
from typing import NamedTuple


class EGameView(Enum):
    MENU = "menu"
    INSTRUCTIONS = "instructions"
    GAME_OVER = "game_over"


class EDifficulty(Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class EGameState(Enum):
    NOT_STARTED = auto()
    RUNNING = auto()
    PAUSE = auto()
    GAME_OVER = auto()
    WIN = auto()


class PacgumSpec(NamedTuple):
    path: str
    scale: float = 0.2
    hover_y: float = 0.4
    rotation_x: float = 0.0


# Super-pacgums use the same PacgumSpec as regular ones — only scaled up
# at render time. Tweak this to make supers more (or less) prominent.
SUPER_PACGUM_SCALE_MULTIPLIER: float = 2.25


class Ambiance(NamedTuple):
    wall: str
    floor: str
    pattern: str
    pacgums: tuple[PacgumSpec, ...]
    super_pacgums: tuple[PacgumSpec, ...]


# --- Config validation bounds ---
DEFAULT_HIGHSCORE_FILE: str = "data/highscores.json"
MIN_LIVES: int = 1
MAX_LIVES: int = 19
MIN_POINTS: int = 1
MIN_LEVEL_DIM: int = 5
MAX_LEVEL_DIM: int = 19
DEFAULT_LEVEL_WIDTH: int = 11
DEFAULT_LEVEL_HEIGHT: int = 11
MIN_LEVELS: int = 1

# --- Gameplay ---
GHOST_COUNT: int = 4

# Movement speeds in cells per second
PLAYER_SPEED: float = 2.0
GHOST_SPEED_NORMAL: float = 1
GHOST_SPEED_FRIGHTENED: float = 2.0
GHOST_SPEED_DEAD: float = 6.0  # returning to spawn after being eaten

# Durations in seconds
FRIGHTENED_DURATION: float = 8.0  # frightened state after a super-pacgum
GHOST_RESPAWN_DELAY: float = 3.0  # pause at spawn before re-entering maze
PLAYER_RESPAWN_DELAY: float = 2.0  # freeze after death before respawn
PLAYER_INVINCIBILITY_DURATION: float = 2.0  # invincibility after respawn


# --- Assets ---
# anim_idle/walk/attack: an int (single animation) or a tuple of ints (a
# random one is picked at each transition into that state).
class ModelSpec(NamedTuple):
    path: str
    anim_idle: int | tuple[int, ...]
    anim_walk: int | tuple[int, ...]
    anim_attack: int | tuple[int, ...]
    rotation_x: float = 0.0
    scale: float = 1
    attack_scale: float = scale
    spawn_y: float = 0.0
    anim_idle_rate: float = 1.0
    anim_walk_rate: float = 1.0
    anim_attack_rate: float = 1.0
    supported: bool = True


# Animations sorted: ['Default_g', 'Idle_g', 'Lunge_g', 'Run1_g', 'Run2_g']
_CROCKIE = ModelSpec(
    path="models/crockie_vgdc.glb",
    scale=0.006,
    attack_scale=0.0018,
    rotation_x=90,
    anim_idle=1,
    anim_walk=(3, 4),  # Run1_g, Run2_g
    anim_attack=2,  # Lunge_g
    supported=False
)

# Animations: ['Moving Idle', 'Tail Swipe']
_GROBBO = ModelSpec(
    path="models/grobbo_alien_hatchling.glb",
    scale=0.00175,
    rotation_x=0,
    anim_idle=0,
    anim_walk=0,
    anim_attack=1,
    attack_scale=0.0011,
    anim_idle_rate=0.05,
    anim_walk_rate=0.6,
    anim_attack_rate=4.0,
    supported=False
)

# Animations: ['BatFlying', 'BatSleeping', 'BatRest']
_HALLOWEEN_BAT = ModelSpec(
    path="models/halloween_bat.glb",
    scale=0.15,
    rotation_x=180,
    spawn_y=0.7,
    anim_idle=0,
    anim_walk=0,
    anim_attack=0,
    attack_scale=0.30,
    anim_idle_rate=0.5,
    anim_walk_rate=1,
    anim_attack_rate=2.0,
    supported=False
)

# Animations: ['Armature.001Armature.002Action.002']
_OPHANIM_ANGEL = ModelSpec(
    path="models/ophanim_angel.glb",
    scale=0.1,
    rotation_x=-90,
    spawn_y=0.75,
    anim_idle=0,
    anim_walk=0,
    anim_attack=0,
    attack_scale=0.28,
    anim_attack_rate=5,
    supported=False
)

# Animations: ['ArmatureArmatureAction']
_SKULL_CRAWLER = ModelSpec(
    path="models/skull_crawler.glb",
    scale=0.07,
    rotation_x=90,
    anim_idle=0,
    anim_walk=0,
    anim_attack=0,
    attack_scale=0.12,
    anim_idle_rate=0.5,
    anim_attack_rate=3,
    supported=False
)

# Animations: ['Swim']
_TUNA_FISH = ModelSpec(
    path="models/tuna_fish.glb",
    scale=0.18,
    rotation_x=90,
    spawn_y=0.5,
    anim_idle=0,
    anim_walk=0,
    anim_attack=0,
    attack_scale=0.3,
    anim_idle_rate=0.5,
    anim_attack_rate=2,
    supported=False
)

# Animations sorted: ['Attack1', 'Attack_Jump', 'Attack_Stabs',
# 'Attack_Stomp', 'Attack_TripleCombo', 'Backstep', 'Death', 'Idle', 'Stun',
# 'Stun_Super', 'Taunt', 'Walk']
_CALIBUR = ModelSpec(
    path="models/calibur_vgdc.glb",
    scale=0.35,
    rotation_x=90,
    anim_idle=7,  # Idle
    anim_walk=11,  # Walk
    anim_attack=(0, 2),  # Attack1/Jump/Stabs/
    attack_scale=0.35
)

# Animations sorted: ['skeleton-skeleton|attack', 'skeleton-skeleton|idle',
# 'skeleton-skeleton|run', 'skeleton-skeleton|spawn',
# 'skeleton-skeleton|taunt']
_ARTOON_SKELETON = ModelSpec(
    path="models/artoon_skeleton.glb",
    scale=0.85,
    rotation_x=90,
    anim_idle=1,  # idle
    anim_walk=2,  # run
    anim_attack=0,  # attack
    attack_scale=0.9,
    supported=False,
)

MODEL_SPECS: list[ModelSpec] = [
    _CROCKIE,  # 0
    _GROBBO,  # 1
    _HALLOWEEN_BAT,  # 2
    _OPHANIM_ANGEL,  # 3
    _SKULL_CRAWLER,  # 4
    _TUNA_FISH,  # 5
    _CALIBUR,  # 6
    _ARTOON_SKELETON,  # 7
]

# Pacgum specs. Loaded via `loader.loadModel` without animation. The split
# between `pacgums` and `super_pacgums` in each Ambiance mirrors gameplay:
# a regular pacgum scores points, a super-pacgum also triggers the
# frightened state on ghosts (and is rendered larger via the multiplier).
_POTATO_CHIPS = PacgumSpec(path="pacgums/potato_chips_tube.glb", scale=1.3)
_COFFEE_MUG = PacgumSpec(path="pacgums/coffee_mug.glb", scale=0.66)
_SODA_CAN = PacgumSpec(path="pacgums/custom_thin_soda_can.glb", scale=0.04)
_SWEDISH_HORSE = PacgumSpec(path="pacgums/dala_swedish_horse.glb")
_DONUT_A = PacgumSpec(path="pacgums/donut_vcbjfbu_low.glb", scale=2.7)
_DONUT_B = PacgumSpec(path="pacgums/donut_vcckafl_low.glb", scale=2.7)
_BUOY = PacgumSpec(path="pacgums/inflatable_buoy.glb")
_RINGS = PacgumSpec(path="pacgums/inflatable_rings.glb", scale=0.05)
_WATERMELON = PacgumSpec(path="pacgums/lowpoly_watermelon.glb")
_PINK_DONUT = PacgumSpec(path="pacgums/pink_donut.glb", scale=0.1)
_POMEGRANATE = PacgumSpec(path="pacgums/pomegranate_scan_lowpoly.glb")
_POTATO = PacgumSpec(path="pacgums/potato_scan_lowpoly.glb")
_ENERGY_CELL = PacgumSpec(path="pacgums/stylized_energy_cell.glb", scale=0.05)

# Textures loaded relative to assets/ (Ursina default search path).
# Pattern marks "solid block" cells (full enclosure) — keep it in the same
# family as the wall so the maze reads as one environment.
# Usage: AMBIANCES["forest"] or random.choice(list(AMBIANCES.values())).
AMBIANCES: dict[str, Ambiance] = {
    "classic": Ambiance(
        wall="textures/wall_brick.jpg",
        floor="textures/floor_marble.jpg",
        pattern="textures/pattern_bathroom.jpg",
        pacgums=(_DONUT_A, _DONUT_B, _COFFEE_MUG),
        super_pacgums=(_PINK_DONUT,) * 4,
    ),
    "dungeon": Ambiance(
        wall="textures/wall_brick.jpg",
        floor="textures/floor_rubble.jpg",
        pattern="textures/wall_brick.jpg",
        pacgums=(_POTATO, _POMEGRANATE),
        super_pacgums=(_ENERGY_CELL,) * 4,
    ),
    "manor": Ambiance(
        wall="textures/wall_fabric.jpg",
        floor="textures/floor_parquet.jpg",
        pattern="textures/wall_wood.jpg",
        pacgums=(_COFFEE_MUG, _PINK_DONUT),
        super_pacgums=(_SWEDISH_HORSE,) * 4,
    ),
    "forest": Ambiance(
        wall="textures/wall_wood.jpg",
        floor="textures/floor_forest.jpg",
        pattern="textures/wall_wood.jpg",
        pacgums=(_POMEGRANATE, _POTATO),
        super_pacgums=(_WATERMELON,) * 4,
    ),
    "ruins": Ambiance(
        wall="textures/wall_brick.jpg",
        floor="textures/floor_moss.jpg",
        pattern="textures/wall_brick.jpg",
        pacgums=(_POTATO,),
        super_pacgums=(_POMEGRANATE,) * 4,
    ),
    "beach": Ambiance(
        wall="textures/wall_wood.jpg",
        floor="textures/floor_sand.jpg",
        pattern="textures/wall_wood.jpg",
        pacgums=(_SODA_CAN, _POTATO_CHIPS, _BUOY),
        super_pacgums=(_RINGS,) * 4,
    ),
    "meme": Ambiance(
        wall="textures/wall_meme.jpg",
        floor="textures/floor_brick.png",
        pattern="textures/wall_meme.jpg",
        pacgums=(_COFFEE_MUG, _PINK_DONUT, _ENERGY_CELL, _SWEDISH_HORSE),
        super_pacgums=(_RINGS,) * 4,
    ),
}
