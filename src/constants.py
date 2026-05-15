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
    scale=0.5,
    rotation_x=90,
    anim_idle=1,
    anim_walk=(3, 4),  # Run1_g, Run2_g
    anim_attack=2,  # Lunge_g
    attack_scale=0.4,
)

# Animations: ['005_attack', 'monster_hit', 'monster_death', '002_crit',
# '002_attack', '001_attack', '001_AOE_twohanded', '004_attack', '002_AOE_all',
# '003_crit', '003_attack', '001_victory_all', '009_attack_x3_ogre_01',
# '009_attack_x3_ogre_02', '009_attack_x3_ogre_03', '008_attack_heavyweapon',
# '007_attack_x3_01', '007_attack_x3_02', '005_buff_ogre', 'monster_idle',
# 'monster_run', '001_stun_sleep', 'monster_idle_HeroScene',
# 'idle_interruption2', 'idle_interruption1']
_CROCODILE = ModelSpec(
    path="models/crocodile.glb",
    scale=1.0,
    rotation_x=0,
    anim_idle=19,  # monster_idle
    anim_walk=20,  # monster_run
    anim_attack=(0, 4, 5, 7, 10, 15),  # 005/002/001/004/003_attack + heavy
    attack_scale=0.9,
    supported=False,
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
    anim_attack_rate=1.0,
)

# Animations: ['BatFlying', 'BatSleeping', 'BatRest']
_HALLOWEEN_BAT = ModelSpec(
    path="models/halloween_bat.glb",
    scale=0.15,
    rotation_x=-90,
    spawn_y=0.7,
    anim_idle=0,
    anim_walk=0,
    anim_attack=0,
    attack_scale=0.30,
    anim_idle_rate=0.5,
    anim_walk_rate=1,
    anim_attack_rate=2.0,
)

# Animations: ['Armature.001Armature.002Action.002']
_OPHANIM_ANGEL = ModelSpec(
    path="models/ophanim_angel.glb",
    scale=0.1,
    rotation_x=0,
    spawn_y=0.75,
    anim_idle=0,
    anim_walk=0,
    anim_attack=0,
    attack_scale=0.9,
)

# Animations: ['ArmatureArmatureAction']
_SKULL_CRAWLER = ModelSpec(
    path="models/skull_crawler.glb",
    scale=0.1,
    rotation_x=180,
    anim_idle=0,
    anim_walk=0,
    anim_attack=0,
    attack_scale=0.9,
    supported=False,
)

# Animations: ['Swim']
_TUNA_FISH = ModelSpec(
    path="models/tuna_fish.glb",
    scale=0.2,
    rotation_x=180,
    spawn_y=0.5,
    anim_idle=0,
    anim_walk=0,
    anim_attack=0,
    attack_scale=0.9,
)

# Animations: ['idle', 'run', 'runVariation', 'walk', 'walkVariation',
# 'walkSpellEarthquake', 'spellWalkSheild', 'death']
_VOLCANO_INFERNO = ModelSpec(
    path="models/volcano_inferno.glb",
    scale=1.0,
    rotation_x=0,
    anim_idle=0,  # idle
    anim_walk=(1, 2, 3, 4),  # run, runVariation, walk, walkVariation
    anim_attack=(5, 6),  # walkSpellEarthquake, spellWalkSheild
    attack_scale=0.9,
    supported=False,
)

# Animations: ['Idle', 'Walk', 'Taunt', 'Attack1', 'Attack_Stabs',
# 'Attack_TripleCombo', 'Attack_Jump', 'Attack_Stomp', 'Backstep', 'Stun',
# 'Stun_Super', 'Death']
_CALIBUR = ModelSpec(
    path="models/calibur_vgdc.glb",
    scale=0.5,
    rotation_x=90,
    anim_idle=0,  # Idle
    anim_walk=1,  # Walk
    anim_attack=(3, 4, 5, 6, 7),  # Attack1/Stabs/TripleCombo/Jump/Stomp
)

# Animations sorted: ['skeleton-skeleton|attack', 'skeleton-skeleton|idle',
# 'skeleton-skeleton|run', 'skeleton-skeleton|spawn',
# 'skeleton-skeleton|taunt']
_ARTOON_SKELETON = ModelSpec(
    path="models/artoon_skeleton.glb",
    scale=1.0,
    rotation_x=90,
    anim_idle=1,  # idle
    anim_walk=2,  # run
    anim_attack=0,  # attack
    attack_scale=0.9,
)

MODEL_SPECS: list[ModelSpec] = [
    _CROCKIE,  # 0
    _CROCODILE,  # 1
    _GROBBO,  # 2
    _HALLOWEEN_BAT,  # 3
    _OPHANIM_ANGEL,  # 4
    _SKULL_CRAWLER,  # 5
    _TUNA_FISH,  # 6
    _VOLCANO_INFERNO,  # 7
    _CALIBUR,  # 8
    _ARTOON_SKELETON,  # 9
]

# Static GLBs used as pickups in the maze. Paths are relative to `assets/`.
# Loaded via `loader.loadModel` without animation. The split mirrors the
# gameplay distinction: a regular pacgum scores points, a super-pacgum also
# triggers the frightened state on ghosts.
PACGUM_MODELS: list[str] = [
    "pacgums/cc0_potato_chips_tube_2.glb",
    "pacgums/coffee_mug.glb",
    "pacgums/custom_thin_soda_can.glb",
    "pacgums/dala_swedish_horse.glb",
    "pacgums/donut_vcbjfbu_low.glb",
    "pacgums/donut_vcckafl_low.glb",
    "pacgums/inflatable_buoy.glb",
    "pacgums/lowpoly_watermelon.glb",
    "pacgums/pink_donut.glb",
    "pacgums/pomegranate_scan_lowpoly.glb",
    "pacgums/potato_scan_lowpoly.glb",
    "pacgums/stylized_energy_cell.glb",
]

SUPER_PACGUM_MODELS: list[str] = [
    "pacgums/super_pacgum_game_ready_free_inflatable_rings.glb",
]

PLAYER_SPEC: ModelSpec = _CALIBUR

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
