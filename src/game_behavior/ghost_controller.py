"""Ghost AI and collision detection with the player.

Implements the four classic Pac-Man targeting strategies (Blinky/Pinky/
Inky/Clyde) and propagates game state transitions to every ghost.
"""

from enum import Enum, auto

from ursina import invoke

import src.constants as C
from src.entities import Ghost, Player, PlayerState
from src.maze import Maze
from src.utils import grid_to_world, world_to_grid


class GhostState(Enum):
    HUNT = auto()
    FRIGHTENED = auto()


class GhostController:
    """Spawn, route, and collide all ghosts against the player."""

    def __init__(
        self, player: Player, maze: Maze, game_state: C.EGameState
    ) -> None:
        self._game_state = game_state
        self.player = player
        self.maze = maze
        self.ghosts: list[Ghost] = self._init_ghosts()

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
        start_grid_indices = [
            (0, 0),
            (self.maze.width - 1, 0),
            (0, self.maze.height - 1),
            (self.maze.width - 1, self.maze.height - 1),
        ]

        for i in range(C.GHOST_COUNT):
            grid_x, grid_y = start_grid_indices[i % len(start_grid_indices)]
            world_x, world_z = grid_to_world(
                grid_x, grid_y, self.maze.width, self.maze.height
            )

            ghost_entity = Ghost(i, x=world_x, z=world_z, maze=self.maze)
            ghosts.append(ghost_entity)

        return ghosts

    def update_ghosts(self) -> None:
        if self.game_state != C.EGameState.RUNNING:
            return
        for ghost in self.ghosts:
            if ghost.ghost_index == 0:
                target_x = self.player.pos_gridx
                target_z = self.player.pos_gridy
            elif ghost.ghost_index == 1:
                target_x, target_z = self._calculate_pinky_target()
            elif ghost.ghost_index == 2:
                target_x, target_z = self._calculate_inky_target(
                    self.ghosts[0]
                )
            elif ghost.ghost_index == 3:
                target_x, target_z = self._calculate_clyde_target(ghost)
            else:
                raise ValueError(
                    f"Unexpected ghost index: {ghost.ghost_index}"
                )

            if self.check_collision_with_player(ghost):
                if self.player.state != PlayerState.UNTOUCHABLE:
                    self.handle_collision(ghost)
            ghost.update_ai(target_x, target_z)

    def check_collision_with_player(self, ghost: Ghost) -> bool:
        px, pz = self.player.x, self.player.z
        gx, gz = ghost.x, ghost.z

        distance_player_ghost = abs(px - gx) + abs(pz - gz)

        return distance_player_ghost < 0.5

    def handle_collision(self, ghost: Ghost) -> None:
        ghost.attack()
        self.player.health -= 1
        self.player.state = PlayerState.UNTOUCHABLE
        invoke(
            self.player._reset_player_state,
            delay=C.PLAYER_INVINCIBILITY_DURATION,
        )

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

        if square_distance > 64:
            raw_x, raw_y = p_grid_x, p_grid_y
        else:
            raw_x, raw_y = 0, self.maze.height - 1
        target_x = max(0, min(raw_x, self.maze.width - 1))
        target_y = max(0, min(raw_y, self.maze.height - 1))

        return (target_x, target_y)
