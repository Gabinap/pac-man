from typing import Any, TYPE_CHECKING
from panda3d.core import ColorAttrib, MaterialAttrib, TextureAttrib
from ursina import Entity

import src.config.constants as C
from src.utils.utils import grid_to_world

if TYPE_CHECKING:
    from src.gameplay.maze import Maze


_MATERIALS_FIXED: set[str] = set()
_BOUNDS_CACHE: dict[str, tuple[float, float, float]] = {}


class Pacgum(Entity):  # type: ignore[misc, unused-ignore]
    """3D collectible that spins in place and awards points on pickup."""

    SCALE_MULTIPLIER: float = 1.0
    SPIN_SPEED: float = 90.0  # degrees per second

    def __init__(
        self,
        spec: C.PacgumSpec,
        grid_x: int,
        grid_y: int,
        maze: "Maze",
        points: int,
    ) -> None:
        """Place the pacgum at (grid_x, grid_y) and fix its materials."""
        world_x, world_z = grid_to_world(
            grid_x, grid_y, maze.width, maze.height
        )
        super().__init__(
            model=f"assets/{spec.path}",
            position=(world_x, spec.hover_y, world_z),
            scale=spec.scale * self.SCALE_MULTIPLIER,
            rotation_x=spec.rotation_x,
            ignore_paused=True,
        )
        self.spec = spec
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.points = points
        self.is_super = False
        self._fix_materials()
        self._recenter_model()

    def _fix_materials(self) -> None:
        """Two PBR quirks Panda3D's default rendering doesn't handle for us:

        1. `metallic > 0` washes the model out to white under the non-PBR
           pipeline — force metallic to 0 on every material.
        2. Materials that only carry a `baseColorFactor` (no texture, e.g.
           the inflatable buoy, energy cell) render as plain white because
           Panda3D shows `diffuse`, not `base_color`. For each geom without
           a texture, copy `base_color` onto a flat `ColorAttrib` so the
           color factor actually shows up.

        Geom data is shared by Panda3D's loader cache, so this only needs
        to run once per GLB path — all subsequent instances inherit it.
        """
        if self.spec.path in _MATERIALS_FIXED:
            return
        model: Any = self.model
        if not model:
            return
        for geom_np in model.find_all_matches("**/+GeomNode"):
            gn = geom_np.node()
            for i in range(gn.get_num_geoms()):
                state = gn.get_geom_state(i)
                ma = state.get_attrib(MaterialAttrib)
                if not ma or not ma.get_material():
                    continue
                mat = ma.get_material()
                mat.set_metallic(0.0)

                ta = state.get_attrib(TextureAttrib)
                if ta is None or ta.get_num_on_stages() == 0:
                    base = mat.get_base_color()
                    new_state = state.set_attrib(ColorAttrib.make_flat(base))
                    gn.set_geom_state(i, new_state)
        _MATERIALS_FIXED.add(self.spec.path)

    def _recenter_model(self) -> None:
        """Shift the loaded mesh so its visual center sits on the entity's
        pivot. Without this, GLBs whose geometry is offset from the file's
        origin trace a circle when we rotate around Y (orbit) instead of
        spinning in place. The per-instance ``set_pos`` is necessary (each
        Entity owns its own NodePath transform) but the bounds computation
        is cached per GLB path.
        """
        model: Any = self.model
        if not model:
            return
        cached = _BOUNDS_CACHE.get(self.spec.path)
        if cached is None:
            bounds = model.get_tight_bounds()
            if bounds is None:
                return
            mins, maxs = bounds
            cached = (
                -(mins.x + maxs.x) * 0.5,
                -(mins.y + maxs.y) * 0.5,
                -(mins.z + maxs.z) * 0.5,
            )
            _BOUNDS_CACHE[self.spec.path] = cached
        model.set_pos(*cached)
