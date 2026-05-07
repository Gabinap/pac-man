from ursina import Button, Text, color, application
from typing import Callable

from src.views.base import BaseView


class MainMenuView(BaseView):
    def __init__(
        self,
        start_game: Callable[[], None],
        show_scores: Callable[[], None],
        show_instructions: Callable[[], None],
    ) -> None:
        super().__init__()

        self.start_game = start_game
        self.show_scores = show_scores
        self.show_instructions = show_instructions

        self.title = Text(
            "PAC-MAN",
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
            y=0.15,
            parent=self,
        )
        self.btn_start = Button(
            text="Start Game",
            color=color.azure,
            scale=(0.4, 0.08),
            y=0.0,
            parent=self,
        )
        self.btn_start.on_click = self._action_start

        self.btn_scores = Button(
            text="View Highscores",
            color=color.azure,
            scale=(0.4, 0.08),
            y=-0.1,
            parent=self,
        )
        self.btn_scores.on_click = self.show_scores

        self.btn_instructions = Button(
            text="Instructions",
            color=color.azure,
            scale=(0.4, 0.08),
            y=-0.2,
            parent=self,
        )
        self.btn_instructions.on_click = self.show_instructions

        self.btn_exit = Button(
            text="Exit",
            color=color.red,
            scale=(0.4, 0.08),
            y=-0.3,
            parent=self,
        )
        self.btn_exit.on_click = application.quit

        self.buttons = [
            self.btn_start,
            self.btn_scores,
            self.btn_instructions,
            self.btn_exit,
        ]

        self.selected_index = 0
        self.update_highlight()

    def _action_start(self) -> None:
        self.start_game()

    def update_highlight(self) -> None:
        for btn in self.buttons:
            btn.color = color.azure
        self.btn_exit.color = color.red
        self.buttons[self.selected_index].color = color.orange

    def input(self, key: str) -> None:
        if not self.enabled:
            return
        if key == "space":
            self._action_start()
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
