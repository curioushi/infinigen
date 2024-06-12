import os
from typing import List
import json
import bpy
import numpy as np
from mathutils import Matrix

from infinigen.assets.robots.robot import Action
from .robot import Robot, ActionRemoveObjects
from infinigen.assets.robots.gripper import create_gripper
import infinigen.assets.robots.motion as motion
import infinigen.core.util.blender as butil
import infinigen.assets.materials.simple_color as simple_color
from infinigen.assets.scatters import scatter_transform
from infinigen.assets.lidars import (
    MID360,
    generate_lidar_clouds,
    add_noise,
    remove_points_near,
    create_pointcloud_mesh,
)


ROCKYONE = None


def get_rockyone():
    global ROCKYONE
    if ROCKYONE is None:
        ROCKYONE = RockyOne()
    return ROCKYONE


class RockyOne(Robot):
    def __init__(self):
        super().__init__()
        butil.delete_collection(butil.get_collection("Robot"))
        self.robot_collection = butil.get_collection("Robot")
        self.base_link = butil.spawn_empty("base_link", disp_type="ARROWS", s=0.5)
        self.lidar_j1_left = MID360(
            "lidar_j1_left",
            num_frames=5,
            location=(0.0, 0, 1.0),
            rotation=(-np.pi / 2, 0, 0),
        )
        self.lidar_j1_right = MID360(
            "lidar_j1_right",
            num_frames=5,
            location=(0.0, 0, 1.0),
            rotation=(np.pi / 2, 0, 0),
        )
        self.gripper_filepath = (
            "/home/shq/Projects/mycode/resolve_collision/data/pick_plan/gripper.json"
        )
        if not os.path.exists(self.gripper_filepath):
            raise Exception("Gripper file not found")
        butil.parent_to(self.lidar_j1_left.object, self.base_link)
        butil.parent_to(self.lidar_j1_right.object, self.base_link)
        self.lidars = [self.lidar_j1_left, self.lidar_j1_right]

        self.perception_result = None
        self.actions_result = None

        butil.group_in_collection([self.base_link], "Robot")

    def perception(self):
        with butil.CollectionVisibility("GT World"):
            gt_world = butil.get_collection("GT World")
            cubes = [obj for obj in gt_world.objects if "CUBE" in obj.name.upper()]
            container = [
                obj for obj in gt_world.objects if "CONTAINER" in obj.name.upper()
            ][0]

            pc, normals, visibility_mask = generate_lidar_clouds(
                cubes, [container], self.lidars
            )
            invisible_list = []
            visible_list = []
            for v, cube in zip(visibility_mask, cubes):
                if v < 0.5:
                    cube["visible"] = 0
                    invisible_list.append(cube)
                else:
                    cube["visible"] = 1
                    visible_list.append(cube)
            pc_noise = add_noise(pc, normals, 0.00)
            points_to_keep, points_to_remove = remove_points_near(
                visible_list, None, pc_noise, distance=0.001
            )
            cloud_mesh = create_pointcloud_mesh(points_to_keep, name="Cloud")

            # delete previous perception world
            perception_world = butil.get_collection("Perception World")
            butil.delete_collection(perception_world)

            # create new perception world
            perception_list = []
            for cube in visible_list:
                new_cube = cube.copy()
                new_cube.data = cube.data.copy()
                new_cube["link_name"] = cube.name
                perception_list.append(new_cube)
                butil.group_in_collection([new_cube], name="Perception World")
            butil.group_in_collection([cloud_mesh], "Perception World")

            self.perception_result = {
                "cubes": perception_list,
                "container": container,
                "cloud": cloud_mesh,
            }
        return self.perception_result

    def dump_perception(self, output_dir):
        if self.perception_result is None:
            raise Exception("No perception result to dump")

        data = []
        for cube in self.perception_result["cubes"]:
            data.append(
                {
                    "tf": np.array(cube.matrix_world.normalized())
                    .astype(float)
                    .tolist(),
                    "cuboid": np.array(cube.scale).astype(float).tolist(),
                }
            )
        with open(f"{output_dir}/boxes.json", "w") as f:
            json.dump(data, f)

    def motion_planning(self):
        # initialize planning world
        perception_world = butil.get_collection("Perception World")
        planning_world = butil.get_collection("Planning World")
        butil.delete_collection(planning_world)
        planning_world = butil.get_collection("Planning World")
        for obj in perception_world.objects:
            new_obj = obj.copy()
            new_obj.data = obj.data.copy()
            butil.group_in_collection([new_obj], "Planning World")

        # do motion planning
        cubes = [obj for obj in planning_world.objects if "CUBE" in obj.name.upper()]
        motion.align_axis(cubes)
        pickable_mask = motion.pickable(cubes)
        pick_plans = motion.pick_plan(
            cubes, pickable_mask, self.gripper_filepath, max_payload=35.0, dsafe=0.0
        )
        pickable_mask = [False] * len(pickable_mask)
        for pick_plan in pick_plans:
            pickable_mask[pick_plan['main_box_index']] = True
        

        # visualize
        gripper, suction_groups = create_gripper("Gripper", self.gripper_filepath)
        gripper_poses = [Matrix(pp["tf_world_flange"]) for pp in pick_plans]
        suction_group_masks = np.array([pp["suction_group_mask"] for pp in pick_plans])
        positions = np.array(
            [gripper_pose.to_translation() for gripper_pose in gripper_poses]
        )
        rotations = np.array(
            [gripper_pose.to_euler() for gripper_pose in gripper_poses]
        )
        grippers = scatter_transform.spawn(gripper, positions, rotations, "Gripper")
        butil.group_in_collection([gripper, grippers], "Planning World")
        butil.delete([gripper])
        for i, (suction_group, suction_group_mask) in enumerate(
            zip(suction_groups, suction_group_masks.T)
        ):
            suction_positions = positions[suction_group_mask]
            suction_rotations = rotations[suction_group_mask]
            suctions = scatter_transform.spawn(
                suction_group, suction_positions, suction_rotations, "Suction"
            )
            butil.group_in_collection([suction_group, suctions], "Planning World")
        butil.delete(suction_groups)

        pickable_cubes = [
            cube for cube, pickable in zip(cubes, pickable_mask) if pickable
        ]
        simple_color.apply(pickable_cubes, "GREEN")

        # generate actions
        actions = []
        for cube, pickable in zip(self.perception_result["cubes"], pickable_mask):
            if pickable:
                world_cube = bpy.data.objects[cube["link_name"]]
                actions.append(ActionRemoveObjects([cube, world_cube]))
        self.actions_result = actions
        return self.actions_result

    def motion_execution(self, actions: List[Action] = None):
        if actions is None:
            actions = self.actions_result
        if actions is not None:
            for action in actions:
                action.execute()
        else:
            raise Exception("No actions to execute")
