from typing import Dict, Any
from ursina import application

import src.config.constants as C
from src.ui.views.base import BaseView
from src.ui.views.main_menu import MainMenuView
from src.ui.views.instructions import InstructionsView
from src.ui.views.game_over import GameOverView
from src.ui.views.pause import PauseView


class ViewRouter:
    def __init__(self, engine: Any) -> None:
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
            set_difficulty=self.engine.set_difficulty,
        )
        self._views[C.EGameView.INSTRUCTIONS] = InstructionsView(
            back_callback=lambda: self.switch_view(C.EGameView.MENU),
        )
        self._views[C.EGameView.GAME_OVER] = GameOverView(
            scores_manager=self.engine.scores_manager,
            score_callback=lambda: self.engine.session.score,
            menu_callback=lambda: self.switch_view(C.EGameView.MENU),
            replay_callback=self.engine.start_game,
            get_is_win=lambda: self.engine.session.is_win,
        )
        self._views[C.EGameView.PAUSE] = PauseView(
            resume_callback=self.engine.resume_game,
            menu_callback=self.engine.quit_to_menu,
        )

    def switch_view(self, target: C.EGameView) -> None:
        if self.current and self.current in self._views:
            old_view = self._views[self.current]
            old_view.on_exit()
            old_view.disable()

        self.current = target

        if target == C.EGameView.GAME_OVER:
            application.paused = True
            if self.engine.hud:
                self.engine.hud.hide()
            if self.engine.session.timer:
                self.engine.session.timer.stop()

        elif target == C.EGameView.PAUSE:
            application.paused = True

        elif target == C.EGameView.MENU:
            application.paused = False
            if self.engine.hud:
                self.engine.hud.hide()
            if self.engine.session.timer:
                self.engine.session.timer.stop()

        new_view = self._views[target]
        new_view.enable()
        new_view.on_enter()

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
