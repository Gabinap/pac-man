from ursina import color, Entity, Mesh

from mazegenerator.mazegenerator import MazeGenerator
from src.entities import Floor
from src.game_config import LevelConfig


NORTH, EAST, SOUTH, WEST = 1, 2, 4, 8

_V3 = tuple[float, float, float]
_V2 = tuple[float, float]


def _face(
    verts: list[_V3],
    uvs: list[_V2] | None,
    tris: list[int],
    corners: list[_V3],
    uv_w: float = 1.0,
    uv_h: float = 1.0,
) -> None:
    b = len(verts)
    verts.extend(corners)
    if uvs is not None:
        uvs.extend([(0.0, 0.0), (uv_w, 0.0), (uv_w, uv_h), (0.0, uv_h)])
    tris.extend([b, b + 1, b + 2, b, b + 2, b + 3])


def _add_wall(
    wv: list[_V3], wu: list[_V2], wt: list[int],
    wx: float, wz: float, s_x: float, s_z: float,
) -> None:
    hx, hz = s_x / 2, s_z / 2
    y0, y1 = 0.0, 1.0
    # top
    _face(wv, wu, wt, [
        (wx - hx, y1, wz - hz), (wx + hx, y1, wz - hz),
        (wx + hx, y1, wz + hz), (wx - hx, y1, wz + hz),
    ], s_x, s_z)
    # north (z- face)
    _face(wv, wu, wt, [
        (wx - hx, y0, wz - hz), (wx + hx, y0, wz - hz),
        (wx + hx, y1, wz - hz), (wx - hx, y1, wz - hz),
    ], s_x, 1.0)
    # south (z+ face)
    _face(wv, wu, wt, [
        (wx + hx, y0, wz + hz), (wx - hx, y0, wz + hz),
        (wx - hx, y1, wz + hz), (wx + hx, y1, wz + hz),
    ], s_x, 1.0)
    # west (x- face)
    _face(wv, wu, wt, [
        (wx - hx, y0, wz + hz), (wx - hx, y0, wz - hz),
        (wx - hx, y1, wz - hz), (wx - hx, y1, wz + hz),
    ], s_z, 1.0)
    # east (x+ face)
    _face(wv, wu, wt, [
        (wx + hx, y0, wz - hz), (wx + hx, y0, wz + hz),
        (wx + hx, y1, wz + hz), (wx + hx, y1, wz - hz),
    ], s_z, 1.0)


def _add_pattern(pv: list[_V3], pt: list[int], px: float, pz: float) -> None:
    hx, hz = 0.5, 0.5
    y0, y1 = 0.0, 1.0
    # top
    _face(pv, None, pt, [
        (px - hx, y1, pz - hz), (px + hx, y1, pz - hz),
        (px + hx, y1, pz + hz), (px - hx, y1, pz + hz),
    ])
    # north
    _face(pv, None, pt, [
        (px - hx, y0, pz - hz), (px + hx, y0, pz - hz),
        (px + hx, y1, pz - hz), (px - hx, y1, pz - hz),
    ])
    # south
    _face(pv, None, pt, [
        (px + hx, y0, pz + hz), (px - hx, y0, pz + hz),
        (px - hx, y1, pz + hz), (px + hx, y1, pz + hz),
    ])
    # west
    _face(pv, None, pt, [
        (px - hx, y0, pz + hz), (px - hx, y0, pz - hz),
        (px - hx, y1, pz - hz), (px - hx, y1, pz + hz),
    ])
    # east
    _face(pv, None, pt, [
        (px + hx, y0, pz - hz), (px + hx, y0, pz + hz),
        (px + hx, y1, pz + hz), (px + hx, y1, pz - hz),
    ])


class Maze:
    def __init__(self, level: LevelConfig, seed: int) -> None:
        gen = MazeGenerator(
            size=(level.width, level.height), perfect=False, seed=seed
        )
        self.grid = gen.maze
        self._build()

    def _build(self) -> None:
        grid = self.grid
        h, w = len(grid), len(grid[0])
        Floor(width=w, height=h)

        wv: list[_V3] = []
        wu: list[_V2] = []
        wt: list[int] = []
        pv: list[_V3] = []
        pt: list[int] = []

        for z, row in enumerate(grid):
            for x, cell in enumerate(row):
                if cell == 15:
                    cx, cz = float(x - w // 2), float(z - h // 2)
                    _add_pattern(pv, pt, cx, cz)

        placed: set[tuple[float, float, str]] = set()

        for z, row in enumerate(grid):
            for x, cell in enumerate(row):
                if cell == 15:
                    continue
                cx, cz = float(x - w // 2), float(z - h // 2)

                if cell & NORTH and (z == 0 or grid[z - 1][x] != 15):
                    key = (cx, cz - 0.5, 'h')
                    if key not in placed:
                        placed.add(key)
                        _add_wall(wv, wu, wt, cx, cz - 0.5, 1.0, 0.1)

                if cell & EAST and (x == w - 1 or grid[z][x + 1] != 15):
                    key = (cx + 0.5, cz, 'v')
                    if key not in placed:
                        placed.add(key)
                        _add_wall(wv, wu, wt, cx + 0.5, cz, 0.1, 1.0)

                if cell & SOUTH and (z == h - 1 or grid[z + 1][x] != 15):
                    key = (cx, cz + 0.5, 'h')
                    if key not in placed:
                        placed.add(key)
                        _add_wall(wv, wu, wt, cx, cz + 0.5, 1.0, 0.1)

                if cell & WEST and (x == 0 or grid[z][x - 1] != 15):
                    key = (cx - 0.5, cz, 'v')
                    if key not in placed:
                        placed.add(key)
                        _add_wall(wv, wu, wt, cx - 0.5, cz, 0.1, 1.0)

        if wv:
            Entity(
                model=Mesh(vertices=wv, uvs=wu, triangles=wt, mode='triangle'),
                texture='wall-brick.png',
                double_sided=True,
            )
        if pv:
            Entity(
                model=Mesh(vertices=pv, triangles=pt, mode='triangle'),
                color=color.blue,
                double_sided=True,
            )
