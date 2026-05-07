"""Game entity dataclasses.

Defines pure data structures representing game objects:
Player, Ghost, Pacgum, SuperPacgum, and Level.
No game logic or rendering — only structured state.
These classes are consumed by game_behavior and visualization.
"""

from ursina import Entity, application
from direct.actor.Actor import Actor
import src.constants as C


class Player(Entity):
    def __init__(
        self,
        glb: str = C.PLAYER_MODEL,
        position: tuple[float, float, float] = (0, 0.4, 0),
        scale: float = 0.25,
    ) -> None:
        super().__init__(position=position, scale=scale)
        model_path = str(application.asset_folder / 'assets' / glb)
        self._actor = Actor(model_path)
        self._actor.reparent_to(self)
        self._actor.loop("Idle")

    def play(self, name: str, loop: bool = True) -> None:
        if loop:
            self._actor.loop(name)
        else:
            self._actor.play(name)

    def stop(self) -> None:
        self._actor.stop()

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
