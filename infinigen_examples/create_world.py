import bpy
import json
import numpy as np
import infinigen.core.util.blender as butil
from mathutils import Matrix


def load_cube_json(filepath):
    cubes = []
    with open(filepath, "r") as f:
        data = json.load(f)
        for item in data:
            cube = butil.spawn_cube(size=1)
            cube.matrix_world = Matrix(np.array(item["tf"]))
            cube.scale = item["size"]
            cubes.append(cube)
    return cubes


butil.clear_scene()

cubes = load_cube_json(
    "/home/shq/Projects/mycode/resolve_collision/data/pickable/boxes.json"
)
butil.group_in_collection(cubes, "GT World")

cubes = load_cube_json("/home/shq/Projects/mycode/resolve_collision/output/output.json")
butil.group_in_collection(cubes, "Pickable")


butil.save_blend("output/test.blend")
