import bpy
import infinigen.core.util.blender as butil
from infinigen.core.placement.factory import AssetFactory
from infinigen.core.nodes.node_wrangler import Nodes, NodeWrangler
from infinigen.core.nodes import node_utils
from infinigen.core import surface


@node_utils.to_nodegroup(
    "nodegroup_wave_board", singleton=False, type="GeometryNodeTree"
)
def nodegroup_wave_board(nw: NodeWrangler):
    # Code generated using version 2.6.5 of the node_transpiler

    group_input = nw.new_node(
        Nodes.GroupInput,
        expose_input=[
            ("NodeSocketFloat", "length", 0.5000),
            ("NodeSocketFloat", "width", 0.5000),
            ("NodeSocketFloat", "wave_step", 0.5000),
            ("NodeSocketFloat", "wave_strength", 0.1000),
            ("NodeSocketInt", "index", 0),
        ],
    )

    multiply = nw.new_node(
        Nodes.Math,
        input_kwargs={0: group_input.outputs["length"]},
        attrs={"operation": "MULTIPLY"},
    )

    combine_xyz_1 = nw.new_node(Nodes.CombineXYZ, input_kwargs={"X": multiply})

    multiply_1 = nw.new_node(
        Nodes.VectorMath,
        input_kwargs={0: combine_xyz_1, 1: (-1.0000, -1.0000, -1.0000)},
        attrs={"operation": "MULTIPLY"},
    )

    combine_xyz_2 = nw.new_node(Nodes.CombineXYZ, input_kwargs={"X": multiply})

    curve_line = nw.new_node(
        Nodes.CurveLine,
        input_kwargs={"Start": multiply_1.outputs["Vector"], "End": combine_xyz_2},
    )

    multiply_2 = nw.new_node(
        Nodes.Math,
        input_kwargs={0: group_input.outputs["width"]},
        attrs={"operation": "MULTIPLY"},
    )

    combine_xyz_4 = nw.new_node(Nodes.CombineXYZ, input_kwargs={"X": multiply_2})

    multiply_3 = nw.new_node(
        Nodes.VectorMath,
        input_kwargs={0: combine_xyz_4, 1: (-1.0000, -1.0000, -1.0000)},
        attrs={"operation": "MULTIPLY"},
    )

    combine_xyz_3 = nw.new_node(Nodes.CombineXYZ, input_kwargs={"X": multiply_2})

    curve_line_1 = nw.new_node(
        Nodes.CurveLine,
        input_kwargs={"Start": multiply_3.outputs["Vector"], "End": combine_xyz_3},
    )

    curve_length = nw.new_node(Nodes.CurveLength, input_kwargs={"Curve": curve_line_1})

    divide = nw.new_node(
        Nodes.Math,
        input_kwargs={0: curve_length, 1: group_input.outputs["wave_step"]},
        attrs={"operation": "DIVIDE"},
    )

    multiply_4 = nw.new_node(
        Nodes.Math, input_kwargs={0: divide, 1: 4.0000}, attrs={"operation": "MULTIPLY"}
    )

    snap = nw.new_node(
        Nodes.Math, input_kwargs={0: multiply_4, 1: 4.0000}, attrs={"operation": "SNAP"}
    )

    add = nw.new_node(Nodes.Math, input_kwargs={0: snap, 1: 2.0000})

    resample_curve = nw.new_node(
        Nodes.ResampleCurve, input_kwargs={"Curve": curve_line_1, "Count": add}
    )

    spline_parameter = nw.new_node(Nodes.SplineParameter)

    add_1 = nw.new_node(
        Nodes.Math,
        input_kwargs={
            0: spline_parameter.outputs["Index"],
            1: group_input.outputs["index"],
        },
    )

    modulo = nw.new_node(
        Nodes.Math, input_kwargs={0: add_1, 1: 4.0000}, attrs={"operation": "MODULO"}
    )

    greater_than = nw.new_node(Nodes.Compare, input_kwargs={0: modulo, 1: 1.0000})

    combine_xyz = nw.new_node(
        Nodes.CombineXYZ, input_kwargs={"Y": group_input.outputs["wave_strength"]}
    )

    set_position = nw.new_node(
        Nodes.SetPosition,
        input_kwargs={
            "Geometry": resample_curve,
            "Selection": greater_than,
            "Offset": combine_xyz,
        },
    )

    curve_to_mesh = nw.new_node(
        Nodes.CurveToMesh,
        input_kwargs={"Curve": curve_line, "Profile Curve": set_position},
    )

    set_shade_smooth = nw.new_node(
        Nodes.SetShadeSmooth,
        input_kwargs={"Geometry": curve_to_mesh, "Shade Smooth": False},
    )

    group_output = nw.new_node(
        Nodes.GroupOutput,
        input_kwargs={"Geometry": set_shade_smooth},
        attrs={"is_active_output": True},
    )


