"""Main menu view: title, navigation buttons, and highscores panel."""

from panda3d.core import TransparencyAttrib
from ursina import Button, Text, color, application, Entity, Quad
from typing import Callable

from src.views.base import BaseView
from src.highscores import Highscores
from src.game_config import GameConfig
import src.constants as C

# color.rgba expects 0-1 floats; color.rgba32 expects 0-255 ints.
# Wes Anderson-inspired: dusty sage / powder blue / mustard / burgundy
# / dusty rose / cream. Muted but multi-hued.
_GLASS = color.rgba32(150, 180, 160, 105)              # dusty sage
_GLASS_HOVER = color.rgba32(180, 205, 220, 140)        # powder blue
_GLASS_SELECTED = color.rgba32(220, 175, 80, 170)      # mustard
_GLASS_EXIT_SELECTED = color.rgba32(165, 70, 75, 180)  # burgundy
_BORDER = color.rgba32(240, 220, 185, 130)             # warm cream
_TEXT = color.rgba32(250, 240, 220, 255)               # cream

# Title & section text palette
_TITLE_COLOR = color.rgba32(230, 150, 170, 255)        # Grand Budapest pink
_TITLE_OUTLINE = color.rgba32(95, 35, 60, 255)         # deep wine — outline
_SUBTITLE_COLOR = color.rgba32(180, 205, 220, 255)     # powder blue
_SCORES_TITLE_COLOR = color.rgba32(225, 180, 80, 255)  # mustard
_SCORE_ENTRY_COLOR = color.rgba32(245, 235, 215, 255)  # cream
_EMPTY_SCORE_COLOR = color.rgba32(150, 160, 145, 255)  # muted sage-grey

# Glass panels
_PANEL_COLOR = color.rgba32(30, 45, 50, 150)           # deep forest-navy
_PANEL_BORDER = color.rgba32(225, 200, 160, 120)       # warm cream

_BTN_W, _BTN_H = 0.42, 0.085
_BTN_SCALE = (_BTN_W, _BTN_H)
_BTN_ASPECT = _BTN_W / _BTN_H  # ~4.94 — passed to Quad to keep corners round
_BORDER_PAD = 0.006
_CORNER_RADIUS = 0.5  # 0.5 = full pill shape
_CORNER_SEGMENTS = 16
_PANEL_RADIUS = 0.35  # pronounced rounding, not a pill
_PANEL_BORDER_PAD = 0.008

_DIFFICULTIES = [C.EDifficulty.EASY, C.EDifficulty.MEDIUM, C.EDifficulty.HARD]


