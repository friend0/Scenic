

class Vertiport:
    def __init__(self, location):
        self.location = location

    def __repr__(self):
        return f'Vertiport({self.location})'

class Corridor:
    def __init__(self, waypoints):
        self.waypoints = waypoints

    def __repr__(self):
        return f'Corridor({self.start}, {self.end})'

class TemporalSpatialConstraint:
    def __init__(self, start, end, geometry):
        self.start = start
        self.end = end
        self.geometry = geometry

    def __repr__(self):
        return f'TemporalSpatialConstraint({self.start}, {self.end}, {self.geometry})'

