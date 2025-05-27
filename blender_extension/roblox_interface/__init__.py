import bpy
from . import roblox_server, manage_roblox_plugin

syncing = False
class VIEW3D_OT_toggle_roblox_sync(bpy.types.Operator):
    bl_idname = "view3d.toggle_roblox_sync"
    bl_label = "Toggle Roblox Sync"
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

# class VIEW3D_OT_OTHER_OPERATOR(bpy.types.Operator):
#     bl_idname = "view3d.hgf_other_operator"
#     bl_label = "HGF Other Operator"
#     bl_options = {"REGISTER", "UNDO"}

#     def execute(self, context):
#         overall_start = time.process_time()
#         send_meshes = {}
#         send_images = {}
#         send_objects = {}

#         if bpy.context.mode == "EDIT_MESH":
#             for object in get_visible_mesh_objects():
#                 if object.mode == "EDIT":
#                     object.update_from_editmode()
#         depsgraph = context.evaluated_depsgraph_get()

#         for object in get_visible_mesh_objects():
#             object = object.evaluated_get(depsgraph)
#             position, rotation, scale = object.matrix_world.decompose()
#             scale, hashes = process_mesh(object.data, scale, send_meshes, process_materials(object.material_slots, send_images))
#             send_object = (
#                 object.name,
#                 object.matrix_world.copy().freeze(),
#                 scale.freeze(),
#                 hashes
#             )

#             object_hash = hash(send_object)
#             send_objects[object_hash] = send_object
        
#         server.fire("sendObjects", send_meshes, send_images, send_objects)
#         print("overall", time.process_time() - overall_start)
#         return {"FINISHED"}

has_set_callback = False
def set_callback(area):
    global has_set_callback
    if not has_set_callback:
        has_set_callback = True

        def callback(is_connected):
            area.tag_redraw()
        roblox_server.is_connected_callbacks.append(callback)

classes = (
    VIEW3D_OT_toggle_roblox_sync,
    # VIEW3D_OT_OTHER_OPERATOR
)

VIEW3D_PT_roblox_sync = None
def register(package):
    global VIEW3D_PT_roblox_sync
    class VIEW3D_PT_roblox_sync(bpy.types.Panel):
        bl_space_type = "VIEW_3D"
        bl_region_type = "UI"
        bl_category = "Roblox"
        bl_label = "Roblox Sync"
        
        def draw(self, context):
            set_callback(context.area)
            preferences = context.preferences
            addon_prefs = preferences.addons[package].preferences

            layout = self.layout
            box = layout.box()
            box.label(text="Local Plugin Directory:")
            box.prop(addon_prefs, "plugins_dir", text="", placeholder="Set Local Plugin Directory")
            box.enabled = not syncing

            can_sync = False
            sync_text = ""
            if not manage_roblox_plugin.is_valid_dir:
                sync_text = "Invalid Plugin Directory"
            elif not roblox_server.is_connected:
                sync_text = "Roblox Studio Not Open"
            else:
                sync_text = "Stop Sync" if syncing else "Start Sync"
                can_sync = True
            
            row = layout.row()
            row.operator("view3d.toggle_roblox_sync", text=sync_text)
            row.enabled = can_sync

            # layout.operator("view3d.hgf_other_operator", text="test button")
    bpy.utils.register_class(VIEW3D_PT_roblox_sync)

def unregister(package):
    global VIEW3D_PT_roblox_sync
    if VIEW3D_PT_roblox_sync:
        bpy.utils.unregister_class(VIEW3D_PT_roblox_sync)
    VIEW3D_PT_roblox_sync = None