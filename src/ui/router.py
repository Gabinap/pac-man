from typing import Dict, Any, TYPE_CHECKING
from ursina import application

import src.config.constants as C
from src.ui.views.base import BaseView
from src.ui.views.main_menu import MainMenuView
from src.ui.views.instructions import InstructionsView
from src.ui.views.game_over import GameOverView
from src.ui.views.pause import PauseView
from src.ui.views.settings import SettingsView
from src.ui.views.next_level import NextLevelView

if TYPE_CHECKING:
    from src.game_engine import GameEngine


class ViewRouter:
    def __init__(self, engine: "GameEngine") -> None:
        self.engine = engine
        self._views: Dict[C.EGameView, BaseView] = {}
        self.current: C.EGameView | None = None

        self._register_views()

    def _register_views(self) -> None:
        self._views[C.EGameView.MENU] = MainMenuView(
            self.engine.config,
            self.engine.scores_manager,
            self.engine.difficulty,
            start_game=self.engine.start_game,
            show_instructions=lambda: self.switch_view(
                C.EGameView.INSTRUCTIONS
            ),
            show_settings=lambda: self.switch_view(C.EGameView.SETTINGS),
            set_difficulty=self.engine.set_difficulty,
        )
        self._views[C.EGameView.SETTINGS] = SettingsView(
            controls=self.engine.controls,
            back_callback=lambda: self.switch_view(C.EGameView.MENU),
        )
        self._views[C.EGameView.INSTRUCTIONS] = InstructionsView(
            back_callback=lambda: self.switch_view(C.EGameView.MENU),
        )
        self._views[C.EGameView.GAME_OVER] = GameOverView(
            scores_manager=self.engine.scores_manager,
            score_callback=lambda: self.engine.session.score,
            menu_callback=self.engine.quit_to_menu,
            replay_callback=self.engine.start_game,
            get_is_win=lambda: self.engine.session.is_win,
        )
        self._views[C.EGameView.PAUSE] = PauseView(
            resume_callback=self.engine.resume_game,
            menu_callback=self.engine.quit_to_menu,
        )
        self._views[C.EGameView.NEXT_LEVEL] = NextLevelView(
            menu_callback=self.engine.quit_to_menu,
            level_callback=lambda: self.engine.session.get_level(),
            go_next_level_callback=self.go_to_next_level,
        )

    def switch_view(self, target: C.EGameView) -> None:
        if self.current and self.current in self._views:
            old_view = self._views[self.current]
            old_view.on_exit()
            old_view.disable()

        self.current = target

        if target == C.EGameView.GAME_OVER:
            self.engine.game_state = C.EGameState.GAME_OVER
            application.paused = True
            if self.engine.hud:
                self.engine.hud.hide()
            if self.engine.session.timer:
                self.engine.session.timer.stop()

        elif target == C.EGameView.PAUSE:
            self.engine.game_state = C.EGameState.PAUSE
            application.paused = True

        elif target == C.EGameView.MENU:
            self.engine.game_state = C.EGameState.PAUSE
            application.paused = True
            if self.engine.hud:
                self.engine.hud.hide()
            if self.engine.session.timer:
                self.engine.session.timer.stop()
        elif target == C.EGameView.NEXT_LEVEL:
            self.engine.game_state = C.EGameState.PAUSE
            application.paused = True

        new_view = self._views[target]
        new_view.enable()
        new_view.on_enter()

    def go_to_next_level(self) -> None:
        self.engine.session.destroy_entities()
        self.engine.session.init_level()
        self.engine.hud.update_level(self.engine.session.current_level_index)
        was_fps = self.engine.camera_effects.fps_mode
        if was_fps:
            self.engine.camera_effects.fps_mode = True
            self.engine.camera_effects.set_fps()

        if self.engine.session.timer:
            self.engine.session.timer.launch_timer()
        self.engine.game_state = C.EGameState.RUNNING

        self.exit_current()
        application.paused = False
        if self.engine.hud:
            self.engine.hud.show()

    def disable_all(self) -> None:
        """Hide every view (used when starting a game)."""
        for view in self._views.values():
            view.disable()
        self.current = None

    def exit_current(self) -> None:
        """Cleanly exit the current view (on_exit + disable + clear)."""
        if self.current and self.current in self._views:
            view = self._views[self.current]
            view.on_exit()
            view.disable()
        self.current = None
