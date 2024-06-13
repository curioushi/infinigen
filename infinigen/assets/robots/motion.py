import json
import tempfile
import numpy as np
import subprocess
from mathutils import Matrix
from subprocess import PIPE
from infinigen.assets.lidars import write_pcd_binary


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


def write_cube_json(filepath, cubes):
    data = []
    for cube in cubes:
        tf = np.array(cube.matrix_world.normalized()).astype(float)
        size = np.array(cube.scale).astype(float)
        data.append({"tf": tf.tolist(), "cuboid": size.tolist()})
    with open(filepath, "w") as f:
        json.dump(data, f)


def align_axis(cubes):
    if not check_executable("align_axis"):
        raise Exception("align_axis executable not found")

    # create temporary directory
    temp_dir = tempfile.mkdtemp()

    input_file = f"{temp_dir}/boxes.json"
    output_file = f"{temp_dir}/aligned.json"

    # create boxes.json
    write_cube_json(input_file, cubes)

    # run align_axis
    subprocess.run(
        ["align_axis", "-i", input_file, "-o", output_file],
        stdout=None,
        stderr=None,
    )

    # read aligned.json
    with open(output_file, "r") as f:
        aligned_data = json.load(f)

    # apply transform
    for item, cube in zip(aligned_data, cubes):
        cube.matrix_world = Matrix(np.array(item["tf"]))
        cube.scale = item["cuboid"]

    return cubes


def pickable(cubes):
    if not check_executable("pickable"):
        raise Exception("pickable executable not found")

    # create temporary directory
    temp_dir = tempfile.mkdtemp()

    input_file = f"{temp_dir}/boxes.json"
    output_file = f"{temp_dir}/pickable.json"

    # create boxes.json
    write_cube_json(input_file, cubes)

    # run pickable
    subprocess.run(
        ["pickable", "-i", input_file, "-o", output_file],
        stdout=None,
        stderr=None,
    )

    # read aligned.json
    with open(output_file, "r") as f:
        pickable = json.load(f)

    return pickable


def pick_plan(boxes, pickable_mask, container, gripper_filepath, cloud=None, **kwargs):
    if not check_executable("pickable"):
        raise Exception("pickable executable not found")

    # create temporary directory
    temp_dir = tempfile.mkdtemp()

    input_boxes_file = f"{temp_dir}/boxes.json"
    write_cube_json(input_boxes_file, boxes)
    input_pickable_file = f"{temp_dir}/pickable.json"
    with open(input_pickable_file, "w") as f:
        json.dump(pickable_mask, f)
    input_container_file = f"{temp_dir}/container.json"
    with open(input_container_file, "w") as f:
        json.dump(container, f)
    input_options_file = f"{temp_dir}/options.json"
    with open(input_options_file, "w") as f:
        json.dump(kwargs, f)
    input_cloud_file = None
    if cloud is not None:
        input_cloud_file = f"{temp_dir}/cloud.pcd"
        write_pcd_binary(input_cloud_file, cloud)

    output_pick_plan_file = f"{temp_dir}/pick_plan.json"

    cmds = [
        "pick_plan",
        "--boxes",
        input_boxes_file,
        "--pickable",
        input_pickable_file,
        "--container",
        input_container_file,
        "--gripper",
        gripper_filepath,
        "--options",
        input_options_file,
        "--output",
        output_pick_plan_file,
    ]
    if cloud is not None:
        cmds.extend(["--cloud", input_cloud_file])
    subprocess.run(cmds, stderr=None, stdout=None)

    with open(output_pick_plan_file, "r") as f:
        pick_plan = json.load(f)

    return pick_plan
