# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import bpy, mathutils
import sys, subprocess, struct, time
from collections import deque
from . import utils, server, manage_roblox_plugin, material, vertex_color
import numpy as np

syncing = False
class VIEW3D_OT_TEST_OPERATOR(bpy.types.Operator):
    bl_idname = "view3d.hgf_test_operator"
    bl_label = "HGF Test Operator"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        global syncing
        syncing = not syncing
        
        return {"FINISHED"}

def get_visible_mesh_objects():
    objects = []
    for object in bpy.context.visible_objects:
        if not (object.id_type == "OBJECT" and object.type == "MESH"):
            continue
        objects.append(object)
    return objects

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

def get_hash(data):
    def freeze_data(data):
        data_type = type(data)
        if (data_type is list) or (data_type is tuple):
            new_data = []
            for item in data:
                new_data.append(freeze_data(item))
            return tuple(new_data)
        elif data_type is dict:
            new_keys = []
            new_values = []
            for key, value in data.items():
                new_keys.append(freeze_data(key))
                new_values.append(freeze_data(value))
            return tuple(new_keys) + tuple(new_values)
        elif (data_type is mathutils.Vector) or (data_type is mathutils.Matrix):
            return data.copy().freeze()
        else:
            return data
    
    return hash(freeze_data(data))

def process_image(image, send_images):
    width, height = tuple(image.size)
    if width == 0 and height == 0:
        return None
    
    pixels = np.empty(width * height * 4, dtype=np.float32)
    image.pixels.foreach_get(pixels)
    np.multiply(pixels, 255, out=pixels)
    image_bytes = struct.pack("<2H", width, height) + pixels.astype(np.uint8).data

    image_hash = hash(image_bytes)
    if not image_hash in send_images:
        send_images[image_hash] = image_bytes
    return image_hash

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

class SeparatedMesh():
    def __init__(self, loop_uvs, loop_colors):
        self.loop_uvs = loop_uvs
        self.loop_colors = loop_colors

        self.verts = ({}, deque())
        self.verts_index = 0
        self.tris = (deque(), deque(), deque(), deque())

class SeparatedMeshes(dict):
    def __getitem__(self, material_index):
        material_index = material_index if material_index in self.assigned_materials else 0
        try:
            return dict.__getitem__(self, material_index)
        except KeyError:
            separated_mesh = SeparatedMesh(self.loop_uvs, self.material_loop_colors.get(material_index))
            dict.__setitem__(self, material_index, separated_mesh)
            return separated_mesh
    
    def __init__(self, mesh, assigned_materials):
        self.loop_uvs = utils.get_loop_uvs(mesh.uv_layers)
        self.assigned_materials = assigned_materials
        self.material_loop_colors = get_loop_colors(mesh, assigned_materials)
        super(SeparatedMeshes, self).__init__()

def process_mesh(mesh, scale, send_meshes, assigned_materials):
    vertices = mesh.vertices
    sign_x = 1 if scale.x >= 0 else -1
    sign_y = 1 if scale.y >= 0 else -1
    sign_z = 1 if scale.z >= 0 else -1
    flip_winding = sign_x * sign_y * sign_z < 0
    sign = mathutils.Vector((sign_x, sign_y, sign_z))
    scale *= sign

    separated_meshes = SeparatedMeshes(mesh, assigned_materials)
    loops = mesh.loops
    for loop_triangle in mesh.loop_triangles:
        s_mesh = separated_meshes[loop_triangle.material_index]
        loop_uvs, loop_colors = s_mesh.loop_uvs, s_mesh.loop_colors

        tri_vis, tri_normals, tri_uvs, tri_colors = s_mesh.tris
        verts_keys, verts = s_mesh.verts
        
        if flip_winding:
            li3, li2, li1 = tuple(loop_triangle.loops)
            l3, l2, l1 = loops[li3], loops[li2], loops[li1]
        else:
            li1, li2, li3 = tuple(loop_triangle.loops)
            l1, l2, l3 = loops[li1], loops[li2], loops[li3]

        vi = l1.vertex_index
        if not vi in verts_keys:
            verts_keys[vi] = s_mesh.verts_index
            s_mesh.verts_index += 1

            vert = vertices[vi].co * sign
            verts.append(vert.x)
            verts.append(vert.y)
            verts.append(vert.z)
        tri_vis.append(verts_keys[vi])

        vi = l2.vertex_index
        if not vi in verts_keys:
            verts_keys[vi] = s_mesh.verts_index
            s_mesh.verts_index += 1

            vert = vertices[vi].co * sign
            verts.append(vert.x)
            verts.append(vert.y)
            verts.append(vert.z)
        tri_vis.append(verts_keys[vi])

        vi = l3.vertex_index
        if not vi in verts_keys:
            verts_keys[vi] = s_mesh.verts_index
            s_mesh.verts_index += 1

            vert = vertices[vi].co * sign
            verts.append(vert.x)
            verts.append(vert.y)
            verts.append(vert.z)
        tri_vis.append(verts_keys[vi])
        
        normal = l1.normal * sign
        tri_normals.append(normal.x)
        tri_normals.append(normal.y)
        tri_normals.append(normal.z)

        normal = l2.normal * sign
        tri_normals.append(normal.x)
        tri_normals.append(normal.y)
        tri_normals.append(normal.z)

        normal = l3.normal * sign
        tri_normals.append(normal.x)
        tri_normals.append(normal.y)
        tri_normals.append(normal.z)

        if loop_uvs:
            uv = loop_uvs[li1].vector
            tri_uvs.append(uv.x)
            tri_uvs.append(uv.y)

            uv = loop_uvs[li2].vector
            tri_uvs.append(uv.x)
            tri_uvs.append(uv.y)

            uv = loop_uvs[li3].vector
            tri_uvs.append(uv.x)
            tri_uvs.append(uv.y)

        if loop_colors:
            color = loop_colors[li1].color_srgb
            tri_colors.append(color[0])
            tri_colors.append(color[1])
            tri_colors.append(color[2])
            tri_colors.append(color[3])

            color = loop_colors[li2].color_srgb
            tri_colors.append(color[0])
            tri_colors.append(color[1])
            tri_colors.append(color[2])
            tri_colors.append(color[3])

            color = loop_colors[li3].color_srgb
            tri_colors.append(color[0])
            tri_colors.append(color[1])
            tri_colors.append(color[2])
            tri_colors.append(color[3])

    hashes = []
    for material_index, s_mesh in separated_meshes.items():
        tri_vis, tri_normals, tri_uvs, tri_colors = s_mesh.tris
        _, verts = s_mesh.verts
        verts_index = s_mesh.verts_index
        flags = int(bool(s_mesh.loop_uvs))
        flags <<= flags
        flags += int(bool(s_mesh.loop_colors))

        tris_len = len(tri_vis) // 3
        verts = np.array(verts, dtype=np.float32)
        tri_vis = np.array(tri_vis, dtype=np.uint16)
        tri_normals = np.array(tri_normals, dtype=np.float32)
        tri_uvs = np.array(tri_uvs, dtype=np.float32)
        tri_colors = np.array(tri_colors, dtype=np.float32)

        np.multiply(tri_normals, 127, out=tri_normals)
        np.multiply(tri_colors, 255, out=tri_colors)

        mesh_bytes = b"".join((
            bytes((flags,)),
            struct.pack("<H", verts_index),
            verts.data,
            struct.pack("<H", tris_len),
            tri_vis.data,
            tri_normals.astype(np.int8).data,
            tri_uvs.data,
            tri_colors.astype(np.uint8).data
        ))
        mesh_hash = hash(mesh_bytes)
        if not mesh_hash in send_meshes:
            send_meshes[mesh_hash] = mesh_bytes
        
        assigned_material = assigned_materials[material_index]
        image_hash = assigned_material["image_hash"]

        has_image = image_hash != None
        mesh_image = (has_image, assigned_material["use_image_transparency"], mesh_hash, round(assigned_material["alpha"] * 255))
        if has_image:
            mesh_image += (image_hash,)
        hashes.append(mesh_image)
    return scale, tuple(hashes)

