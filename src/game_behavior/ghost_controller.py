from enum import Enum, auto
import src.constants as C
from ursina import Entity, color
from src.utils import grid_to_world


class GhostState(Enum):
    HUNT = auto()
    FRIGTHENED = auto()


class GhostController:
    def __init__(self, maze_width: int = 11, maze_height: int = 11) -> None:
        self.ghosts: list[Entity] = self._init_ghosts(maze_width, maze_height)

    def _init_ghosts(self, maze_width: int, maze_height: int) -> list[Entity]:
        ghosts = []
        ghost_colors = [color.red, color.pink, color.cyan, color.orange]

        start_grid_indices = [
            (0, 0),
            (maze_width - 1, 0),
            (0, maze_height - 1),
            (maze_width - 1, maze_height - 1),
        ]

        for i in range(C.GHOST_COUNT):
            grid_x, grid_y = start_grid_indices[i % len(start_grid_indices)]
            world_x, world_z = grid_to_world(
                grid_x, grid_y, maze_width, maze_height
            )
            ghost_entity = Entity(
                model="sphere",
                color=ghost_colors[i % len(ghost_colors)],
                scale=0.8,
                x=world_x,
                y=0.5,
                z=world_z,
            )
            ghosts.append(ghost_entity)

        return ghosts
