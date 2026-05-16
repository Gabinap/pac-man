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
    """Global key bindings: escape/q to quit, f to toggle FPS view."""
    if key == "escape" or key == "q":
        application.quit()
    if key == "f" and _renderer is not None:
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
    global _renderer
    config = load_config(_parse_args())
    _renderer = GameRender(config)
    _renderer.app.run()


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
