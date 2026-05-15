"""Spawning and pickup detection for pacgums and super-pacgums.

Spawns a Pacgum on every open cell (spec picked from the ambiance pool)
and 4 SuperPacgums at strategic positions. Each frame, checks Manhattan
distance against the player (same rule as the ghost↔player collision in
GhostController) and removes any picked-up pacgum, calling the score hook.
"""

import random
from typing import Callable

from ursina import destroy

import src.constants as C
from src.entities import Pacgum, Player, SuperPacgum
from src.game_config import GameConfig
from src.maze import Maze


_PICKUP_DISTANCE: float = 0.5


class PacgumController:
    def __init__(
        self,
        player: Player,
        maze: Maze,
        ambiance: C.Ambiance,
        gcf: GameConfig,
        on_score: Callable[[int], None],
    ) -> None:
        self.player = player
        self.maze = maze
        self.gcf = gcf
        self.on_score = on_score
        self.pacgums: list[Pacgum] = []
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
            if cell != 15 and (x, z) not in
            self._candidates + [(self._h // 2, self._w // 2)]
        ]

    def _super_positions(
        self, open_cells: set[tuple[int, int]]
    ) -> list[tuple[int, int]]:
        chosen: list[tuple[int, int]] = []
        for cx, cy in self._candidates:
            if (cx, cy) in open_cells:
                chosen.append((cx, cy))
                continue
            # walk inward until we hit an open cell
            for dx in range(self._w):
                for dy in range(self._h):
                    fx = min(max(cx + dx, 0), self._w - 1)
                    fy = min(max(cy + dy, 0), self._h - 1)
                    if (fx, fy) in open_cells and (fx, fy) not in chosen:
                        chosen.append((fx, fy))
                        break
                else:
                    continue
                break
        return chosen

    def _spawn(self, ambiance: C.Ambiance) -> None:
        rng = random.Random(self.gcf.seed)
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
                    points=self.gcf.points_per_super_pacgum,
                )
            )

        for gx, gy in regular_cells:
            if (gx, gy) in super_set:
                continue
            spec = rng.choice(ambiance.pacgums)
            self.pacgums.append(
                Pacgum(
                    spec=spec,
                    grid_x=gx,
                    grid_y=gy,
                    maze=self.maze,
                    points=self.gcf.points_per_pacgum,
                )
            )

    def _picked_up(self, pacgum: Pacgum) -> bool:
        dx = abs(self.player.x - pacgum.x)
        dz = abs(self.player.z - pacgum.z)
        return (dx + dz) < _PICKUP_DISTANCE

    def update(self) -> None:
        remaining: list[Pacgum] = []
        for pacgum in self.pacgums:
            if self._picked_up(pacgum):
                self.on_score(pacgum.points)
                destroy(pacgum)
            else:
                remaining.append(pacgum)
        self.pacgums = remaining

    def destroy_all(self) -> None:
        for pacgum in self.pacgums:
            destroy(pacgum)
        self.pacgums = []
