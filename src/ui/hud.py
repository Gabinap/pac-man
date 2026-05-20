"""HUD overlay: split into left and right columns to keep the map clear."""

from ursina import Text, time, camera

import src.config.constants as C
from src.utils.views_utils import make_panel

_L = -0.85  # left column x anchor
_R = 0.85  # right column x anchor

# FPS jitters every frame — smooth over a short window so the readout is
# legible and doesn't redraw 60 times per second with random integers.
_FPS_SMOOTHING: float = 0.2


class HUD:
    def __init__(self, view_mode: C.EViewMode) -> None:
        self._view_mode = view_mode

        # Background pills — created before text so they sit behind (z=0.019).
        self._bg_panels: list = [
            # Left cluster: Lv / Lives / Pacgums / Super / Ghosts
            *make_panel(camera.ui, x=-0.645, y=0.285, w=0.44, h=0.42),
            # Right cluster: FPS / Score
            *make_panel(camera.ui, x=0.672, y=0.415, w=0.42, h=0.175),
        ]

        self._level_text = self._left("Lv.1", 0.45, scale=2)
        self._health_text = self._left("Lives: 0", 0.38, scale=2)
        self._pacgums_text = self._left("Pacgums: 0", 0.26, scale=1.5)
        self._super_text = self._left("Super: 0", 0.19, scale=1.5)
        self._ghosts_text = self._left("Ghosts: 0", 0.12, scale=1.5)

        self._fps_text = self._right("FPS: 0", 0.45, scale=2)
        self._score_text = self._right("Score: 0", 0.38, scale=2)

        self._fps_avg: float = 0.0
        self.visible = False

    @staticmethod
    def _left(text: str, y: float, scale: float = 1.5) -> Text:
        return Text(
            text=text,
            origin=(-0.5, 0),
            position=(_L, y),
            scale=scale,
        )

    @staticmethod
    def _right(text: str, y: float, scale: float = 1.5) -> Text:
        return Text(
            text=text,
            origin=(0.5, 0),
            position=(_R, y),
            scale=scale,
        )

    def show(self) -> None:
        for entity in self._all_entities():
            entity.enabled = True
        self.visible = True

    def hide(self) -> None:
        for entity in self._all_entities():
            entity.enabled = False
        self.visible = False

    def _all_entities(self) -> list:
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
        self._score_text.text = f"Score: {score}"

    def update_level(self, level: int) -> None:
        self._level_text.text = f"Lv.{level + 1}"

    def update_health(self, health: int) -> None:
        self._health_text.text = (
            "Lives: ∞" if health < 0 else f"Lives: {health}"
        )

    def update_pacgums(self, count: int) -> None:
        self._pacgums_text.text = f"Pacgums: {count}"

    def update_super_pacgums(self, count: int) -> None:
        self._super_text.text = f"Super: {count}"

    def update_ghosts_killed(self, count: int) -> None:
        self._ghosts_text.text = f"Ghosts killed: {count}"

    def update(self) -> None:
        if time.dt > 0:
            instant_fps = 1.0 / time.dt
            if self._fps_avg == 0.0:
                self._fps_avg = instant_fps
            else:
                self._fps_avg += (instant_fps - self._fps_avg) * _FPS_SMOOTHING

        new_fps_text = f"FPS: {int(self._fps_avg)}"
        if self._fps_text.text != new_fps_text:
            self._fps_text.text = new_fps_text
