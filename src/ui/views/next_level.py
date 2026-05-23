"""Next-level screen: congratulates the player and offers to continue."""

from typing import Callable

from ursina import Text

from src.ui.views.base import BaseView
from src.utils.views_utils import (
    SCORES_TITLE_COLOR,
    SUBTITLE_COLOR,
    handle_menu_input,
    make_button,
    update_menu_highlight,
)


class NextLevelView(BaseView):
    """Interstitial screen shown after completing a level."""

    def __init__(
        self,
        menu_callback: Callable[[], None],
        level_callback: Callable[[], int],
        go_next_level_callback: Callable[[], None],
    ) -> None:
        """Build the level-complete panel with Next and Back buttons."""
        super().__init__()

        self.menu_callback = menu_callback
        self.level_callback = level_callback
        self.go_next_level_callback = go_next_level_callback
        Text(
            text="Well done !",
            origin=(0, 0),
            y=0.35,
            scale=3,
            color=SUBTITLE_COLOR,
            parent=self,
        )
        self.level_text = Text(
            text=f"Level {level_callback()} completed",
            origin=(0, 0),
            y=0.25,
            scale=3,
            color=SCORES_TITLE_COLOR,
            parent=self,
        )
        self.next_btn = make_button(self, "Next", y=-0.3)
        self.next_btn.on_click = self.go_next_level_callback
        self.btn_back = make_button(self, "Back to menu", y=-0.4)
        self.btn_back.on_click = self.menu_callback

        self.elements = [self.next_btn, self.btn_back]
        self.selected_index = 0
        self.update_highlight()

    def update_highlight(self) -> None:
        """Apply selection highlight to the currently focused element."""
        update_menu_highlight(self.elements, self.selected_index)

    def input(self, key: str) -> None:
        """Handle navigation and shortcut keys for this view."""
        if not self.enabled:
            return

        if key in ("backspace", "escape", "space"):
            self.menu_callback()
            return
        if key == "p":
            self.go_next_level_callback()

        self.selected_index = handle_menu_input(
            key, self.elements, self.selected_index
        )
        self.update_highlight()

    def on_enter(self) -> None:
        """Refresh the level number text when the view is activated."""
        self.level_text.text = f"Level {self.level_callback() - 1} completed"
