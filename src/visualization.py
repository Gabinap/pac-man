"""Ursina application and rendering layer.

Initializes the Ursina app, loads 3D models and assets,
manages the camera (top-down perspective and first-person),
renders all entities each frame, and delegates all game
logic to game_behavior via the global update() callback.
Entry point for the Ursina event loop.
"""

from ursina import color, Entity, Ursina, camera, window, application
from src.game_config import GameConfig
from src.main_menu import MainMenu


class GameRender(Entity):
    def __init__(self, gcf: GameConfig):
        self.app = Ursina()
        super().__init__()
        self.gcf = gcf
        # camera.position = (0, 7, -2)
        # camera.fov = 90
        # camera.rotation_x = 80
        window.color = color.rgb(0, 0, 0)
        self.menu = MainMenu(
            start_game=self.start_game,
            show_scores=self.show_scores,
            show_instructions=self.show_instructions,
        )

        self.app.run()

    def start_game(self) -> None:
        print("Started the game")

    def show_scores(self) -> None:
        print("Show scores")

    def show_instructions(self) -> None:
        print("Show instructions")

    def update(self):
        pass

    def input(self, key):
        if key == "q":
            application.quit()