class VIEW3D_OT_OTHER_OPERATOR(bpy.types.Operator):
    bl_idname = "view3d.hgf_other_operator"
    bl_label = "HGF Other Operator"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        overall_start = time.process_time()
        send_meshes = {}
        send_images = {}
        send_objects = {}

        if bpy.context.mode == "EDIT_MESH":
            for object in get_visible_mesh_objects():
                if object.mode == "EDIT":
                    object.update_from_editmode()
        depsgraph = context.evaluated_depsgraph_get()

        for object in get_visible_mesh_objects():
            object = object.evaluated_get(depsgraph)
            position, rotation, scale = object.matrix_world.decompose()
            scale, hashes = process_mesh(object.data, scale, send_meshes, process_materials(object.material_slots, send_images))
            send_object = (
                object.name,
                object.matrix_world.copy().freeze(),
                scale.freeze(),
                hashes
            )

            object_hash = hash(send_object)
            send_objects[object_hash] = send_object
        
        server.fire("sendObjects", send_meshes, send_images, send_objects)
        print("overall", time.process_time() - overall_start)
        return {"FINISHED"}

has_set_callback = False
def set_callback(area):
    global has_set_callback
    if not has_set_callback:
        has_set_callback = True

        def callback(is_connected):
            area.tag_redraw()
        server.is_connected_callbacks.append(callback)

class VIEW3D_PT_MainPanel(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "HGF Utils"
    bl_label = "Roblox Mesh Sync"
    
    def draw(self, context):
        set_callback(context.area)
        preferences = context.preferences
        addon_prefs = preferences.addons[__package__].preferences

        layout = self.layout
        
        box = layout.box()
        box.label(text="Local Plugin Directory:")
        box.prop(addon_prefs, "plugins_dir", text="", placeholder="Set Local Plugin Directory")
        box.enabled = not syncing

        row = layout.row()

        can_sync = False
        sync_text = ""
        if not manage_roblox_plugin.is_valid_dir:
            sync_text = "Invalid Plugin Directory"
        elif not server.is_connected:
            sync_text = "Roblox Studio Not Open"
        else:
            sync_text = "Stop Sync" if syncing else "Start Sync"
            can_sync = True

        row.operator("view3d.hgf_test_operator", text=sync_text)
        row.enabled = can_sync

        layout.operator("view3d.hgf_other_operator", text="test button")

classes = (
    VIEW3D_PT_MainPanel,
    VIEW3D_OT_TEST_OPERATOR,
    VIEW3D_OT_OTHER_OPERATOR
)
modules = (
    utils,
    server,
    manage_roblox_plugin,
    material,
    vertex_color
)

def register_module(module):
    if "classes" in module:
        for cls in module["classes"]:
            bpy.utils.register_class(cls)
def unregister_module(module):
    if "classes" in module:
        for cls in reversed(module["classes"]):
            bpy.utils.unregister_class(cls)
    if "listeners" in module:
        for listener in module["listeners"]:
            utils.unlisten(listener)
        module["listeners"].clear()

def register():
    register_module(globals())
    for module in modules:
        register_module(module.__dict__)
        module.register()

def unregister():
    unregister_module(globals())
    for module in modules:
        module.unregister()
        unregister_module(module.__dict__)