"""Game entity dataclasses.

Defines pure data structures representing game objects:
Player, Ghost, Pacgum, SuperPacgum, and Level.
No game logic or rendering — only structured state.
These classes are consumed by game_behavior and visualization.
"""

from ursina import Entity, invoke, held_keys, time, color
from direct.actor.Actor import Actor
from panda3d.core import MaterialAttrib
import src.constants as C
from src.utils import world_to_grid, grid_to_world
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.maze import Maze


class AnimatedEntity(Entity):
    def __init__(
        self, spec: C.ModelSpec, maze: "Maze", speed: float = 0.0
    ) -> None:
        super().__init__()
        self.spec = spec
        self.actor = Actor(f"assets/{spec.path}")
        self.actor.reparent_to(self)
        self._fix_metallic()
        self.scale = spec.scale
        self.rotation_x = spec.rotation_x
        self._anims = self.actor.get_anim_names()
        self.idle()

        self.maze = maze
        self.speed = speed
        self.grid_direction: tuple[int, int] = (0, 0)
        self.pos_gridx: int = 0
        self.pos_gridy: int = 0

    def update_grid_position(self) -> None:
        self.pos_gridx, self.pos_gridy = world_to_grid(
            self.x, self.z, self.maze.width, self.maze.height
        )

    def move_in_direction(self, dir_x: int, dir_y: int) -> None:
        if dir_x == 0 and dir_y == 0:
            return

        self.grid_direction = (dir_x, dir_y)
        center_x, center_z = grid_to_world(
            self.pos_gridx, self.pos_gridy, self.maze.width, self.maze.height
        )
        cell_value = self.maze.grid[self.pos_gridy][self.pos_gridx]
        align_speed = 15.0

        if dir_x != 0:
            self.z += (center_z - self.z) * align_speed * time.dt
            self.x += dir_x * self.speed * time.dt
            if dir_x == 1 and (cell_value & 2):
                self.x = min(self.x, center_x)
            elif dir_x == -1 and (cell_value & 8):
                self.x = max(self.x, center_x)

        elif dir_y != 0:
            self.x += (center_x - self.x) * align_speed * time.dt
            self.z -= dir_y * self.speed * time.dt
            if dir_y == -1 and (cell_value & 1):
                self.z = min(self.z, center_z)
            elif dir_y == 1 and (cell_value & 4):
                self.z = max(self.z, center_z)

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
        super().__init__(
            spec=C.GHOST_SPECS[0], maze=maze, speed=C.PLAYER_SPEED
        )

    def update(self) -> None:
        self.update_grid_position()

        if held_keys["w"] or held_keys["up arrow"]:
            self.move_in_direction(0, -1)
        elif held_keys["s"] or held_keys["down arrow"]:
            self.move_in_direction(0, 1)
        elif held_keys["a"] or held_keys["left arrow"]:
            self.move_in_direction(-1, 0)
        elif held_keys["d"] or held_keys["right arrow"]:
            self.move_in_direction(1, 0)


class Ghost(Entity):
    def __init__(
        self,
        index: int = 0,
        position: tuple[float, float, float] = (0.0, 0.5, 0.0),
        maze: "Maze" = None,
    ) -> None:
        ghost_colors = [color.red, color.pink, color.cyan, color.orange]
        my_color = ghost_colors[index % len(ghost_colors)]

        super().__init__(
            model="sphere", color=my_color, scale=0.8, position=position
        )

        self.ghost_index = index
        self.maze = maze
        self.speed = 3.5
        self.grid_direction: tuple[int, int] = (0, 0)
        self.pos_gridx, self.pos_gridy = world_to_grid(
            self.x, self.z, self.maze.width, self.maze.height
        )

    def update_ai(self, target_x: int, target_y: int) -> None:
        self.pos_gridx, self.pos_gridy = world_to_grid(
            self.x, self.z, self.maze.width, self.maze.height
        )
        center_x, center_z = grid_to_world(
            self.pos_gridx, self.pos_gridy, self.maze.width, self.maze.height
        )
        cell_value = self.maze.grid[self.pos_gridy][self.pos_gridx]

        dist_to_center = abs(self.x - center_x) + abs(self.z - center_z)

        if dist_to_center < 0.1 or self.grid_direction == (0, 0):

            directions = [(0, -1, 1), (-1, 0, 8), (0, 1, 4), (1, 0, 2)]

            best_dir = self.grid_direction
            min_dist = float("inf")

            for dx, dy, wall_flag in directions:
                if cell_value & wall_flag:
                    continue

                if (
                    self.grid_direction != (0, 0)
                    and dx == -self.grid_direction[0]
                    and dy == -self.grid_direction[1]
                ):
                    continue

                next_x = self.pos_gridx + dx
                next_y = self.pos_gridy + dy
                dist = (next_x - target_x) ** 2 + (next_y - target_y) ** 2

                if dist < min_dist:
                    min_dist = dist
                    best_dir = (dx, dy)

            self.grid_direction = best_dir

        self.move_in_direction(self.grid_direction[0], self.grid_direction[1])

    def move_in_direction(self, dir_x: int, dir_y: int) -> None:
        if dir_x == 0 and dir_y == 0:
            return

        center_x, center_z = grid_to_world(
            self.pos_gridx, self.pos_gridy, self.maze.width, self.maze.height
        )
        cell_value = self.maze.grid[self.pos_gridy][self.pos_gridx]
        align_speed = 15.0

        if dir_x != 0:
            self.z += (center_z - self.z) * align_speed * time.dt
            self.x += dir_x * self.speed * time.dt
            if dir_x == 1 and (cell_value & 2):
                self.x = min(self.x, center_x)
            elif dir_x == -1 and (cell_value & 8):
                self.x = max(self.x, center_x)

        elif dir_y != 0:
            self.x += (center_x - self.x) * align_speed * time.dt
            self.z -= dir_y * self.speed * time.dt
            if dir_y == -1 and (cell_value & 1):
                self.z = min(self.z, center_z)
            elif dir_y == 1 and (cell_value & 4):
                self.z = max(self.z, center_z)

        # ANIMATED A REVENIR DESSUS
        # spec = C.GHOST_SPECS[index % len(C.GHOST_SPECS)]

        # if not spec.supported:
        #     raise ValueError(
        #         f"Ghost model at index {index} is not supported by Actor"
        #     )
        # super().__init__(spec)


class Floor(Entity):
    def __init__(self, width: int, height: int, texture: str) -> None:
        super().__init__(
            model="plane",
            texture=texture,
            texture_scale=(width, height),
            scale=(width, 1, height),
            position=(0, 0, 0),
        )
