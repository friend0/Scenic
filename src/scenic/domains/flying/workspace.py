"""Workspaces for the driving domain."""

from scenic.core.workspaces import Workspace

class Map:
    """Create a map from a center coordinate and extent"""

    def __init__(self, center, extent) -> None:
        pass 
    
    def show(self):
        pass

class FlyingWorkspace(Workspace):
    """Workspace created from a GPS center coordinate and map extent""" 

    def __init__(self, center, extent):
        self.center = center
        self.extent = extent
        self.map = NewMap(center, extent)
        super().__init__()

    def show2D(self, plt):
        self.map.show()

    @property
    def minimumZoomSize(self):
        return 20
