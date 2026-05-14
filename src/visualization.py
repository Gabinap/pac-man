"""Ursina application and rendering layer.

Initializes the Ursina app, manages the main menu and game views,
loads 3D models and assets, manages the camera (top-down perspective
and first-person), renders all entities each frame, and delegates all
game logic to game_behavior via the global update() callback.
Entry point for the Ursina event loop.
"""

from ursina import (
    color,
    Entity,
    Ursina,
    camera,
    window,
    mouse,
    scene,
    held_keys,
    time,
    application,
)
from ursina.prefabs.first_person_controller import FirstPersonController
from panda3d.core import Shader, Texture
from enum import Enum
from typing import Any

import random
from src.constants import AMBIANCES
from src.entities import Player
from src.game_config import GameConfig
from src.maze import Maze
from src.views.base import BaseView
from src.views.main_menu import MainMenuView
from src.views.instructions import InstructionsView
from src.views.game_over import GameOverView
from src.game_behavior.ghost_controller import GhostController, GhostState


class EGameView(Enum):
    MENU = "menu"
    GAME = "game"
    INSTRUCTIONS = "instructions"
    GAME_OVER = "game_over"


class GameRender(Entity):
    def __init__(self, gcf: GameConfig) -> None:
        self.app: Any = Ursina(development_mode=True)
        super().__init__()
        self.gcf = gcf
        self._fps_mode = False
        self._fps_ctrl: Any = None
        self._barrel_quad: Any = None
        self._manager: Any = None
        self._barrel_strength: float = 0.2
        self._game_initialized = False
        self._views: dict[EGameView, BaseView] = {}
        self._current: EGameView | None = None

        window.color = color.black
        window.exit_button.enabled = False

        self._register(
            EGameView.MENU,
            MainMenuView(
                self.gcf,
                start_game=lambda: self.switch_view(EGameView.GAME),
                show_instructions=lambda: self.switch_view(
                    EGameView.INSTRUCTIONS
                ),
            ),
        )
        self._register(
            EGameView.INSTRUCTIONS,
            InstructionsView(
                back_callback=lambda: self.switch_view(EGameView.MENU),
            ),
        )
        self._register(
            EGameView.GAME_OVER,
            GameOverView(
                submit_callback=self._on_replay,
                menu_callback=lambda: self.switch_view(EGameView.MENU),
            ),
        )
        self.switch_view(EGameView.MENU)

    def _register(self, name: EGameView, view: BaseView) -> None:
        self._views[name] = view

    def _init_game(self) -> None:
        """Build maze, camera, and barrel distortion
        (runs once on first Start)."""
        if self._game_initialized:
            return
        self._game_initialized = True
        window.color = color.rgb(0, 0.2, 0)
        level = self.gcf.levels[0]
        ambiance = (
            AMBIANCES[level.ambiance]
            if level.ambiance is not None
            else random.choice(list(AMBIANCES.values()))
        )
        self.maze = Maze(level=level, seed=self.gcf.seed, ambiance=ambiance)
        self._setup_barrel(strength=self._barrel_strength)
        self._set_topdown()

        self._player = Player(self.maze, self.gcf)
        self._ghost_controller = GhostController(self._player, self.maze)

    def _setup_barrel(self, strength: float = 0.2) -> None:
        from direct.filter.FilterManager import FilterManager

        self._barrel_strength = strength
        manager = FilterManager(self.app.win, self.app.cam)
        tex = Texture()
        self._barrel_quad = manager.renderSceneInto(colortex=tex)
        self._barrel_quad.setShader(
            Shader.load(
                Shader.SL_GLSL,
                vertex="shaders/barrel.vert",
                fragment="shaders/barrel.frag",
            )
        )
        self._barrel_quad.setShaderInput("tex", tex)
        self._barrel_quad.setShaderInput("strength", 0.0)
        self._manager = manager

    def _enable_barrel(self) -> None:
        if self._barrel_quad is not None:
            self._barrel_quad.setShaderInput("strength", self._barrel_strength)

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

    def switch_view(self, target: EGameView) -> None:
        if self._current is not None and self._current in self._views:
            old = self._views[self._current]
            old.on_exit()
            old.disable()

        self._current = target

        if target == EGameView.GAME_OVER:
            application.paused = True
        if target == EGameView.GAME:
            application.paused = False
            self._init_game()
            return

        view = self._views[target]
        view.enable()
        view.on_enter()

    def _on_replay(self, player_name: str) -> None:
        print(f"Saved score for : {player_name}")
        self._game_initialized = False
        self.switch_view(EGameView.GAME)

    def update(self) -> None:
        if self._game_initialized and self._current == EGameView.GAME:
            if self._player.health <= 0:
                self.switch_view(EGameView.GAME_OVER)
                return
            self._ghost_controller.update_ghosts()

        if self._fps_mode and self._fps_ctrl is not None:
            speed = 5
            if held_keys["space"]:
                self._fps_ctrl.y += speed * time.dt
            if held_keys["shift"]:
                self._fps_ctrl.y -= speed * time.dt
