"""End-of-run screen: name input, score submission, replay/menu buttons."""

from typing import Callable
import string

from ursina import Text, InputField, color, application
from src.ui.views.base import BaseView
from src.utils.highscores import Highscores
from src.utils.views_utils import (
    handle_menu_input,
    make_button,
    update_menu_highlight,
)


class GameOverView(BaseView):
    """End-of-run screen letting the player register their score."""

    def __init__(
        self,
        scores_manager: Highscores,
        score_callback: Callable[[], int],
        menu_callback: Callable[[], None],
        replay_callback: Callable[[], None],
        get_is_win: Callable[[], bool],
    ) -> None:
        super().__init__()
        self.scores_manager = scores_manager
        self.score_callback = score_callback
        self.menu_callback = menu_callback
        self.replay_callback = replay_callback
        self.get_is_win = get_is_win

        self.has_submitted = False
        allowed_chars = string.ascii_letters + string.digits + " "

        self.title = Text(
            "",
            parent=self,
            scale=4,
            origin=(0, 0),
            y=0.3,
            z=-1,
            ignore_paused=True,
        )

        self.input_label = Text(
            "Enter your name:",
            parent=self,
            origin=(0, 0),
            y=0.16,
            color=color.white,
            z=-1,
            ignore_paused=True,
        )

        self.name_input = InputField(
            parent=self,
            y=0.1,
            z=-1,
            character_limit=10,
            limit_content_to=allowed_chars,
        )
        self.name_input.ignore_paused = True

        self.input_error = Text(
            "",
            parent=self,
            origin=(0, 0),
            y=0.05,
            color=color.red,
            z=-1,
            ignore_paused=True,
        )

        self.btn_register = make_button(
            self, "Register score", y=-0.1, z=-1, ignore_paused=True
        )
        self.btn_register.on_click = self._on_register
        self.btn_replay = make_button(
            self, "Replay", y=-0.2, z=-1, ignore_paused=True
        )
        self.btn_replay.on_click = self.replay_callback
        self.btn_menu = make_button(
            self, "Main menu", y=-0.3, z=-1, ignore_paused=True
        )
        self.btn_menu.on_click = self.menu_callback

        self.name_input.on_click = self._on_register
        self.elements = [
            self.name_input,
            self.btn_register,
            self.btn_replay,
            self.btn_menu,
        ]
        self.selected_index = 0

    def on_enter(self) -> None:
        if self.get_is_win():
            self.title.text = "SUCCESS"
            self.title.color = color.gold
        else:
            self.title.text = "GAME OVER"
            self.title.color = color.red
        self.name_input.text = ""
        self.input_error.text = ""
        self.selected_index = 0
        self.has_submitted = False
        self.update_highlight()

    def _on_register(self) -> None:
        if self.has_submitted:
            return
        player_name = self.name_input.text.strip()
        if not player_name:
            self.input_error.text = "Please enter a name!"
            self.input_error.color = color.red
        else:
            score = self.score_callback()
            add_score_msg = self.scores_manager.add_score(player_name, score)
            self.input_error.text = add_score_msg
            self.input_error.color = color.green
            self.has_submitted = True

    def update_highlight(self) -> None:
        update_menu_highlight(self.elements, self.selected_index)

    def input(self, key: str) -> None:
        if not self.enabled:
            return

        if key == "escape":
            application.quit()
            return

        self.selected_index = handle_menu_input(
            key, self.elements, self.selected_index
        )
        self.update_highlight()
