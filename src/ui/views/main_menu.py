"""Main menu view: title, navigation buttons, and highscores panel."""

from typing import Callable

from ursina import Text, application, Entity, destroy

from src.ui.views.base import BaseView
from src.utils.highscores import Highscores
from src.config.game_config import GameConfig
from src.utils.views_utils import (
    DIFFICULTIES,
    EMPTY_SCORE_COLOR,
    SCORES_TITLE_COLOR,
    SCORE_ENTRY_COLOR,
    SUBTITLE_COLOR,
    TITLE_COLOR,
    TITLE_OUTLINE,
    handle_menu_input,
    make_button,
    make_outlined_text,
    make_panel,
    update_menu_highlight,
)
import src.config.constants as C


class MainMenuView(BaseView):
    """Title screen with glassmorphism buttons and a highscores panel."""

    def __init__(
        self,
        config: GameConfig,
        scores_manager: Highscores,
        difficulty: C.EDifficulty,
        start_game: Callable[[], None],
        show_instructions: Callable[[], None],
        show_settings: Callable[[], None] = lambda: None,
        set_difficulty: Callable[[C.EDifficulty], None] = lambda _: None,
    ) -> None:
        super().__init__()

        self.start_game = start_game
        self.show_instructions = show_instructions
        self.show_settings = show_settings
        self.difficulty = difficulty
        self.config = config
        self.scores_manager = scores_manager
        self._set_difficulty = set_difficulty

        self.title = make_outlined_text(
            self,
            "PAC-MAN",
            y=0.32,
            scale=6,
            fill=TITLE_COLOR,
            outline=TITLE_OUTLINE,
        )
        self.start_text = Text(
            text="Press SPACE to play",
            origin=(0, 0),
            color=SUBTITLE_COLOR,
            scale=1.5,
            y=0.2,
            parent=self,
        )

        self.btn_start = make_button(self, "Start Game", y=0.1)
        self.btn_start.on_click = self.start_game

        self.btn_difficulty = make_button(
            self, self._difficulty_label(), y=0.0
        )
        self.btn_difficulty.on_click = self.change_difficulty

        self.btn_instructions = make_button(self, "Instructions", y=-0.1)
        self.btn_instructions.on_click = self.show_instructions

        self.btn_settings = make_button(
            self, "設定", y=0.4, x=0.6, w=0.10, h=0.10
        )
        if self.btn_settings.text_entity is not None:
            self.btn_settings.text_entity.font = "DroidSansFallbackFull.ttf"
        self.btn_settings.on_click = self.show_settings

        self.btn_exit = make_button(self, "Exit", y=-0.2)
        self.btn_exit.on_click = application.quit

        self.buttons = [
            self.btn_start,
            self.btn_difficulty,
            self.btn_instructions,
            self.btn_exit,
            self.btn_settings,
        ]
        self.selected_index = 0
        self.update_highlight()
        self._score_entries: list[Entity] = []
        self._render_highscores()

    def on_enter(self) -> None:
        # Re-render dynamic scores each time the menu is shown, so a fresh
        # high score submitted from the game-over screen appears immediately.
        self._render_score_entries()

    def update_highlight(self) -> None:
        update_menu_highlight(self.buttons, self.selected_index)

    def _render_highscores(self) -> None:
        make_panel(self, x=-0.6, y=0.4, w=0.42, h=0.07)
        Text(
            "- BEST SCORES -",
            parent=self,
            origin=(-0.5, 0),
            x=-0.8,
            y=0.4,
            scale=1.5,
            color=SCORES_TITLE_COLOR,
        )
        self._render_score_entries()

    def _render_score_entries(self) -> None:
        for entry in self._score_entries:
            destroy(entry)
        self._score_entries.clear()

        scores_list = self.scores_manager.get_top_scores()
        start_y = 0.3

        if not scores_list:
            self._score_entries.append(
                Text(
                    "No scores yet...",
                    parent=self,
                    origin=(-0.5, 0),
                    x=-0.8,
                    y=start_y,
                    scale=0.8,
                    color=EMPTY_SCORE_COLOR,
                )
            )
            return

        for i, (name, score) in enumerate(scores_list[:10]):
            self._score_entries.append(
                Text(
                    f"{i+1}. {name} - {score}",
                    parent=self,
                    origin=(-0.5, 0),
                    x=-0.8,
                    y=start_y - (i * 0.08),
                    scale=0.8,
                    color=SCORE_ENTRY_COLOR,
                )
            )

    def input(self, key: str) -> None:
        if not self.enabled:
            return
        # 'space' → start_game is handled centrally in GameEngine.input to
        # avoid a race with the pause logic.
        self.selected_index = handle_menu_input(
            key, self.buttons, self.selected_index
        )
        self.update_highlight()

    def _difficulty_label(self) -> str:
        if self.difficulty == C.EDifficulty.EASY:
            lives_str = "∞ lives"
        elif self.difficulty == C.EDifficulty.HARD:
            lives_str = "1 life"
        else:
            lives_str = f"{self.config.lives} lives"
        return f"Difficulty: {self.difficulty.value} ({lives_str})"

    def change_difficulty(self) -> None:
        idx = DIFFICULTIES.index(self.difficulty)
        self.difficulty = DIFFICULTIES[(idx + 1) % len(DIFFICULTIES)]
        self._set_difficulty(self.difficulty)
        self.btn_difficulty.text = self._difficulty_label()
