import bpy
from mathutils import Matrix
import numpy as np
import json
import infinigen.core.util.blender as butil


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
    def __init__(self, filepath):
        self.tf_flange_tip = np.eye(4)
        self.suction_groups = []

        with open(filepath, "r") as f:
            data = json.load(f)
            self.tf_flange_tip = np.array(data["tf_flange_tip"])
            self.suction_groups = data["suction_groups"]
            flange = butil.spawn_empty("Gripper", disp_type="ARROWS", s=0.1)
            tip = butil.spawn_empty("Tip", disp_type="ARROWS", s=0.1)
            tip.matrix_world = Matrix(self.tf_flange_tip)
            butil.parent_to(tip, flange)
            group_shapes = []
            for i, group in enumerate(self.suction_groups):
                polygon = np.array(group["shape"])
                coords = np.hstack((polygon, np.zeros((polygon.shape[0], 1))))
                coords = coords @ self.tf_flange_tip[:3, :3].T + self.tf_flange_tip[:3, 3]
                group_shape = create_polygon(
                    f"SuctionGroup_{i}", coords
                )
                group_shapes.append(group_shape)
            with butil.SelectObjects(group_shapes):
                bpy.ops.object.join()
            group_shape = group_shapes[0]
            group_shape.name = "SuctionGroups"
            butil.parent_to(group_shape, tip)
            self.object = flange
            
