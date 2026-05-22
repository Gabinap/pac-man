"""Ghost AI and collision detection with the player.

Implements the four classic Pac-Man targeting strategies (Blinky/Pinky/
Inky/Clyde) and propagates game state transitions to every ghost.
"""

from enum import Enum, auto
from typing import TYPE_CHECKING, Callable
from collections import deque

import src.config.constants as C
from src.gameplay.entities import Ghost, Player, PlayerState
from src.gameplay.maze import Maze
from src.utils.utils import grid_to_world, world_to_grid

if TYPE_CHECKING:
    from src.game_engine import GameEngine


class GhostState(Enum):
    HUNT = auto()
    FRIGHTENED = auto()


class GhostController:
    """Spawn, route, and collide all ghosts against the player."""

    def __init__(
        self,
        engine: "GameEngine",
        player: Player,
        maze: Maze,
        game_state: C.EGameState,
        add_score: Callable[[int], None],
        ghost_count: int = C.GHOST_COUNT,
    ) -> None:
        self.engine = engine
        self._game_state = game_state
        self.player = player
        self.maze = maze
        self._ghost_count = ghost_count
        self.start_grid_indices = [
            (0, 0),
            (self.maze.width - 1, 0),
            (0, self.maze.height - 1),
            (self.maze.width - 1, self.maze.height - 1),
        ]
        self.ghosts: list[Ghost] = self._init_ghosts()
        self.ghosts_killed = 0
        self._add_score = add_score

        if self.engine and self.engine.hud:
            self.engine.hud.update_ghosts_killed(self.ghosts_killed)

    @property
    def game_state(self) -> C.EGameState:
        return self._game_state

    @game_state.setter
    def game_state(self, value: C.EGameState) -> None:
        self._game_state = value
        for ghost in self.ghosts:
            ghost.game_state = value
            if value == C.EGameState.RUNNING:
                ghost.walk()
            elif value == C.EGameState.GAME_OVER:
                attack_idx = ghost.spec.anim_attack
                if isinstance(attack_idx, tuple):
                    attack_names = {ghost._anims[i] for i in attack_idx}
                else:
                    attack_names = {ghost._anims[attack_idx]}
                if ghost._current_anim not in attack_names:
                    ghost.idle()

    def _init_ghosts(self) -> list[Ghost]:
        ghosts: list[Ghost] = []

        for i in range(self._ghost_count):
            grid_x, grid_y = self.start_grid_indices[
                i % len(self.start_grid_indices)
            ]
            world_x, world_z = grid_to_world(
                grid_x, grid_y, self.maze.width, self.maze.height
            )

            ghost_entity = Ghost(i, x=world_x, z=world_z, maze=self.maze)
            # Ghost.__init__ inherits game_state=NOT_STARTED via AnimatedEntity
            # regardless of actual state. On level 1 this is fine
            # (start_game flips RUNNING via the setter, which calls walk()),
            # but on level 2+ init_level does not touch engine.game_state, so
            # the setter never fires, ghost.update() forces idle every frame.
            # Propagate it explicitly here.
            ghost_entity.game_state = self._game_state
            ghosts.append(ghost_entity)

        return ghosts

    def update_ghosts(self) -> None:
        if self.game_state != C.EGameState.RUNNING:
            return

        for ghost in self.ghosts:
            if ghost.is_stunned:
                continue

            target_x, target_z = self._get_target_for_ghost(ghost)
            ghost.update_grid_position()

            ghost_grid = (ghost.pos_gridx, ghost.pos_gridy)
            target_grid = (target_x, target_z)

            if not hasattr(ghost, "_bfs_path"):
                ghost._bfs_path = []
                ghost._last_target = None

            if ghost._last_target != target_grid or (
                not ghost._bfs_path and ghost_grid != target_grid
            ):
                ghost._last_target = target_grid
                ghost._bfs_path = self._bfs_find_path(ghost_grid, target_grid)
                if ghost._bfs_path:
                    ghost._bfs_path.pop(0)

            if ghost._bfs_path and ghost_grid == ghost._bfs_path[0]:
                ghost._bfs_path.pop(0)

            if ghost._bfs_path:
                next_x, next_y = ghost._bfs_path[0]
            else:
                next_x, next_y = target_x, target_z

            if self.check_collision_with_player(ghost):
                can_eat = (
                    self.player.state == PlayerState.EMPOWERED
                    or self.player.cheat_mode
                )
                if can_eat:
                    if not ghost.is_stunned:
                        self.player.attack()
                        ghost.stun()
                        self.ghosts_killed += 1
                        self._add_score(self.engine.config.points_per_ghost)
                        if self.engine and self.engine.hud:
                            self.engine.hud.update_ghosts_killed(
                                self.ghosts_killed
                            )
                elif (
                    self.player.state != PlayerState.UNTOUCHABLE
                    and self.player.state != PlayerState.STUNNED
                ):
                    self.handle_attack(ghost, self.player)
            if not ghost.is_attacking and not ghost.is_stunned:
                ghost.update_ai(next_x, next_y)

    def _get_target_for_ghost(self, ghost: Ghost) -> tuple[int, int]:
        if self.player.state == PlayerState.EMPOWERED:
            return self._calculate_flee_target()
        if ghost.ghost_index == 1:
            return self._calculate_pinky_target()
        if ghost.ghost_index == 2:
            return self._calculate_inky_target(self.ghosts[0])
        if ghost.ghost_index == 3:
            return self._calculate_clyde_target(ghost)

        return (self.player.pos_gridx, self.player.pos_gridy)

    def _calculate_flee_target(self) -> tuple[int, int]:
        max_dist: int = -1
        best_corner = (0, 0)
        for corner_x, corner_y in self.start_grid_indices:
            dist = ((corner_x - self.player.pos_gridx) ** 2) + (
                (corner_y - self.player.pos_gridy) ** 2
            )
            if dist > max_dist:
                max_dist = dist
                best_corner = (corner_x, corner_y)
        return best_corner

    def check_collision_with_player(self, ghost: Ghost) -> bool:
        px, pz = self.player.x, self.player.z
        gx, gz = ghost.x, ghost.z

        distance_player_ghost = abs(px - gx) + abs(pz - gz)

        return distance_player_ghost < C.PICKUP_DISTANCE

    def handle_attack(self, attacker: Ghost, target: Player) -> None:
        duration = attacker.attack()
        if not target.infinite_lives:
            target.health -= 1
            if self.engine and self.engine.hud:
                self.engine.hud.update_health(target.health)
        target.be_stunned(duration)

    def _bfs_find_path(
        self, start: tuple[int, int], target: tuple[int, int]
    ) -> list[tuple[int, int]]:
        """Calcule le chemin le plus court sur la grille à l'aide d'un BFS."""
        if start == target:
            return [start]

        queue = deque([[start]])
        visited = {start}

        dirs = [(0, -1, 1), (-1, 0, 8), (0, 1, 4), (1, 0, 2)]

        while queue:
            path = queue.popleft()
            cx, cy = path[-1]

            if (cx, cy) == target:
                return path

            cell_value = self.maze.grid[cy][cx]
            for dx, dy, wall_flag in dirs:
                if cell_value & wall_flag:
                    continue

                nx, ny = cx + dx, cy + dy
                if 0 <= nx < self.maze.width and 0 <= ny < self.maze.height:
                    if (nx, ny) not in visited:
                        visited.add((nx, ny))
                        queue.append(path + [(nx, ny)])

        return []

    def _calculate_pinky_target(self) -> tuple[int, int]:
        p_grid_x, p_grid_y = world_to_grid(
            self.player.x, self.player.z, self.maze.width, self.maze.height
        )
        raw_x = p_grid_x + (4 * self.player.grid_direction[0])
        raw_y = p_grid_y + (4 * self.player.grid_direction[1])
        target_x = max(0, min(raw_x, self.maze.width - 1))
        target_y = max(0, min(raw_y, self.maze.height - 1))
        return (target_x, target_y)

    def _calculate_inky_target(self, blinky: Ghost) -> tuple[int, int]:
        p_grid_x, p_grid_y = world_to_grid(
            self.player.x, self.player.z, self.maze.width, self.maze.height
        )
        b_grid_x, b_grid_y = world_to_grid(
            blinky.x, blinky.z, self.maze.width, self.maze.height
        )

        pivot_x = p_grid_x + (2 * self.player.grid_direction[0])
        pivot_y = p_grid_y + (2 * self.player.grid_direction[1])

        vector_x = pivot_x - b_grid_x
        vector_y = pivot_y - b_grid_y

        raw_x = b_grid_x + (2 * vector_x)
        raw_y = b_grid_y + (2 * vector_y)

        target_x = max(0, min(raw_x, self.maze.width - 1))
        target_y = max(0, min(raw_y, self.maze.height - 1))

        return (target_x, target_y)

    def _calculate_clyde_target(self, clyde: Ghost) -> tuple[int, int]:
        p_grid_x, p_grid_y = world_to_grid(
            self.player.x, self.player.z, self.maze.width, self.maze.height
        )
        c_grid_x, c_grid_y = world_to_grid(
            clyde.x, clyde.z, self.maze.width, self.maze.height
        )

        square_distance = (p_grid_x - c_grid_x) ** 2 + (
            p_grid_y - c_grid_y
        ) ** 2

        if square_distance > 15:
            raw_x, raw_y = p_grid_x, p_grid_y
        else:
            raw_x, raw_y = 0, self.maze.height - 1
        target_x = max(0, min(raw_x, self.maze.width - 1))
        target_y = max(0, min(raw_y, self.maze.height - 1))

        return (target_x, target_y)
