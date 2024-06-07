import bpy
from mathutils import Matrix
import numpy as np
import json
import infinigen.core.util.blender as butil
import infinigen.assets.utils.decorate as decorate
import infinigen.assets.materials.simple_color as simple_color


def create_polygon(name, coords):
    curve_data = bpy.data.curves.new(name="PolygonCurve", type="CURVE")
    curve_data.dimensions = "3D"

    curve_object = bpy.data.objects.new(name=name, object_data=curve_data)
    bpy.context.collection.objects.link(curve_object)
    polyline = curve_data.splines.new("POLY")
    polyline.points.add(len(coords) - 1)

    for i, coord in enumerate(coords):
        x, y, z = coord
        polyline.points[i].co = (x, y, z, 1)
    return curve_object


class Gripper:
    def __init__(self, filepath=None):
        self.tf_flange_tip = None
        self.flange = None
        self.tip = None
        self.suction_groups = []

        if filepath is not None:
            self.load_from_file(filepath)

    def load_from_file(self, filepath):
        with open(filepath, "r") as f:
            data = json.load(f)
            tf_flange_tip = np.array(data["tf_flange_tip"])
            flange = butil.spawn_empty("Gripper", disp_type="ARROWS", s=0.1)
            tip = butil.spawn_empty("Tip", disp_type="ARROWS", s=0.1)
            tip.matrix_world = Matrix(tf_flange_tip)
            butil.parent_to(tip, flange)
            for i, group in enumerate(data["suction_groups"]):
                polygon = np.array(group["shape"])
                coords = np.hstack((polygon, np.zeros((polygon.shape[0], 1))))
                coords = coords @ tf_flange_tip[:3, :3].T + tf_flange_tip[:3, 3]
                suction_group = create_polygon(f"SuctionGroup_{i}", coords)
                suction_group.data.bevel_depth = 0.008
                butil.parent_to(suction_group, tip)
                self.suction_groups.append(suction_group)
            self.tf_flange_tip = tf_flange_tip
            self.tip = tip
            self.flange = flange

    def activate(self, suction_group_indices):
        for index in suction_group_indices:
            suction_group = self.suction_groups[index]
            simple_color.apply(suction_group, "RED")

    def deactivate(self):
        for suction_group in self.suction_groups:
            with butil.SelectObjects(suction_group):
                while len(suction_group.data.materials):
                    bpy.ops.object.material_slot_remove()

    def duplicate(self):
        new_gripper = Gripper()
        flange = self.flange.copy()
        tip = self.tip.copy()
        suction_groups = [sg.copy() for sg in self.suction_groups]
        for new_sg, sg in zip(suction_groups, self.suction_groups):
            new_sg.data = sg.data.copy()
            bpy.context.collection.objects.link(new_sg)
        bpy.context.collection.objects.link(flange)
        bpy.context.collection.objects.link(tip)

        butil.parent_to(tip, flange)
        for sg in suction_groups:
            butil.parent_to(sg, tip)

        new_gripper.flange = flange
        new_gripper.tip = tip
        new_gripper.suction_groups = suction_groups
        new_gripper.tf_flange_tip = self.tf_flange_tip

        return new_gripper

    def tip_to(self, tf_world_tip):
        tf_world_flange = tf_world_tip @ np.linalg.inv(self.tf_flange_tip)
        self.flange.matrix_world = Matrix(tf_world_flange)
