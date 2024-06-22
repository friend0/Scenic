from scenic.domains.flying.flying_workspace import FlyingWorkspace
from scenic.simulators.utils.colors import Color

param map_options = {}

network : Network = Network.fromFile(globalParameters.map, **gloabalParameters.map_options)

workspace = FlyingWorkspace()

vertiport : Region = workspace.vertiport