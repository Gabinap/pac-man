"""Grid <-> world coordinate conversions for the maze."""


def grid_to_world(
    grid_x: int, grid_y: int, maze_width: int, maze_height: int
) -> tuple[float, float]:
    """Convert grid cell (x, y) to centered world (x, z) coordinates."""
    world_x = float(grid_x - (maze_width // 2))
    world_z = float((maze_height // 2) - grid_y)
    return world_x, world_z


def world_to_grid(
    world_x: float, world_z: float, maze_width: int, maze_height: int
) -> tuple[int, int]:
    """Convert world (x, z) to the nearest grid cell (x, y)."""
    raw_x = world_x + (maze_width // 2)
    raw_y = (maze_height // 2) - world_z
    grid_x = int(round(raw_x))
    grid_y = int(round(raw_y))
    return grid_x, grid_y
