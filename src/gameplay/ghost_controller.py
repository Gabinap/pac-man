"""Ghost AI and collision detection with the player.

Ghosts target a random cell within a ring around the player; ring
size grows with ghost count. Each ghost picks a new target once it
arrives. Flees to its home corner while the player is empowered.
"""

import random
from collections import deque
from collections.abc import Callable
from typing import TYPE_CHECKING

import src.config.constants as C
from src.gameplay.entities import Ghost, Player, PlayerState
from src.gameplay.maze import Maze
from src.utils.utils import grid_to_world

if TYPE_CHECKING:
    from src.game_engine import GameEngine


class GhostController:
    """Spawn, route, and collide all ghosts against the player."""

    _RING_8: list[tuple[int, int]] = [
        (dx, dy) for dx in range(-1, 2) for dy in range(-1, 2) if dx or dy
    ]
    _RING_12: list[tuple[int, int]] = [
        (dx, dy)
        for dx in range(-2, 3)
        for dy in range(-2, 3)
        if 0 < abs(dx) + abs(dy) <= 2
    ]
    _RING_16: list[tuple[int, int]] = [
        (dx, dy)
        for dx in range(-2, 3)
        for dy in range(-2, 3)
        if max(abs(dx), abs(dy)) == 2
    ]

    def __init__(
        self,
        engine: "GameEngine",
        player: Player,
        maze: Maze,
        game_state: C.EGameState,
        add_score: Callable[[int], None],
        ghost_count: int = C.GHOST_COUNT,
    ) -> None:
        """Initialize ghosts, path caches, and score callback."""
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
        n = len(self.ghosts)
        self._ghost_paths: list[list[tuple[int, int]]] = [[] for _ in range(n)]
        self._ghost_targets: list[tuple[int, int] | None] = [None] * n
        self.ghosts_killed = 0
        self._add_score = add_score

        if self.engine and self.engine.hud:
            self.engine.hud.update_ghosts_killed(self.ghosts_killed)

    @property
    def game_state(self) -> C.EGameState:
        """Current game state shared across all ghosts."""
        return self._game_state

    @game_state.setter
    def game_state(self, value: C.EGameState) -> None:
        """Propagate new state to every ghost and trigger animations."""
        self._game_state = value
        for ghost in self.ghosts:
            ghost.game_state = value
            if value == C.EGameState.RUNNING:
                ghost.walk()
            elif value == C.EGameState.PAUSE:
                ghost.idle()
            elif value == C.EGameState.GAME_OVER:
                attack_idx = ghost.spec.anim_attack
                if isinstance(attack_idx, tuple):
                    attack_names = {ghost._anims[i] for i in attack_idx}
                else:
                    attack_names = {ghost._anims[attack_idx]}
                if ghost._current_anim not in attack_names:
                    ghost.idle()

    def _init_ghosts(self) -> list[Ghost]:
        """Spawn one ghost per corner, cycling if ghost_count > 4."""
        ghosts: list[Ghost] = []

        for i in range(self._ghost_count):
            grid_x, grid_y = self.start_grid_indices[
                i % len(self.start_grid_indices)
            ]
            world_x, world_z = grid_to_world(
                grid_x, grid_y, self.maze.width, self.maze.height
            )

            ghost_entity = Ghost(i, x=world_x, z=world_z, maze=self.maze)
            # Ghost.__init__ sets game_state=NOT_STARTED regardless of actual
            # state. On level 2+ the setter never fires; propagate explicitly.
            ghost_entity.game_state = self._game_state
            ghosts.append(ghost_entity)

        return ghosts

    def update_ghosts(self) -> None:
        """Update path, collision, and movement for every active ghost."""
        if self.game_state != C.EGameState.RUNNING:
            return

        for i, ghost in enumerate(self.ghosts):
            if ghost.is_stunned:
                self._ghost_targets[i] = None
                continue
            ghost.update_grid_position()
            next_x, next_y = self._update_ghost_path(ghost, i)
            self._handle_ghost_collision(ghost)
            if not ghost.is_attacking and not ghost.is_stunned:
                ghost.update_ai(next_x, next_y)

    def _update_ghost_path(self, ghost: Ghost, i: int) -> tuple[int, int]:
        """Assign a new target when reached; return the next grid cell."""
        ghost_grid = (ghost.pos_gridx, ghost.pos_gridy)

        if self.player.state == PlayerState.EMPOWERED:
            flee = self._calculate_flee_target(ghost)
            if self._ghost_targets[i] != flee:
                self._ghost_targets[i] = flee
                self._ghost_paths[i] = self._bfs_find_path(ghost_grid, flee)
                if self._ghost_paths[i]:
                    self._ghost_paths[i].pop(0)
        elif (
            self._ghost_targets[i] is None
            or ghost_grid == self._ghost_targets[i]
        ):
            target = self._pick_random_ring_target()
            self._ghost_targets[i] = target
            self._ghost_paths[i] = self._bfs_find_path(ghost_grid, target)
            if self._ghost_paths[i]:
                self._ghost_paths[i].pop(0)

        if self._ghost_paths[i] and ghost_grid == self._ghost_paths[i][0]:
            self._ghost_paths[i].pop(0)

        if self._ghost_paths[i]:
            return self._ghost_paths[i][0]
        return self._ghost_targets[i] or ghost_grid

    def _pick_random_ring_target(self) -> tuple[int, int]:
        """Return a random walkable cell from the ring around the player."""
        n = len(self.ghosts)
        if n < 5:
            offsets = self._RING_8
        elif n < 8:
            offsets = self._RING_12
        else:
            offsets = self._RING_16

        px, py = self.player.pos_gridx, self.player.pos_gridy
        candidates = [
            (px + dx, py + dy)
            for dx, dy in offsets
            if (
                0 <= px + dx < self.maze.width
                and 0 <= py + dy < self.maze.height
                and self.maze.grid[py + dy][px + dx] != 15
            )
        ]
        if not candidates:
            return (px, py)
        return random.choice(candidates)

    def _handle_ghost_collision(self, ghost: Ghost) -> None:
        """Apply eat or attack logic when ghost overlaps the player."""
        if not self.check_collision_with_player(ghost):
            return

        can_eat = (
            self.player.state == PlayerState.EMPOWERED
            or self.player.cheat_mode
        )
        if can_eat:
            if not ghost.is_stunned:
                self.engine.audio_manager.play_sound("punch.wav")
                self.player.attack()
                ghost.stun()
                self.ghosts_killed += 1
                self._add_score(self.engine.config.points_per_ghost)
                if self.engine and self.engine.hud:
                    self.engine.hud.update_ghosts_killed(self.ghosts_killed)
        elif (
            self.player.state != PlayerState.UNTOUCHABLE
            and self.player.state != PlayerState.STUNNED
        ):
            self.handle_attack(ghost, self.player)

    def _calculate_flee_target(self, ghost: Ghost) -> tuple[int, int]:
        """Return the ghost's home corner as its flee destination."""
        corner_idx = ghost.ghost_index % len(self.start_grid_indices)
        return self.start_grid_indices[corner_idx]

    def check_collision_with_player(self, ghost: Ghost) -> bool:
        """Return True if ghost is within pickup distance of the player."""
        distance = abs(self.player.x - ghost.x) + abs(self.player.z - ghost.z)
        return distance < C.PICKUP_DISTANCE

    def handle_attack(self, attacker: Ghost, target: Player) -> None:
        """Trigger attacker's attack animation and stun the target."""
        self.engine.audio_manager.play_sound("ghost_attack.wav")
        duration = attacker.attack()
        if not target.infinite_lives:
            target.health -= 1
            if self.engine and self.engine.hud:
                self.engine.hud.update_health(target.health)
        target.be_stunned(duration)

    def _bfs_find_path(
        self, start: tuple[int, int], target: tuple[int, int]
    ) -> list[tuple[int, int]]:
        """Return the shortest walkable path from start to target."""
        if start == target:
            return [start]

        parent: dict[tuple[int, int], tuple[int, int] | None] = {start: None}
        queue: deque[tuple[int, int]] = deque([start])
        dirs = [(0, -1, 1), (-1, 0, 8), (0, 1, 4), (1, 0, 2)]

        while queue:
            cx, cy = queue.popleft()

            if (cx, cy) == target:
                path: list[tuple[int, int]] = []
                node: tuple[int, int] | None = (cx, cy)
                while node is not None:
                    path.append(node)
                    node = parent[node]
                path.reverse()
                return path

            cell_value = self.maze.grid[cy][cx]
            for dx, dy, wall_flag in dirs:
                if cell_value & wall_flag:
                    continue
                nx, ny = cx + dx, cy + dy
                if 0 <= nx < self.maze.width and 0 <= ny < self.maze.height:
                    if (nx, ny) not in parent:
                        parent[(nx, ny)] = (cx, cy)
                        queue.append((nx, ny))

        return []
