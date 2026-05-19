import random
from collections.abc import Callable
from functools import wraps
from typing import Any, TYPE_CHECKING
from direct.actor.Actor import Actor
from panda3d.core import MaterialAttrib
from ursina import Entity, application, invoke
from ursina import time as _ursina_time

import src.config.constants as C
from src.utils.utils import grid_to_world, world_to_grid

if TYPE_CHECKING:
    from src.gameplay.maze import Maze

ursina_time: Any = _ursina_time


def _skip_if_destroyed(method: Callable[..., Any]) -> Callable[..., Any]:
    @wraps(method)
    def wrapped(self: Entity, *args: Any, **kwargs: Any) -> Any:
        if self.is_empty():
            return None
        return method(self, *args, **kwargs)

    return wrapped


def _pick_anim(spec: int | tuple[int, ...]) -> int:
    return random.choice(spec) if isinstance(spec, tuple) else spec


_METALLIC_FIXED: set[str] = set()


class AnimatedEntity(Entity):
    """Animated GLB entity with grid-aligned movement and one-shot anims."""

    x: float
    y: float
    z: float
    rotation_y: float

    def __init__(
        self, spec: C.ModelSpec, maze: "Maze", speed: float = 0.0
    ) -> None:
        super().__init__()
        self.spec = spec
        _loader: Any = application.base.loader
        raw = _loader.loadModel(f"assets/{spec.path}")
        char_paths = raw.find_all_matches("**/+Character")
        n_chars = char_paths.get_num_paths()
        actors = [Actor(char_paths.get_path(i)) for i in range(n_chars)]
        if not actors:
            actors = [Actor(f"assets/{spec.path}")]
        for a in actors:
            a.reparent_to(self)
        self._actors: list[Actor] = actors
        self.actor = actors[0]
        self._fix_metallic()
        self.scale = spec.scale
        self.rotation_x = spec.rotation_x
        self.y = spec.spawn_y
        self._anims = sorted(self.actor.get_anim_names())
        self._current_anim: str | None = None
        self._oneshot_seq: Any = None

        self.game_state: C.EGameState = C.EGameState.NOT_STARTED
        self.maze = maze
        self.speed = speed
        self.is_attacking: bool = False
        self.is_stunned: bool = False
        self._grid_direction: tuple[int, int] = (0, 0)
        self._facing: tuple[int, int] = (0, 0)
        self.pos_gridx: int
        self.pos_gridy: int
        self.update_grid_position()
        self.idle()

    _DIR_TO_ROT_Y: dict[tuple[int, int], float] = {
        (1, 0): 270,
        (-1, 0): 90,
        (0, 1): 0,
        (0, -1): 180,
    }

    @property
    def grid_direction(self) -> tuple[int, int]:
        return self._grid_direction

    @grid_direction.setter
    def grid_direction(self, value: tuple[int, int]) -> None:
        self._grid_direction = value

    def _rotate_toward(self, dir_x: int, dir_y: int) -> None:
        if (dir_x, dir_y) == self._facing:
            return
        self._facing = (dir_x, dir_y)
        raw = self._DIR_TO_ROT_Y.get((dir_x, dir_y))
        if raw is not None:
            delta = (raw - self.rotation_y + 180) % 360 - 180
            duration = C.ROTATION_DURATION_PER_90 * abs(delta) / 90
            self.animate_rotation_y(self.rotation_y + delta, duration)

    def update_grid_position(self) -> None:
        raw_x, raw_y = world_to_grid(
            self.x, self.z, self.maze.width, self.maze.height
        )

        self.pos_gridx = max(0, min(raw_x, self.maze.width - 1))
        self.pos_gridy = max(0, min(raw_y, self.maze.height - 1))

    def move_in_direction(self, dir_x: int, dir_y: int) -> None:
        if dir_x == 0 and dir_y == 0:
            return

        self._rotate_toward(dir_x, dir_y)
        self.grid_direction = (dir_x, dir_y)
        center_x, center_z = grid_to_world(
            self.pos_gridx, self.pos_gridy, self.maze.width, self.maze.height
        )
        cell_value = self.maze.grid[self.pos_gridy][self.pos_gridx]
        align = C.GRID_ALIGN_SPEED * ursina_time.dt

        if dir_x != 0:
            self.z += (center_z - self.z) * align
            self.x += dir_x * self.speed * ursina_time.dt
            if dir_x == 1 and (cell_value & 2):
                self.x = min(self.x, center_x)
            elif dir_x == -1 and (cell_value & 8):
                self.x = max(self.x, center_x)

        elif dir_y != 0:
            self.x += (center_x - self.x) * align
            self.z -= dir_y * self.speed * ursina_time.dt
            if dir_y == -1 and (cell_value & 1):
                self.z = min(self.z, center_z)
            elif dir_y == 1 and (cell_value & 4):
                self.z = max(self.z, center_z)

    def _fix_metallic(self) -> None:
        if self.spec.path in _METALLIC_FIXED:
            return
        for actor in self._actors:
            for np in actor.find_all_matches("**/+GeomNode"):
                for i in range(np.node().get_num_geoms()):
                    ma = np.node().get_geom_state(i).get_attrib(MaterialAttrib)
                    if ma and ma.get_material():
                        ma.get_material().set_metallic(0.0)
        _METALLIC_FIXED.add(self.spec.path)

    def _play_on_all(self, anim: str, rate: float, loop: bool = True) -> None:
        if self._current_anim == anim:
            for actor in self._actors:
                if anim in actor.get_anim_names():
                    actor.set_play_rate(rate, anim)
            return
        self._current_anim = anim
        for actor in self._actors:
            if anim in actor.get_anim_names():
                actor.set_play_rate(rate, anim)
                if loop:
                    actor.loop(anim)
                else:
                    actor.play(anim)

    def idle(self) -> None:
        anim = self._anims[_pick_anim(self.spec.anim_idle)]
        self._play_on_all(anim, self.spec.anim_idle_rate)

    def walk(self) -> None:
        anim = self._anims[_pick_anim(self.spec.anim_walk)]
        self._play_on_all(anim, self.spec.anim_walk_rate)

    def _finish_oneshot(self, for_idle: bool = True) -> None:
        self._oneshot_seq = None
        self.is_attacking = False
        for actor in self._actors:
            actor.stop()
        self._current_anim = None
        if for_idle:
            self.idle()
        else:
            self.walk()

    def attack(self) -> float:
        if self._oneshot_seq:
            self._oneshot_seq.pause()
        self.is_attacking = True
        anim = self._anims[_pick_anim(self.spec.anim_attack)]
        raw = self.actor.get_duration(anim)
        rate = self.spec.anim_attack_rate
        duration = (raw if raw is not None else 1.0) / rate
        half = duration / 2
        for actor in self._actors:
            actor.stop()
        self._current_anim = None
        self._play_on_all(anim, rate, loop=False)
        scale_up: Any = self.animate_scale(self.spec.attack_scale, half / 2)
        scale_up.ignore_paused = True
        invoke(
            self._restore_scale,
            half * 2,
            delay=half / 2,
            ignore_paused=True,
        )
        self._oneshot_seq = invoke(
            self._finish_oneshot,
            for_idle=False,
            delay=duration,
            ignore_paused=True,
        )
        return duration

    @_skip_if_destroyed
    def _blink_loop(self, condition_callable: Callable[[], bool]) -> None:
        if condition_callable():
            self.visible: bool = not self.visible
            invoke(self._blink_loop, condition_callable, delay=0.15)

    @_skip_if_destroyed
    def _restore_scale(self, duration: float) -> None:
        seq: Any = self.animate_scale(self.spec.scale, duration)
        seq.ignore_paused = True

    def update(self) -> None:
        if self.game_state != C.EGameState.RUNNING:
            if not self._oneshot_seq:
                self.idle()
            return
