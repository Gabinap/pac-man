"""Ursina runtime: window, camera, views, and per-frame game loop.

Owns the lifecycle of the player, ghosts, maze, and pacgums, and routes
input/state changes to the right subsystem.
"""

from typing import Any
import random

from ursina import (
    color,
    Entity,
    Ursina,
    Button,
    camera,
    window,
    mouse,
    scene,
    held_keys,
    time,
    application,
    destroy,
    invoke,
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
from src.views.pause import PauseView
from src.game_behavior.ghost_controller import GhostController
from src.game_behavior.pacgum_controller import PacgumController
from src.highscores import Highscores
from src.hud import HUD
from src.timer import Timer


class GameRender(Entity):
    """Owns the Ursina app, the active view, and the in-game entities."""

    def __init__(self, config: GameConfig) -> None:
        self.app: Any = Ursina(development_mode=False)
        super().__init__()
        self.config = config

        self._fps_mode = False
        self._fps_ctrl: Any = None
        self._barrel_quad: Any = None
        self._manager: Any = None
        self._barrel_strength: float = 0.2
        self._shake_active: bool = False

        self._game_initialized = False
        self._game_state = C.EGameState.NOT_STARTED
        self._difficulty = C.EDifficulty.MEDIUM
        self._current_level_index = 0
        self._is_win = False
        self._cheat_mode: bool = False
        self._key_buffer: str = ""
        self._ignore_next_space: bool = False
        self._cheat_bar: Entity = Entity(
            parent=camera.ui,
            model="quad",
            color=color.red,
            scale=(2, 0.008),
            position=(0, -0.49, -0.5),
            enabled=False,
        )
        self.scores_manager = Highscores(self.config)
        self._score = 0
        self._timer: Timer | None = None
        self.maze: Maze | None = None
        self._player: Player | None = None
        self._ghost_controller: GhostController | None = None
        self._pacgum_controller: PacgumController | None = None
        self._hud: HUD | None = None

        window.color = color.black
        window.exit_button.enabled = False

        self._setup_barrel()
        self._preload_assets()

        self._views: dict[C.EGameView, BaseView] = {}
        self._current: C.EGameView | None = None
        self._register_views()

        self._hud = HUD(
            view_mode=C.EViewMode.TOPDOWN,
            get_score=lambda: self._score,
            get_health=self._get_health,
            get_level=lambda: self._current_level_index + 1,
            get_pacgums=self._get_pacgum_count,
            get_super_pacgums=self._get_super_count,
            get_ghosts_killed=lambda: 0,
        )
        self._hud.hide()
        self._init_game()
        self.switch_view(C.EGameView.MENU)

    @property
    def game_state(self) -> C.EGameState:
        return self._game_state

    @game_state.setter
    def game_state(self, value: C.EGameState) -> None:
        self._game_state = value
        if self._player is not None:
            self._player.game_state = value
        if self._ghost_controller is not None:
            self._ghost_controller.game_state = value

    def _get_health(self) -> int:
        if self._player is None:
            return 0
        if self._player.infinite_lives or self._player.cheat_mode:
            return -1
        return self._player.health

    def _get_pacgum_count(self) -> int:
        if self._pacgum_controller is None:
            return 0
        return sum(
            1 for p in self._pacgum_controller.pacgums if not p.is_super
        )

    def _get_super_count(self) -> int:
        if self._pacgum_controller is None:
            return 0
        return sum(
            1 for p in self._pacgum_controller.pacgums if p.is_super
        )

    def _preload_assets(self) -> None:
        """Warm Panda3D's loader cache with every model we may need at
        runtime. Without this, the first frame that spawns a ghost or
        pacgum pays the parse-and-upload cost mid-game; doing it upfront
        moves the spike to startup where the menu masks it.
        """
        loader: Any = self.app.loader
        for spec in C.MODEL_SPECS:
            if spec.supported:
                loader.loadModel(f"assets/{spec.path}")
        seen: set[str] = set()
        for amb in C.AMBIANCES.values():
            for p_spec in (*amb.pacgums, *amb.super_pacgums):
                if p_spec.path in seen:
                    continue
                seen.add(p_spec.path)
                loader.loadModel(f"assets/{p_spec.path}")

    def _register_views(self) -> None:
        self._views[C.EGameView.MENU] = MainMenuView(
            self.config,
            self.scores_manager,
            self._difficulty,
            start_game=self.start_game,
            show_instructions=lambda: self.switch_view(
                C.EGameView.INSTRUCTIONS
            ),
            set_difficulty=lambda d: setattr(self, "_difficulty", d),
        )
        self._views[C.EGameView.INSTRUCTIONS] = InstructionsView(
            back_callback=lambda: self.switch_view(C.EGameView.MENU),
        )
        self._views[C.EGameView.GAME_OVER] = GameOverView(
            scores_manager=self.scores_manager,
            score_callback=lambda: self.score,
            menu_callback=lambda: self.switch_view(C.EGameView.MENU),
            replay_callback=self.start_game,
            get_is_win=lambda: self._is_win,
        )
        self._views[C.EGameView.PAUSE] = PauseView(
            resume_callback=self._resume_game,
            menu_callback=self._quit_to_menu,
        )

    def start_game(self) -> None:
        self._ignore_next_space = True
        for view in self._views.values():
            view.disable()

        if self.game_state == C.EGameState.GAME_OVER:
            self._destroy_entities()
            self.score = 0
            self._current_level_index = 0
            self._is_win = False
            self._init_game()

        self._current = None
        self.game_state = C.EGameState.RUNNING
        if self._hud:
            self._hud.show()
        if self._timer:
            self._timer.launch_timer()
        application.paused = False

    def _destroy_entities(self) -> None:
        if not self._game_initialized:
            return

        if self._timer:
            self._timer.destroy_timer()
        if self.maze:
            destroy(self.maze)
        if self._player:
            destroy(self._player)
        if self._ghost_controller:
            for ghost in self._ghost_controller.ghosts:
                destroy(ghost)
        if self._pacgum_controller:
            self._pacgum_controller.destroy_all()

        self._game_initialized = False

    def _init_game(self) -> None:
        window.color = color.rgb(0, 0.2, 0)
        level = self.config.levels[self._current_level_index]
        ambiance = (
            C.AMBIANCES[level.ambiance]
            if level.ambiance is not None
            else random.choice(list(C.AMBIANCES.values()))
        )
        ghost_count = (
            level.ghost_count
            if level.ghost_count is not None
            else C.GHOST_COUNT
        )
        level_max_time = (
            level.level_max_time
            if level.level_max_time is not None
            else self.config.level_max_time
        )
        self._timer = Timer(level_max_time)
        seed = (
            self.config.seed
            if self._current_level_index == 0
            else random.randint(0, 2 ** 31)
        )
        self.maze = Maze(level=level, seed=seed, ambiance=ambiance)
        self._set_topdown()
        if self._difficulty == C.EDifficulty.EASY:
            effective_lives = 0
        elif self._difficulty == C.EDifficulty.HARD:
            effective_lives = 1
        else:
            effective_lives = self.config.lives
        self._player = Player(
            self.maze, self.config, self.game_state, lives=effective_lives
        )
        self._player.cheat_mode = self._cheat_mode
        self._ghost_controller = GhostController(
            self._player, self.maze, self.game_state, ghost_count
        )
        self._pacgum_controller = PacgumController(
            self._player, self.maze, ambiance, self.config,
            self.add_score, self.on_level_complete
        )

        self._game_initialized = True

    @property
    def score(self) -> int:
        return self._score

    @score.setter
    def score(self, value: int) -> None:
        self._score = value

    def add_score(self, points: int) -> None:
        self.score += points

    def _quit_to_menu(self) -> None:
        self._destroy_entities()
        self.score = 0
        self._current_level_index = 0
        self._is_win = False
        self.game_state = C.EGameState.NOT_STARTED
        self._init_game()
        application.paused = False
        self.switch_view(C.EGameView.MENU)

    def _resume_game(self) -> None:
        if self._current and self._current in self._views:
            self._views[self._current].on_exit()
            self._views[self._current].disable()
        self._current = None
        self.game_state = C.EGameState.RUNNING
        application.paused = False

    def on_level_complete(self) -> None:
        if self._timer and self._timer.is_running:
            self._timer.stop()
            self.add_score(self._timer.duration)
        self._current_level_index += 1
        if self._current_level_index >= len(self.config.levels):
            self._is_win = True
            self.game_state = C.EGameState.GAME_OVER
            self.switch_view(C.EGameView.GAME_OVER)
            return
        self._destroy_entities()
        self._init_game()
        # _init_game creates fresh entities with the current game_state, so
        # no manual sync is needed here.
        if self._timer:
            self._timer.launch_timer()
        self._set_topdown()

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
        lvl = self.config.levels[self._current_level_index]
        y = max(lvl.width, lvl.height) * 0.6
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
            if self._hud:
                self._hud.hide()
            if self._timer:
                self._timer.stop()
                self._timer.hide()
        elif target == C.EGameView.PAUSE:
            application.paused = True
        elif target == C.EGameView.MENU:
            application.paused = False
            if self._hud:
                self._hud.hide()
            if self._timer:
                self._timer.stop()
                self._timer.hide()

        view = self._views[target]
        view.enable()
        view.on_enter()

    def _set_cheat(self, on: bool) -> None:
        if self._cheat_mode == on:
            return
        self._cheat_mode = on
        if self._player:
            self._player.cheat_mode = on
        self._cheat_bar.enabled = on

    def _shake_screen(
        self, mag: float = 0.3, dur: float = 0.25, period: float = 0.03
    ) -> None:
        # Top-down camera looks down the Y axis, so shake X/Z (horizontal
        # plane) for a 2D screen-space jitter. Y would change "altitude"
        # and read as zoom, not shake.
        if self._shake_active:
            return
        self._shake_active = True
        base_x, base_z = camera.x, camera.z
        elapsed = [0.0]

        def step() -> None:
            elapsed[0] += period
            if elapsed[0] >= dur:
                camera.x, camera.z = base_x, base_z
                self._shake_active = False
                return
            decay = 1 - elapsed[0] / dur
            camera.x = base_x + random.uniform(-mag, mag) * decay
            camera.z = base_z + random.uniform(-mag, mag) * decay
            invoke(step, delay=period)

        step()

    def input(self, key: str) -> None:
        if self._handle_pause_toggle(key):
            return
        self._update_cheat_buffer(key)
        self._handle_cheat_keys(key)
        self._handle_menu_shake(key)

    def _handle_pause_toggle(self, key: str) -> bool:
        if key != "space":
            return False
        if self._ignore_next_space:
            self._ignore_next_space = False
            return True
        in_game = self._current is None
        if self.game_state == C.EGameState.RUNNING and in_game:
            self.game_state = C.EGameState.PAUSE
            self.switch_view(C.EGameView.PAUSE)
            return True
        if (self.game_state == C.EGameState.PAUSE
                and self._current == C.EGameView.PAUSE):
            self._resume_game()
            return True
        return False

    def _update_cheat_buffer(self, key: str) -> None:
        if len(key) != 1 or not key.isalpha():
            return
        self._key_buffer = (self._key_buffer + key)[-6:]
        if self._key_buffer.endswith("cheat"):
            self._set_cheat(True)
        elif self._key_buffer.endswith("normal"):
            self._set_cheat(False)

    def _handle_cheat_keys(self, key: str) -> None:
        if not self._cheat_mode:
            return
        if self.game_state != C.EGameState.RUNNING or self._current is not None:
            return
        if key == "p" and self._pacgum_controller:
            self._pacgum_controller.eat_all()
        elif key == "o" and self._player:
            self._player.empower()

    def _handle_menu_shake(self, key: str) -> None:
        if key != "left mouse down":
            return
        if self._current != C.EGameView.MENU or self._fps_mode:
            return
        if isinstance(mouse.hovered_entity, Button):
            return
        self._shake_screen()

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
            if self._player.health <= 0 and not self._player.infinite_lives:
                self.game_state = C.EGameState.GAME_OVER
                self._player.game_state = self.game_state
                self._ghost_controller.game_state = self.game_state
                self.switch_view(C.EGameView.GAME_OVER)
                return

            self._ghost_controller.update_ghosts()
            if self._pacgum_controller:
                self._pacgum_controller.update()
            if self._hud:
                self._hud.update()
