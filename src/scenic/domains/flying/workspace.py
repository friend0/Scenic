"""Workspaces for the flying domain."""

from typing import Tuple
from scenic.core.workspaces import Workspace

import cartopy.crs as ccrs
from cartopy.io.img_tiles import GoogleTiles

import networkx as nx
import osmnx as ox

class FlyingWorkspace(Workspace):
    """Workspace created from an origin coordinate, and map extent."""

    tiler = GoogleTiles(style="satellite")
    projection = tiler.crs

    def __init__(
        self,
        origin: Tuple[float, float],
        extents: Tuple[float, float, float, float],
    ):
        self.origin = origin
        if extents is None:
            extents = [-122.07, -122.049, 36.9955, 37.0038]
        self.extents = extents
        super().__init__()

    #TODO: should plot map and terrain around origin
    def show2D(self, plt=None):
        if plt is None:
            import matplotlib.pyplot as plt
        # plt.gca().set_aspect("equal")
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1, projection=self.projection)
        ax.set_extent(self.extents, crs=ccrs.PlateCarree())

        ax.add_image(self.tiler, 18)

        ax.coastlines('10m')
        plt.show()

    @property
    def minimumZoomSize(self):
        return 20


ws = FlyingWorkspace(origin=[-122.0704035818135, 37.00387969885156],
                     extents=[-122.07, -122.049, 36.9955, 37.0038])
ws.show2D()

# G = ox.graph_from_place("Santa Cruz, California, USA", network_type="drive")
B = ox.features_from_place("UC Santa Cruz, California, USA", tags={'building': True})
for feature in B:
    print(feature)
fig, ax = ox.plot_footprints(B)