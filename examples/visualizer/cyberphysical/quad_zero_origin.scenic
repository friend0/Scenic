import trimesh
from pathlib import Path

# Load plane mesh from file and create plane shape from it
plane_shape = MeshShape.fromFile(localPath("../../../assets/meshes/quad_zero.stl"))
num_buildings = 10

class Plane:
    shape: plane_shape
    length: 1
    width: 1
    height: .25

class Building:
    shape: BoxShape(dimensions=(1, 1, 2))

ego = new Plane at (0,0,0)
for building in range(num_buildings):
    building = new Building at (Range(-num_buildings,num_buildings), Range(-num_buildings,num_buildings), 0), 
        facing (Range(0,180 deg), 0, 0)