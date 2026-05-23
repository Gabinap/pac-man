"""Keyboard input handling: cheat codes, cheat actions, and menu clicks."""

from typing import TYPE_CHECKING
from ursina import color, Entity, camera, mouse, Button
import src.config.constants as C

if TYPE_CHECKING:
    from src.game_engine import GameEngine


class InputManager:
    """Cheat-code buffer, cheat key actions, and menu screen-shake on click."""

    def __init__(self, engine: 'GameEngine') -> None:
        """Set up the cheat buffer and on-screen cheat indicator bar."""
        self.engine = engine
        self._key_buffer: str = ""
        self.cheat_mode: bool = False

        self._cheat_bar: Entity = Entity(
            parent=camera.ui,
            model="quad",
            color=color.red,
            scale=(2, 0.008),
            position=(0, -0.49, -0.5),
            enabled=False,
        )

    def handle_input(self, key: str) -> None:
        """Route a key event to the cheat buffer and action handlers."""
        self._update_cheat_buffer(key)
        self._handle_cheat_keys(key)
        self._handle_gameplay_mouse_click(key)

    def _update_cheat_buffer(self, key: str) -> None:
        """Append alphabetic keys to the rolling buffer and detect codes."""
        if len(key) != 1 or not key.isalpha():
            return

        self._key_buffer = (self._key_buffer + key)[-6:]

        if self._key_buffer.endswith("cheat"):
            self.set_cheat_mode(True)
        elif self._key_buffer.endswith("normal"):
            self.set_cheat_mode(False)

    def set_cheat_mode(self, enabled: bool) -> None:
        """Enable or disable cheat mode and update the indicator bar."""
        if self.cheat_mode == enabled:
            return

        self.cheat_mode = enabled
        self._cheat_bar.enabled = enabled

        if self.engine.session.player:
            self.engine.session.player.cheat_mode = enabled
        if self.engine.hud:
            self.engine.hud.update_health(self.engine.session.get_health())

    def _handle_cheat_keys(self, key: str) -> None:
        """Execute cheat-only key actions (eat all pacgums, empower)."""
        if not self.cheat_mode:
            return

        if (
            self.engine.game_state != C.EGameState.RUNNING
            or self.engine.router.current is not None
        ):
            return

        if key == "p" and self.engine.session.pacgum_controller:
            if hasattr(self.engine.session.pacgum_controller, "eat_all"):
                self.engine.session.pacgum_controller.eat_all()

        elif key == "o" and self.engine.session.player:
            if hasattr(self.engine.session.player, "empower"):
                self.engine.session.player.empower()

    def _handle_gameplay_mouse_click(self, key: str) -> None:
        """Screen-shake on left click in the main menu (not on a button)."""
        if key != "left mouse down":
            return
        if self.engine.router.current != C.EGameView.MENU:
            return
        if self.engine.camera_effects.fps_mode:
            return
        if isinstance(mouse.hovered_entity, Button):
            return
        self.engine._shake_screen()
