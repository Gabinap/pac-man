"""HUD overlay: split into left and right columns to keep the map clear."""

from typing import Any
from ursina import Text, time, camera, Entity, curve, invoke
import src.config.constants as C
from src.utils.views_utils import (
    EMPOWERED_BAR_COLOR,
    SCORES_TITLE_COLOR,
    TEXT_COLOR,
    make_panel,
)

_L = -0.85  # left column x anchor
_R = 0.85  # right column x anchor

# FPS jitters every frame — smooth over a short window so the readout is
# legible and doesn't redraw 60 times per second with random integers.
_FPS_SMOOTHING: float = 0.2


class HUD:
    """In-game heads-up display: score, lives, timer, and empowered bar."""

    def __init__(self, view_mode: C.EViewMode) -> None:
        """Build all HUD text entities and background panels."""
        self._view_mode = view_mode

        self._bg_panels: list[Any] = [
            *make_panel(camera.ui, x=-0.7, y=0.285, w=0.4, h=0.42),
            *make_panel(camera.ui, x=0.72, y=0.38, w=0.31, h=0.22),
        ]

        self._level_text = self._left("Lv.1", 0.45, scale=2)
        self._health_text = self._left("Lives: 0", 0.38, scale=2)
        self._pacgums_text = self._left("Pacgums: 0", 0.26, scale=1.5)
        self._super_text = self._left("Super: 0", 0.19, scale=1.5)
        self._ghosts_text = self._left("Ghosts: 0", 0.12, scale=1.5)

        self._fps_text = self._right("FPS: 0", 0.45, scale=2)
        self._score_text = self._right("Score: 0", 0.38, scale=2)
        self._empowered_bar_text = self._right(
            "Empowered", 0.20, scale=1, enabled=False, color=SCORES_TITLE_COLOR
        )
        self._empowered_bar = Entity(
            model="quad",
            parent=camera.ui,
            color=EMPOWERED_BAR_COLOR,
            origin=(0.5, 0),
            position=(_R, 0.15),
            scale=(
                0.18,
                0.02,
            ),
            enabled=False,
        )
        self._hide_bar_seq = None

        self._fps_avg: float = 0.0
        self.visible = False

    @staticmethod
    def _left(text: str, y: float, scale: float = 1.5) -> Text:
        """Create a left-aligned HUD text entity."""
        return Text(
            text=text,
            origin=(-0.5, 0),
            position=(_L, y),
            scale=scale,
            color=TEXT_COLOR,
        )

    @staticmethod
    def _right(text: str, y: float, scale: float = 1.5, **kwargs: Any) -> Text:
        """Create a right-aligned HUD text entity."""
        kwargs.setdefault("color", TEXT_COLOR)
        return Text(
            text=text, origin=(0.5, 0), position=(_R, y), scale=scale, **kwargs
        )

    def show(self) -> None:
        """Enable all HUD entities."""
        for entity in self._all_entities():
            entity.enabled = True
        self.visible = True

    def hide(self) -> None:
        """Disable all HUD entities."""
        for entity in self._all_entities():
            entity.enabled = False
        self.visible = False

    def _all_entities(self) -> list[Any]:
        """Return all persistently visible HUD entities."""
        return [
            *self._bg_panels,
            self._level_text,
            self._health_text,
            self._pacgums_text,
            self._super_text,
            self._ghosts_text,
            self._fps_text,
            self._score_text,
        ]

    def update_score(self, score: int) -> None:
        """Update the score display."""
        self._score_text.text = f"Score: {score}"

    def update_level(self, level: int) -> None:
        """Update the level display."""
        self._level_text.text = f"Lv.{level + 1}"

    def update_health(self, health: int) -> None:
        """Update the lives display; negative health means infinite lives."""
        self._health_text.text = (
            "Lives: ∞" if health < 0 else f"Lives: {health}"
        )

    def update_pacgums(self, count: int) -> None:
        """Update the remaining pacgum count display."""
        self._pacgums_text.text = f"Pacgums: {count}"

    def update_super_pacgums(self, count: int) -> None:
        """Update the remaining super-pacgum count display."""
        self._super_text.text = f"Super: {count}"

    def update_ghosts_killed(self, count: int) -> None:
        """Update the ghosts-killed counter display."""
        self._ghosts_text.text = f"Ghosts killed: {count}"

    def show_empowered_bar(self) -> None:
        """Show the empowered bar draining over FRIGHTENED_DURATION."""
        self._empowered_bar.enable()
        self._empowered_bar_text.enable()
        if self._hide_bar_seq:
            self._hide_bar_seq.pause()
            self._hide_bar_seq = None
        self._empowered_bar.scale_x = 0.18
        self._empowered_bar.animate(
            "scale_x", 0, duration=C.FRIGHTENED_DURATION, curve=curve.linear
        )

        self._hide_bar_seq = invoke(
            self._hide_empowered_bar, delay=C.FRIGHTENED_DURATION
        )

    def _hide_empowered_bar(self) -> None:
        """Hide the empowered bar and its label."""
        self._empowered_bar.disable()
        self._empowered_bar_text.disable()

    def update(self) -> None:
        """Smooth the FPS average and refresh the FPS text once per frame."""
        if time.dt > 0:
            instant_fps = 1.0 / time.dt
            if self._fps_avg == 0.0:
                self._fps_avg = instant_fps
            else:
                self._fps_avg += (instant_fps - self._fps_avg) * _FPS_SMOOTHING

        new_fps_text = f"FPS: {int(self._fps_avg)}"
        if self._fps_text.text != new_fps_text:
            self._fps_text.text = new_fps_text
