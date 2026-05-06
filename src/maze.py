from ursina import Entity

from mazegenerator.mazegenerator import MazeGenerator
from src.entities import Floor, Pattern, Wall
from src.game_config import LevelConfig


NORTH, EAST, SOUTH, WEST = 1, 2, 4, 8


class Maze:
    def __init__(self, level: LevelConfig, seed: int) -> None:
        gen = MazeGenerator(
            size=(level.width, level.height), perfect=False, seed=seed
            )
        self.grid = gen.maze
        self._build()

    def _build(self) -> None:
        grid = self.grid  # list[list[int]]
        h, w = len(grid), len(grid[0])
        static_root = Entity()
        Floor(width=w, height=h)
        for z, row in enumerate(grid):
            for x, cell in enumerate(row):
                if cell == 15:
                    cx, cz = x - w // 2, z - h // 2
                    Pattern((cx, cz), parent=static_root)

        placed: set[tuple[float, float, str]] = set()

        for z, row in enumerate(grid):
            for x, cell in enumerate(row):
                cx, cz = x - w // 2, z - h // 2
                if cell == 15:
                    continue

                if cell & NORTH and (z == 0 or grid[z-1][x] != 15):
                    key = (cx + 0.0, cz - 0.5, 'h')
                    if key not in placed:
                        placed.add(key)
                        Wall((cx, cz-0.5), (True, False), parent=static_root)

                if cell & EAST and (x == w-1 or grid[z][x+1] != 15):
                    key = (cx + 0.5, cz + 0.0, 'v')
                    if key not in placed:
                        placed.add(key)
                        Wall((cx+0.5, cz), (False, True), parent=static_root)

                if cell & SOUTH and (z == h-1 or grid[z+1][x] != 15):
                    key = (cx + 0.0, cz + 0.5, 'h')
                    if key not in placed:
                        placed.add(key)
                        Wall((cx, cz+0.5), (True, False), parent=static_root)

                if cell & WEST and (x == 0 or grid[z][x-1] != 15):
                    key = (cx - 0.5, cz + 0.0, 'v')
                    if key not in placed:
                        placed.add(key)
                        Wall((cx-0.5, cz), (False, True), parent=static_root)
        static_root.flattenStrong()
