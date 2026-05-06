from mazegenerator.mazegenerator import MazeGenerator
from src.entities import Wall, Floor
from src.game_config import LevelConfig


class Maze:
    def __init__(self, level: LevelConfig, seed: int) -> None:
        gen = MazeGenerator(size=(level.width, level.height), perfect=False, seed=seed)
        self.grid = gen.maze
        self._build()

    NORTH, EAST, SOUTH, WEST = 1, 2, 4, 8

    def _build(self) -> None:
        grid = self.grid  # list[list[int]]
        h, w = len(grid), len(grid[0])
        Floor(width=w, height=h)
        placed: set[tuple[float, float, str]] = set()

        for z, row in enumerate(grid):
            for x, cell in enumerate(row):
                cx, cz = x - w // 2, z - h // 2

                if cell & NORTH:
                    key = (cx + 0.0, cz - 0.5, 'h')
                    if key not in placed:
                        placed.add(key)
                        Wall((cx, cz - 0.5), (True, False))  # mur horizontal

                if cell & EAST:
                    key = (cx + 0.5, cz + 0.0, 'v')
                    if key not in placed:
                        placed.add(key)
                        Wall((cx + 0.5, cz), (False, True))  # mur vertical

                if cell & SOUTH:
                    key = (cx + 0.0, cz + 0.5, 'h')
                    if key not in placed:
                        placed.add(key)
                        Wall((cx, cz + 0.5), (True, False))

                if cell & WEST:
                    key = (cx - 0.5, cz + 0.0, 'v')
                    if key not in placed:
                        placed.add(key)
                        Wall((cx - 0.5, cz), (False, True))

