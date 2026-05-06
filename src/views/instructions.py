from ursina import Entity, Text, Button, color, camera
from typing import Callable


class InstructionsView(Entity):
    def __init__(self, back_callback: Callable) -> None:
        super().__init__(parent=camera.ui, enabled=False)

        self.back_callback = back_callback
        Text(
            text="- Instructions -",
            origin=(0, 0),
            y=0.35,
            scale=3,
            color=color.yellow,
            parent=self,
        )

        self.btn_back = Button(
            text="Back",
            color=color.gray,
            scale=(0.2, 0.08),
            y=-0.4,
            parent=self,
        )
        self.btn_back.on_click = self.back_callback

    def input(self, key: str) -> None:
        if self.enabled and key in ("escape", "backspace"):
            self.back_callback()
