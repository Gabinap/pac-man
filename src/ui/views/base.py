"""Base class for all game views."""

from ursina import Entity, camera


class BaseView(Entity):
    """Abstract base for all game views; parented to camera.ui."""

    def __init__(self) -> None:
        """Create the view entity, disabled and paused-safe."""
        super().__init__(parent=camera.ui, enabled=False, ignore_paused=True)

    def on_enter(self) -> None:
        """Called when the router activates this view."""

    def on_exit(self) -> None:
        """Called when the router deactivates this view."""
