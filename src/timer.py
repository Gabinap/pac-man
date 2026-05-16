from typing import Callable, Optional
from ursina import Entity, Text, destroy, invoke


class Timer(Entity):
    def __init__(
        self, duration: int, on_timeout: Optional[Callable[[], None]] = None
    ) -> None:
        super().__init__()
        self.initial_duration = duration
        self.duration = duration
        self.on_timeout = on_timeout
        self.is_running = False

        self.text_entity = Text(
            text="",
            origin=(0, 0),
            position=(0.2, 0.45),
            scale=2,
        )
        self._update_text()

    def launch_timer(self) -> None:
        self.duration = self.initial_duration
        if not self.is_running:
            self.is_running = True
            self._update_text()
            self._tick()

    def _tick(self) -> None:
        if not self.is_running:
            return

        if self.duration > 0:
            self.duration -= 1
            self._update_text()
            invoke(self._tick, delay=1.0)
        else:
            self.is_running = False
            if self.on_timeout:
                self.on_timeout()

    def _update_text(self) -> None:
        self.text_entity.text = f"Time: {self.duration}"

    def stop(self) -> None:
        self.is_running = False

    def destroy_timer(self) -> None:
        self.stop()
        destroy(self.text_entity)
        destroy(self)
