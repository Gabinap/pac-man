"""Key binding configuration for player controls."""

from dataclasses import dataclass, field


@dataclass
class ControlsConfig:
    """Default keyboard bindings for all player actions."""
    move_up: str = "w"
    move_down: str = "s"
    move_left: str = "a"
    move_right: str = "d"
    pause: str = "space"
    toggle_hud: str = "h"
    toggle_fps: str = "f"
    menu_moves: list[str] = field(
        default_factory=lambda: ["down arrow", "tab", "up arrow"]
    )
