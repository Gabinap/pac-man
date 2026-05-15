"""Base class for all game views."""

from ursina import Entity, camera


class BaseView(Entity):
    def __init__(self) -> None:
        super().__init__(parent=camera.ui, enabled=False, ignore_paused=True)

    def on_enter(self) -> None:
        pass

    def on_exit(self) -> None:
        self.destroy()
