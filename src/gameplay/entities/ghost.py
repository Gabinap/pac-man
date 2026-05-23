import random
from typing import TYPE_CHECKING
from ursina import invoke

import src.config.constants as C
from src.utils.utils import grid_to_world
from .animated_entity import AnimatedEntity, _skip_if_destroyed

if TYPE_CHECKING:
    from src.gameplay.maze import Maze


class Ghost(AnimatedEntity):
    def __init__(
        self,
        index: int = 0,
        x: float = 0,
        z: float = 0,
        maze: "Maze | None" = None,
    ) -> None:
        assert maze is not None
        spec = random.choice([s for s in C.MODEL_SPECS if s.supported])
        super().__init__(
            spec=spec,
            maze=maze,
            speed=C.GHOST_SPEED_NORMAL * spec.speed_multiplier,
        )
        self.x, self.z = x, z
        self.spawn_x = x
        self.spawn_z = z
        self.ghost_index = index
        self.last_decision_cell: tuple[int, int] = (-1, -1)
        self.walk()

    def stun(self, duration: float = C.GHOST_RESPAWN_DELAY) -> None:
        self.is_stunned = True

        self.x = self.spawn_x
        self.z = self.spawn_z
        self.update_grid_position()
        self.idle()

        self._blink_loop(lambda: self.is_stunned)

        invoke(self._end_ghost_stun, delay=duration)

    @_skip_if_destroyed
    def _end_ghost_stun(self) -> None:
        self.is_stunned = False
        self.visible = True
        self.walk()

    def _compute_best_dir(
        self, target_x: int, target_y: int, cell_value: int
    ) -> tuple[int, int]:
        directions = [(0, -1, 1), (-1, 0, 8), (0, 1, 4), (1, 0, 2)]
        possible_paths = []
        for dx, dy, wall_flag in directions:
            if cell_value & wall_flag:
                continue
            if (
                self.grid_direction != (0, 0)
                and dx == -self.grid_direction[0]
                and dy == -self.grid_direction[1]
            ):
                continue
            possible_paths.append((dx, dy))

        if not possible_paths:
            return (-self.grid_direction[0], -self.grid_direction[1])

        best_dir = self.grid_direction
        min_dist = float("inf")
        for dx, dy in possible_paths:
            dist = (self.pos_gridx + dx - target_x) ** 2 + (
                self.pos_gridy + dy - target_y
            ) ** 2
            if dist < min_dist:
                min_dist = dist
                best_dir = (dx, dy)
        return best_dir

    def update_ai(self, target_x: int, target_y: int) -> None:
        self.update_grid_position()
        center_x, center_z = grid_to_world(
            self.pos_gridx, self.pos_gridy, self.maze.width, self.maze.height
        )
        cell_value = self.maze.grid[self.pos_gridy][self.pos_gridx]
        dist_to_center = abs(self.x - center_x) + abs(self.z - center_z)
        at_center = dist_to_center < C.AI_CENTER_THRESHOLD

        if at_center or self.grid_direction == (0, 0):
            best_dir = self._compute_best_dir(target_x, target_y, cell_value)
            self._rotate_toward(*best_dir)
            if at_center or self.grid_direction == (0, 0):
                self.grid_direction = best_dir

        self.move_in_direction(self.grid_direction[0], self.grid_direction[1])
