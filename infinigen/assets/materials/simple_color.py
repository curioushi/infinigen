import bpy
import infinigen.assets.utils.decorate as decorate


def simple_color(name, color):
    if name in bpy.data.materials:
        return bpy.data.materials[name]
    material = bpy.data.materials.new(name=name)
    material.use_nodes = True
    nodes = material.node_tree.nodes
    for node in nodes:
        nodes.remove(node)

    bsdf_node = nodes.new(type="ShaderNodeBsdfPrincipled")
    bsdf_node.location = (0, 0)

    output_node = nodes.new(type="ShaderNodeOutputMaterial")
    output_node.location = (200, 0)

    links = material.node_tree.links
    links.new(bsdf_node.outputs["BSDF"], output_node.inputs["Surface"])

    bsdf_node.inputs["Base Color"].default_value = color
    bsdf_node.inputs["Roughness"].default_value = 0.5
    return material


def apply(obj, color_name):
    color_map = {
        "RED": (1, 0, 0, 1),
        "GREEN": (0, 1, 0, 1),
        "BLUE": (0, 0, 1, 1),
    }
    if color_name in color_map:
        color = color_map[color_name]
    else:
        raise ValueError(f"Color {color_name} not supported")
    mat = simple_color(color_name, color)
    decorate.assign_material(obj, mat)
