"""Pause overlay: resume and return-to-menu buttons."""

from typing import Callable

from ursina import Text, color

from src.ui.views.base import BaseView
from src.utils.views_utils import (
    handle_menu_input,
    make_button,
    make_panel,
    update_menu_highlight,
)


class PauseView(BaseView):
    """Semi-transparent overlay shown when the game is paused."""

    def __init__(
        self,
        resume_callback: Callable[[], None],
        menu_callback: Callable[[], None],
    ) -> None:
        super().__init__()
        self.resume_callback = resume_callback

        make_panel(self, x=0, y=0.02, w=0.55, h=0.54)

        Text(
            text="PAUSED",
            parent=self,
            scale=5,
            origin=(0, 0),
            y=0.2,
            color=color.white,
            z=-1,
            ignore_paused=True,
        )
        Text(
            text="Space to resume",
            parent=self,
            scale=1.5,
            origin=(0, 0),
            y=0.07,
            color=color.light_gray,
            z=-1,
            ignore_paused=True,
        )
        self.btn_resume = make_button(
            self, "Resume", y=-0.1, z=-1, ignore_paused=True
        )
        self.btn_resume.on_click = resume_callback
        self.btn_menu = make_button(
            self, "Main menu", y=-0.2, z=-1, ignore_paused=True
        )
        self.btn_menu.on_click = menu_callback
        self.buttons = [self.btn_resume, self.btn_menu]
        self.selected_index = 0
        self._update_highlight()

    def _update_highlight(self) -> None:
        update_menu_highlight(self.buttons, self.selected_index)

    def on_enter(self) -> None:
        self.selected_index = 0
        self._update_highlight()

    def input(self, key: str) -> None:
        if not self.enabled:
            return
        # 'space' → resume is handled centrally in GameEngine.input.
        self.selected_index = handle_menu_input(
            key, self.buttons, self.selected_index
        )
        self._update_highlight()