@node_utils.to_nodegroup(
    "nodegroup_split_faces", singleton=False, type="GeometryNodeTree"
)
def nodegroup_split_faces(nw: NodeWrangler):
    # Code generated using version 2.6.5 of the node_transpiler

    group_input = nw.new_node(
        Nodes.GroupInput, expose_input=[("NodeSocketGeometry", "Geometry", None)]
    )

    normal = nw.new_node(Nodes.InputNormal)

    separate_xyz = nw.new_node(Nodes.SeparateXYZ, input_kwargs={"Vector": normal})

    greater_than = nw.new_node(
        Nodes.Compare, input_kwargs={0: separate_xyz.outputs["X"]}
    )

    separate_geometry = nw.new_node(
        Nodes.SeparateGeometry,
        input_kwargs={
            "Geometry": group_input.outputs["Geometry"],
            "Selection": greater_than,
        },
        attrs={"domain": "FACE"},
    )

    less_than = nw.new_node(
        Nodes.Compare,
        input_kwargs={0: separate_xyz.outputs["X"]},
        attrs={"operation": "LESS_THAN"},
    )

    separate_geometry_1 = nw.new_node(
        Nodes.SeparateGeometry,
        input_kwargs={
            "Geometry": separate_geometry.outputs["Inverted"],
            "Selection": less_than,
        },
        attrs={"domain": "FACE"},
    )

    separate_xyz_2 = nw.new_node(Nodes.SeparateXYZ, input_kwargs={"Vector": normal})

    greater_than_1 = nw.new_node(
        Nodes.Compare, input_kwargs={0: separate_xyz_2.outputs["Y"]}
    )

    separate_geometry_2 = nw.new_node(
        Nodes.SeparateGeometry,
        input_kwargs={
            "Geometry": separate_geometry_1.outputs["Inverted"],
            "Selection": greater_than_1,
        },
        attrs={"domain": "FACE"},
    )

    less_than_1 = nw.new_node(
        Nodes.Compare,
        input_kwargs={0: separate_xyz_2.outputs["Y"]},
        attrs={"operation": "LESS_THAN"},
    )

    separate_geometry_3 = nw.new_node(
        Nodes.SeparateGeometry,
        input_kwargs={
            "Geometry": separate_geometry_2.outputs["Inverted"],
            "Selection": less_than_1,
        },
        attrs={"domain": "FACE"},
    )

    separate_xyz_3 = nw.new_node(Nodes.SeparateXYZ, input_kwargs={"Vector": normal})

    greater_than_2 = nw.new_node(
        Nodes.Compare, input_kwargs={0: separate_xyz_3.outputs["Z"]}
    )

    separate_geometry_4 = nw.new_node(
        Nodes.SeparateGeometry,
        input_kwargs={
            "Geometry": separate_geometry_3.outputs["Inverted"],
            "Selection": greater_than_2,
        },
        attrs={"domain": "FACE"},
    )

    less_than_2 = nw.new_node(
        Nodes.Compare,
        input_kwargs={0: separate_xyz_3.outputs["Z"]},
        attrs={"operation": "LESS_THAN"},
    )

    separate_geometry_5 = nw.new_node(
        Nodes.SeparateGeometry,
        input_kwargs={
            "Geometry": separate_geometry_4.outputs["Inverted"],
            "Selection": less_than_2,
        },
        attrs={"domain": "FACE"},
    )

    group_output = nw.new_node(
        Nodes.GroupOutput,
        input_kwargs={
            "Face X+": separate_geometry.outputs["Selection"],
            "Face X-": separate_geometry_1.outputs["Selection"],
            "Face Y+": separate_geometry_2.outputs["Selection"],
            "Face Y-": separate_geometry_3.outputs["Selection"],
            "Face Z+": separate_geometry_4.outputs["Selection"],
            "Face Z-": separate_geometry_5.outputs["Selection"],
        },
        attrs={"is_active_output": True},
    )


