"""Game entity dataclasses.

Defines pure data structures representing game objects:
Player, Ghost, Pacgum, SuperPacgum, and Level.
No game logic or rendering — only structured state.
These classes are consumed by game_behavior and visualization.
"""

from ursina import color, Entity


class Wall(Entity):
    def __init__(self, coor: tuple[float, float], scale: tuple[bool, bool],
                 **kwargs) -> None:
        x, z = coor
        s_x = 1.0 if scale[0] else 0.1
        s_z = 1.0 if scale[1] else 0.1
        super().__init__(position=(x, 0.5, z), **kwargs)
        hx, hz = s_x / 2, s_z / 2
        Entity(parent=self, model='plane', texture='wall-brick.png',
               position=(0, 0.5, 0), scale=(s_x, 1, s_z),
               texture_scale=(s_x, s_z))
        Entity(parent=self, model='plane', texture='wall-brick.png',
               position=(0, 0, -hz), rotation=(90, 180, 0),
               scale=(s_x, 1, 1), texture_scale=(s_x, 1))
        Entity(parent=self, model='plane', texture='wall-brick.png',
               position=(0, 0, hz), rotation=(90, 0, 0),
               scale=(s_x, 1, 1), texture_scale=(s_x, 1))
        Entity(parent=self, model='plane', texture='wall-brick.png',
               position=(-hx, 0, 0), rotation=(90, -90, 0),
               scale=(s_z, 1, 1), texture_scale=(s_z, 1))
        Entity(parent=self, model='plane', texture='wall-brick.png',
               position=(hx, 0, 0), rotation=(90, 90, 0),
               scale=(s_z, 1, 1), texture_scale=(s_z, 1))


class Ghost(Entity):
    def __init__(self) -> None:
        super().__init__(model='ghost.png')

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


class Pattern(Entity):
    def __init__(self, coor: tuple[int, int], **kwargs) -> None:
        x, z = coor
        super().__init__(
            model='cube',
            color=color.blue,
            position=(x, 0.5, z),
            scale=(1, 1, 1),
            **kwargs
        )
