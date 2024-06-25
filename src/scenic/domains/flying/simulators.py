"""Abstract interface to simulators supporting the flying domain."""

from scenic.core.simulators import Simulation, Simulator


class FlyingSimulator(Simulator):
    """A `Simulator` supporting the flying domain."""

    ...


class FlyingSimulation(Simulation):
    """A `Simulation` with a simulator supporting the flying domain."""

    ...
