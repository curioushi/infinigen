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


def create_gripper(name, filepath):
    with open(filepath, "r") as f:
        data = json.load(f)
        tf_flange_tip = np.array(data["tf_flange_tip"])
        objects = []
        for i, group in enumerate(data["suction_groups"]):
            rect = np.array(group["shape"])
            mins, maxs = rect[0], rect[1]
            polygon = np.array(
                [mins, [maxs[0], mins[1]], maxs, [mins[0], maxs[1]], mins]
            )
            coords = np.hstack((polygon, np.zeros((polygon.shape[0], 1))))
            coords = coords @ tf_flange_tip[:3, :3].T + tf_flange_tip[:3, 3]
            suction_group = create_polygon(f"SuctionGroup_{i}", coords)
            objects.append(suction_group)
        objects.append(
            create_polygon("LinkFlangeTip", np.array([[0, 0, 0], tf_flange_tip[:3, 3]]))
        )

        with butil.SelectObjects(objects):
            bpy.ops.object.convert(target="MESH")

        suction_groups = []
        for obj in objects[:-1]:
            suction_group = obj.copy()
            suction_group.data = obj.data.copy()
            suction_groups.append(suction_group)

        with butil.SelectObjects(objects):
            bpy.ops.object.join()

        gripper = objects[0]
        gripper.name = name
        return gripper, suction_groups