class MainMenuView(BaseView):
    """Title screen with glassmorphism buttons and a highscores panel."""

    def __init__(
        self,
        config: GameConfig,
        scores_manager: Highscores,
        difficulty: C.EDifficulty,
        start_game: Callable[[], None],
        show_instructions: Callable[[], None],
        set_difficulty: Callable[[C.EDifficulty], None] = lambda _: None,
    ) -> None:
        super().__init__()

        self.start_game = start_game
        self.show_instructions = show_instructions
        self.difficulty = difficulty
        self.config = config
        self.scores_manager = scores_manager
        self._set_difficulty = set_difficulty

        self.title = self._make_outlined_text(
            "PAK-MAN",
            y=0.32,
            scale=6,
            fill=_TITLE_COLOR,
            outline=_TITLE_OUTLINE,
            thickness=0.008,
        )
        self.start_text = Text(
            text="Press SPACE to play",
            origin=(0, 0),
            color=_SUBTITLE_COLOR,
            scale=1.5,
            y=0.2,
            parent=self,
        )

        self.btn_start = self._make_button("Start Game", y=0.1)
        self.btn_start.on_click = self.start_game

        self.btn_difficulty = self._make_button(
            f"Difficulty: {self.difficulty.value}", y=0.0
        )
        self.btn_difficulty.on_click = self.change_difficulty

        self.btn_instructions = self._make_button("Instructions", y=-0.1)
        self.btn_instructions.on_click = self.show_instructions

        self.btn_exit = self._make_button("Exit", y=-0.2)
        self.btn_exit.on_click = application.quit

        self.buttons = [
            self.btn_start,
            self.btn_difficulty,
            self.btn_instructions,
            self.btn_exit,
        ]
        self.selected_index = 0
        self.update_highlight()
        self._render_highscores()

    def _make_outlined_text(
        self,
        text: str,
        y: float,
        scale: float,
        fill: object,
        outline: object,
        thickness: float = 0.008,
    ) -> Text:
        # Panda3D's TextNode has no real outline — fake it with 8 offset
        # copies behind the main text (cardinal + diagonal directions).
        offsets = [
            (-1, 0), (1, 0), (0, -1), (0, 1),
            (-0.7, -0.7), (0.7, -0.7), (-0.7, 0.7), (0.7, 0.7),
        ]
        for dx, dy in offsets:
            Text(
                text,
                origin=(0, 0),
                x=dx * thickness,
                y=y + dy * thickness,
                z=0.001,
                scale=scale,
                color=outline,
                parent=self,
            )
        return Text(
            text,
            origin=(0, 0),
            y=y,
            scale=scale,
            color=fill,
            parent=self,
        )

    def _make_panel(
        self, x: float, y: float, w: float, h: float
    ) -> None:
        aspect = w / h if h > 0 else 1.0
        border = Entity(
            model=Quad(
                radius=_PANEL_RADIUS, segments=12, aspect=aspect
            ),
            color=_PANEL_BORDER,
            scale=(w + _PANEL_BORDER_PAD, h + _PANEL_BORDER_PAD),
            position=(x, y, 0.02),
            parent=self,
        )
        border.setTransparency(TransparencyAttrib.MAlpha)
        panel = Entity(
            model=Quad(
                radius=_PANEL_RADIUS, segments=12, aspect=aspect
            ),
            color=_PANEL_COLOR,
            scale=(w, h),
            position=(x, y, 0.019),
            parent=self,
        )
        panel.setTransparency(TransparencyAttrib.MAlpha)

    def _make_button(self, text: str, y: float) -> Button:
        border = Entity(
            model=Quad(
                radius=_CORNER_RADIUS,
                segments=_CORNER_SEGMENTS,
                aspect=_BTN_ASPECT,
            ),
            color=_BORDER,
            scale=(
                _BTN_SCALE[0] + _BORDER_PAD,
                _BTN_SCALE[1] + _BORDER_PAD,
            ),
            position=(0, y, 0.001),
            parent=self,
        )
        border.setTransparency(TransparencyAttrib.MAlpha)
        btn = Button(
            text=text,
            model=Quad(
                radius=_CORNER_RADIUS,
                segments=_CORNER_SEGMENTS,
                aspect=_BTN_ASPECT,
            ),
            color=_GLASS,
            highlight_color=_GLASS_HOVER,
            pressed_color=_GLASS_HOVER,
            scale=_BTN_SCALE,
            y=y,
            parent=self,
        )
        btn.setTransparency(TransparencyAttrib.MAlpha)
        btn.text_entity.color = _TEXT
        return btn

    def update_highlight(self) -> None:
        for btn in self.buttons:
            btn.color = _GLASS
        selected = self.buttons[self.selected_index]
        if selected is self.btn_exit:
            selected.color = _GLASS_EXIT_SELECTED
        else:
            selected.color = _GLASS_SELECTED

    def _render_highscores(self) -> None:
        self._make_panel(x=-0.6, y=0.4, w=0.42, h=0.07)
        Text(
            "- BEST SCORES -",
            parent=self,
            origin=(-0.5, 0),
            x=-0.8,
            y=0.4,
            scale=1.5,
            color=_SCORES_TITLE_COLOR,
        )

        scores_list = self.scores_manager.get_top_scores()

        start_y = 0.3

        if not scores_list:
            Text(
                "No scores yet...",
                parent=self,
                origin=(-0.5, 0),
                x=-0.8,
                y=start_y,
                scale=0.8,
                color=_EMPTY_SCORE_COLOR,
            )
            return

        for i, (name, score) in enumerate(scores_list[:10]):
            Text(
                f"{i+1}. {name} - {score}",
                parent=self,
                origin=(-0.5, 0),
                x=-0.8,
                y=start_y - (i * 0.08),
                scale=0.8,
                color=_SCORE_ENTRY_COLOR,
            )

    def input(self, key: str) -> None:
        if not self.enabled:
            return
        if key == "space":
            self.start_game()
        elif key == "up arrow":
            self.selected_index = (
                self.selected_index - 1
            ) % len(self.buttons)
            self.update_highlight()
        elif key == "down arrow":
            self.selected_index = (
                self.selected_index + 1
            ) % len(self.buttons)
            self.update_highlight()
        elif key == "enter":
            action = self.buttons[self.selected_index].on_click
            if action:
                action()
        elif key in ("q", "escape"):
            application.quit()

    def change_difficulty(self) -> None:
        idx = _DIFFICULTIES.index(self.difficulty)
        self.difficulty = _DIFFICULTIES[(idx + 1) % len(_DIFFICULTIES)]
        self._set_difficulty(self.difficulty)
        self.btn_difficulty.text = f"Difficulty: {self.difficulty.value}"
