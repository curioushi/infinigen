import bpy
import bmesh
import struct
import json
import tempfile
import numpy as np
import subprocess
from subprocess import PIPE
from typing import List
import infinigen.core.util.blender as butil
import infinigen.assets.utils.decorate as decorate


class Lidar:
    def __init__(self, name, model, num_frames=None, location=None, rotation=None):
        self.name = name
        self.model = model
        self.num_frames = num_frames
        self.empty = butil.spawn_empty(self.name, disp_type="ARROWS", s=0.2)
        decorate.transform(self.empty, translation=location, rotation=rotation)

    def get_info(self):
        return {
            "tf": np.array(self.empty.matrix_world.normalized()).astype(float).tolist(),
            "model": self.model,
            "num_frames": self.num_frames,
        }


class MID360(Lidar):
    def __init__(self, name, num_frames=1, location=None, rotation=None):
        super().__init__(name, "LIVOX-MID-360", num_frames, location, rotation)


def load_pcd_binary(filepath):
    with open(filepath, "rb") as f:
        while True:
            line = f.readline().strip().decode("utf-8")
            if line.startswith("DATA"):
                break
        data = f.read()

    point_size = 3 * 4
    num_points = len(data) // point_size

    points = np.zeros((num_points, 3), dtype=np.float32)
    for i in range(num_points):
        x, y, z = struct.unpack_from("fff", data, offset=i * point_size)
        points[i] = [x, y, z]

    return points


def create_pointcloud_mesh(points):
    mesh = bpy.data.meshes.new(name="PointCloudMesh")
    obj = bpy.data.objects.new("PointCloud", mesh)
    bpy.context.collection.objects.link(obj)

    bm = bmesh.new()
    for v in points:
        bm.verts.new(v)
    bm.to_mesh(mesh)
    bm.free()

    obj.display_type = "WIRE"
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    return obj


def generate_lidar_clouds(cubes, scene_objs, lidars: List[Lidar]):
    def check_executable(executable):
        try:
            result = subprocess.run(["which", executable], stdout=PIPE, stderr=PIPE)
            if result.returncode == 0:
                return True
            else:
                return False
        except Exception as e:
            print(f"An error occurred: {e}")
            return False

    if not check_executable("simulate_lidar"):
        raise Exception("simulate_lidar is not installed.")

    # create temporary directory
    temp_dir = tempfile.mkdtemp()

    # create boxes.json
    data = []
    for cube in cubes:
        tf = np.array(cube.matrix_world.normalized()).astype(float)
        size = np.array(cube.scale).astype(float)
        data.append({"tf": tf.tolist(), "size": size.tolist()})
    with open(f"{temp_dir}/boxes.json", "w") as f:
        json.dump(data, f)

    # create lidars.json
    lidar_infos = [lidar.get_info() for lidar in lidars]
    with open(f"{temp_dir}/lidars.json", "w") as f:
        json.dump(lidar_infos, f)

    # create scene_mesh.stl
    with butil.SelectObjects(scene_objs):
        bpy.ops.export_mesh.stl(
            filepath=f"{temp_dir}/scene_mesh.stl", use_selection=True
        )

    # run simulate_lidar
    output_pcd = f"{temp_dir}/clouds.pcd"
    subprocess.run(
        ["simulate_lidar", "-i", temp_dir, "-o", output_pcd],
        stdout=PIPE,
        stderr=PIPE,
    )

    pc = load_pcd_binary(output_pcd)
    return create_pointcloud_mesh(pc)
