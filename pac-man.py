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
import warnings
import contextlib
import os
from pathlib import Path
from typing import Any

warnings.filterwarnings("ignore")

from src.config.parser import load_config  # noqa: E402
from src.game_engine import GameEngine  # noqa: E402

_DATA_DIR = Path("data")
_LOG_FILE = _DATA_DIR / "crash.log"

_renderer: "GameEngine | None" = None


def input(key: str) -> None:
    """Global key bindings: configurable FPS toggle."""
    if _renderer is not None and key == _renderer.controls.toggle_fps:
        _renderer.camera_effects.toggle_fps()


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
        if (Path("data") / "config.json").exists():
            return "data/config.json"
    return sys.argv[1]


def _patch_ursina_text() -> None:
    """Guard ursina's font_setter against None font paths in compiled bins.

    In a panda3d compiled binary the CWD changes to the binary directory
    while sys.argv[0] still holds the original relative path, so ursina's
    _search_for_file returns None for every font lookup.  The upstream code
    then crashes on None.parent.  This wraps the setter to fall back to
    panda3d's own FontPool (which uses the VFS model path, already pointing
    at the binary's fonts/ directory) when the file-system search fails.
    """
    import ursina.text as _ut
    from panda3d.core import FontPool

    _orig_setter = _ut.Text.font.fset

    def _safe_setter(self: Any, value: str) -> None:
        try:
            _orig_setter(self, value)
        except AttributeError:
            font = FontPool.load_font(value)
            if font:
                self._font = font
                font.clear()
                font.setPixelsPerUnit(self.resolution)
                font.setLineHeight(self.line_height)
                if self.text:
                    self.text = self.raw_text

    _ut.Text.font = property(_ut.Text.font.fget, _safe_setter)


def _register_gltf_loader() -> None:
    """Register panda3d-gltf's loader with Panda3D's C++ loader registry.

    In a frozen panda3d binary the [panda3d.loaders] entry-point discovery
    that normally runs at panda3d init time cannot read dist-info metadata,
    so GltfLoader is never registered and .glb files are unrecognised.
    Calling register_type() here replicates what the entry-point mechanism
    would do in a normal Python environment.
    """
    try:
        from panda3d.core import LoaderFileTypeRegistry
        from gltf._loader import GltfLoader
        LoaderFileTypeRegistry.get_global_ptr().register_type(GltfLoader)
    except Exception:
        pass


def _fix_binary_paths() -> None:
    """Fix asset/font lookup for compiled panda3d binaries.

    In a compiled binary, sys.argv[0] is a relative path (e.g.
    ./build/manylinux2014_x86_64/pac-man), so application.asset_folder
    and the model path are relative too.  When ursina's load_model globs
    for a file and passes the result to panda3d's loader, panda3d prepends
    the (absolute) model-path entries to the relative file path and produces
    a doubled path that doesn't exist.

    Fix 1: resolve application.asset_folder to an absolute path so every
            subsequent glob and loadModel call uses absolute paths.
    Fix 2: add the binary's fonts/ subdirectory to the model path so
            FontPool.load_font can find the fonts bundled by build_apps.
    """
    from ursina import application as _app
    from panda3d.core import getModelPath
    binary_dir = Path(sys.argv[0]).resolve().parent
    _app.asset_folder = binary_dir
    for sub in ("fonts", "assets/fonts"):
        d = binary_dir / sub
        if d.exists():
            getModelPath().append_path(str(d))


def main() -> None:
    """Run the full game lifecycle: config → menu → game loop → cleanup."""
    global _renderer
    from panda3d.core import loadPrcFileData
    loadPrcFileData("", "notify-level error")
    loadPrcFileData("", "notify-level-ffmpeg error")
    loadPrcFileData("", "notify-level-pnmimage error")
    from ursina import window

    window.show_ursina_splash = False
    _register_gltf_loader()
    _fix_binary_paths()
    _patch_ursina_text()
    config = load_config(_parse_args())
    with open(os.devnull, "w") as devnull, \
            contextlib.redirect_stdout(devnull):
        _renderer = GameEngine(config)
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
