from ursina import color, Entity, Ursina, window, application
from src.game_config import GameConfig
from src.views.main_menu import MainMenuView
from src.views.highscores import HighscoresView
from src.views.instructions import InstructionsView
from enum import Enum


class EGameView(Enum):
    MENU = "menu"
    GAME = "game"
    SCORES = "scores"
    INSTRUCTIONS = "instructions"


class GameRender(Entity):
    def __init__(self, gcf: GameConfig):
        self.app = Ursina(development_mode=False)
        super().__init__()
        self.gcf = gcf
        window.color = color.black
        window.exit_button.enabled = False
        self.menu_view = MainMenuView(
            start_game=lambda: self.switch_view(EGameView.GAME.value),
            show_scores=lambda: self.switch_view(EGameView.SCORES.value),
            show_instructions=lambda: self.switch_view(
                EGameView.INSTRUCTIONS.value
            ),
        )

        self.scores_view = HighscoresView(
            gcf=self.gcf,
            back_callback=lambda: self.switch_view(EGameView.MENU.value),
        )

        self.instructions_view = InstructionsView(
            back_callback=lambda: self.switch_view(EGameView.MENU.value)
        )
        # TODO: self.game_view = GameView(...)

        self.current_view = None

        self.switch_view(EGameView.MENU.value)

        self.app.run()  # type: ignore

    def switch_view(self, view_name: str) -> None:
        self.menu_view.disable()
        self.scores_view.disable()
        self.instructions_view.disable()
        # self.game_view.disable()

        if view_name == EGameView.MENU.value:
            self.menu_view.enable()

        elif view_name == EGameView.SCORES.value:
            self.scores_view.load_and_display_scores()
            self.scores_view.enable()
        elif view_name == EGameView.INSTRUCTIONS.value:
            self.instructions_view.enable()
        elif view_name == EGameView.GAME.value:
            print("Game started !")
            # self.game_view.start_new_level()
            # self.game_view.enable()
