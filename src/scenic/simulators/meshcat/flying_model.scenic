"""Scenic world model for traffic scenarios in the Newtonian simulator.

This model implements the basic :obj:`~scenic.domains.driving.model.Car` class from the
:obj:`scenic.domains.driving` domain.
Vehicles support the basic actions and behaviors from the driving domain.

A path to a map file for the scenario should be provided as the ``map`` global parameter;
see the driving domain's documentation for details.
"""

from scenic.simulators.newtonian.model import *

from scenic.domains.driving.model import *  # includes basic actions and behaviors

from scenic.simulators.utils.colors import Color

simulator NewtonianSimulator(network, render=render)

class NewtonianActor(FlyingObject):
    thrust: 0
    position: Vector3
    velocity: Vector3
    quaternion: Quaternion
    omega: Vector3
    # todo: fill in vehicle properties

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._control = None    # used internally to accumulate control updates

    def setPosition(self, pos, elevation):
        # todo: fix broken elevation input
        self.position = pos

    def setVelocity(self, vel):
        self.velocity = vel

    def setThrust(self, thrust):
        self.thrust = thrust

class Vehicle(Vehicle, NewtonianActor):
    pass

class Multirotor(Vehicle, Steers):
    @property
    def withFlying(self):
        return True 
    
    @property
    def isCar(self):
        return False

class Obstacles:
    """Abstract class for debris scattered randomly in the workspace."""
    position: new Point in workspace
    yaw: Range(0, 360) deg
