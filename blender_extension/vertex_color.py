import bpy, bmesh
from . import utils
import bl_ui

vertex_color_name = "BaseShading"
vertex_paint_modes = ("VERTEX_PAINT", "SCULPT")

active_object_name, sculpt_object_name = None, None
recent_vertex_paint_mode = None
sculpt_mesh_mappings = {}
def enter_vertex_paint(last_mode):
    global sculpt_object_name
    global active_object_name
    global recent_vertex_paint_mode
    with utils.pause_updates():
        editable_objects = bpy.context.selected_editable_objects
        if len(editable_objects) > 1:
            active_object_name = bpy.context.active_object.name
            object_mode = bpy.context.active_object.mode

            selected_objects = []
            for object in bpy.context.selected_objects:
                selected_objects.append(object)

                bpy.context.view_layer.objects.active = object
                bpy.ops.object.mode_set(mode="OBJECT")
                object.select_set(False)

            sculpt_mesh = bpy.data.meshes.new("temp_sculpt_mesh")
            sculpt_object = bpy.data.objects.new("temp_sculpt_object", sculpt_mesh)
            sculpt_object_name = sculpt_object.name
            bpy.context.collection.objects.link(sculpt_object)
            sculpt_object.select_set(True)
            bpy.context.view_layer.objects.active = sculpt_object

            sculpt_bmesh = bmesh.new()
            sculpt_uv_layer = sculpt_bmesh.loops.layers.uv.new()
            sculpt_color_layer = sculpt_bmesh.loops.layers.color.new(vertex_color_name)

            copied_materials = []
            object_slot_mappings = {}
            for object in editable_objects:
                object_slot_mapping = {}
                object_slot_mappings[object] = object_slot_mapping
                for material_slot in object.material_slots:
                    material = material_slot.material
                    if material in copied_materials:
                        slot_index = copied_materials.index(material)
                    else:
                        slot_index = len(copied_materials)
                        copied_materials.append(material)
                        bpy.ops.object.material_slot_add()
                        sculpt_object.material_slots[slot_index].material = material
                    object_slot_mapping[material_slot.slot_index] = slot_index
            
            sculpt_mesh_mappings.clear()
            sculpt_vi, sculpt_fi = 0, 0
            sculpt_verts = sculpt_bmesh.verts
            sculpt_faces = sculpt_bmesh.faces
            for object in editable_objects:
                object_slot_mapping = object_slot_mappings[object]
                vert_mapping = {}
                face_mapping = {}
                matrix_world = object.matrix_world.copy()
                mesh_mapping = (vert_mapping, face_mapping, matrix_world)
                sculpt_mesh_mappings[object.name] = mesh_mapping

                read_mesh = object.data #this is unevaluated object's mesh (before modifiers are applied)
                read_bmesh = bmesh.new()
                read_bmesh.from_mesh(read_mesh)
                read_uv_layer = read_bmesh.loops.layers.uv.active
                read_color_layer = read_bmesh.loops.layers.color.get(vertex_color_name)

                vert_lookup = {}
                for read_vi, read_vert in enumerate(read_bmesh.verts):
                    sculpt_vert = sculpt_verts.new(matrix_world @ read_vert.co)
                    vert_mapping[read_vi] = sculpt_vi
                    sculpt_vi += 1

                    sculpt_vert.normal = read_vert.normal
                    vert_lookup[read_vert] = sculpt_vert

                for read_fi, read_face in enumerate(read_bmesh.faces):
                    new_verts = []
                    for read_vert in read_face.verts:
                        new_verts.append(vert_lookup[read_vert])

                    sculpt_face = sculpt_faces.new(new_verts)
                    face_mapping[read_fi] = sculpt_fi
                    sculpt_fi += 1

                    for i, read_loop in enumerate(read_face.loops):
                        sculpt_loop = sculpt_face.loops[i]
                        sculpt_loop[sculpt_uv_layer].uv = read_loop[read_uv_layer].uv
                        sculpt_loop[sculpt_color_layer] = read_loop[read_color_layer]

                        sculpt_edge = sculpt_loop.edge
                        read_edge = read_loop.edge
                        sculpt_edge.seam = read_edge.seam
                        sculpt_edge.smooth = read_edge.smooth
                    sculpt_face.material_index = object_slot_mapping[read_face.material_index]
                    sculpt_face.normal = read_face.normal

            sculpt_bmesh.to_mesh(sculpt_mesh)
            sculpt_mesh.color_attributes.active_color = sculpt_mesh.color_attributes.get(vertex_color_name)
            bpy.ops.object.shade_smooth()

            for object in selected_objects:
                object.hide_viewport = True
            bpy.ops.object.mode_set(mode=object_mode)
            bpy.ops.ed.undo_push()
        
