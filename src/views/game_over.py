from typing import Callable
import string

from ursina import Text, Button, InputField, color, application
from src.views.base import BaseView


class GameOverView(BaseView):
    def __init__(
        self,
        register_callback: Callable[[str], None],
        menu_callback: Callable[[], None],
        replay_callback: Callable[[], None],
    ) -> None:
        super().__init__()
        allowed_chars = string.ascii_letters + string.digits + " "

        self.register_callback = register_callback
        self.menu_callback = menu_callback
        self.replay_callback = replay_callback
        self.has_submitted = False

        self.title = Text(
            "GAME OVER",
            parent=self,
            scale=4,
            origin=(0, 0),
            y=0.3,
            color=color.red,
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
            active=self.has_submitted,
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

        self.btn_register = Button(
            text="Register score",
            parent=self,
            y=-0.1,
            scale=(0.3, 0.05),
            on_click=self._on_register,
            z=-1,
            ignore_paused=True,
        )
        self.btn_replay = Button(
            text="Replay",
            parent=self,
            y=-0.2,
            scale=(0.3, 0.05),
            on_click=self.replay_callback,
            z=-1,
            ignore_paused=True,
        )
        self.btn_menu = Button(
            text="Main menu",
            parent=self,
            y=-0.3,
            scale=(0.3, 0.05),
            on_click=self.menu_callback,
            z=-1,
            ignore_paused=True,
        )

        self.elements = [
            self.name_input,
            self.btn_register,
            self.btn_replay,
            self.btn_menu,
        ]
        self.selected_index = 0

    def on_enter(self) -> None:
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
            self.register_callback(player_name)
            self.input_error.text = f"Score saved for {player_name}"
            self.input_error.color = color.green
            self.has_submitted = True

    def update_highlight(self) -> None:
        self.name_input.color = color.black
        self.btn_register.color = color.azure
        self.btn_replay.color = color.azure
        self.btn_menu.color = color.azure

        current = self.elements[self.selected_index]
        current.color = color.orange

        if isinstance(current, InputField):
            current.active = True
        else:
            self.name_input.active = False

    def input(self, key: str) -> None:
        if not self.enabled:
            return

        if key in ("down arrow", "tab"):
            self.selected_index = (self.selected_index + 1) % len(
                self.elements
            )
            self.update_highlight()

        elif key in ("up arrow", "shift+tab"):
            self.selected_index = (self.selected_index - 1) % len(
                self.elements
            )
            self.update_highlight()

        elif key == "enter":
            current = self.elements[self.selected_index]
            if isinstance(current, InputField):
                self._on_register()
            elif hasattr(current, "on_click") and current.on_click:
                current.on_click()

        elif key in ("escape"):
            application.quit()
