from typing import TYPE_CHECKING
import src.config.constants as C
from .pacgum import Pacgum

if TYPE_CHECKING:
    from src.gameplay.maze import Maze


class SuperPacgum(Pacgum):
    SCALE_MULTIPLIER: float = C.SUPER_PACGUM_SCALE_MULTIPLIER

    def __init__(
        self,
        spec: C.PacgumSpec,
        grid_x: int,
        grid_y: int,
        maze: "Maze",
        points: int,
    ) -> None:
        super().__init__(spec, grid_x, grid_y, maze, points)
        self.is_super = True
