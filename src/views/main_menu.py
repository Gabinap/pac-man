from ursina import Button, Text, color, application
from typing import Callable

from src.views.base import BaseView
from src.highscores import Highscores
from src.game_config import GameConfig
import src.constants as C


class MainMenuView(BaseView):
    def __init__(
        self,
        gcf: GameConfig,
        scores_manager: Highscores,
        difficulty: C.EDifficulty,
        start_game: Callable[[], None],
        show_instructions: Callable[[], None],
    ) -> None:
        super().__init__()

        self.start_game = start_game
        self.show_instructions = show_instructions
        self.difficulty = difficulty
        self.gcf = gcf
        self.scores_manager = scores_manager

        self.title = Text(
            "PAK-MAN",
            origin=(0, 0),
            y=0.3,
            scale=4,
            color=color.yellow,
            parent=self,
        )
        self.start_text = Text(
            text="Press SPACE to play",
            origin=(0, 0),
            color=color.white,
            scale=1.5,
            y=0.2,
            parent=self,
        )

        self.btn_start = Button(
            text="Start Game",
            color=color.azure,
            scale=(0.4, 0.08),
            y=0.1,
            parent=self,
        )
        self.btn_start.on_click = self.start_game

        self.btn_difficulty = Button(
            text=f"Difficulty: {self.difficulty.value}",
            color=color.azure,
            scale=(0.4, 0.08),
            y=0.0,
            parent=self,
        )
        self.btn_difficulty.on_click = self.change_difficulty

        self.btn_instructions = Button(
            text="Instructions",
            color=color.azure,
            scale=(0.4, 0.08),
            y=-0.1,
            parent=self,
        )
        self.btn_instructions.on_click = self.show_instructions

        self.btn_exit = Button(
            text="Exit",
            color=color.red,
            scale=(0.4, 0.08),
            y=-0.2,
            parent=self,
        )
        self.btn_exit.on_click = application.quit

        self.buttons = [
            self.btn_start,
            self.btn_difficulty,
            self.btn_instructions,
            self.btn_exit,
        ]
        self.selected_index = 0
        self.update_highlight()
        self._render_highscores()

    def update_highlight(self) -> None:
        for btn in self.buttons:
            btn.color = color.azure
        self.btn_exit.color = color.red
        self.buttons[self.selected_index].color = color.orange

    def _render_highscores(self) -> None:
        Text(
            "- BEST SCORES -",
            parent=self,
            origin=(-0.5, 0),
            x=-0.8,
            y=0.4,
            scale=1.5,
            color=color.gold,
        )

        scores_list = self.scores_manager.get_top_scores()

        start_y = 0.3

        if not scores_list:
            Text(
                "No scores yet...",
                parent=self,
                origin=(-0.5, 0),
                x=-0.8,
                y=start_y,
                scale=0.8,
                color=color.gray,
            )
            return

        for i, data in enumerate(scores_list[:10]):
            name = data[0]
            score = data[1]

            Text(
                f"{i+1}. {name} - {score}",
                parent=self,
                origin=(-0.5, 0),
                x=-0.8,
                y=start_y - (i * 0.08),
                scale=0.8,
                color=color.white,
            )

    def input(self, key: str) -> None:
        if not self.enabled:
            return
        if key == "space":
            self.start_game()
        elif key == "up arrow":
            self.selected_index = (self.selected_index - 1) % len(self.buttons)
            self.update_highlight()
        elif key == "down arrow":
            self.selected_index = (self.selected_index + 1) % len(self.buttons)
            self.update_highlight()
        elif key == "enter":
            action = self.buttons[self.selected_index].on_click
            if action:
                action()
        elif key in ("q", "escape"):
            application.quit()

    def change_difficulty(self) -> None:
        if self.difficulty == C.EDifficulty.EASY:
            self.difficulty = C.EDifficulty.MEDIUM
        elif self.difficulty == C.EDifficulty.MEDIUM:
            self.difficulty = C.EDifficulty.HARD
        elif self.difficulty == C.EDifficulty.HARD:
            self.difficulty = C.EDifficulty.EASY

        self.btn_difficulty.text = f"Difficulty: {self.difficulty.value}"
