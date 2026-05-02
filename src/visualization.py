"""Ursina application and rendering layer.

Initializes the Ursina app, loads 3D models and assets,
manages the camera (top-down perspective and first-person),
renders all entities each frame, and delegates all game
logic to game_behavior via the global update() callback.
Entry point for the Ursina event loop.
"""

from ursina import color, Entity, Ursina, camera, window, application


class game_render(Entity):
    def __init__(self, gcf):
        self.app = Ursina()
        super().__init__()
        self.gcf = gcf
        camera.position = (0, 7, -2)
        camera.fov = 90
        camera.rotation_x = 80
        window.color = color.rgb(0, 0.2, 0)
        Entity(model='cube', color=color.red, position=(0, 0, 0))
        Entity(model='cube', color=color.blue, position=(2, 0, 3))
        Entity(model='cube', color=color.green, position=(-5, 0, -1))
        self.app.run()

    def update(self):
        pass

    def input(self, key):
        if key == 'q':
            application.quit()
