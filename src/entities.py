"""Game entity dataclasses.

Defines pure data structures representing game objects:
Player, Ghost, Pacgum, SuperPacgum, and Level.
No game logic or rendering — only structured state.
These classes are consumed by game_behavior and visualization.
"""

import random
from enum import Enum, auto
from typing import Any, TYPE_CHECKING

from direct.actor.Actor import Actor
from panda3d.core import MaterialAttrib
from ursina import Entity, application, held_keys
from ursina import time as _ursina_time

import src.constants as C
from src.game_config import GameConfig
from src.utils import grid_to_world, world_to_grid

if TYPE_CHECKING:
    from src.maze import Maze

ursina_time: Any = _ursina_time


def _pick_anim(spec: int | tuple[int, ...]) -> int:
    return random.choice(spec) if isinstance(spec, tuple) else spec


class AnimatedEntity(Entity):
    x: float
    y: float
    z: float
    rotation_y: float

    def __init__(
        self, spec: C.ModelSpec, maze: "Maze", speed: float = 0.0
    ) -> None:
        super().__init__()
        self.spec = spec
        # Some GLBs (Sketchfab/FAB exports) split a model across multiple
        # skins sharing the same skeleton root (body + eyes + weapon, etc.).
        # Each becomes a separate Character once the panda3d-gltf patches
        # land — wrap each as its own Actor so all skins render and animate.
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
        self.idle()

        self.maze = maze
        self.speed = speed
        self._grid_direction: tuple[int, int] = (0, 0)
        self._facing: tuple[int, int] = (0, 0)
        self.pos_gridx: int
        self.pos_gridy: int
        self.update_grid_position()

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
            duration = 0.15 * abs(delta) / 90
            self.animate_rotation_y(self.rotation_y + delta, duration)

    def update_grid_position(self) -> None:
        self.pos_gridx, self.pos_gridy = world_to_grid(
            self.x, self.z, self.maze.width, self.maze.height
        )

    def move_in_direction(self, dir_x: int, dir_y: int) -> None:
        if dir_x == 0 and dir_y == 0:
            return

        self._rotate_toward(dir_x, dir_y)
        self.grid_direction = (dir_x, dir_y)
        center_x, center_z = grid_to_world(
            self.pos_gridx, self.pos_gridy, self.maze.width, self.maze.height
        )
        cell_value = self.maze.grid[self.pos_gridy][self.pos_gridx]
        align_speed = 15.0

        if dir_x != 0:
            self.z += (center_z - self.z) * align_speed * ursina_time.dt
            self.x += dir_x * self.speed * ursina_time.dt
            if dir_x == 1 and (cell_value & 2):
                self.x = min(self.x, center_x)
            elif dir_x == -1 and (cell_value & 8):
                self.x = max(self.x, center_x)

        elif dir_y != 0:
            self.x += (center_x - self.x) * align_speed * ursina_time.dt
            self.z -= dir_y * self.speed * ursina_time.dt
            if dir_y == -1 and (cell_value & 1):
                self.z = min(self.z, center_z)
            elif dir_y == 1 and (cell_value & 4):
                self.z = max(self.z, center_z)

    def _fix_metallic(self) -> None:
        for actor in self._actors:
            for np in actor.find_all_matches("**/+GeomNode"):
                for i in range(np.node().get_num_geoms()):
                    ma = np.node().get_geom_state(i).get_attrib(MaterialAttrib)
                    if ma and ma.get_material():
                        ma.get_material().set_metallic(0.0)

    def _play_on_all(self, anim: str, rate: float) -> None:
        if self._current_anim == anim:
            return
        self._current_anim = anim
        for actor in self._actors:
            if anim in actor.get_anim_names():
                actor.set_play_rate(rate, anim)
                actor.loop(anim)

    def idle(self) -> None:
        anim = self._anims[_pick_anim(self.spec.anim_idle)]
        self._play_on_all(anim, self.spec.anim_idle_rate)

    def walk(self) -> None:
        anim = self._anims[_pick_anim(self.spec.anim_walk)]
        self._play_on_all(anim, self.spec.anim_walk_rate)

    def attack(self) -> None:
        anim = self._anims[_pick_anim(self.spec.anim_attack)]
        self._play_on_all(anim, self.spec.anim_attack_rate)
        self.animate_scale(self.spec.attack_scale, 0.15)

    def update(self) -> None:
        pass


