"""Spawning and pickup detection for pacgums and super-pacgums.

Spawns a Pacgum on every open cell (spec picked from the ambiance pool)
and 4 SuperPacgums at strategic positions. Each frame, checks Manhattan
distance against the player (same rule as the ghost↔player collision in
GhostController) and removes any picked-up pacgum, calling the score hook.
"""

import random
from typing import Any, TYPE_CHECKING

from ursina import destroy
from ursina import time as _ursina_time

import src.config.constants as C
from src.gameplay.entities import Pacgum, Player, SuperPacgum
from src.config.game_config import GameConfig
from src.gameplay.maze import Maze

if TYPE_CHECKING:
    from src.game_engine import GameEngine

ursina_time: Any = _ursina_time


class PacgumController:
    """Spawn pacgums/super-pacgums and award points on player pickup."""

    def __init__(
        self,
        engine: "GameEngine",
        player: Player,
        maze: Maze,
        ambiance: C.Ambiance,
        config: GameConfig,
    ) -> None:
        self.engine = engine
        self.player = player
        self.maze = maze
        self.config = config
        self.pacgums: list[Pacgum] = []
        self.pacgum_count = 0
        self.super_count = 0

        self._w, self._h = self.maze.width, self.maze.height
        self._candidates = [
            (1, 1),
            (self._w - 2, 1),
            (1, self._h - 2),
            (self._w - 2, self._h - 2),
        ]
        self._spawn(ambiance)

    def _open_cells(self) -> list[tuple[int, int]]:
        return [
            (x, z)
            for z, row in enumerate(self.maze.grid)
            for x, cell in enumerate(row)
            if cell != 15
            and (x, z) not in self._candidates + [(self._h // 2, self._w // 2)]
        ]

    def _super_positions(
        self, open_cells: set[tuple[int, int]]
    ) -> list[tuple[int, int]]:
        chosen: list[tuple[int, int]] = []
        for cx, cy in self._candidates:
            spot = self._find_open_near(cx, cy, open_cells, chosen)
            if spot is not None:
                chosen.append(spot)
        return chosen

    def _find_open_near(
        self,
        cx: int,
        cy: int,
        open_cells: set[tuple[int, int]],
        taken: list[tuple[int, int]],
    ) -> tuple[int, int] | None:
        for dx in range(self._w):
            for dy in range(self._h):
                fx = min(max(cx + dx, 0), self._w - 1)
                fy = min(max(cy + dy, 0), self._h - 1)
                if (fx, fy) in open_cells and (fx, fy) not in taken:
                    return (fx, fy)
        return None

    def _spawn(self, ambiance: C.Ambiance) -> None:
        rng = random.Random(self.config.seed)
        regular_cells = self._open_cells()
        # _super_positions falls back to any non-wall cell; build the full
        # open set (without the candidate filter) for that lookup.
        full_open = {
            (x, z)
            for z, row in enumerate(self.maze.grid)
            for x, cell in enumerate(row)
            if cell != 15
        }
        super_cells = self._super_positions(full_open)
        super_set = set(super_cells)

        for (gx, gy), spec in zip(
            super_cells, ambiance.super_pacgums, strict=False
        ):
            self.pacgums.append(
                SuperPacgum(
                    spec=spec,
                    grid_x=gx,
                    grid_y=gy,
                    maze=self.maze,
                    points=self.config.points_per_super_pacgum,
                )
            )
            self.super_count += 1

        eligible = [c for c in regular_cells if c not in super_set]
        for gx, gy in eligible:
            spec = rng.choice(ambiance.pacgums)
            self.pacgums.append(
                Pacgum(
                    spec=spec,
                    grid_x=gx,
                    grid_y=gy,
                    maze=self.maze,
                    points=self.config.points_per_pacgum,
                )
            )
            self.pacgum_count += 1

        if self.engine and self.engine.hud:
            self.engine.hud.update_pacgums(self.pacgum_count)
            self.engine.hud.update_super_pacgums(self.super_count)

    def _picked_up(self, pacgum: Pacgum) -> bool:
        dx = abs(self.player.x - pacgum.x)
        dz = abs(self.player.z - pacgum.z)
        return bool((dx + dz) < C.PICKUP_DISTANCE)

    def update(self) -> None:
        if not self.pacgums:
            return
        # Centralized spin: one tight Python loop instead of N Entity.update
        # callbacks dispatched by Ursina every frame.
        spin = Pacgum.SPIN_SPEED * ursina_time.dt
        remaining: list[Pacgum] = []
        for pacgum in self.pacgums:
            pacgum.rotation_y += spin
            if self._picked_up(pacgum):
                self.engine.session.add_score(pacgum.points)
                if pacgum.is_super:
                    self.player.empower()
                    self.engine.hud.show_empowered_bar()
                    self.super_count -= 1
                    self.engine.hud.update_super_pacgums(self.super_count)
                else:
                    self.pacgum_count -= 1
                    self.engine.hud.update_pacgums(self.pacgum_count)
                destroy(pacgum)
            else:
                remaining.append(pacgum)
        self.pacgums = remaining
        if not self.pacgums:
            self.engine.session.on_level_complete()

    def eat_all(self) -> None:
        for p in self.pacgums:
            self.engine.session.add_score(p.points)
            destroy(p)
        self.pacgum_count = 0
        self.super_count = 0
        self.engine.hud.update_pacgums(0)
        self.engine.hud.update_super_pacgums(0)
        self.pacgums = []
        self.engine.session.on_level_complete()

    def destroy_all(self) -> None:
        for pacgum in self.pacgums:
            destroy(pacgum)
        self.pacgums = []
