"""Workspaces for the flying domain."""

from typing import Tuple

import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import networkx as nx
import osmnx as ox
from cartopy.io.img_tiles import GoogleTiles
from scenic.core.workspaces import Workspace


class FlyingWorkspace(Workspace):
    """Workspace created from an origin coordinate, and map extent."""

    tiler = GoogleTiles(style="satellite")
    projection = tiler.crs

    def __init__(
        self,
        origin: Tuple[float, float],
        extents: Tuple[float, float, float, float],
    ):
        super().__init__()
        self.projection = ccrs.PlateCarree()
        self.origin = origin
        if extents is None:
            extents = (-122.07, -122.049, 36.9955, 37.0038)
        self.extents = extents

    # TODO: should plot map and terrain around origin
    def show2D(self, plt=plt):
        # plt.gca().set_aspect("equal")
        fig, ax = plt.subplots(
            1, 1, figsize=(10, 10), subplot_kw=dict(projection=self.projection)
        )
        # ax = fig.add_subplot(1, 1, 1, projection=self.projection)
        # ax.set_extent(self.extents, crs=self.projection)
        ax.set_extent((-122.07, -122.049, 36.9955, 37.0038), crs=self.projection)

        ax.add_image(self.tiler, 18)

        ax.coastlines("10m")
        plt.show()

    def show3D(self):
        pass


ws = FlyingWorkspace(
    origin=(-122.0704035818135, 37.00387969885156),
    extents=(-122.07, -122.049, 36.9955, 37.0038),
)
ws.show2D()

G = ox.graph_from_place("Santa Cruz, California, USA", network_type="drive")
B = ox.features_from_place("UC Santa Cruz, California, USA", tags={"building": True})
# for feature in G:
#     print(feature)
fig, ax = ox.plot_graph(G)
