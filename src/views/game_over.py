from typing import Callable

from ursina import Entity, Text, Button, InputField, color, camera
from src.views.base import BaseView
import string


class GameOverView(BaseView):
    def __init__(
        self,
        submit_callback: Callable[[str], None],
        menu_callback: Callable[[], None],
    ) -> None:
        super().__init__()
        self.parent_entity = Entity(
            parent=camera.ui, enabled=False, ignore_paused=True
        )
        allowed_chars = string.ascii_letters + string.digits + " "

        self.bg = Entity(
            parent=self.parent_entity,
            model="quad",
            scale=99,
            color=color.rgba(0, 0, 0, 200),
            z=1,
            ignore_paused=True,
        )

        self.title = Text(
            "GAME OVER",
            parent=self.parent_entity,
            scale=4,
            origin=(0, 0),
            y=0.3,
            color=color.red,
            z=-1,
            ignore_paused=True,
        )

        self.input_label = Text(
            "Enter your name:",
            parent=self.parent_entity,
            origin=(0, 0),
            y=0.16,
            color=color.white,
            z=-1,
            ignore_paused=True,
        )
        self.name_input = InputField(
            parent=self.parent_entity,
            y=0.1,
            z=-1,
            character_limit=10,
            limit_content_to=allowed_chars,
        )
        self.name_input.ignore_paused = True

        self.btn_submit = Button(
            "Register and replay",
            parent=self.parent_entity,
            y=-0.1,
            scale=(0.3, 0.05),
            on_click=self._on_submit,
            z=-1,
            ignore_paused=True,
        )
        self.btn_menu = Button(
            "Main menu",
            parent=self.parent_entity,
            y=-0.2,
            scale=(0.3, 0.05),
            on_click=menu_callback,
            z=-1,
            ignore_paused=True,
        )

        self.submit_callback = submit_callback

    def _on_submit(self) -> None:
        player_name = self.name_input.text
        if not player_name:
            player_name = "UNKNOWN"
        self.submit_callback(player_name)

    def enable(self) -> None:
        self.parent_entity.enable()
        self.name_input.text = ""
        self.name_input.active = True

    def disable(self) -> None:
        self.parent_entity.disable()

    def input(self, key: str) -> None:
        if key == "escape" or key == "q":
            application.quit()
