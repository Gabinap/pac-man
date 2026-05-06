"""Game entity dataclasses.

Defines pure data structures representing game objects:
Player, Ghost, Pacgum, SuperPacgum, and Level.
No game logic or rendering — only structured state.
These classes are consumed by game_behavior and visualization.
"""

from ursina import Entity
import src.constants as C


class Player(Entity):
    def __init__(self) -> None:
        super().__init__(model=C.PLAYER_MODEL)

    def update(self) -> None:
        pass


class Ghost(Entity):
    def __init__(self, index: int = 0) -> None:
        super().__init__(model=C.GHOST_MODELS[index % len(C.GHOST_MODELS)])

    def update(self) -> None:
        pass


class Floor(Entity):
    def __init__(self, width: int, height: int, texture: str) -> None:
        super().__init__(
            model='plane',
            texture=texture,
            texture_scale=(width, height),
            scale=(width, 1, height),
            position=(0, 0, 0),
        )