def exit_vertex_paint(new_mode):
    global active_object_name
    global sculpt_object_name
    with utils.pause_updates():
        if sculpt_object_name:
            sculpt_object = bpy.data.objects.get(sculpt_object_name)
            object_mode = bpy.context.active_object.mode
            if sculpt_object:
                for object in bpy.context.selected_objects:
                    object.select_set(False)
                sculpt_mesh = sculpt_object.data
                sculpt_bmesh = bmesh.new()
                sculpt_bmesh.from_mesh(sculpt_mesh)

                sculpt_uv_layer = sculpt_bmesh.loops.layers.uv.active
                sculpt_color_layer = sculpt_bmesh.loops.layers.color.get(vertex_color_name)

                sculpt_verts = sculpt_bmesh.verts
                sculpt_faces = sculpt_bmesh.faces
                sculpt_verts.ensure_lookup_table()
                sculpt_faces.ensure_lookup_table()
                for object_name, mesh_mapping in sculpt_mesh_mappings.items():
                    object = bpy.data.objects.get(object_name)
                    vert_mapping, face_mapping, matrix_world = mesh_mapping

                    read_mesh = object.data
                    read_bmesh = bmesh.new()
                    read_bmesh.from_mesh(read_mesh)

                    read_uv_layer = read_bmesh.loops.layers.uv.active
                    read_color_layer = read_bmesh.loops.layers.color.get(vertex_color_name)

                    matrix_world_inverse = matrix_world.inverted()
                    for read_vi, read_vert in enumerate(read_bmesh.verts):
                        sculpt_vert = sculpt_verts[vert_mapping[read_vi]]
                        read_vert.co = matrix_world_inverse @ sculpt_vert.co
                        read_vert.normal = sculpt_vert.normal
                    
                    for read_fi, read_face in enumerate(read_bmesh.faces):
                        sculpt_face = sculpt_faces[face_mapping[read_fi]]

                        for i, read_loop in enumerate(read_face.loops):
                            sculpt_loop = sculpt_face.loops[i]
                            read_loop[read_uv_layer].uv = sculpt_loop[sculpt_uv_layer].uv
                            read_loop[read_color_layer] = sculpt_loop[sculpt_color_layer]

                            sculpt_edge = sculpt_loop.edge
                            read_edge = read_loop.edge
                            read_edge.seam = sculpt_edge.seam
                            read_edge.smooth = sculpt_edge.smooth
                        read_face.normal = sculpt_face.normal

                    read_bmesh.to_mesh(read_mesh)
                    bpy.context.view_layer.objects.active = sculpt_object
                    bpy.ops.object.shade_smooth()
            
                sculpt_object.select_set(True)
                bpy.ops.object.mode_set(mode="OBJECT")
                bpy.ops.object.delete()

            for object_name in sculpt_mesh_mappings.keys():
                object = bpy.data.objects.get(object_name)

                object.hide_viewport = False
                object.select_set(True)
                bpy.context.view_layer.objects.active = object
                bpy.ops.object.mode_set(mode=object_mode)
            bpy.context.view_layer.objects.active = bpy.data.objects.get(active_object_name)

def add_vertex_color(mesh):
    if not mesh.color_attributes.get(vertex_color_name):
        mesh.attributes.new(vertex_color_name, "BYTE_COLOR", "CORNER")

@bpy.app.handlers.persistent
def load_post(file):
    for mesh in bpy.data.meshes:
        add_vertex_color(mesh)

@bpy.app.handlers.persistent
def save_pre(file):
    if sculpt_object_name and bpy.data.objects.get(sculpt_object_name):
        with utils.pause_updates():
            bpy.ops.object.mode_set(mode="OBJECT")
            exit_vertex_paint(None)

def add_vertex_colors():
    for object in bpy.context.selected_editable_objects:
        if object.type == "MESH":
            add_vertex_color(object.data)

class VIEW3D_PT_sculpt_dyntopo(bl_ui.space_view3d_toolbar.VIEW3D_PT_sculpt_dyntopo): #overwrite original panel
    @classmethod
    def poll(cls, context):
        return super().poll(context) and (sculpt_object_name and not bpy.data.objects.get(sculpt_object_name))

class VIEW3D_PT_sculpt_voxel_remesh(bl_ui.space_view3d_toolbar.VIEW3D_PT_sculpt_voxel_remesh): #overwrite original panel
    @classmethod
    def poll(cls, context):
        return super().poll(context) and (sculpt_object_name and not bpy.data.objects.get(sculpt_object_name))

classes = (VIEW3D_PT_sculpt_dyntopo, VIEW3D_PT_sculpt_voxel_remesh,)
listeners = []
def register():
    bpy.app.handlers.load_post.append(load_post)
    bpy.app.handlers.save_pre.append(save_pre)
    listeners.append(utils.listen_mode(vertex_paint_modes, enter=enter_vertex_paint, exit=exit_vertex_paint))
    listeners.append(utils.listen_depsgraph_update(add_vertex_colors))

def unregister():
    if load_post in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(load_post)
    if save_pre in bpy.app.handlers.save_pre:
        bpy.app.handlers.save_pre.remove(save_pre)
    bpy.ops.object.mode_set(mode="OBJECT")
    exit_vertex_paint(None)