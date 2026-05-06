"""Game entity dataclasses.

Defines pure data structures representing game objects:
Player, Ghost, Pacgum, SuperPacgum, and Level.
No game logic or rendering — only structured state.
These classes are consumed by game_behavior and visualization.
"""

from ursina import Entity


class Wall(Entity):
    def __init__(self, coor: tuple[int, int], scale: tuple[bool, bool]) -> None:
        x, z = coor
        s_x, s_z = 1 if scale[0] else 0.1, 1 if scale[1] else 0.1
        super().__init__(
            model='cube',
            texture='wall-brick.png',
            position=(x, 0.5, z),
            scale=(s_x, 1, s_z),
        )


class Ghost(Entity):
    def __init__(self) -> None:
        super().__init__(model='ghost.obj')

    def update(self) -> None:
        pass


class Floor(Entity):
    def __init__(self, width: int, height: int) -> None:
        super().__init__(
            model='plane',
            texture='floor.png',
            texture_scale=(width, height),
            scale=(width, 1, height),
            position=(0, 0, 0),
        )
