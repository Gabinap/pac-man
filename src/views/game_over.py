from ursina import Entity, Text, Button, InputField, color, camera
from src.views.base import BaseView


class GameOverView(BaseView):
    def __init__(self, submit_callback, menu_callback) -> None:
        super().__init__()
        self.parent_entity = Entity(
            parent=camera.ui, enabled=False, ignore_paused=True
        )

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

        self.name_input = InputField(
            parent=self.parent_entity,
            y=0.1,
            z=-1,
            default_value="Enter your name...",
            character_limit=10,
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
            "Menu Principal",
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
        self.submit_callback(player_name)

    def enable(self) -> None:
        self.parent_entity.enable()
        self.name_input.active = True

    def disable(self) -> None:
        self.parent_entity.disable()
