"""Pause overlay: resume and return-to-menu buttons."""

from typing import Callable

from ursina import Text, Button, color

from src.ui.views.base import BaseView


_SELECTED = color.rgba32(220, 175, 80, 200)
_NORMAL = color.rgba32(80, 80, 80, 200)


class PauseView(BaseView):
    """Semi-transparent overlay shown when the game is paused."""

    def __init__(
        self,
        resume_callback: Callable[[], None],
        menu_callback: Callable[[], None],
    ) -> None:
        super().__init__()
        self.resume_callback = resume_callback

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
        self.btn_resume = Button(
            text="Resume",
            parent=self,
            scale=(0.25, 0.06),
            y=-0.1,
            on_click=resume_callback,
            z=-1,
            ignore_paused=True,
        )
        self.btn_menu = Button(
            text="Main menu",
            parent=self,
            scale=(0.25, 0.06),
            y=-0.2,
            on_click=menu_callback,
            z=-1,
            ignore_paused=True,
        )
        self.buttons = [self.btn_resume, self.btn_menu]
        self.selected_index = 0
        self._update_highlight()

    def _update_highlight(self) -> None:
        for i, btn in enumerate(self.buttons):
            btn.color = _SELECTED if i == self.selected_index else _NORMAL

    def on_enter(self) -> None:
        self.selected_index = 0
        self._update_highlight()

    def input(self, key: str) -> None:
        if not self.enabled:
            return
        # 'space' → resume is handled centrally in GameEngine.input.
        if key == "up arrow":
            self.selected_index = (
                self.selected_index - 1
            ) % len(self.buttons)
            self._update_highlight()
        elif key == "down arrow":
            self.selected_index = (
                self.selected_index + 1
            ) % len(self.buttons)
            self._update_highlight()
        elif key == "enter":
            action = self.buttons[self.selected_index].on_click
            if action:
                action()
