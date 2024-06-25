"""Newtonian simulator implementation."""

import time
import math
import pathlib
import shapely
from scenic.core.geometry import allChains, findMinMax
import scenic.core.errors as errors

from scenic.domains.flying.simulators import FlyingSimulation, FlyingSimulator
from scenic.syntax.veneer import verbosePrint

current_dir = pathlib.Path(__file__).parent.absolute()

WIDTH = 1280
HEIGHT = 800


class WebSimulator(FlyingSimulator):
    """Implementation of `Simulator` for the web simulator.

    Args:
        render (bool): whether to render the simulation in a browser window.

    """

    def __init__(self, network=None, render=False, export_gif=False):
        super().__init__()
        self.export_gif = export_gif
        self.render = render

    def createSimulation(self, scene, **kwargs):
        simulation = WebSimulation(scene, self.render, **kwargs)
        return simulation


class WebSimulation(FlyingSimulation):
    """Implementation of `Simulation` for the web simulator."""

    def __init__(self, scene, render, timestep, **kwargs):
        self.render = render
        self.frames = []

        if timestep is None:
            timestep = 0.1

        super().__init__(scene, timestep=timestep, **kwargs)

    def setup(self):
        super().setup()

        if self.render:
            min_x, max_x = findMinMax(obj.x for obj in self.objects)
            min_y, max_y = findMinMax(obj.y for obj in self.objects)

            # todo: create a new browser window
            # self.window = NewBrowserWindow()
            x, y, _ = self.objects[0].position
            self.min_x, self.max_x = min_x - 50, max_x + 50
            self.min_y, self.max_y = min_y - 50, max_y + 50
            self.size_x = self.max_x - self.min_x
            self.size_y = self.max_y - self.min_y
            self.screen_poly = shapely.geometry.Polygon(
                (
                    (self.min_x, self.min_y),
                    (self.max_x, self.min_y),
                    (self.max_x, self.max_y),
                    (self.min_x, self.max_y),
                )
            )
            # determine window size
            self.draw_objects()

    def scenicToScreenVal(self, pos):
        x, y = pos[:2]
        x_prop = (x - self.min_x) / self.size_x
        y_prop = (y - self.min_y) / self.size_y
        return int(x_prop * WIDTH), HEIGHT - 1 - int(y_prop * HEIGHT)

    def createObjectInSimulator(self, obj):
        # Set actor's initial speed
        obj.speed = math.hypot(*obj.velocity)

        if hasattr(obj, "elevation"):
            obj.elevation = 0.0

    def isOnScreen(self, x, y):
        return self.min_x <= x <= self.max_x and self.min_y <= y <= self.max_y

    def step(self):
        for obj in self.objects:
            obj.speed = obj.velocity.norm()
            obj.position += obj.velocity * self.timestep
            obj.heading += obj.angularSpeed * self.timestep

        if self.render:
            self.draw_objects()

    def draw_objects(self):
        for i, obj in enumerate(self.objects):
            # plot objects in mesh
            ...
        # plot any other relevant objects
        time.sleep(self.timestep)

    def getProperties(self, obj, properties):
        yaw, _, _ = obj.parentOrientation.globalToLocalAngles(obj.heading, 0, 0)

        values = dict(
            position=obj.position,
            yaw=yaw,
            pitch=0,
            roll=0,
            speed=obj.speed,
            velocity=obj.velocity,
            angularSpeed=obj.angularSpeed,
            angularVelocity=obj.angularVelocity,
        )
        if "elevation" in properties:
            values["elevation"] = obj.elevation
        return values

    def destroy(self):
        if self.render:
            ...
