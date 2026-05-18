import random
from typing import Any
from ursina import camera, scene, mouse, held_keys, time, invoke
from panda3d.core import Shader, Texture


class CameraEffectsManager:
    """View modes (Topdown / FPS), barrel distortion, and camera shake."""

    def __init__(self, engine: Any) -> None:
        self.engine = engine
        self.fps_mode: bool = False
        self.fps_ctrl: Any = None
        self._barrel_quad: Any = None
        self._manager: Any = None
        self._barrel_strength: float = 0.2
        self._shake_active: bool = False

        self.setup_barrel()

    def setup_barrel(self) -> None:
        """Install the Panda3D barrel-distortion shader."""
        from direct.filter.FilterManager import FilterManager

        if self._manager is not None:
            return
        self._manager = FilterManager(self.engine.app.win, self.engine.app.cam)
        tex = Texture()
        self._barrel_quad = self._manager.renderSceneInto(colortex=tex)
        self._barrel_quad.setShader(
            Shader.load(
                Shader.SL_GLSL,
                vertex="shaders/barrel.vert",
                fragment="shaders/barrel.frag",
            )
        )
        self._barrel_quad.setShaderInput("tex", tex)
        self._barrel_quad.setShaderInput("strength", 0.0)

    def enable_barrel(self) -> None:
        if self._barrel_quad:
            self._barrel_quad.setShaderInput("strength", self._barrel_strength)

    def disable_barrel(self) -> None:
        if self._barrel_quad:
            self._barrel_quad.setShaderInput("strength", 0.0)

    def set_topdown(self) -> None:
        if self.fps_ctrl:
            self.fps_ctrl.enabled = False

        camera.parent = scene
        lvl = self.engine.config.levels[
            self.engine.session.current_level_index
        ]
        y = max(lvl.width, lvl.height) * 0.6
        camera.position = (0, y * 1.25, -y * 0.30)
        camera.rotation_x = 80
        camera.rotation_y = 0
        camera.rotation_z = 0
        camera.fov = 110

        mouse.locked = False
        mouse.visible = True
        self.enable_barrel()

    def set_fps(self) -> None:
        from ursina.prefabs.first_person_controller import (
            FirstPersonController,
        )

        self.disable_barrel()
        if self.fps_ctrl is None:
            self.fps_ctrl = FirstPersonController(
                position=(1, 2, 1), gravity=0
            )
        else:
            self.fps_ctrl.enabled = True

        mouse.locked = True
        mouse.visible = False

    def toggle_fps(self) -> None:
        self.fps_mode = not self.fps_mode
        if self.fps_mode:
            self.set_fps()
        else:
            self.set_topdown()

    def shake_screen(
        self, mag: float = 0.3, dur: float = 0.25, period: float = 0.03
    ) -> None:
        if self._shake_active or self.fps_mode:
            return
        self._shake_active = True
        base_x, base_z = camera.x, camera.z
        elapsed = [0.0]

        def step() -> None:
            elapsed[0] += period
            if elapsed[0] >= dur:
                camera.x, camera.z = base_x, base_z
                self._shake_active = False
                return
            decay = 1 - elapsed[0] / dur
            camera.x = base_x + random.uniform(-mag, mag) * decay
            camera.z = base_z + random.uniform(-mag, mag) * decay
            invoke(step, delay=period)

        step()

    def update_fps_controls(self) -> None:
        """Handle vertical movement keys in FPS mode."""
        if self.fps_mode and self.fps_ctrl:
            speed = 5
            if held_keys["space"]:
                self.fps_ctrl.y += speed * time.dt
            if held_keys["shift"]:
                self.fps_ctrl.y -= speed * time.dt