class PlayerState(Enum):
    NORMAL = auto()
    UNTOUCHABLE = auto()
    HUNT = auto()


class Player(AnimatedEntity):
    def __init__(
        self, maze: "Maze", gcf: GameConfig, game_state: C.EGameState
    ) -> None:
        super().__init__(
            spec=C.MODEL_SPECS[7], maze=maze, speed=C.PLAYER_SPEED
        )
        self.game_state = game_state
        self.gcf = gcf
        self.health = gcf.lives
        self.state = PlayerState.NORMAL
        print("player lives:", self.health)

    def _reset_player_state(self) -> None:
        self.state = PlayerState.NORMAL

    def update(self) -> None:
        if self.game_state != C.EGameState.RUNNING:
            self.idle()
            return
        moving = False

        if held_keys["w"] or held_keys["up arrow"]:
            self.move_in_direction(0, -1)
            moving = True
        elif held_keys["s"] or held_keys["down arrow"]:
            self.move_in_direction(0, 1)
            moving = True
        elif held_keys["a"] or held_keys["left arrow"]:
            self.move_in_direction(-1, 0)
            moving = True
        elif held_keys["d"] or held_keys["right arrow"]:
            self.move_in_direction(1, 0)
            moving = True

        if moving:
            self.walk()
        else:
            self.grid_direction = (0, 0)
            self.idle()

        self.update_grid_position()


class Ghost(AnimatedEntity):
    def __init__(
        self,
        index: int = 0,
        x: float = 0,
        z: float = 0,
        maze: "Maze | None" = None,
    ) -> None:
        assert maze is not None
        spec = random.choice([s for s in C.MODEL_SPECS if s.supported])
        super().__init__(spec=spec, maze=maze, speed=C.GHOST_SPEED_NORMAL)
        self.x, self.z = x, z
        self.ghost_index = index
        self.walk()

    def _compute_best_dir(
        self, target_x: int, target_y: int, cell_value: int
    ) -> tuple[int, int]:
        directions = [(0, -1, 1), (-1, 0, 8), (0, 1, 4), (1, 0, 2)]
        possible_paths = []
        for dx, dy, wall_flag in directions:
            if cell_value & wall_flag:
                continue
            if (
                self.grid_direction != (0, 0)
                and dx == -self.grid_direction[0]
                and dy == -self.grid_direction[1]
            ):
                continue
            possible_paths.append((dx, dy))

        if not possible_paths:
            return (-self.grid_direction[0], -self.grid_direction[1])

        best_dir = self.grid_direction
        min_dist = float("inf")
        for dx, dy in possible_paths:
            dist = (self.pos_gridx + dx - target_x) ** 2 + (
                self.pos_gridy + dy - target_y
            ) ** 2
            if dist < min_dist:
                min_dist = dist
                best_dir = (dx, dy)
        return best_dir

    def update_ai(self, target_x: int, target_y: int) -> None:
        self.update_grid_position()
        center_x, center_z = grid_to_world(
            self.pos_gridx, self.pos_gridy, self.maze.width, self.maze.height
        )
        cell_value = self.maze.grid[self.pos_gridy][self.pos_gridx]
        dist_to_center = abs(self.x - center_x) + abs(self.z - center_z)

        if dist_to_center < 0.1 or self.grid_direction == (0, 0):
            best_dir = self._compute_best_dir(target_x, target_y, cell_value)
            self._rotate_toward(*best_dir)
            if dist_to_center < 0.1 or self.grid_direction == (0, 0):
                self.grid_direction = best_dir

        self.move_in_direction(self.grid_direction[0], self.grid_direction[1])


class Floor(Entity):
    def __init__(self, width: int, height: int, texture: str) -> None:
        super().__init__(
            model="plane",
            texture=texture,
            texture_scale=(width, height),
            scale=(width, 1, height),
            position=(0, 0, 0),
        )
