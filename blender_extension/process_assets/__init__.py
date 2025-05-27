import bpy, mathutils
import struct
import numpy as np

def get_loop_colors(mesh, assigned_materials):
    material_loop_colors = {}
    color_attributes = mesh.color_attributes
    for material_index, material_group in assigned_materials.items():
        if material_group["color_attribute_name"] != None:
            color_attribute = color_attributes.get(material_group["color_attribute_name"])
            if color_attribute:
                material_loop_colors[material_index] = color_attribute.data
            else:
                all_color_attributes = color_attributes.values()
                material_loop_colors[material_index] = all_color_attributes[0].data if len(all_color_attributes) > 0 else None

    return material_loop_colors

def output_socket_is_connected(output_socket):
    for link in output_socket.links:
        if link.is_valid and (not link.is_muted) and node_is_connected(link.to_node, link.to_socket):
            return True
    return False

def node_is_connected(node, input_socket):
    if type(node) is bpy.types.ShaderNodeOutputMaterial:
        return node.is_active_output
            
    if node.mute:
        for internal_link in node.internal_links:
            if internal_link.is_valid and (internal_link.from_socket == input_socket):
                if output_socket_is_connected(internal_link.to_socket):
                    return True
    else:
        for output_socket in node.outputs:
            if output_socket_is_connected(output_socket):
                return True
    return False

def process_materials(material_slots, send_images):
    assigned_materials = {}
    for material_slot in material_slots:
        material = material_slot.material
        if material and material.node_tree:
            color_attribute_name = None
            image_node = None
            bsdf_node = None
            for node in material.node_tree.nodes:
                match type(node):
                    case bpy.types.ShaderNodeTexImage:
                        if output_socket_is_connected(node.outputs.get("Color")) and node.image:
                            image_node = node
                    case bpy.types.ShaderNodeVertexColor:
                        if output_socket_is_connected(node.outputs.get("Color")):
                            color_attribute_name = node.layer_name
                    case bpy.types.ShaderNodeBsdfPrincipled:
                        if output_socket_is_connected(node.outputs.get("BSDF")):
                            bsdf_node = node

            
            use_image_transparency = False
            if image_node and bsdf_node:
                for link in bsdf_node.inputs.get("Alpha").links:
                    if link.is_valid and (not link.is_muted) and (link.from_node == image_node):
                        use_image_transparency = True
                        break

            assigned_materials[material_slot.slot_index] = {
                "color_attribute_name": color_attribute_name, 
                "image_hash": process_image(image_node.image, send_images) if image_node else None,
                "alpha": bsdf_node.inputs.get("Alpha").default_value if bsdf_node else None,
                "use_image_transparency": use_image_transparency
            }

    if len(assigned_materials) == 0:
        assigned_materials[0] = {
            "color_attribute_name": None, 
            "image_hash": None,
            "alpha": 1,
            "use_image_transparency": False
        }
    return assigned_materials