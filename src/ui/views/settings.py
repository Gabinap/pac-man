from typing import Callable

from ursina import Button, Text

from src.config.controls import ControlsConfig
from src.ui.views.base import BaseView
from src.utils.views_utils import (
    SUBTITLE_COLOR,
    SCORES_TITLE_COLOR,
    SCORE_ENTRY_COLOR,
    handle_menu_input,
    make_button,
    make_panel,
    make_section_divider,
    update_menu_highlight,
)

_SECTION_COLOR = SCORES_TITLE_COLOR
_LABEL_COLOR = SCORE_ENTRY_COLOR

_KEY_DISPLAY: dict[str, str] = {
    "space": "Space",
    "up arrow": "↑",
    "down arrow": "↓",
    "left arrow": "←",
    "right arrow": "→",
    "enter": "Enter",
    "backspace": "Del",
    "tab": "Tab",
    "escape": "Esc",
    "shift": "Shift",
    "control": "Ctrl",
    "alt": "Alt",
}

_CONTROL_DEFS: list[tuple[str, str]] = [
    ("move_up",    "Move Up"),
    ("move_down",  "Move Down"),
    ("move_left",  "Move Left"),
    ("move_right", "Move Right"),
    ("pause",      "Pause / Start"),
    ("toggle_hud", "Toggle HUD"),
    ("toggle_fps", "Toggle FPS"),
]

_KEY_BTN_W = 0.20
_KEY_BTN_H = 0.073


def _display_key(key: str) -> str:
    return _KEY_DISPLAY.get(key, key.upper())


def _is_bindable(key: str) -> bool:
    if key == "escape":
        return False
    if key.endswith(" up"):
        return False
    if "mouse" in key or "scroll" in key:
        return False
    if key in ("shift", "control", "alt", "windows", "tab"):
        return False
    return True


class SettingsView(BaseView):
    def __init__(
        self,
        controls: ControlsConfig,
        back_callback: Callable[[], None],
    ) -> None:
        super().__init__()

        self._controls = controls
        self.back_callback = back_callback
        self._awaiting_key_for: str | None = None

        self._sound_on: bool = True
        self._volume: int = 70

        self._key_buttons: dict[str, Button] = {}
        self._build_ui()

    # ── Build ──────────────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        Text(
            text="Settings",
            origin=(0, 0),
            y=0.43,
            scale=3,
            color=SUBTITLE_COLOR,
            parent=self,
        )

        # ── Sound ──
        make_section_divider(self, y=0.32, label="SOUND")
        self._btn_sound = make_button(
            self, self._sound_label(), y=0.22, x=-0.12, w=0.22, h=_KEY_BTN_H
        )
        self._btn_sound.on_click = self._toggle_sound

        self._btn_volume = make_button(
            self, self._volume_label(), y=0.22, x=0.16, w=0.22, h=_KEY_BTN_H
        )
        self._btn_volume.on_click = self._cycle_volume

        # ── Controls ──
        make_panel(self, x=0, y=-0.17, w=0.70, h=0.65)
        make_section_divider(self, y=0.11, label="CONTROLS")

        for i, (attr, label) in enumerate(_CONTROL_DEFS):
            row_y = 0.03 - i * 0.08
            Text(
                text=label,
                origin=(-0.5, 0),
                x=-0.28,
                y=row_y,
                scale=1.15,
                color=_LABEL_COLOR,
                parent=self,
            )
            btn = make_button(
                self, self._key_label(attr), y=row_y, x=0.20,
                w=_KEY_BTN_W, h=_KEY_BTN_H,
            )
            btn.on_click = lambda a=attr: self._start_capture(a)
            self._key_buttons[attr] = btn

        self.btn_back = make_button(
            self, "Back", x=0.82, y=-0.46, w=_KEY_BTN_W, h=_KEY_BTN_H
            )
        self.btn_back.on_click = self._on_back

        self.buttons = [
            self._btn_sound,
            self._btn_volume,
            *[self._key_buttons[attr] for attr, _ in _CONTROL_DEFS],
            self.btn_back,
        ]
        self.selected_index = 0
        self.update_highlight()

    # ── Helpers ────────────────────────────────────────────────────────────

    def _key_label(self, attr: str) -> str:
        return f"[{_display_key(getattr(self._controls, attr))}]"

    def _sound_label(self) -> str:
        return f"Sound: {'ON' if self._sound_on else 'OFF'}"

    def _volume_label(self) -> str:
        return f"Vol: {self._volume}%"

    def _toggle_sound(self) -> None:
        self._sound_on = not self._sound_on
        self._btn_sound.text = self._sound_label()

    def _cycle_volume(self) -> None:
        self._volume = (self._volume % 100) + 10
        self._btn_volume.text = self._volume_label()

    def _start_capture(self, attr: str) -> None:
        if self._awaiting_key_for is not None:
            return
        self._awaiting_key_for = attr
        self._key_buttons[attr].text = "Press key..."

    def _cancel_capture(self) -> None:
        if self._awaiting_key_for is None:
            return
        attr = self._awaiting_key_for
        self._awaiting_key_for = None
        self._key_buttons[attr].text = self._key_label(attr)

    # ── Events ─────────────────────────────────────────────────────────────

    def on_exit(self) -> None:
        self._cancel_capture()

    def update_highlight(self) -> None:
        update_menu_highlight(self.buttons, self.selected_index)

    def input(self, key: str) -> None:
        if not self.enabled:
            return

        if self._awaiting_key_for is not None:
            if key == "escape":
                self._cancel_capture()
            elif _is_bindable(key):
                attr = self._awaiting_key_for
                self._awaiting_key_for = None
                setattr(self._controls, attr, key)
                self._key_buttons[attr].text = self._key_label(attr)
            return

        if key in ("backspace", "escape"):
            self._on_back()
            return

        self.selected_index = handle_menu_input(
            key, self.buttons, self.selected_index
        )
        self.update_highlight()

    def _on_back(self) -> None:
        self._cancel_capture()
        self.back_callback()
