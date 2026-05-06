"""Ursina application and rendering layer.

Initializes the Ursina app, loads 3D models and assets,
manages the camera (top-down perspective and first-person),
renders all entities each frame, and delegates all game
logic to game_behavior via the global update() callback.
Entry point for the Ursina event loop.
"""

from ursina import (
    color, Entity, Ursina,
    camera, window, mouse, scene,
    held_keys, time
)
from ursina.prefabs.first_person_controller import FirstPersonController

from typing import Any

from src.game_config import GameConfig
from src.maze import Maze


class game_render(Entity):
    def __init__(self, gcf: GameConfig) -> None:
        self.app = Ursina()
        super().__init__()
        self.gcf = gcf
        self._fps_mode = False
        self._fps_ctrl: Any = None

        window.color = color.rgb(0, 0.2, 0)
        camera.position = (0, 7, -2)
        camera.fov = 90
        camera.rotation_x = 80

        Maze(level=next(gcf.levels), seed=gcf.seed)

    def _set_topdown(self) -> None:
        if self._fps_ctrl is not None:
            self._fps_ctrl.enabled = False
        camera.parent = scene
        camera.position = (0, 7, -2)
        camera.rotation_x = 80
        camera.rotation_y = 0
        camera.rotation_z = 0
        camera.fov = 90
        mouse.locked = False
        mouse.visible = True

    def _set_fps(self) -> None:
        if self._fps_ctrl is None:
            self._fps_ctrl = FirstPersonController(
                position=(1, 2, 1),
                gravity=0,
            )
        else:
            self._fps_ctrl.enabled = True
        mouse.locked = True
        mouse.visible = False

    def toggle_fps(self) -> None:
        """Toggle between top-down and FPS camera modes."""
        self._fps_mode = not self._fps_mode
        if self._fps_mode:
            self._set_fps()
        else:
            self._set_topdown()

    def update(self) -> None:
        if self._fps_mode and self._fps_ctrl is not None:
            speed = 5
            if held_keys['space']:
                self._fps_ctrl.y += speed * time.dt
            if held_keys['shift']:
                self._fps_ctrl.y -= speed * time.dt
