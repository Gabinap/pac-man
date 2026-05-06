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
from panda3d.core import Shader, Texture

from typing import Any

from src.game_config import GameConfig
from src.maze import Maze


class game_render(Entity):
    def __init__(self, gcf: GameConfig) -> None:
        self.app: Any = Ursina()
        super().__init__()
        self.gcf = gcf
        self._fps_mode = False
        self._fps_ctrl: Any = None
        self._barrel_quad: Any = None
        self._manager: Any = None
        self._barrel_strength: float = 0.4

        window.color = color.rgb(0, 0.2, 0)
        Maze(level=gcf.levels[0], seed=gcf.seed)
        self._setup_barrel(strength=0.2)
        self._set_topdown()

    def _setup_barrel(self, strength: float = 0.4) -> None:
        from direct.filter.FilterManager import FilterManager
        self._barrel_strength = strength
        manager = FilterManager(self.app.win, self.app.cam)
        tex = Texture()
        self._barrel_quad = manager.renderSceneInto(colortex=tex)
        self._barrel_quad.setShader(Shader.load(
            Shader.SL_GLSL,
            vertex="shaders/barrel.vert",
            fragment="shaders/barrel.frag",
        ))
        self._barrel_quad.setShaderInput("tex", tex)
        self._barrel_quad.setShaderInput("strength", 0.0)
        self._manager = manager

    def _enable_barrel(self) -> None:
        if self._barrel_quad is not None:
            self._barrel_quad.setShaderInput(
                "strength", self._barrel_strength
            )

    def _disable_barrel(self) -> None:
        if self._barrel_quad is not None:
            self._barrel_quad.setShaderInput("strength", 0.0)

    def _set_topdown(self) -> None:
        if self._fps_ctrl is not None:
            self._fps_ctrl.enabled = False
        camera.parent = scene
        y = max(self.gcf.levels[0].width, self.gcf.levels[0].height) * 0.6
        camera.position = (0, y * 1.25, -y * 0.30)
        camera.rotation_x = 80
        camera.rotation_y = 0
        camera.rotation_z = 0
        camera.fov = 110
        mouse.locked = False
        mouse.visible = True
        self._enable_barrel()

    def _set_fps(self) -> None:
        self._disable_barrel()
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
