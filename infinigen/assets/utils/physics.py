# Copyright (c) Princeton University.
# This source code is licensed under the BSD 3-Clause license found in the LICENSE file in the root directory of this source tree.

# Authors: Lingjie Mei


import bpy
import numpy as np
import json
import subprocess
from mathutils import Matrix
from subprocess import PIPE
import infinigen.core.util.blender as butil
from infinigen.core.util.logging import Suppress


def resolve_collision(cubes, min_bound=None, max_bound=None):
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

    if not check_executable("resolve_collision"):
        raise Exception("resolve_collision is not installed.")

    data = []
    for cube in cubes:
        tf = np.array(cube.matrix_world.normalized()).astype(float)
        size = np.array(cube.scale).astype(float)
        data.append({"tf": tf.tolist(), "cuboid": size.tolist()})
    with open("/tmp/stacking.json", "w") as f:
        json.dump(data, f)

    cmds = ["resolve_collision", "-i", "/tmp/stacking.json", "-o", "/tmp/stacking.json"]
    if min_bound is not None and max_bound is not None:
        cmds.extend(
            [
                "--min-bound=" + ",".join(map(str, min_bound)),
                "--max-bound=" + ",".join(map(str, max_bound)),
            ]
        )
    subprocess.run(cmds, stdout=PIPE, stderr=PIPE)

    with open("/tmp/stacking.json", "r") as f:
        data = json.load(f)

    for item, cube in zip(data, cubes):
        tf = Matrix(item["tf"])
        cube.matrix_world = tf
        cube.scale = item["cuboid"]


def free_fall(actives, passives, place_fn, t=100):
    height = 0.0
    for o in sorted(actives, key=lambda o: -o.dimensions[-1]):
        height = place_fn(o, height)
    with EnablePhysics(actives, passives):
        bpy.context.scene.frame_end = t
        with Suppress():
            bpy.ops.ptcache.bake_all(True)
        bpy.context.scene.frame_current = t
        with butil.SelectObjects(actives):
            bpy.ops.object.visual_transform_apply()


class EnablePhysics:

    def __init__(self, actives, passives):
        self.actives = actives
        self.passives = passives

    def __enter__(self):
        self.frame = bpy.context.scene.frame_current
        self.frame_start = bpy.context.scene.frame_end
        self.frame_end = bpy.context.scene.frame_start
        for a in self.actives:
            with butil.SelectObjects(a):
                bpy.ops.rigidbody.objects_add(type="ACTIVE")
                bpy.ops.rigidbody.mass_calculate()
                bpy.context.object.rigid_body.use_margin = True
                bpy.context.object.rigid_body.collision_margin = 0
        for p in self.passives:
            with butil.SelectObjects(p):
                bpy.ops.rigidbody.objects_add(type="PASSIVE")
                bpy.context.object.rigid_body.collision_shape = "MESH"
                bpy.context.object.rigid_body.use_margin = True
                bpy.context.object.rigid_body.collision_margin = 0

    def __exit__(self, *_):
        bpy.ops.rigidbody.world_remove()
        bpy.context.scene.frame_set(self.frame)
        bpy.context.scene.frame_start = self.frame_start
        bpy.context.scene.frame_end = self.frame_end
