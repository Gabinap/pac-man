"""Data structures for game configuration.

Defines the GameConfig dataclass populated by the parser
from the JSON configuration file. Contains all tunable
game parameters: lives, scoring values, level definitions,
highscore file path, time limits, and random seed.
"""

from dataclasses import dataclass, field
import random


@dataclass
class LevelConfig:
    """Single level parameters passed to the A-Maze-ing generator."""

    width: int = 11
    height: int = 11
    ambiance: str | None = None
    ghost_count: int | None = None  # None → use GameConfig default (4)
    level_max_time: int | None = None  # None → use GameConfig default (90)


@dataclass
class GameConfig:
    """All tunable game parameters loaded from the JSON config file."""

    highscore_filename: str = "data/highscores.json"
    lives: int = 3
    points_per_pacgum: int = 10
    points_per_super_pacgum: int = 100
    points_per_ghost: int = 200
    seed: int = random.randint(0, 1000)
    level_max_time: int = 90
    levels: list[LevelConfig] = field(default_factory=lambda: [LevelConfig()])
