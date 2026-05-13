"""Game entity dataclasses.

Defines pure data structures representing game objects:
Player, Ghost, Pacgum, SuperPacgum, and Level.
No game logic or rendering — only structured state.
These classes are consumed by game_behavior and visualization.
"""

import random
from ursina import Entity, invoke
from direct.actor.Actor import Actor
from panda3d.core import MaterialAttrib
import src.constants as C


def _pick_anim(spec: int | tuple[int, ...]) -> int:
    return random.choice(spec) if isinstance(spec, tuple) else spec


class AnimatedEntity(Entity):
    def __init__(self, spec: C.ModelSpec) -> None:
        super().__init__()
        self.spec = spec
        self.actor = Actor(f"assets/{spec.path}")
        self.actor.reparent_to(self)
        self._fix_metallic()
        self.scale = spec.scale
        self.rotation_x = spec.rotation_x
        self.y = spec.spawn_y
        self._anims = self.actor.get_anim_names()
        self.idle()

    def _fix_metallic(self) -> None:
        for np in self.actor.find_all_matches('**/+GeomNode'):
            for i in range(np.node().get_num_geoms()):
                ma = np.node().get_geom_state(i).get_attrib(MaterialAttrib)
                if ma and ma.get_material():
                    ma.get_material().set_metallic(0.0)

    def idle(self) -> None:
        anim = self._anims[_pick_anim(self.spec.anim_idle)]
        self.actor.set_play_rate(self.spec.anim_idle_rate, anim)
        self.actor.loop(anim)

    def walk(self) -> None:
        anim = self._anims[_pick_anim(self.spec.anim_walk)]
        self.actor.set_play_rate(self.spec.anim_walk_rate, anim)
        self.actor.loop(anim)

    def attack(self) -> None:
        anim = self._anims[_pick_anim(self.spec.anim_attack)]
        frames = self.actor.get_num_frames(anim) or 24
        duration = frames / 24.0 / self.spec.anim_attack_rate
        self.actor.set_play_rate(self.spec.anim_attack_rate, anim)
        self.actor.play(anim)
        self.animate_scale(self.spec.attack_scale, 0.15)
        invoke(lambda: self.animate_scale(self.spec.scale, 0.15), delay=0.15)
        invoke(self.idle, delay=duration)

    def update(self) -> None:
        pass

# crash 1 7
# in progress
# are perfect 0 2
class Player(AnimatedEntity):
    def __init__(self) -> None:
        super().__init__(C.GHOST_SPECS[2])


class Ghost(AnimatedEntity):
    def __init__(self, index: int = 0) -> None:
        spec = C.GHOST_SPECS[index % len(C.GHOST_SPECS)]
        if not spec.supported:
            raise ValueError(f"Ghost model at index {index} is not supported by Actor")
        super().__init__(spec)


class Floor(Entity):
    def __init__(self, width: int, height: int, texture: str) -> None:
        super().__init__(
            model='plane',
            texture=texture,
            texture_scale=(width, height),
            scale=(width, 1, height),
            position=(0, 0, 0),
        )
