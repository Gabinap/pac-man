from enum import Enum, auto
import src.constants as C
from ursina import Entity, color, invoke
from src.utils import grid_to_world, world_to_grid
from src.entities import Ghost, Player, PlayerState
from src.maze import Maze


class GhostState(Enum):
    HUNT = auto()
    FRIGTHENED = auto()


class GhostController:
    def __init__(self, t_player: Player, maze: Maze) -> None:
        self.t_player = t_player
        self.maze = maze
        self.ghosts: list[Ghost] = self._init_ghosts()

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

            ghost_entity = Ghost(
                i, position=(world_x, 0.5, world_z), maze=self.maze
            )
            ghosts.append(ghost_entity)

        return ghosts

    def update_ghosts(self) -> None:
        collided: bool = False
        for ghost in self.ghosts:
            target_x, target_z = 0, 0

            if ghost.ghost_index == 0:
                target_x = self.t_player.pos_gridx
                target_z = self.t_player.pos_gridy
                collided = self.check_collision_with_player(ghost)
            elif ghost.ghost_index == 1:
                target_x, target_z = self._calculate_pinky_target()
                collided = self.check_collision_with_player(ghost)
            elif ghost.ghost_index == 2:
                target_x, target_z = self._calculate_inky_target(
                    self.ghosts[0]
                )
                collided = self.check_collision_with_player(ghost)
            elif ghost.ghost_index == 3:
                target_x, target_z = self._calculate_clyde_target(ghost)
                collided = self.check_collision_with_player(ghost)

            if collided and self.t_player.state != PlayerState.UNTOUCHABLE:
                self.handle_collision()
            ghost.update_ai(target_x, target_z)

    def check_collision_with_player(self, ghost: Ghost) -> bool:
        px, pz = self.t_player.x, self.t_player.z
        gx, gz = ghost.x, ghost.z

        distance_player_ghost = abs(px - gx) + abs(pz - gz)

        if distance_player_ghost < 0.5:
            return True

        return False

    def handle_collision(self) -> None:
        self.t_player.health -= 1
        print(
            f"Collided and lost a live... Remaining lives : {self.t_player.health}"
        )

        if self.t_player.health <= 0:
            print("GAME OVER")
        else:
            self.t_player.state = PlayerState.UNTOUCHABLE
            invoke(
                self.t_player._reset_player_state,
                delay=C.PLAYER_INVINCIBILITY_DURATION,
            )

    def _calculate_pinky_target(self) -> tuple[int, int]:
        p_grid_x, p_grid_y = world_to_grid(
            self.t_player.x, self.t_player.z, self.maze.width, self.maze.height
        )
        raw_x = p_grid_x + (4 * self.t_player.grid_direction[0])
        raw_y = p_grid_y + (4 * self.t_player.grid_direction[1])
        target_x = max(0, min(raw_x, self.maze.width - 1))
        target_y = max(0, min(raw_y, self.maze.height - 1))
        return (target_x, target_y)

    def _calculate_inky_target(self, blinky: Ghost) -> tuple[int, int]:
        p_grid_x, p_grid_y = world_to_grid(
            self.t_player.x, self.t_player.z, self.maze.width, self.maze.height
        )
        b_grid_x, b_grid_y = world_to_grid(
            blinky.x, blinky.z, self.maze.width, self.maze.height
        )

        pivot_x = p_grid_x + (2 * self.t_player.grid_direction[0])
        pivot_y = p_grid_y + (2 * self.t_player.grid_direction[1])

        vecteur_x = pivot_x - b_grid_x
        vecteur_y = pivot_y - b_grid_y

        raw_x = b_grid_x + (2 * vecteur_x)
        raw_y = b_grid_y + (2 * vecteur_y)

        target_x = max(0, min(raw_x, self.maze.width - 1))
        target_y = max(0, min(raw_y, self.maze.height - 1))

        return (target_x, target_y)

    def _calculate_clyde_target(self, clyde: Ghost) -> tuple[int, int]:
        p_grid_x, p_grid_y = world_to_grid(
            self.t_player.x, self.t_player.z, self.maze.width, self.maze.height
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
