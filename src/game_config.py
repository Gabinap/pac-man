"""Data structures for game configuration.

Defines the GameConfig dataclass populated by the parser
from the JSON configuration file. Contains all tunable
game parameters: lives, scoring values, level definitions,
highscore file path, time limits, and random seed.
"""

from dataclasses import dataclass, field


@dataclass
class LevelConfig:
    """Single level parameters passed to the A-Maze-ing generator."""

    width: int = 11
    height: int = 11


@dataclass
class GameConfig:
    """All tunable game parameters loaded from the JSON config file."""

    highscore_filename: str = "highscores.json"
    lives: int = 3
    points_per_pacgum: int = 10
    points_per_super_pacgum: int = 50
    points_per_ghost: int = 200
    seed: int = 42
    level_max_time: int = 90
    levels: list[LevelConfig] = field(
        default_factory=lambda: [LevelConfig()]
    )
