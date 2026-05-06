"""Entry point for the Pac-Man game.

Validates the command-line argument, loads the configuration,
and launches the Ursina visualization layer.
Any unhandled exception is caught at the top level, logged to
data/crash.log, and reported cleanly — no Python traceback shown.

Usage:
    python3 pac-man.py <config.json>
"""

import sys
import logging
import traceback
from pathlib import Path
from ursina import application

from src.parser import load_config
from src.visualization import GameRender

_DATA_DIR = Path("data")
_LOG_FILE = _DATA_DIR / "crash.log"

_renderer: "GameRender | None" = None


def input(key: str) -> None:
    if key == 'escape' or key == 'q':
        application.quit()
    if key == 'f' and _renderer is not None:
        _renderer.toggle_fps()


def _setup_crash_logger() -> logging.Logger:
    """Return a logger that appends crash reports to data/crash.log."""
    try:
        _DATA_DIR.mkdir(exist_ok=True)
    except OSError as e:
        print(
            f"Warning: could not create '{_DATA_DIR}': {e}"
            " — crash logging disabled"
        )
        return logging.getLogger("pacman.crash.null")

    logger = logging.getLogger("pacman.crash")
    logger.setLevel(logging.ERROR)
    if not logger.handlers:
        handler = logging.FileHandler(_LOG_FILE, encoding="utf-8")
        handler.setFormatter(
            logging.Formatter(
                "%(asctime)s  %(levelname)s\n%(message)s\n" + "-" * 60
            )
        )
        logger.addHandler(handler)
    return logger


def _parse_args() -> str:
    """Return the config file path, or exit cleanly on bad usage."""
    if len(sys.argv) != 2:
        print("Usage: python3 pac-man.py <config.json>")
        sys.exit(1)
    return sys.argv[1]


def main() -> None:
    """Run the full game lifecycle: config → menu → game loop → cleanup."""

    # --- 1. Configuration ---
    # load_config strips comments, validates every key, clamps bad values,
    # and calls sys.exit(1) with a clear message on fatal errors (missing file,
    # invalid JSON). Unknown keys are silently ignored.
    global _renderer
    gcf = load_config(_parse_args())
    _renderer = GameRender(gcf)  # app.run() is called inside __init__

    # --- 2. Visualization / game loop ---
    # TODO: call visualization.run(gcf) once the Ursina layer is implemented.
    #
    # visualization.run(gcf) will:
    #
    #   a) Window setup
    #      - Open an Ursina window (title "Pac-Man", resolution configurable).
    #      - Set up the camera top-down (or toggle FPS with a key).
    #
    #   b) Asset loading
    #      - Load wall, floor, pacgum, super-pacgum, ghost and player models.
    #      - Load sound effects (waka, death, power-up, ghost eaten).
    #
    #   c) Main menu
    #      - Display: Start Game | View Highscores | Instructions | Exit.
    #      - Load highscores from gcf.highscore_filename (missing = ok).
    #      - Show the top-10 scores on the highscores screen.
    #
    #   d) Level initialisation  (called once per level)
    #      - Generate the maze via the A-Maze-ing package:
    #            mazegenerator(width, height, seed, PERFECT=False)
    #        The first level uses gcf.seed; next levels use a random seed.
    #      - Spawn Player at the center of the maze.
    #      - Spawn 4 Ghosts, one in each corner.
    #      - Place Pacgums (small dots) in every open corridor.
    #      - Place SuperPacgums (power pellets) in the 4 corner cells.
    #
    #   e) Game loop  — Ursina calls game_behavior.update() every frame
    #      - Read buffered input (arrow keys / WASD) and move the player
    #        one cell if the target corridor is passable.
    #      - Move each ghost according to its AI:
    #            • Normal state  → chase player (distance-based or random).
    #            • Frightened state → flee player (triggered by super-pacgum).
    #            • Dead state    → respawn at home corner after a delay.
    #      - Collision detection:
    #            • Pacgum hit → remove dot, score += gcf.points_per_pacgum.
    #            • SuperPacgum hit → remove pellet,
    #                                score += gcf.points_per_super_pacgum,
    #                                all ghosts enter frightened state.
    #            • Ghost (frightened) → remove, score += gcf.points_per_ghost.
    #            • Ghost (normal) → lives -= 1, respawn player at center.
    #      - HUD update every frame: score | lives | level | remaining time.
    #      - Level clear → all pacgums eaten → next level (keep score + lives).
    #      - Timeout → gcf.level_max_time reached → restart level or game over
    #                        (implementation choice, document in README).
    #      - Game over     → lives == 0 → show Game Over screen.
    #      - Victory       → all levels completed → show Victory screen.
    #
    #   f) End-of-game screen (win or lose)
    #      - Display final score.
    #      - Prompt player name (max 10 alphanumeric chars + spaces).
    #      - Append entry to highscore list, keep top 10, save to disk.
    #      - Return to main menu.
    #
    #   g) Cheat mode  (activated by a key combination, for peer review)
    #      - Invincibility  : ghosts cannot kill the player.
    #      - Level skip     : immediately complete the current level.
    #      - Ghost freeze   : all ghosts stop moving.
    #      - Extra lives    : add lives to the player.
    #      - Speed boost    : player moves faster.

    # TODO: replace with visualization.run(gcf)
    print(
        f"Config OK — {len(gcf.levels)} level(s),"
        f" lives={gcf.lives}, seed={gcf.seed}"
    )
    print("Visualization not yet implemented.")


if __name__ == "__main__":
    _crash_log = _setup_crash_logger()
    try:
        main()
    except KeyboardInterrupt:
        print("\nGame interrupted.")
        sys.exit(0)
    except Exception as exc:
        _crash_log.error(
            "%s: %s\n%s", type(exc).__name__, exc, traceback.format_exc()
        )
        print(
            f"Unexpected error: {type(exc).__name__}: {exc}\n"
            f"Details logged to {_LOG_FILE}"
        )
        sys.exit(1)
