"""Flat textured plane that fills the maze footprint."""

from ursina import Entity


class Floor(Entity):
    """Textured ground plane scaled to the maze dimensions."""

    def __init__(self, width: int, height: int, texture: str) -> None:
        """Create a plane entity of the given size with the given texture."""
        super().__init__(
            model="plane",
            texture=texture,
            texture_scale=(width, height),
            scale=(width, 1, height),
            position=(0, 0, 0),
        )
