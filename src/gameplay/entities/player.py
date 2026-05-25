"""Player entity: input handling, state machine, and animation triggers."""

import random
from enum import Enum, auto
from typing import Any, TYPE_CHECKING
from ursina import held_keys, invoke, mouse
import time
import src.config.constants as C
from src.config.controls import ControlsConfig
from src.config.game_config import GameConfig
from .animated_entity import AnimatedEntity, _pick_anim, _skip_if_destroyed

if TYPE_CHECKING:
    from src.gameplay.maze import Maze
    from src.game_engine import GameEngine


_FPS_DIRS: tuple[tuple[int, int], ...] = ((0, 1), (-1, 0), (0, -1), (1, 0))


def _rotation_to_grid_dir(angle: float) -> tuple[int, int]:
    """Snap a rotation_y angle to the nearest cardinal grid direction."""
    return _FPS_DIRS[int((angle % 360 + 45) / 90) % 4]


class PlayerState(Enum):
    """Possible states of the player character."""

    NORMAL = auto()
    UNTOUCHABLE = auto()
    EMPOWERED = auto()
    STUNNED = auto()


class Player(AnimatedEntity):
    """Player character with directional movement and a state machine."""

    _TAUNT_ANIM = "skeleton-skeleton|taunt"
    _TAUNT_INTERVAL = 5.0
    _TAUNT_CHANCE = 1 / 3
    _FPS_SENSITIVITY: float = 40.0

    def __init__(
        self,
        maze: "Maze",
        engine: "GameEngine",
        lives: int | None = None,
        controls: ControlsConfig | None = None,
    ) -> None:
        """Initialize lives, state, controls, and schedule the taunt timer."""
        super().__init__(spec=C.PLAYER_SPEC, maze=maze, speed=C.PLAYER_SPEED)
        self.engine = engine
        self.game_state = self.engine.game_state
        self.config = self.engine.config
        self._controls = controls if controls is not None else ControlsConfig()
        effective_lives = lives if lives is not None else self.config.lives
        self.infinite_lives: bool = effective_lives == 0
        self._health = effective_lives
        self.state = PlayerState.NORMAL
        self.cheat_mode: bool = False
        self.fps_mode: bool = False
        self._empower_seq: Any = None
        self.spawn_x = self.x
        self.spawn_z = self.z
        self.last_walk_sound_time = 0.0
        self.spawn()
        if self._TAUNT_ANIM in self.actor.get_anim_names():
            invoke(self._maybe_taunt, delay=self._TAUNT_INTERVAL)

    @property
    def health(self) -> int:
        """Return the current life count."""
        return self._health

    @health.setter
    def health(self, value: int) -> None:
        """Set the life count."""
        self._health = value

    def empower(self) -> None:
        """Enter EMPOWERED state: scale up and schedule the reversion."""
        if self._empower_seq:
            self._empower_seq.pause()
        self.state = PlayerState.EMPOWERED
        self.animate_scale(self.spec.scale * 2, duration=0.2)
        self._empower_seq = invoke(
            self._end_empower, delay=C.FRIGHTENED_DURATION - 0.3
        )

    @_skip_if_destroyed
    def _end_empower(self) -> None:
        """Shrink back and transition to NORMAL after EMPOWERED expires."""
        self._empower_seq = None
        self.animate_scale(self.spec.scale, duration=0.3)

        def _make_vulnerable() -> None:
            if self._empower_seq is None:
                self.state = PlayerState.NORMAL

        invoke(_make_vulnerable, delay=0.3)

    def be_stunned(self, duration: float) -> None:
        """Enter STUNNED state for the given duration after a ghost hit."""
        if self._oneshot_seq:
            self._oneshot_seq.pause()
            self._oneshot_seq = None
        for actor in self._actors:
            actor.stop()
        self._current_anim = None
        self.state = PlayerState.STUNNED
        self.animate_scale(self.spec.scale * 0.5, 0.1)
        invoke(self._end_stun, delay=duration)

    @_skip_if_destroyed
    def _end_stun(self) -> None:
        """End stun, teleport to spawn, and blink while UNTOUCHABLE."""
        self.animate_scale(self.spec.scale, 0.2)
        self.state = PlayerState.UNTOUCHABLE
        self.x = self.spawn_x
        self.z = self.spawn_z
        self.update_grid_position()

        self._blink_loop(lambda: self.state is PlayerState.UNTOUCHABLE)

        invoke(self._reset_player_state, delay=C.PLAYER_INVINCIBILITY_DURATION)

    @_skip_if_destroyed
    def _restore_scale(self, duration: float) -> None:
        """Animate the scale back to the correct size for the current state."""
        target = (
            self.spec.scale * 2
            if self.state == PlayerState.EMPOWERED
            else self.spec.scale
        )
        seq: Any = self.animate_scale(target, duration)
        seq.ignore_paused = True

    @_skip_if_destroyed
    def _reset_player_state(self) -> None:
        """Make the player visible and return to NORMAL state."""
        self.visible = True
        self.state = PlayerState.NORMAL

    def spawn(self) -> None:
        """Play the spawn animation, or fall back to idle if unavailable."""
        spawn_anim = "skeleton-skeleton|spawn"
        if spawn_anim in self.actor.get_anim_names():
            if self._oneshot_seq:
                self._oneshot_seq.pause()
            rate = 0.12
            self._play_on_all(spawn_anim, rate, loop=False)
            raw = self.actor.get_duration(spawn_anim)
            duration = raw if raw is not None else 1.0
            self._oneshot_seq = invoke(
                self._finish_oneshot, delay=duration / rate
            )
        else:
            self.idle()

    def _maybe_taunt(self) -> None:
        """Randomly trigger the taunt animation when truly idle."""
        idle_name = self._anims[_pick_anim(self.spec.anim_idle)]
        is_truly_idle = (
            self.game_state == C.EGameState.RUNNING
            and self._oneshot_seq is None
            and self._current_anim == idle_name
        )
        if is_truly_idle and random.random() < self._TAUNT_CHANCE:
            self._play_taunt()
        invoke(self._maybe_taunt, delay=self._TAUNT_INTERVAL)

    def _play_taunt(self) -> None:
        """Play the taunt one-shot animation."""
        if self._oneshot_seq:
            self._oneshot_seq.pause()
        self._play_on_all(self._TAUNT_ANIM, 1.0, loop=False)
        raw = self.actor.get_duration(self._TAUNT_ANIM)
        duration = raw if raw is not None else 1.0
        self._oneshot_seq = invoke(self._finish_oneshot, delay=duration)

    def update(self) -> None:
        """Process movement input and drive walk/idle animations each frame."""
        if self.game_state != C.EGameState.RUNNING:
            if not self._oneshot_seq:
                self.idle()
            return
        if self.state == PlayerState.STUNNED:
            return
        base = (
            C.PLAYER_SPEED * C.CHEAT_SPEED_MULTIPLIER
            if self.cheat_mode and held_keys["shift"]
            else C.PLAYER_SPEED
        )
        self.speed = (
            base * 1.5 if self.state == PlayerState.EMPOWERED else base
        )
        moving = False

        c = self._controls
        if self.fps_mode:
            self.rotation_y += mouse.velocity[0] * self._FPS_SENSITIVITY
            self.visible = False
            forward = _rotation_to_grid_dir(self.rotation_y)
            right = _rotation_to_grid_dir(self.rotation_y - 90)
            dir_x, dir_y = 0, 0
            if held_keys[c.move_up] or held_keys["up arrow"]:
                dir_x, dir_y = -forward[0], -forward[1]
            elif held_keys[c.move_down] or held_keys["down arrow"]:
                dir_x, dir_y = forward
            elif held_keys[c.move_right] or held_keys["right arrow"]:
                dir_x, dir_y = right
            elif held_keys[c.move_left] or held_keys["left arrow"]:
                dir_x, dir_y = -right[0], -right[1]
            if dir_x != 0 or dir_y != 0:
                self.move_in_direction(dir_x, dir_y)
                moving = True
        else:
            if self.state is not PlayerState.UNTOUCHABLE:
                self.visible = True
            if held_keys[c.move_up] or held_keys["up arrow"]:
                self.move_in_direction(0, -1)
                moving = True
            elif held_keys[c.move_down] or held_keys["down arrow"]:
                self.move_in_direction(0, 1)
                moving = True
            elif held_keys[c.move_left] or held_keys["left arrow"]:
                self.move_in_direction(-1, 0)
                moving = True
            elif held_keys[c.move_right] or held_keys["right arrow"]:
                self.move_in_direction(1, 0)
                moving = True

        if moving:
            if time.time() - self.last_walk_sound_time > 0.4:
                if self.engine and self.engine.audio_manager:
                    self.engine.audio_manager.play_sound("walk.wav")
                self.last_walk_sound_time = time.time()
            if self._oneshot_seq and not self.is_attacking:
                self._oneshot_seq.pause()
                self._oneshot_seq = None
        else:
            if self.engine.audio_manager:
                self.engine.audio_manager.stop_sound()
        if not self.is_attacking:
            if moving:
                self.walk()
            else:
                self.grid_direction = (0, 0)
                if not self._oneshot_seq:
                    self.idle()

        self.update_grid_position()
