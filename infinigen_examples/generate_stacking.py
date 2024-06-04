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
from infinigen.assets.lidars import (
    MID360,
    generate_lidar_clouds,
    create_pointcloud_mesh,
    add_noise,
    remove_points_near,
    write_pcd_binary,
)
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

    sku_gen = SingleSKUGenerator(SKU((0.595, 0.195, 0.395)))
    stacking_factory = SingleSKUStackingFactory()
    inner_size = np.array([4.0, 3.0, 3.0])
    free_space_length = 1.0
    cubes = stacking_factory.create_boxes(
        (inner_size[0] - free_space_length, inner_size[1], inner_size[2]),
        sku_gen,
    )
    for cube in cubes:
        decorate.transform(
            cube, translation=(free_space_length, -inner_size[1] / 2, 0.3)
        )
        decorate.transform(
            cube,
            translation=uniform(-0.03, 0.03, 3),
            rotation=uniform(-0.1, 0.1, 3),
            scale=uniform(0.9, 1.0, 3),
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
    decorate.transform(container, translation=[inner_size[0] / 2, 0, inner_size[1] / 2])

    lidar1 = MID360(
        "J1-1", num_frames=5, location=(0.0, 0, 1.0), rotation=(np.pi / 2, 0, 0)
    )
    lidar2 = MID360(
        "J1-2", num_frames=5, location=(0.0, 0, 1.0), rotation=(-np.pi / 2, 0, 0)
    )
    lidars = [lidar1, lidar2]
    pc, normals, visibility_mask = generate_lidar_clouds(cubes, [container], lidars)

    invisible_list = []
    visible_list = []
    for v, cube in zip(visibility_mask, cubes):
        if v < 0.5:
            invisible_list.append(cube)
        else:
            visible_list.append(cube)

    pc_noise = add_noise(pc, normals, 0.01)

    points_to_keep, points_to_remove = remove_points_near(
        visible_list, [container], pc, distance=0.03
    )

    butil.delete(invisible_list)
    cloud_mesh = create_pointcloud_mesh(points_to_keep, name="Cloud")

    output_dir = Path(f"output/container_{i:04}")
    shutil.rmtree(output_dir, ignore_errors=True)
    os.makedirs(output_dir, exist_ok=True)

    # write point cloud
    write_pcd_binary(str(output_dir / "cloud.pcd"), points_to_keep)
    write_box_json(str(output_dir / "boxes.json"), cubes)
    write_box_json(str(output_dir / "visible_boxes.json"), visible_list)
    # write container
    with open(str(output_dir / "container.json"), "w") as f:
        json.dump(
            {
                "length": inner_size[0],
                "width": inner_size[1],
                "height": inner_size[2],
            },
            f,
        )
    with butil.SelectObjects([container]):
        bpy.ops.export_mesh.stl(
            filepath=str(output_dir / "container.stl"), use_selection=True
        )
    butil.save_blend(str(output_dir / "scene.blend"))
