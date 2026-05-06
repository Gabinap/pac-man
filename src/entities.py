"""Game entity dataclasses.

Defines pure data structures representing game objects:
Player, Ghost, Pacgum, SuperPacgum, and Level.
No game logic or rendering — only structured state.
These classes are consumed by game_behavior and visualization.
"""

from ursina import Entity


class Wall(Entity):
    def __init__(self, x: int, z: int) -> None:
        super().__init__(
            model='cube',
            texture='wall-brick.png',
            position=(x, 0.5, z),
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
