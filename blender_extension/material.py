import bpy, bl_ui, mathutils
import copy
from bpy_extras.node_utils import find_node_input
from . import utils, vertex_color

opaque_node_properties = {
    "ShaderNodeTexImage": {
        "properties": {
            "location": mathutils.Vector((30, -50)),
            "width": 240,
            "height": 100,
        },
        "inputs": {
            "Vector": { "enabled": False }
        },
        "outputs": {
            "Alpha": { "enabled": False }
        }
    },
    "ShaderNodeMix": {
        "properties": {
            "location": mathutils.Vector((320, -100)),
            "width": 140,
            "height": 100,
            "data_type": "RGBA",
            "blend_type": "MULTIPLY",
            "clamp_result": True,
            "clamp_factor": True,
            "factor_mode": "UNIFORM",
            "show_options": False,
        },
        "inputs": {
            "Factor_Float": {
                "enabled": False,
                "default_value": 1,
            },
        },
    },
    "ShaderNodeVertexColor": {
        "properties": {
            "location": mathutils.Vector((130, -300)),
            "width": 140,
            "height": 100,
            "layer_name": vertex_color.vertex_color_name
        },
        "outputs": {
            "Alpha": { "enabled": False }
        }
    },
    "ShaderNodeBsdfPrincipled": {
        "properties": {
            "location": mathutils.Vector((510, -80)),
            "width": 240,
            "height": 100,
        },
        "inputs": {
            "Metallic": {
                "enabled": False,
                "default_value": 0
            },
            "Roughness": {
                "enabled": False,
                "default_value": 1
            },
            "IOR": {
                "enabled": False,
                "default_value": 1
            },
            "Alpha": { "enabled": True },
            "Normal": { "enabled": False },
            "Weight": { "enabled": False },
            "Diffuse Roughness": { "enabled": False },
            "Subsurface Weight": { "enabled": False },
            "Subsurface Radius": { "enabled": False },
            "Subsurface Scale": { "enabled": False },
            "Subsurface IOR": { "enabled": False },
            "Subsurface Anisotropy": { "enabled": False },
            "Specular IOR Level": { "enabled": False },
            "Specular Tint": { "enabled": False },
            "Anisotropic": { "enabled": False },
            "Anisotropic Rotation": { "enabled": False },
            "Tangent": { "enabled": False },
            "Transmission Weight": { "enabled": False },
            "Coat Weight": { "enabled": False },
            "Coat Roughness": { "enabled": False },
            "Coat IOR": { "enabled": False },
            "Coat Tint": { "enabled": False },
            "Coat Normal": { "enabled": False },
            "Sheen Weight": { "enabled": False },
            "Sheen Roughness": { "enabled": False },
            "Sheen Tint": { "enabled": False },
            "Emission Color": { "enabled": False },
            "Emission Strength": { "enabled": False },
            "Thin Film Thickness": { "enabled": False },
            "Thin Film IOR": { "enabled": False },
        },
    },
    "ShaderNodeOutputMaterial": {
        "properties": {
            "location": mathutils.Vector((790, -80)),
            "width": 140,
            "height": 100,
            "target": "EEVEE",
            "show_options": False,
            "is_active_output": True,
        },
        "inputs": {
            "Volume": { "enabled": False },
            "Displacement": { "enabled": False },
            "Thickness": { "enabled": False },
        }
    },
}

transparent_node_properties = copy.deepcopy(opaque_node_properties)
transparent_node_properties.pop("ShaderNodeMix")
transparent_node_properties.pop("ShaderNodeVertexColor")
transparent_node_properties["ShaderNodeTexImage"]["outputs"]["Alpha"] = { "enabled": True }

opaque_node_links = [
    [["ShaderNodeTexImage", "Color"], ["ShaderNodeMix", "A_Color"]],
    [["ShaderNodeVertexColor", "Color"], ["ShaderNodeMix", "B_Color"]],
    [["ShaderNodeMix", "Result_Color"], ["ShaderNodeBsdfPrincipled", "Base Color"]],
    [["ShaderNodeBsdfPrincipled", "BSDF"], ["ShaderNodeOutputMaterial", "Surface"]],
]

transparent_node_links = [
    [["ShaderNodeTexImage", "Color"], ["ShaderNodeBsdfPrincipled", "Base Color"]],
    [["ShaderNodeTexImage", "Alpha"], ["ShaderNodeBsdfPrincipled", "Alpha"]],
    [["ShaderNodeBsdfPrincipled", "BSDF"], ["ShaderNodeOutputMaterial", "Surface"]],
]

def search_sockets(modify_nodes, socket_type, bl_idname, socket_identifier):
    for socket in getattr(modify_nodes.get(bl_idname), socket_type):
        if socket.identifier == socket_identifier:
            return socket
        
custom_frame_name = "CustomMaterialFrame"
def get_custom_material_label(mat):
    return ("Transparent " if mat.use_image_transparency else "") + "Image Material " + ("[Enabled]" if mat.use_custom_material else "[Disabled]")

def get_custom_material_frame(nodes):
    frame = nodes.get(custom_frame_name)
    if frame and (frame.bl_idname == "NodeFrame"):
        return frame

