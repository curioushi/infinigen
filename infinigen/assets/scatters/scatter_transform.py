import bpy
import bmesh
import mathutils
from numpy.random import uniform, normal, randint
import infinigen.core.util.blender as butil
from infinigen.core.nodes.node_wrangler import Nodes, NodeWrangler
from infinigen.core.nodes import node_utils
from infinigen.core.util.color import color_category
from infinigen.core import surface


@node_utils.to_nodegroup(
    "nodegroup_geometry_with_rotation_attr", singleton=False, type="GeometryNodeTree"
)
def nodegroup_geometry_with_rotation_attr(nw: NodeWrangler):
    # Code generated using version 2.6.5 of the node_transpiler

    group_input = nw.new_node(
        Nodes.GroupInput,
        expose_input=[
            ("NodeSocketGeometry", "Geometry", None),
            ("NodeSocketGeometry", "Rotation", None),
        ],
    )

    position_1 = nw.new_node(Nodes.InputPosition)

    store_named_attribute = nw.new_node(
        Nodes.StoreNamedAttribute,
        input_kwargs={
            "Geometry": group_input.outputs["Rotation"],
            "Name": "rotation",
            3: position_1,
        },
        attrs={"data_type": "FLOAT_VECTOR"},
    )

    join_geometry = nw.new_node(
        Nodes.JoinGeometry,
        input_kwargs={
            "Geometry": [store_named_attribute, group_input.outputs["Geometry"]]
        },
    )

    named_attribute = nw.new_node(
        Nodes.NamedAttribute,
        input_kwargs={"Name": "rotation"},
        attrs={"data_type": "FLOAT_VECTOR"},
    )

    capture_attribute_1 = nw.new_node(
        Nodes.CaptureAttribute,
        input_kwargs={
            "Geometry": join_geometry,
            1: named_attribute.outputs["Attribute"],
        },
        attrs={"data_type": "FLOAT_VECTOR"},
    )

    index = nw.new_node(Nodes.Index)

    domain_size = nw.new_node(
        Nodes.DomainSize, input_kwargs={"Geometry": join_geometry}
    )

    divide = nw.new_node(
        Nodes.Math,
        input_kwargs={0: domain_size.outputs["Point Count"], 1: 2.0000},
        attrs={"operation": "DIVIDE"},
    )

    add = nw.new_node(Nodes.Math, input_kwargs={0: index, 1: divide})

    round = nw.new_node(Nodes.Math, input_kwargs={0: add}, attrs={"operation": "ROUND"})

    sample_index = nw.new_node(
        Nodes.SampleIndex,
        input_kwargs={
            "Geometry": capture_attribute_1.outputs["Geometry"],
            3: capture_attribute_1.outputs["Attribute"],
            "Index": round,
        },
        attrs={"data_type": "FLOAT_VECTOR"},
    )

    capture_attribute_2 = nw.new_node(
        Nodes.CaptureAttribute,
        input_kwargs={
            "Geometry": capture_attribute_1.outputs["Geometry"],
            1: sample_index.outputs[2],
        },
        attrs={"data_type": "FLOAT_VECTOR"},
    )

    index_1 = nw.new_node(Nodes.Index)

    domain_size = nw.new_node(
        Nodes.DomainSize,
        input_kwargs={"Geometry": group_input.outputs["Geometry"]},
    )

    less_than = nw.new_node(
        Nodes.Compare,
        input_kwargs={2: index_1, 3: domain_size.outputs["Point Count"]},
        attrs={"operation": "LESS_THAN", "data_type": "INT"},
    )

    separate_geometry = nw.new_node(
        Nodes.SeparateGeometry,
        input_kwargs={
            "Geometry": capture_attribute_2.outputs["Geometry"],
            "Selection": less_than,
        },
    )

    group_output = nw.new_node(
        Nodes.GroupOutput,
        input_kwargs={
            "Geometry": separate_geometry.outputs["Selection"],
            "Rotation": capture_attribute_2.outputs["Attribute"],
        },
        attrs={"is_active_output": True},
    )


def geometry_nodes(nw: NodeWrangler):
    # Code generated using version 2.6.5 of the node_transpiler

    group_input = nw.new_node(
        Nodes.GroupInput,
        expose_input=[
            ("NodeSocketGeometry", "Geometry", None),
            ("NodeSocketObject", "InputGeometry", None),
            ("NodeSocketObject", "PositionGeometry", None),
            ("NodeSocketObject", "RotationGeometry", None),
        ],
    )

    object_info_1 = nw.new_node(
        Nodes.ObjectInfo,
        input_kwargs={"Object": group_input.outputs["PositionGeometry"]},
    )

    object_info_2 = nw.new_node(
        Nodes.ObjectInfo,
        input_kwargs={"Object": group_input.outputs["RotationGeometry"]},
    )

    geometrywithrotationattr = nw.new_node(
        nodegroup_geometry_with_rotation_attr().name,
        input_kwargs={
            "Geometry": object_info_1.outputs["Geometry"],
            "Rotation": object_info_2.outputs["Geometry"],
        },
    )

    object_info = nw.new_node(
        Nodes.ObjectInfo,
        input_kwargs={
            "Object": group_input.outputs["InputGeometry"],
            "As Instance": True,
        },
    )

    instance_on_points = nw.new_node(
        Nodes.InstanceOnPoints,
        input_kwargs={
            "Points": geometrywithrotationattr.outputs["Geometry"],
            "Instance": object_info.outputs["Geometry"],
            "Rotation": geometrywithrotationattr.outputs["Rotation"],
        },
    )

    realize_instances = nw.new_node(
        Nodes.RealizeInstances, input_kwargs={"Geometry": instance_on_points}
    )

    group_output = nw.new_node(
        Nodes.GroupOutput,
        input_kwargs={"Geometry": realize_instances},
        attrs={"is_active_output": True},
    )


def create_points(points, name=None):
    name = name or "Points"
    mesh = bpy.data.meshes.new(name="PointsMesh")
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)

    bm = bmesh.new()
    for v in points:
        bm.verts.new(v)
    bm.to_mesh(mesh)
    bm.free()
    return obj


def spawn(input_geo, positions, rotations, name=None):
    plane = butil.spawn_plane()
    position_geo = create_points(positions, name="Positions")
    rotation_geo = create_points(rotations, name="Rotations")
    mod = surface.add_geomod(plane, geometry_nodes, selection=None, attributes=[])
    surface.set_geomod_inputs(
        mod,
        {
            "InputGeometry": input_geo,
            "PositionGeometry": position_geo,
            "RotationGeometry": rotation_geo,
        },
    )
    butil.apply_modifiers(plane, mod)
    if name is not None:
        plane.name = name
    butil.delete([position_geo, rotation_geo])
    return plane
