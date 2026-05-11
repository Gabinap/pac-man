"""Game entity dataclasses.

Defines pure data structures representing game objects:
Player, Ghost, Pacgum, SuperPacgum, and Level.
No game logic or rendering — only structured state.
These classes are consumed by game_behavior and visualization.
"""

from ursina import Entity, invoke, held_keys, time
from direct.actor.Actor import Actor
from panda3d.core import MaterialAttrib
import src.constants as C
from src.utils import world_to_grid, grid_to_world
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.maze import Maze


class AnimatedEntity(Entity):
    def __init__(self, spec: C.ModelSpec) -> None:
        super().__init__()
        self.spec = spec
        self.actor = Actor(f"assets/{spec.path}")
        self.actor.reparent_to(self)
        self._fix_metallic()
        self.scale = spec.scale
        self.rotation_x = spec.rotation_x
        self._anims = self.actor.get_anim_names()
        self.idle()

    def _fix_metallic(self) -> None:
        for np in self.actor.find_all_matches("**/+GeomNode"):
            for i in range(np.node().get_num_geoms()):
                ma = np.node().get_geom_state(i).get_attrib(MaterialAttrib)
                if ma and ma.get_material():
                    ma.get_material().set_metallic(0.0)

    def idle(self) -> None:
        anim = self._anims[self.spec.anim_idle]
        self.actor.set_play_rate(self.spec.anim_idle_rate, anim)
        self.actor.loop(anim)

    def walk(self) -> None:
        anim = self._anims[self.spec.anim_walk]
        self.actor.set_play_rate(self.spec.anim_walk_rate, anim)
        self.actor.loop(anim)

    def attack(self) -> None:
        anim = self._anims[self.spec.anim_attack]
        frames = self.actor.get_num_frames(anim) or 24
        duration = frames / 24.0 / self.spec.anim_attack_rate
        self.actor.set_play_rate(self.spec.anim_attack_rate, anim)
        self.actor.play(anim)
        self.animate_scale(self.spec.attack_scale, 0.15)
        invoke(lambda: self.animate_scale(self.spec.scale, 0.15), delay=0.15)
        invoke(self.idle, delay=duration)

    def update(self) -> None:
        pass


class Player(AnimatedEntity):
    def __init__(self, maze: "Maze") -> None:
        super().__init__(C.GHOST_SPECS[0])
        self.speed = C.PLAYER_SPEED
        self.maze = maze

    def update(self) -> None:
        pos_x, pos_y = world_to_grid(
            self.x,
            self.z,
            self.maze.width,
            self.maze.height,
        )
        center_x, center_z = grid_to_world(
            pos_x, pos_y, self.maze.width, self.maze.height
        )
        cell_value = self.maze.grid[pos_y][pos_x]
        align_speed = 15.0
        if held_keys["w"] or held_keys["up arrow"]:
            self.x += (center_x - self.x) * align_speed * time.dt
            self.z += self.speed * time.dt
            if cell_value & 1:
                self.z = min(self.z, center_z)

        elif held_keys["s"] or held_keys["down arrow"]:
            self.x += (center_x - self.x) * align_speed * time.dt
            self.z -= self.speed * time.dt
            if cell_value & 4:
                self.z = max(self.z, center_z)

        elif held_keys["a"] or held_keys["left arrow"]:
            self.z += (center_z - self.z) * align_speed * time.dt
            self.x -= self.speed * time.dt
            if cell_value & 8:
                self.x = max(self.x, center_x)

        elif held_keys["d"] or held_keys["right arrow"]:
            self.z += (center_z - self.z) * align_speed * time.dt
            self.x += self.speed * time.dt
            if cell_value & 2:
                self.x = min(self.x, center_x)


class Ghost(AnimatedEntity):
    def __init__(self, index: int = 0, position=tuple[float, float]) -> None:
        spec = C.GHOST_SPECS[index % len(C.GHOST_SPECS)]
        if not spec.supported:
            raise ValueError(
                f"Ghost model at index {index} is not supported by Actor"
            )
        super().__init__(spec)


class Floor(Entity):
    def __init__(self, width: int, height: int, texture: str) -> None:
        super().__init__(
            model="plane",
            texture=texture,
            texture_scale=(width, height),
            scale=(width, 1, height),
            position=(0, 0, 0),
        )
