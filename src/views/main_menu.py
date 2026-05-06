from ursina import Entity, Button, Text, color, application, camera
from typing import Callable


class MainMenuView(Entity):
    def __init__(
        self,
        start_game: Callable,
        show_scores: Callable,
        show_instructions: Callable,
    ) -> None:
        super().__init__(parent=camera.ui)

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
            color=color.azure,  # type: ignore
            scale=(0.4, 0.08),
            y=0.0,
            parent=self,
        )
        self.btn_start.on_click = self._action_start

        self.btn_scores = Button(
            text="View Highscores",
            color=color.azure,  # type: ignore
            scale=(0.4, 0.08),
            y=-0.1,
            parent=self,
        )
        self.btn_scores.on_click = self.show_scores

        self.btn_instructions = Button(
            text="Instructions",
            color=color.azure,  # type: ignore
            scale=(0.4, 0.08),
            y=-0.2,
            parent=self,
        )
        self.btn_instructions.on_click = self.show_instructions

        self.btn_exit = Button(
            text="Exit",
            color=color.red,  # type: ignore
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

    def _action_start(self):
        self.disable()
        self.start_game()

    def update_highlight(self):
        for btn in self.buttons:
            btn.color = color.azure
        self.btn_exit.color = color.red

        selected_btn = self.buttons[self.selected_index]
        selected_btn.color = color.orange

    def input(self, key):
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