@node_utils.to_nodegroup(
    "nodegroup_container_wall", singleton=False, type="GeometryNodeTree"
)
def nodegroup_container_wall(nw: NodeWrangler):
    # Code generated using version 2.6.5 of the node_transpiler

    group_input = nw.new_node(
        Nodes.GroupInput,
        expose_input=[
            ("NodeSocketVector", "inner_size", (0.0000, 0.0000, 0.0000)),
            ("NodeSocketVector", "thickness", (0.0000, 0.0000, 0.0000)),
            ("NodeSocketFloat", "wave_step", 0.5000),
            ("NodeSocketFloat", "wave_strength", 0.5000),
        ],
    )

    separate_xyz = nw.new_node(
        Nodes.SeparateXYZ, input_kwargs={"Vector": group_input.outputs["inner_size"]}
    )

    separate_xyz_1 = nw.new_node(
        Nodes.SeparateXYZ, input_kwargs={"Vector": group_input.outputs["thickness"]}
    )

    multiply = nw.new_node(
        Nodes.Math,
        input_kwargs={
            0: separate_xyz_1.outputs["Y"],
            1: group_input.outputs["wave_strength"],
        },
        attrs={"operation": "MULTIPLY"},
    )

    wave_board = nw.new_node(
        nodegroup_wave_board().name,
        input_kwargs={
            "length": separate_xyz.outputs["Z"],
            "width": separate_xyz.outputs["X"],
            "wave_step": group_input.outputs["wave_step"],
            "wave_strength": multiply,
        },
    )

    multiply_1 = nw.new_node(
        Nodes.Math,
        input_kwargs={0: separate_xyz.outputs["Y"]},
        attrs={"operation": "MULTIPLY"},
    )

    combine_xyz = nw.new_node(Nodes.CombineXYZ, input_kwargs={"Y": multiply_1})

    transform_geometry_3 = nw.new_node(
        Nodes.Transform,
        input_kwargs={
            "Geometry": wave_board,
            "Translation": combine_xyz,
            "Rotation": (1.5708, 1.5708, 0.0000),
        },
    )

    transform_geometry_4 = nw.new_node(
        Nodes.Transform,
        input_kwargs={
            "Geometry": transform_geometry_3,
            "Scale": (1.0000, -1.0000, 1.0000),
        },
    )

    multiply_2 = nw.new_node(
        Nodes.Math,
        input_kwargs={
            0: separate_xyz_1.outputs["Z"],
            1: group_input.outputs["wave_strength"],
        },
        attrs={"operation": "MULTIPLY"},
    )

    wave_board_1 = nw.new_node(
        nodegroup_wave_board().name,
        input_kwargs={
            "length": separate_xyz.outputs["Y"],
            "width": separate_xyz.outputs["X"],
            "wave_step": group_input.outputs["wave_step"],
            "wave_strength": multiply_2,
        },
    )

    transform_geometry_5 = nw.new_node(
        Nodes.Transform,
        input_kwargs={"Geometry": wave_board_1, "Rotation": (3.1416, 0.0000, 1.5708)},
    )

    multiply_3 = nw.new_node(
        Nodes.Math,
        input_kwargs={0: separate_xyz.outputs["Z"]},
        attrs={"operation": "MULTIPLY"},
    )

    combine_xyz_1 = nw.new_node(Nodes.CombineXYZ, input_kwargs={"Z": multiply_3})

    transform_geometry_6 = nw.new_node(
        Nodes.Transform,
        input_kwargs={
            "Geometry": transform_geometry_5,
            "Translation": combine_xyz_1,
            "Scale": (1.0000, -1.0000, 1.0000),
        },
    )

    multiply_4 = nw.new_node(
        Nodes.Math,
        input_kwargs={
            0: separate_xyz_1.outputs["X"],
            1: group_input.outputs["wave_strength"],
        },
        attrs={"operation": "MULTIPLY"},
    )

    wave_board_2 = nw.new_node(
        nodegroup_wave_board().name,
        input_kwargs={
            "length": separate_xyz.outputs["Z"],
            "width": separate_xyz.outputs["Y"],
            "wave_step": group_input.outputs["wave_step"],
            "wave_strength": multiply_4,
        },
    )

    transform_geometry_7 = nw.new_node(
        Nodes.Transform,
        input_kwargs={"Geometry": wave_board_2, "Rotation": (3.1416, 1.5708, 0.0000)},
    )

    multiply_5 = nw.new_node(
        Nodes.Math,
        input_kwargs={0: separate_xyz.outputs["X"]},
        attrs={"operation": "MULTIPLY"},
    )

    combine_xyz_2 = nw.new_node(Nodes.CombineXYZ, input_kwargs={"X": multiply_5})

    transform_geometry_8 = nw.new_node(
        Nodes.Transform,
        input_kwargs={"Geometry": transform_geometry_7, "Translation": combine_xyz_2},
    )

    join_geometry = nw.new_node(
        Nodes.JoinGeometry,
        input_kwargs={
            "Geometry": [
                transform_geometry_3,
                transform_geometry_4,
                transform_geometry_6,
                transform_geometry_8,
            ]
        },
    )

    group_output = nw.new_node(
        Nodes.GroupOutput,
        input_kwargs={"Geometry": join_geometry},
        attrs={"is_active_output": True},
    )


