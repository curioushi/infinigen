import bpy
import numpy as np
from numpy.random import uniform
from infinigen.assets.warehouse.stacking import (
    SKU,
    SingleSKUGenerator,
    SingleSKUStackingFactory,
)
from infinigen.assets.warehouse.container import ContainerFactory
from infinigen.assets.utils import physics, decorate
from infinigen.core.util.logging import Suppress
import infinigen.core.util.blender as butil

butil.clear_scene()

sku_gen = SingleSKUGenerator(SKU((0.595, 0.195, 0.395)))
stacking_factory = SingleSKUStackingFactory()
cubes = stacking_factory.create_boxes((3.0, 3.0, 3.0), sku_gen)
for cube in cubes:
    decorate.transform(cube, translation=(1, 0, 0.3))
    decorate.transform(
        cube,
        translation=uniform(-0.03, 0.03, 3),
        rotation=uniform(-0.1, 0.1, 3),
        scale=uniform(0.9, 1.0, 3),
        local=True,
    )

plane = butil.spawn_plane(size=100)
decorate.transform(plane, translation=(0, 0, 0))
plane2 = butil.spawn_plane(size=100)
decorate.transform(plane2, translation=(0, 0, 0), rotation=(0, np.pi / 2, 0))
plane3 = butil.spawn_plane(size=100)
decorate.transform(plane3, translation=(4, 0, 0), rotation=(0, np.pi / 2, 0))
plane4 = butil.spawn_plane(size=100)
decorate.transform(plane4, translation=(0, 0, 0), rotation=(np.pi / 2, 0, 0))
plane5 = butil.spawn_plane(size=100)
decorate.transform(plane5, translation=(0, 3, 0), rotation=(np.pi / 2, 0, 0))


fall_time = 200
with physics.EnablePhysics(cubes, [plane, plane2, plane3, plane4, plane5]):
    bpy.context.scene.frame_end = fall_time
    with Suppress():
        bpy.ops.ptcache.bake_all(True)
    bpy.context.scene.frame_current = fall_time
    with butil.SelectObjects(cubes):
        bpy.ops.object.visual_transform_apply()

physics.resolve_collision(cubes, min_bound=(0, -0.05, 0), max_bound=(4, 3, 3))
butil.delete([plane, plane2, plane3, plane4, plane5])

container_factory = ContainerFactory()
container = container_factory.create_asset(inner_size=(4, 3, 3))
decorate.transform(container, translation=(2, 1.5, 1.5))


butil.save_blend("output2.blend")
