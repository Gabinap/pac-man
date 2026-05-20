from dataclasses import dataclass


@dataclass
class ControlsConfig:
    move_up: str = "w"
    move_down: str = "s"
    move_left: str = "a"
    move_right: str = "d"
    pause: str = "space"
    toggle_hud: str = "h"
    toggle_fps: str = "f"
