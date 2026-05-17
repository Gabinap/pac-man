from typing import Any
from ursina import Entity, Ursina, window, color, application

import src.config.constants as C
from src.config.game_config import GameConfig
from src.utils.highscores import Highscores
from src.ui.hud import HUD

# Importation de nos 4 Managers Spécialisés
from src.ui.router import ViewRouter
from src.config.input_manager import InputManager
from src.config.camera_effects import CameraEffectsManager
from src.gameplay.session import GameSession


class GameEngine(Entity):
    def __init__(self, config: GameConfig) -> None:
        self.app: Any = Ursina(development_mode=False)
        super().__init__()
        self.config = config

        # États généraux
        self._game_state = C.EGameState.NOT_STARTED
        self.difficulty = C.EDifficulty.MEDIUM
        self.scores_manager = Highscores(self.config)

        # Instanciation des gestionnaires autonomes
        self.camera_effects = CameraEffectsManager(engine=self)
        self.session = GameSession(engine=self)
        self.router = ViewRouter(engine=self)
        self.input_manager = InputManager(engine=self)

        # Configuration cosmétique de la fenêtre — deep forest-navy de la
        # palette Wes-Anderson (cohérent avec les panneaux du menu).
        window.color = color.rgb32(30, 45, 50)
        window.exit_button.enabled = False

        self._preload_assets()

        # Initialisation du HUD lié aux propriétés de la session dynamique
        self.hud = HUD(view_mode=C.EViewMode.TOPDOWN)
        self.hud.hide()

        # Premier amorçage
        self.session.init_level()
        self.router.switch_view(C.EGameView.MENU)

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

    def _preload_assets(self) -> None:
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

    def start_game(self) -> None:
        """Lancé via les boutons de l'UI."""
        self.router.disable_all()

        # Si Replay après un Game Over, on reset entièrement la session de jeu
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
        """Passerelle pour l'input manager."""
        self.camera_effects.shake_screen()

    def input(self, key: str) -> None:
        # Espace : un seul handler centralisé pour éviter les courses entre
        # MainMenuView et l'engine (start → pause immédiat sur le même press).
        if key == "space":
            # Depuis le menu, peu importe l'état (NOT_STARTED ou GAME_OVER
            # quand on revient d'une partie), space relance une partie.
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

        # Délégation des touches secondaires (triche, clics).
        # FPS toggle géré par pac-man.py sur 'f' — ne PAS rebind 't' ici,
        # ça intercepterait la dernière lettre de "cheat".
        self.input_manager.handle_input(key)

    def update(self) -> None:
        """Cadence d'horloge globale d'Ursina."""
        self.camera_effects.update_fps_controls()

        if (
            not self.session.game_initialized
            or self.game_state != C.EGameState.RUNNING
        ):
            return

        # Traitement de la défaite du joueur — ignorer les invincibilités
        # (infinite_lives en EASY, cheat_mode), sinon EASY trigger game-over
        # immédiatement puisque les vies démarrent à 0.
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

        # Mise à jour des sous-systèmes de jeu indépendants
        if self.session.ghost_controller:
            self.session.ghost_controller.update_ghosts()
        if self.session.pacgum_controller:
            self.session.pacgum_controller.update()
        if self.hud:
            self.hud.update()
