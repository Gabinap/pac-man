"""Configuration file parser for the Pac-Man game.

Reads and validates the JSON configuration file passed as
a command-line argument. Handles comment stripping, type
checking, value clamping, and unknown key ignoring.
Returns a populated GameConfig instance on success, or
exits cleanly with a descriptive message on failure.
"""

import json
import sys
from typing import Any

from src import constants as C
from src.game_config import GameConfig, LevelConfig


def _strip_comments(text: str) -> str:
    """Remove full-line # and // comments before JSON parsing."""
    lines = []
    for line in text.splitlines():
        stripped = line.lstrip()
        if stripped.startswith(("#", "//")):
            continue
        lines.append(line)
    return "\n".join(lines)


def _clamp_int(
    raw: Any,
    key: str,
    default: int,
    min_val: int | None = 0,
    max_val: int | None = None,
) -> int:
    """Return int, clamped to [min_val, max_val], or default on type error."""
    if not isinstance(raw, int) or isinstance(raw, bool):
        print(
            f"Warning: '{key}' must be an integer"
            f" — using default {default}"
        )
        return default
    value = raw
    if min_val is not None and value < min_val:
        print(
            f"Warning: '{key}' = {value} is below"
            f" minimum {min_val} — clamping"
        )
        value = min_val
    if max_val is not None and value > max_val:
        print(
            f"Warning: '{key}' = {value} is above"
            f" maximum {max_val} — clamping"
        )
        value = max_val
    return value


def _parse_level(raw: Any, index: int) -> LevelConfig:
    """Parse and validate one entry from the levels array."""
    default = LevelConfig(C.DEFAULT_LEVEL_WIDTH, C.DEFAULT_LEVEL_HEIGHT)
    if not isinstance(raw, dict):
        print(
            f"Warning: levels[{index}] is not an object"
            f" — using default {default.width}x{default.height}"
        )
        return default

    width = _clamp_int(
        raw.get("width", default.width),
        f"levels[{index}].width",
        default.width,
        C.MIN_LEVEL_DIM,
        C.MAX_LEVEL_DIM,
    )
    height = _clamp_int(
        raw.get("height", default.height),
        f"levels[{index}].height",
        default.height,
        C.MIN_LEVEL_DIM,
        C.MAX_LEVEL_DIM,
    )

    # A-Maze-ing requires odd dimensions to produce valid corridors
    if width % 2 == 0:
        width += 1
        print(
            f"Warning: levels[{index}].width must be odd"
            f" — adjusted to {width}"
        )
    if height % 2 == 0:
        height += 1
        print(
            f"Warning: levels[{index}].height must be odd"
            f" — adjusted to {height}"
        )

    ambiance: str | None = None
    raw_ambiance = raw.get("ambiance")
    if raw_ambiance is not None:
        if isinstance(raw_ambiance, str) and raw_ambiance in C.AMBIANCES:
            ambiance = raw_ambiance
        else:
            known = ", ".join(C.AMBIANCES.keys())
            print(
                f"Warning: levels[{index}].ambiance"
                f" '{raw_ambiance}' unknown"
                f" — valid: {known} — using random"
            )

    ghost_count: int | None = None
    if "ghost_count" in raw:
        ghost_count = _clamp_int(
            raw["ghost_count"],
            f"levels[{index}].ghost_count",
            C.GHOST_COUNT,
            C.MIN_GHOST_COUNT,
            C.MAX_GHOST_COUNT,
        )

    level_max_time: int | None = None
    if "level_max_time" in raw:
        level_max_time = _clamp_int(
            raw["level_max_time"],
            f"levels[{index}].level_max_time",
            90,
            0,
        )

    return LevelConfig(
        width=width,
        height=height,
        ambiance=ambiance,
        ghost_count=ghost_count,
        level_max_time=level_max_time,
    )


def load_config(path: str) -> GameConfig:
    """Load, validate, and return the game configuration from *path*.

    Args:
        path: Path to the JSON-with-comments config file.

    Returns:
        A fully populated GameConfig with safe defaults for any missing key.
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            raw_text = f.read()
    except FileNotFoundError:
        print(f"Error: config file '{path}' not found")
        sys.exit(1)
    except OSError as e:
        print(f"Error: cannot read '{path}': {e}")
        sys.exit(1)

    cleaned = _strip_comments(raw_text)

    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError as e:
        print(f"Error: '{path}' contains invalid JSON: {e}")
        sys.exit(1)

    if not isinstance(data, dict):
        print(f"Error: '{path}' must contain a JSON object at the top level")
        sys.exit(1)

    config = GameConfig()

    if "highscore_filename" in data:
        value = data["highscore_filename"]
        if isinstance(value, str) and value.strip():
            config.highscore_filename = value.strip()
        else:
            print(
                f"Warning: 'highscore_filename' is invalid"
                f" — using default '{config.highscore_filename}'"
            )

    config.lives = _clamp_int(
        data.get("lives", config.lives),
        "lives", config.lives, C.MIN_LIVES, C.MAX_LIVES
    )
    config.points_per_pacgum = _clamp_int(
        data.get("points_per_pacgum", config.points_per_pacgum),
        "points_per_pacgum",
        config.points_per_pacgum,
    )
    config.points_per_super_pacgum = _clamp_int(
        data.get("points_per_super_pacgum", config.points_per_super_pacgum),
        "points_per_super_pacgum",
        config.points_per_super_pacgum,
    )
    config.points_per_ghost = _clamp_int(
        data.get("points_per_ghost", config.points_per_ghost),
        "points_per_ghost",
        config.points_per_ghost,
    )
    config.seed = _clamp_int(
        data.get("seed", config.seed), "seed", config.seed, min_val=None
    )
    config.level_max_time = _clamp_int(
        data.get("level_max_time", config.level_max_time),
        "level_max_time",
        config.level_max_time,
    )

    if "levels" in data:
        raw_levels = data["levels"]
        if not isinstance(raw_levels, list) or len(raw_levels) < C.MIN_LEVELS:
            print(
                "Warning: 'levels' must be a non-empty list"
                " — using default single level"
            )
        else:
            config.levels = [
                _parse_level(lvl, i) for i, lvl in enumerate(raw_levels)
            ]

    return config
