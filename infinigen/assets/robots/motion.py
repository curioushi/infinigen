import json
import tempfile
import numpy as np
import subprocess
from mathutils import Matrix
from subprocess import PIPE


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
        data.append({"tf": tf.tolist(), "size": size.tolist()})
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
        stdout=PIPE,
        stderr=PIPE,
    )

    # read aligned.json
    with open(output_file, "r") as f:
        aligned_data = json.load(f)

    # apply transform
    for item, cube in zip(aligned_data, cubes):
        cube.matrix_world = Matrix(np.array(item["tf"]))
        cube.scale = item["size"]

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
        stdout=PIPE,
        stderr=PIPE,
    )

    # read aligned.json
    with open(output_file, "r") as f:
        pickable = json.load(f)

    return pickable

# def pick_plan(boxes, pickable_mask, gripper):
#     if not check_executable("pickable"):
#         raise Exception("pickable executable not found")
    
#     # create temporary directory
#     temp_dir = tempfile.mkdtemp()

#     input_boxes_file = f"{temp_dir}/boxes.json"
#     input_pickable_file = f"{temp_dir}/pickable.json"
#     input_gripper_file = f"{temp_dir}/gripper.json"