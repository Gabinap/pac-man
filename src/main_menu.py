from ursina import Entity, Button, Text, color, application, camera
from typing import Callable


class MainMenu(Entity):
    def __init__(self, start_callback: Callable) -> None:
        super().__init__(parent=camera.ui)
        self.start_callback = start_callback
        self.title = Text(
            "PAC-MAN",
            origin=(0, 0),
            y=0.3,
            scale=4,
            color=color.yellow,
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

        self.btn_scores = Button(
            text="View Highscores",
            color=color.azure,
            scale=(0.4, 0.08),
            y=0.0,
            parent=self,
        )
        self.btn_scores.on_click = self.show_scores

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
