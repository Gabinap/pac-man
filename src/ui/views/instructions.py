"""Instructions screen: static text and a back button."""

from ursina import Text, Button, color
from typing import Callable

from src.ui.views.base import BaseView


class InstructionsView(BaseView):
    """Static help screen reachable from the main menu."""

    def __init__(self, back_callback: Callable[[], None]) -> None:
        super().__init__()

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
        if self.enabled and key in ("backspace", "escape", "space", "enter"):
            self.back_callback()
