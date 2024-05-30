import bpy
from numpy.random import uniform
from infinigen.assets.utils import physics, decorate
from infinigen.core.util.logging import Suppress
import infinigen.core.util.blender as butil

butil.clear_scene()
cubes = []
for _ in range(30):
    cubes.append(butil.spawn_cube(size=1))

for cube in cubes:
    decorate.transform(
        cube,
        translation=uniform(-5, 5, 3),
        rotation=uniform(-3.14, 3.13, 3),
        scale=uniform(0.5, 2, 3),
        local=False,
    )
    decorate.transform(cube, translation=(0, 0, 10))

plane = butil.spawn_plane(size=100)


fall_time = 100
with physics.EnablePhysics(cubes, [plane]):
    bpy.context.scene.frame_end = fall_time
    with Suppress():
        bpy.ops.ptcache.bake_all(True)
    bpy.context.scene.frame_current = fall_time
    with butil.SelectObjects(cubes):
        bpy.ops.object.visual_transform_apply()

butil.save_blend("output.blend")

## Serialize the scene
# import bpy
# import json
# import numpy as np

# data = []
# cubes = [obj for obj in bpy.data.objects if 'Cube' in obj.name]
# for cube in cubes:
#     tf = np.array(cube.matrix_world.normalized()).astype(float)
#     size = np.array(cube.scale).astype(float)
#     data.append({
#         'tf': tf.tolist(),
#         'size': size.tolist()
#     })

# with open('stacking.json', 'w') as f:
#     json.dump(data, f)


## Deserialize the scene
# import json
# import numpy as np
# from infinigen.assets.utils import decorate
# from mathutils import Matrix
# import infinigen.core.util.blender as butil

# with open("/home/shq/Projects/mycode/resolve_collision/stacking_output.json", "r") as f:
#     data = json.load(f)

# for item in data:
#     print(item['tf'])
#     print(item['size'])
#     obj = butil.spawn_cube(size=1)
#     obj.matrix_world = Matrix(np.array(item['tf']))
#     obj.scale = item['size']
