"""Instructions screen: static text and a back button."""

from typing import Callable

from ursina import Text

from src.ui.views.base import BaseView
from src.utils.views_utils import (
    TITLE_COLOR,
    handle_menu_input,
    make_button,
    update_menu_highlight,
)


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
            color=TITLE_COLOR,
            parent=self,
        )

        self.btn_back = make_button(self, "Back", y=-0.4)
        self.btn_back.on_click = self.back_callback

        self.elements = [self.btn_back]
        self.selected_index = 0
        self.update_highlight()

    def update_highlight(self) -> None:
        update_menu_highlight(self.elements, self.selected_index)

    def input(self, key: str) -> None:
        if not self.enabled:
            return

        if key in ("backspace", "escape", "space"):
            self.back_callback()
            return

        self.selected_index = handle_menu_input(
            key, self.elements, self.selected_index
        )
        self.update_highlight()
