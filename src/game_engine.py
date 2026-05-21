from typing import Any
from ursina import Entity, Ursina, window, color, application, Text, camera

import src.config.constants as C
from src.config.game_config import GameConfig
from src.config.controls import ControlsConfig
from src.utils.highscores import Highscores
from src.ui.hud import HUD
import random
from src.ui.router import ViewRouter
from src.config.input_manager import InputManager
from src.config.camera_effects import CameraEffectsManager
from src.gameplay.session import GameSession
import time


class GameEngine(Entity):
    def __init__(self, config: GameConfig) -> None:
        self.app: Any = Ursina(development_mode=False)
        super().__init__(ignore_paused=True)
        self.loading_image, self.loading_text, self.loading_progress_images = (
            self.create_loading_entities()
        )
        self.config = config

        self._game_state = C.EGameState.NOT_STARTED
        self.difficulty = C.EDifficulty.MEDIUM
        self.controls = ControlsConfig()
        self.scores_manager = Highscores(self.config)

        self.camera_effects = CameraEffectsManager(engine=self)
        self.session = GameSession(engine=self)
        self.router = ViewRouter(engine=self)
        self.input_manager = InputManager(engine=self)

        window.color = color.rgb32(30, 45, 50)
        window.exit_button.enabled = False

        self.assets_to_load = self._get_assets_to_load()
        self.total_assets = len(self.assets_to_load)
        self.is_loading = True
        self.frames_to_wait = 4

    @property
    def game_state(self) -> C.EGameState:
        return self._game_state

    @game_state.setter
    def game_state(self, value: C.EGameState) -> None:
        self._game_state = value
        if self.session.player:
            self.session.player.game_state = value
        if self.session.ghost_controller:
            self.session.ghost_controller.game_state = value

    def create_loading_entities(self) -> tuple[Entity, Text, list[Entity]]:
        random_loading_image_path = random.choice(C.LOADING_IMAGES_PATHS)
        loading_image = Entity(
            parent=camera.ui,
            model="quad",
            texture=random_loading_image_path,
            scale=(window.aspect_ratio, 1),
            position=(0, 0, 1),
            color=color.gray,
        )
        loading_text = Text(
            text="Loading... 0%",
            origin=(0, 0),
            position=(0, -0.3),
            scale=1.2,
            color=color.white,
        )
        list_progress_image: list[Entity] = []
        for i in range(3):
            list_progress_image.append(
                Entity(
                    parent=camera.ui,
                    texture=C.LOADING_PROGRESS_PATH,
                    model="quad",
                    scale=(
                        0.04,
                        0.04,
                    ),
                    position=(0.135 + (i * 0.05), -0.295),
                    color=color.white,
                    enabled=False,
                )
            )
        return (loading_image, loading_text, list_progress_image)

    def _get_assets_to_load(self) -> list[str]:
        paths = []
        for spec in C.MODEL_SPECS:
            if spec.supported:
                paths.append(f"assets/{spec.path}")

        seen: set[str] = set()
        for amb in C.AMBIANCES.values():
            for p_spec in (*amb.pacgums, *amb.super_pacgums):
                if p_spec.path in seen:
                    continue
                seen.add(p_spec.path)
                paths.append(f"assets/{p_spec.path}")

        return paths

    def _post_load_init(self) -> None:
        self.loading_text.disable()
        self.loading_image.disable()
        self.disable_progression_images()
        self.hud = HUD(view_mode=C.EViewMode.TOPDOWN)
        self.session.init_level()
        self.router.switch_view(C.EGameView.MENU)

    def disable_progression_images(self) -> None:
        for image in self.loading_progress_images:
            image.disable()

    def start_game(self) -> None:
        self.router.disable_all()

        if self.game_state == C.EGameState.GAME_OVER:
            self.session.destroy_entities()
            self.session.score = 0
            self.session.current_level_index = 0
            self.session.is_win = False
            self.session.init_level()

        self.game_state = C.EGameState.RUNNING
        if self.hud:
            self.hud.show()
        if self.session.timer:
            self.session.timer.launch_timer()
        application.paused = False

    def resume_game(self) -> None:
        self.router.exit_current()
        self.game_state = C.EGameState.RUNNING
        application.paused = False

    def quit_to_menu(self) -> None:
        self.session.destroy_entities()
        self.session.score = 0
        self.session.current_level_index = 0
        self.session.is_win = False
        self.game_state = C.EGameState.NOT_STARTED
        self.session.init_level()
        application.paused = False
        self.router.switch_view(C.EGameView.MENU)

    def _shake_screen(self) -> None:
        self.camera_effects.shake_screen()

    def set_difficulty(self, difficulty: C.EDifficulty) -> None:
        self.difficulty = difficulty
        self.session.apply_difficulty_to_player()

    def input(self, key: str) -> None:

        if key == self.controls.pause:
            if self.router.current == C.EGameView.MENU and (
                self.game_state == C.EGameState.NOT_STARTED
                or self.game_state == C.EGameState.GAME_OVER
            ):
                self.start_game()
                return
            if (
                self.game_state == C.EGameState.RUNNING
                and self.router.current is None
            ):
                self.game_state = C.EGameState.PAUSE
                self.router.switch_view(C.EGameView.PAUSE)
                return
            if (
                self.game_state == C.EGameState.PAUSE
                and self.router.current == C.EGameView.PAUSE
            ):
                self.resume_game()
                return
        if (
            key == self.controls.toggle_hud
            or key == self.controls.toggle_hud.upper()
        ):
            if self.game_state is C.EGameState.RUNNING:
                if self.hud.visible:
                    self.hud.hide()
                    if self.session.timer:
                        self.session.timer.hide()
                else:
                    self.hud.show()
                    if self.session.timer:
                        self.session.timer.show()

        self.input_manager.handle_input(key)

    def preloading_assets(self) -> None:
        loaded = self.total_assets - len(self.assets_to_load)
        progress = (
            int((loaded / self.total_assets) * 100)
            if self.total_assets > 0
            else 100
        )
        self.loading_text.text = f"Loading... {progress}%"

        step = int(time.time() * 3) % 4

        for i, img in enumerate(self.loading_progress_images):
            if i < step:
                img.enabled = True
            else:
                img.enabled = False

        if not self.assets_to_load:
            self.is_loading = False

            self.loading_text.disable()
            self.loading_image.disable()
            for img in self.loading_progress_images:
                img.disable()

            self._post_load_init()
            return

        path = self.assets_to_load.pop(0)
        self.app.loader.loadModel(path)

    def update(self) -> None:
        if self.is_loading:
            if self.frames_to_wait > 0:
                self.frames_to_wait -= 1
                return
            self.preloading_assets()
            return

        if (
            not self.session.game_initialized
            or self.game_state != C.EGameState.RUNNING
        ):
            return

        player = self.session.player
        if (
            player
            and player.health <= 0
            and not player.infinite_lives
            and not player.cheat_mode
        ):
            self.game_state = C.EGameState.GAME_OVER
            self.router.switch_view(C.EGameView.GAME_OVER)
            return

        if self.session.ghost_controller:
            self.session.ghost_controller.update_ghosts()
        if self.session.pacgum_controller:
            self.session.pacgum_controller.update()
        if self.hud:
            self.hud.update()
        if self.camera_effects.fps_mode:
            self.camera_effects.update_fps_camera()
