from typing import Any
import random

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
    destroy,
)
from ursina.prefabs.first_person_controller import FirstPersonController
from panda3d.core import Shader, Texture

import src.constants as C
from src.entities import Player
from src.game_config import GameConfig
from src.maze import Maze
from src.views.base import BaseView
from src.views.main_menu import MainMenuView
from src.views.instructions import InstructionsView
from src.views.game_over import GameOverView
from src.game_behavior.ghost_controller import GhostController
from src.highscores import Highscores


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
        self.game_state = C.EGameState.NOT_STARTED
        self._difficulty = C.EDifficulty.MEDIUM
        self.scores_manager = Highscores(self.gcf)
        self.score = 0

        self.maze: Maze | None = None
        self._player: Player | None = None
        self._ghost_controller: GhostController | None = None

        window.color = color.black
        window.exit_button.enabled = False

        self._setup_barrel()

        self._views: dict[C.EGameView, BaseView] = {}
        self._current: C.EGameView | None = None
        self._register_views()

        self._init_game()
        self.switch_view(C.EGameView.GAME_OVER)

    def _register_views(self) -> None:
        self._views[C.EGameView.MENU] = MainMenuView(
            self.gcf,
            self.scores_manager,
            self._difficulty,
            start_game=self.start_game,
            show_instructions=lambda: self.switch_view(
                C.EGameView.INSTRUCTIONS
            ),
        )
        self._views[C.EGameView.INSTRUCTIONS] = InstructionsView(
            back_callback=lambda: self.switch_view(C.EGameView.MENU),
        )
        self._views[C.EGameView.GAME_OVER] = GameOverView(
            scores_manager=self.scores_manager,
            score_callback=self.get_score,
            menu_callback=lambda: self.switch_view(C.EGameView.MENU),
            replay_callback=self.start_game,
        )

    def start_game(self) -> None:
        for view in self._views.values():
            view.disable()

        if self.game_state == C.EGameState.GAME_OVER:
            self._destroy_entities()
            self._init_game()

        self.game_state = C.EGameState.RUNNING

        if self._player:
            self._player.game_state = self.game_state
        if self._ghost_controller:
            self._ghost_controller.game_state = self.game_state

        application.paused = False

    def _destroy_entities(self) -> None:
        if not self._game_initialized:
            return

        if self.maze:
            destroy(self.maze)
        if self._player:
            destroy(self._player)
        if self._ghost_controller:
            for ghost in self._ghost_controller.ghosts:
                destroy(ghost)

        self._game_initialized = False

    def _init_game(self) -> None:
        window.color = color.rgb(0, 0.2, 0)
        level = self.gcf.levels[0]
        ambiance = (
            C.AMBIANCES[level.ambiance]
            if level.ambiance is not None
            else random.choice(list(C.AMBIANCES.values()))
        )
        self.score = 0
        self.maze = Maze(level=level, seed=self.gcf.seed, ambiance=ambiance)
        self._set_topdown()

        self._player = Player(self.maze, self.gcf, self.game_state)
        self._ghost_controller = GhostController(
            self._player, self.maze, self.game_state
        )

        self._game_initialized = True

    def _setup_barrel(self) -> None:
        from direct.filter.FilterManager import FilterManager

        if self._manager is not None:
            return
        self._manager = FilterManager(self.app.win, self.app.cam)
        tex = Texture()
        self._barrel_quad = self._manager.renderSceneInto(colortex=tex)
        self._barrel_quad.setShader(
            Shader.load(
                Shader.SL_GLSL,
                vertex="shaders/barrel.vert",
                fragment="shaders/barrel.frag",
            )
        )
        self._barrel_quad.setShaderInput("tex", tex)
        self._barrel_quad.setShaderInput("strength", 0.0)

    def _enable_barrel(self) -> None:
        if self._barrel_quad:
            self._barrel_quad.setShaderInput("strength", self._barrel_strength)

    def _disable_barrel(self) -> None:
        if self._barrel_quad:
            self._barrel_quad.setShaderInput("strength", 0.0)

    def _set_topdown(self) -> None:
        if self._fps_ctrl:
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
                position=(1, 2, 1), gravity=0
            )
        else:
            self._fps_ctrl.enabled = True

        mouse.locked = True
        mouse.visible = False

    def toggle_fps(self) -> None:
        self._fps_mode = not self._fps_mode
        if self._fps_mode:
            self._set_fps()
        else:
            self._set_topdown()

    def switch_view(self, target: C.EGameView) -> None:
        if self._current and self._current in self._views:
            old = self._views[self._current]
            old.on_exit()
            old.disable()

        self._current = target

        if target == C.EGameView.GAME_OVER:
            application.paused = True

        view = self._views[target]
        view.enable()
        view.on_enter()

    def get_score(self) -> int:
        return self.score

    def update(self) -> None:
        if self._fps_mode and self._fps_ctrl:
            speed = 5
            if held_keys["space"]:
                self._fps_ctrl.y += speed * time.dt
            if held_keys["shift"]:
                self._fps_ctrl.y -= speed * time.dt

        if (
            not self._game_initialized
            or self.game_state != C.EGameState.RUNNING
        ):
            return

        if self._player and self._ghost_controller:
            if self._player.health <= 0:
                self.game_state = C.EGameState.GAME_OVER
                self._player.game_state = self.game_state
                self._ghost_controller.game_state = self.game_state
                self.switch_view(C.EGameView.GAME_OVER)
                return
            self._ghost_controller.update_ghosts()