@node_utils.to_nodegroup(
    "nodegroup_container_framework", singleton=False, type="GeometryNodeTree"
)
def nodegroup_container_framework(nw: NodeWrangler):
    # Code generated using version 2.6.5 of the node_transpiler

    group_input = nw.new_node(
        Nodes.GroupInput,
        expose_input=[
            ("NodeSocketVector", "inner_size", (0.0000, 0.0000, 0.0000)),
            ("NodeSocketVector", "thickness", (0.0000, 0.0000, 0.0000)),
        ],
    )

    scale = nw.new_node(
        Nodes.VectorMath,
        input_kwargs={0: group_input.outputs["thickness"], "Scale": 2.0000},
        attrs={"operation": "SCALE"},
    )

    add = nw.new_node(
        Nodes.VectorMath,
        input_kwargs={0: group_input.outputs["inner_size"], 1: scale.outputs["Vector"]},
    )

    cube_1 = nw.new_node(Nodes.MeshCube, input_kwargs={"Size": add.outputs["Vector"]})

    cube = nw.new_node(
        Nodes.MeshCube, input_kwargs={"Size": group_input.outputs["inner_size"]}
    )

    transform_geometry_1 = nw.new_node(
        Nodes.Transform,
        input_kwargs={
            "Geometry": cube.outputs["Mesh"],
            "Scale": (1.0000, 100.0000, 1.0000),
        },
    )

    transform_geometry = nw.new_node(
        Nodes.Transform,
        input_kwargs={
            "Geometry": cube.outputs["Mesh"],
            "Scale": (100.0000, 1.0000, 1.0000),
        },
    )

    transform_geometry_2 = nw.new_node(
        Nodes.Transform,
        input_kwargs={
            "Geometry": cube.outputs["Mesh"],
            "Scale": (1.0000, 1.0000, 100.0000),
        },
    )

    difference = nw.new_node(
        Nodes.MeshBoolean,
        input_kwargs={
            "Mesh 1": cube_1.outputs["Mesh"],
            "Mesh 2": [transform_geometry_1, transform_geometry, transform_geometry_2],
        },
    )

    split_faces = nw.new_node(
        nodegroup_split_faces().name, input_kwargs={"Geometry": cube.outputs["Mesh"]}
    )

    join_geometry = nw.new_node(
        Nodes.JoinGeometry,
        input_kwargs={
            "Geometry": [difference.outputs["Mesh"], split_faces.outputs["Face Z-"]]
        },
    )

    group_output = nw.new_node(
        Nodes.GroupOutput,
        input_kwargs={"Geometry": join_geometry},
        attrs={"is_active_output": True},
    )


def geometry_nodes(nw: NodeWrangler):
    # Code generated using version 2.6.5 of the node_transpiler

    group_input = nw.new_node(
        Nodes.GroupInput,
        expose_input=[
            ("NodeSocketVectorTranslation", "inner_size", (1.0000, 1.0000, 1.0000)),
            ("NodeSocketVectorTranslation", "thickness", (0.0000, 0.0000, 0.0000)),
            ("NodeSocketFloat", "wave_step", 0.5000),
            ("NodeSocketFloat", "wave_strength", 0.1000),
        ],
    )

    container_framework = nw.new_node(
        nodegroup_container_framework().name,
        input_kwargs={
            "inner_size": group_input.outputs["inner_size"],
            "thickness": group_input.outputs["thickness"],
        },
    )

    container_wall = nw.new_node(
        nodegroup_container_wall().name,
        input_kwargs={
            "inner_size": group_input.outputs["inner_size"],
            "thickness": group_input.outputs["thickness"],
            "wave_step": group_input.outputs["wave_step"],
            "wave_strength": group_input.outputs["wave_strength"],
        },
    )

    join_geometry = nw.new_node(
        Nodes.JoinGeometry,
        input_kwargs={"Geometry": [container_framework, container_wall]},
    )

    group_output = nw.new_node(
        Nodes.GroupOutput,
        input_kwargs={"Geometry": join_geometry},
        attrs={"is_active_output": True},
    )


class ContainerFactory(AssetFactory):
    def __init__(self, factory_seed=None):
        super().__init__(factory_seed)

    def create_asset(self, **params) -> bpy.types.Object:
        container = butil.spawn_cube(name="container")
        mod = surface.add_geomod(container, geometry_nodes)

        # parameters
        inner_size = params.pop("inner_size", (6.0, 2.0, 2.0))
        thickness = params.pop("thickness", (0.2, 0.2, 0.2))
        wave_step = params.pop("wave_step", 0.4)
        wave_strength = params.pop("wave_strength", 0.5)
        surface.set_geomod_inputs(
            mod,
            {
                "inner_size": inner_size,
                "thickness": thickness,
                "wave_step": wave_step,
                "wave_strength": wave_strength,
            },
        )
        # butil.apply_modifiers(container, mod)
        return container
