"""Newtonian simulator implementation."""

from cmath import atan, pi, tan
import math
from math import copysign, degrees, radians, sin
import os
import pathlib
import time

from PIL import Image
import numpy as np

import scenic.core.errors as errors  # isort: skip

if errors.verbosityLevel == 0:  # suppress pygame advertisement at zero verbosity
    os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"
import pygame
import shapely

from scenic.core.geometry import allChains, findMinMax
from scenic.core.regions import toPolygon
from scenic.core.simulators import SimulationCreationError
from scenic.core.vectors import Orientation, Vector
from scenic.domains.driving.controllers import (
    PIDLateralController,
    PIDLongitudinalController,
)
from scenic.domains.driving.roads import Network
from scenic.domains.driving.simulators import DrivingSimulation, DrivingSimulator
from scenic.syntax.veneer import verbosePrint

current_dir = pathlib.Path(__file__).parent.absolute()

WIDTH = 1280
HEIGHT = 800
MAX_ACCELERATION = 5.6  # in m/s2, seems to be a pretty reasonable value
MAX_BRAKING = 4.6

ROAD_COLOR = (0, 0, 0)
ROAD_WIDTH = 2
LANE_COLOR = (96, 96, 96)
CENTERLINE_COLOR = (224, 224, 224)
SIDEWALK_COLOR = (0, 128, 255)
SHOULDER_COLOR = (96, 96, 96)


class WebSimulator(DrivingSimulator):
    """Implementation of `Simulator` for the web simulator.

    Args:
        network (Network): road network to display in the background, if any.
        render (bool): whether to render the simulation in a window.

    .. versionchanged:: 3.0

        The **timestep** argument is removed: it can be specified when calling
        `simulate` instead. The default timestep for the Newtonian simulator
        when not otherwise specified is still 0.1 seconds.
    """

    def __init__(self, network=None, render=False, export_gif=False):
        super().__init__()
        self.export_gif = export_gif
        self.render = render
        self.network = network

    def createSimulation(self, scene, **kwargs):
        simulation = WebSimulation(
            scene, self.network, self.render, self.export_gif, **kwargs
        )
        if self.export_gif and self.render:
            simulation.generate_gif("simulation.gif")
        return simulation


class WebSimulation(DrivingSimulation):
    """Implementation of `Simulation` for the web simulator."""

    def __init__(self, scene, network, render, export_gif, timestep, **kwargs):
        self.export_gif = export_gif
        self.render = render
        self.network = network
        self.frames = []

        if timestep is None:
            timestep = 0.1

        super().__init__(scene, timestep=timestep, **kwargs)

    def setup(self):
        super().setup()

        if self.render:
            # determine window size
            self.parse_network()
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
            current_speed = obj.velocity.norm()
            if hasattr(obj, "hand_brake"):
                forward = obj.velocity.dot(Vector(0, 1).rotatedBy(obj.heading)) >= 0
                signed_speed = current_speed if forward else -current_speed
                if obj.hand_brake or obj.brake > 0:
                    braking = MAX_BRAKING * max(obj.hand_brake, obj.brake)
                    acceleration = braking * self.timestep
                    if acceleration >= current_speed:
                        signed_speed = 0
                    elif forward:
                        signed_speed -= acceleration
                    else:
                        signed_speed += acceleration
                else:
                    acceleration = obj.throttle * MAX_ACCELERATION
                    if obj.reverse:
                        acceleration *= -1
                    signed_speed += acceleration * self.timestep

                obj.velocity = Vector(0, signed_speed).rotatedBy(obj.heading)
                if obj.steer:
                    turning_radius = obj.length / sin(obj.steer * math.pi / 2)
                    obj.angularSpeed = -signed_speed / turning_radius
                else:
                    obj.angularSpeed = 0
                obj.speed = abs(signed_speed)
            else:
                obj.speed = current_speed
            obj.position += obj.velocity * self.timestep
            obj.heading += obj.angularSpeed * self.timestep

        if self.render:
            self.draw_objects()
            pygame.event.pump()

    def draw_objects(self):
        self.screen.fill((255, 255, 255))

        for i, obj in enumerate(self.objects):
            ...
            # plot objects in mesh
        #plot any other relevant objects
        time.sleep(self.timestep)

    def generate_gif(self, filename="simulation.gif"):
        imgs = [Image.fromarray(frame) for frame in self.frames]
        imgs[0].save(
            filename, save_all=True, append_images=imgs[1:], duration=50, loop=0
        )

    def getProperties(self, obj, properties):
        yaw, _, _ = obj.parentOrientation.globalToLocalAngles(obj.heading, 0, 0)

        values = dict(
            position=obj.position,
            yaw=yaw,
            pitch=0,
            roll=0,
            velocity=obj.velocity,
            speed=obj.speed,
            angularSpeed=obj.angularSpeed,
            angularVelocity=obj.angularVelocity,
        )
        if "elevation" in properties:
            values["elevation"] = obj.elevation
        return values

    def destroy(self):
        if self.render:
            pygame.quit()
