import os
import json
import bpy
import shutil
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
from pathlib import Path


def write_box_json(filepath, boxes):
    data = []
    for box in boxes:
        tf = np.array(box.matrix_world.normalized()).astype(float)
        size = np.array(box.scale).astype(float)
        data.append({"tf": tf.tolist(), "size": size.tolist()})
    with open(filepath, "w") as f:
        json.dump(data, f)


for i in range(100):
    butil.clear_scene()

    sku_size = (0.6, 0.4, 0.38)
    sku_gen = SingleSKUGenerator(SKU(sku_size))
    stacking_factory = SingleSKUStackingFactory()
    inner_size = np.array([4.0, 2.34, 2.64])
    free_space_length = 1.0
    cubes = stacking_factory.create_boxes(
        (inner_size[0] - free_space_length, inner_size[1], inner_size[2]),
        sku_gen,
    )
    gap_y = inner_size[1] % sku_size[1]
    for cube in cubes:
        decorate.transform(
            cube, translation=(free_space_length, -inner_size[1] / 2 + gap_y / 2, 0.3)
        )
        decorate.transform(
            cube,
            translation=uniform(-0.01, 0.01, 3),
            rotation=uniform(0.0, 0.0, 3),
            scale=uniform(1.00, 1.00, 3),
            # rotation=uniform(-0.06, 0.06, 3),
            # scale=uniform(0.98, 1.02, 3),
            local=True,
        )

    plane = butil.spawn_plane(size=100)
    plane2 = butil.spawn_plane(size=100)
    decorate.transform(plane2, translation=(0, 0, 0), rotation=(0, np.pi / 2, 0))
    plane3 = butil.spawn_plane(size=100)
    decorate.transform(
        plane3, translation=(inner_size[0], 0, 0), rotation=(0, np.pi / 2, 0)
    )
    plane4 = butil.spawn_plane(size=100)
    decorate.transform(
        plane4, translation=(0, -inner_size[1] / 2, 0), rotation=(np.pi / 2, 0, 0)
    )
    plane5 = butil.spawn_plane(size=100)
    decorate.transform(
        plane5, translation=(0, inner_size[1] / 2, 0), rotation=(np.pi / 2, 0, 0)
    )

    fall_time = 200
    with physics.EnablePhysics(cubes, [plane, plane2, plane3, plane4, plane5]):
        bpy.context.scene.frame_end = fall_time
        with Suppress():
            bpy.ops.ptcache.bake_all(True)
        bpy.context.scene.frame_current = fall_time
        with butil.SelectObjects(cubes):
            bpy.ops.object.visual_transform_apply()

    physics.resolve_collision(
        cubes,
        min_bound=(0, -inner_size[1] / 2, 0),
        max_bound=(inner_size[0], inner_size[1] / 2, inner_size[2]),
    )
    butil.delete([plane, plane2, plane3, plane4, plane5])

    container_factory = ContainerFactory()
    container = container_factory.create_asset(inner_size=inner_size)
    decorate.transform(container, translation=[inner_size[0] / 2, 0, inner_size[2] / 2])

    butil.group_in_collection(cubes, "GT World")
    butil.group_in_collection([container], "GT World")

    output_dir = Path(f"output/{i:04}")
    shutil.rmtree(output_dir, ignore_errors=True)
    os.makedirs(output_dir, exist_ok=True)

    butil.save_blend(str(output_dir / "scene.blend"))
