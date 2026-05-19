from ursina import Entity


class Floor(Entity):
    def __init__(self, width: int, height: int, texture: str) -> None:
        super().__init__(
            model="plane",
            texture=texture,
            texture_scale=(width, height),
            scale=(width, 1, height),
            position=(0, 0, 0),
        )
