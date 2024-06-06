import bpy
import json
import numpy as np
import infinigen.core.util.blender as butil
from mathutils import Matrix

butil.clear_scene()

filepath = "/home/shq/Downloads/test_symmetry/test/sym24.json"
with open(filepath, "r") as f:
    data = json.load(f)
    for item in data:
        cube = butil.spawn_cube(size=1)
        cube.matrix_world = Matrix(np.array(item["tf"]))
        cube.scale = item["size"]

butil.save_blend('output/test.blend')