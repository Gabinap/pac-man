"""Game-wide constants for the Pac-Man project.

Defines fixed values used across the application such as
movement speeds, grid dimensions, ghost respawn delays,
power-up durations, and default configuration values.
These values are never modified at runtime.
"""

# --- Config validation bounds ---
DEFAULT_HIGHSCORE_FILE: str = "highscores.json"
MIN_LIVES: int = 1
MAX_LIVES: int = 9
MIN_POINTS: int = 0
MIN_LEVEL_DIM: int = 5
MAX_LEVEL_DIM: int = 99
DEFAULT_LEVEL_WIDTH: int = 21
DEFAULT_LEVEL_HEIGHT: int = 21
MIN_LEVELS: int = 1

