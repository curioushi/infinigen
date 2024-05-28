import bpy
import infinigen.core.util.blender as butil
from infinigen.core.nodes.node_wrangler import Nodes, NodeWrangler
from infinigen.core import surface
from infinigen.core.placement.factory import AssetFactory

import bpy
import bpy
import mathutils
from numpy.random import uniform, normal, randint
from infinigen.core.nodes.node_wrangler import Nodes, NodeWrangler
from infinigen.core.nodes import node_utils
from infinigen.core.util.color import color_category
from infinigen.core import surface


@node_utils.to_nodegroup(
    "nodegroup_node_group", singleton=False, type="GeometryNodeTree"
)
def nodegroup_node_group(nw: NodeWrangler):
    # Code generated using version 2.6.5 of the node_transpiler

    group_input = nw.new_node(
        Nodes.GroupInput,
        expose_input=[
            ("NodeSocketVectorTranslation", "Inner Size", (1.0000, 1.0000, 1.0000)),
            ("NodeSocketFloat", "Thickness", 0.0000),
        ],
    )

    cube = nw.new_node(
        Nodes.MeshCube, input_kwargs={"Size": group_input.outputs["Inner Size"]}
    )

    multiply = nw.new_node(
        Nodes.Math,
        input_kwargs={0: group_input.outputs["Thickness"]},
        attrs={"operation": "MULTIPLY"},
    )

    combine_xyz = nw.new_node(
        Nodes.CombineXYZ,
        input_kwargs={
            "X": multiply,
            "Y": group_input.outputs["Thickness"],
            "Z": group_input.outputs["Thickness"],
        },
    )

    add = nw.new_node(
        Nodes.VectorMath,
        input_kwargs={0: group_input.outputs["Inner Size"], 1: combine_xyz},
    )

    cube_1 = nw.new_node(Nodes.MeshCube, input_kwargs={"Size": add.outputs["Vector"]})

    multiply_1 = nw.new_node(
        Nodes.Math, input_kwargs={0: multiply}, attrs={"operation": "MULTIPLY"}
    )

    combine_xyz_1 = nw.new_node(Nodes.CombineXYZ, input_kwargs={"X": multiply_1})

    transform_geometry = nw.new_node(
        Nodes.Transform,
        input_kwargs={"Geometry": cube_1.outputs["Mesh"], "Translation": combine_xyz_1},
    )

    group_output = nw.new_node(
        Nodes.GroupOutput,
        input_kwargs={
            "Inner Cube": cube.outputs["Mesh"],
            "Outer Cube": transform_geometry,
        },
        attrs={"is_active_output": True},
    )


def geometry_nodes(nw: NodeWrangler):
    # Code generated using version 2.6.5 of the node_transpiler

    group_input = nw.new_node(
        Nodes.GroupInput,
        expose_input=[
            ("NodeSocketVectorTranslation", "Inner Size", (1.0000, 1.0000, 1.0000)),
            ("NodeSocketFloat", "Thickness", 0.0000),
        ],
    )

    nodegroup = nw.new_node(
        nodegroup_node_group().name,
        input_kwargs={
            "Inner Size": group_input.outputs["Inner Size"],
            "Thickness": group_input.outputs["Thickness"],
        },
    )

    join_geometry = nw.new_node(
        Nodes.JoinGeometry,
        input_kwargs={
            "Geometry": [
                nodegroup.outputs["Inner Cube"],
                nodegroup.outputs["Outer Cube"],
            ]
        },
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
        container = butil.spawn_cube()
        mod = surface.add_geomod(container, geometry_nodes)
        surface.set_geomod_inputs(mod, {"Inner Size": (6, 2, 2), "Thickness": 0.2})
        return container