def is_in_custom_material(nodes, node, frame=None):
    if not frame:
        frame = get_custom_material_frame(nodes)
    if frame:
        return node.parent == frame

def disable_custom_material(mat):
    nodes = mat.node_tree.nodes
    frame = get_custom_material_frame(nodes)
    if frame:
        frame.label = get_custom_material_label(mat)
        for node in nodes:
            if node.parent == frame and node.bl_idname == "ShaderNodeOutputMaterial":
                nodes.remove(node)
    
    output_node_exists = False
    for node in nodes:
        if node.bl_idname == "ShaderNodeOutputMaterial":
            output_node_exists = True
            break
    if not output_node_exists:
        node = nodes.new(type="ShaderNodeOutputMaterial")
        node.location = mathutils.Vector((200, 160))

def init_custom_material(mat):
    node_properties = transparent_node_properties if mat.use_image_transparency else opaque_node_properties
    node_links = transparent_node_links if mat.use_image_transparency else opaque_node_links

    if mat.node_tree:
        nodes = mat.node_tree.nodes
        frame = get_custom_material_frame(nodes)
        is_new = False
        if not frame:
            frame = nodes.new(type="NodeFrame")
            frame.name = custom_frame_name
            frame.use_custom_color = True
            frame.color = mathutils.Color((0.35, 0.35, 0.35))
            frame.label_size = 30
            frame.shrink = True
            frame.location = mathutils.Vector((-500, -80))
            is_new = True
        
        frame.label = get_custom_material_label(mat)
        modify_nodes = {}
        for node in nodes:
            if is_in_custom_material(nodes, node, frame):
                if node.bl_idname in node_properties:
                    modify_nodes[node.bl_idname] = node
                else:
                    nodes.remove(node)

        for bl_idname in node_properties.keys():
            if not bl_idname in modify_nodes:
                node = nodes.new(type=bl_idname)
                node.parent = frame
                modify_nodes[bl_idname] = node

        links = mat.node_tree.links
        for link in links:
            if (link.from_node.parent == frame) or (link.to_node.parent == frame):
                links.remove(link)
        for link in node_links:
            links.new(search_sockets(modify_nodes, "outputs", *link[0]), search_sockets(modify_nodes, "inputs", *link[1]))

        if is_new:
            image = None
            for node in nodes:
                if node.parent != frame and node.bl_idname == "ShaderNodeTexImage":
                    image = node.image
                    break
            if image:
                modify_nodes.get("ShaderNodeTexImage").image = image

        for bl_idname, node in modify_nodes.items():
            properties = node_properties.get(bl_idname)
            for k, v in properties["properties"].items():
                setattr(node, k, v)
            
            input_properties = properties.get("inputs")
            if input_properties:
                for input_socket in node.inputs:
                    socket_properties = input_properties.get(input_socket.identifier)
                    if socket_properties:
                        for k, v in socket_properties.items():
                            setattr(input_socket, k, v)

            output_properties = properties.get("outputs")
            if output_properties:
                for output_socket in node.outputs:
                    socket_properties = output_properties.get(output_socket.identifier)
                    if socket_properties:
                        for k, v in socket_properties.items():
                            setattr(output_socket, k, v)

def update_use_custom_material(self, _=None):
    if self.use_custom_material:
        init_custom_material(self)
    else:
        disable_custom_material(self)
bpy.types.Material.use_custom_material = bpy.props.BoolProperty(default=True, update=update_use_custom_material)
bpy.types.Material.use_image_transparency = bpy.props.BoolProperty(default=False, update=update_use_custom_material)
def material_added():
    update_use_custom_material(bpy.context.material)

class EEVEE_MATERIAL_PT_surface(bl_ui.properties_material.EEVEE_MATERIAL_PT_surface): #overwrite original panel
    def draw(self, context):
        layout = self.layout
        mat = context.material

        box = layout.box()
        box.prop(mat, "use_custom_material", text="Use Custom Material")
        if mat.use_custom_material:
            nodes = mat.node_tree.nodes
            image_node, bsdf_node = None, None
            for node in nodes:
                if is_in_custom_material(nodes, node):
                    match type(node):
                        case bpy.types.ShaderNodeTexImage:
                            image_node = node
                        case bpy.types.ShaderNodeBsdfPrincipled:
                            bsdf_node = node
            
            if image_node.image and image_node.image.preview:
                layout.template_icon(image_node.image.preview.icon_id, scale=4)
            layout.template_ID(image_node, "image", new="image.new", open="image.open")
            
            layout.prop(mat, "use_image_transparency", text="Use Image Transparency")
            layout.use_property_split = True
            if not mat.use_image_transparency:
                alpha_socket = None
                for socket in bsdf_node.inputs:
                    if socket.identifier == "Alpha":
                        alpha_socket = socket
                        break
                layout.prop(alpha_socket, "default_value", text="Alpha")
        else:
            super().draw(context)

@bpy.app.handlers.persistent
def load_post(file):
    for mat in bpy.data.materials:
        update_use_custom_material(mat)

listeners = []
classes = (EEVEE_MATERIAL_PT_surface,)
def register():
    bpy.app.handlers.load_post.append(load_post)
    listeners.append(utils.listen_operator("MATERIAL_OT_new", material_added))

def unregister():
    if load_post in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(load_post)