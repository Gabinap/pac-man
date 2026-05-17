"""HUD overlay: split into left and right columns to keep the map clear."""

from typing import Callable

from ursina import Text, time

import src.config.constants as C

_L = -0.85  # left column x anchor
_R = 0.85   # right column x anchor

# FPS jitters every frame — smooth over a short window so the readout is
# legible and doesn't redraw 60 times per second with random integers.
_FPS_SMOOTHING: float = 0.2


class HUD:
    def __init__(
        self,
        view_mode: C.EViewMode,
        get_score: Callable[[], int],
        get_health: Callable[[], int],
        get_level: Callable[[], int],
        get_pacgums: Callable[[], int],
        get_super_pacgums: Callable[[], int],
        get_ghosts_killed: Callable[[], int],
    ) -> None:
        self._view_mode = view_mode
        self._get_score = get_score
        self._get_health = get_health
        self._get_level = get_level
        self._get_pacgums = get_pacgums
        self._get_super_pacgums = get_super_pacgums
        self._get_ghosts_killed = get_ghosts_killed

        # left column
        self._level_text = self._left("Lv.1", 0.45, scale=2)
        self._health_text = self._left("Lives: 0", 0.38, scale=2)
        self._pacgums_text = self._left("Pacgums: 0", 0.26, scale=1.5)
        self._super_text = self._left("Super: 0", 0.19, scale=1.5)
        self._ghosts_text = self._left("Ghosts: 0", 0.12, scale=1.5)
        self._controls_text = self._left(
            "Move: WASD / Arrows", -0.42, scale=1.3
        )

        # right column
        self._fps_text = self._right("FPS: 0", 0.45, scale=2)
        self._score_text = self._right("Score: 0", 0.38, scale=2)

        # Cached last-rendered values: skip the property write when the
        # string hasn't changed. Stored as strings so we compare with the
        # already-formatted text and avoid one branch.
        self._cache: dict[str, str] = {}
        self._fps_avg: float = 0.0

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

    def hide(self) -> None:
        for entity in self._all_entities():
            entity.enabled = False

    def _all_entities(self) -> list:
        return [
            self._level_text,
            self._health_text,
            self._pacgums_text,
            self._super_text,
            self._ghosts_text,
            self._controls_text,
            self._fps_text,
            self._score_text,
        ]

    def _set(self, key: str, entity: Text, new_text: str) -> None:
        if self._cache.get(key) == new_text:
            return
        entity.text = new_text
        self._cache[key] = new_text

    def update(self) -> None:
        self._set("level", self._level_text, f"Lv.{self._get_level()}")
        health = self._get_health()
        self._set(
            "health",
            self._health_text,
            "Lives: ∞" if health < 0 else f"Lives: {health}",
        )
        self._set(
            "pacgums", self._pacgums_text, f"Pacgums: {self._get_pacgums()}"
        )
        self._set(
            "super", self._super_text, f"Super: {self._get_super_pacgums()}"
        )
        self._set(
            "ghosts", self._ghosts_text, f"Ghosts: {self._get_ghosts_killed()}"
        )
        self._set("score", self._score_text, f"Score: {self._get_score()}")

        if time.dt > 0:
            instant_fps = 1.0 / time.dt
            if self._fps_avg == 0.0:
                self._fps_avg = instant_fps
            else:
                self._fps_avg += (
                    instant_fps - self._fps_avg
                ) * _FPS_SMOOTHING
        self._set("fps", self._fps_text, f"FPS: {int(self._fps_avg)}")
