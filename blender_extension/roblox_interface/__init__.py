import bpy

def register(utils):
    manage_roblox_plugin = utils.import_module("manage_roblox_plugin")
    roblox_server = utils.import_module("roblox_server")

    def get_visible_mesh_objects():
        objects = []
        for object in bpy.context.visible_objects:
            if not (object.id_type == "OBJECT" and object.type == "MESH"):
                continue
            objects.append(object)
        return objects

    syncing = False
    class VIEW3D_OT_toggle_roblox_sync(bpy.types.Operator):
        bl_idname = "view3d.toggle_roblox_sync"
        bl_label = "Toggle Roblox Sync"
        bl_options = {"REGISTER", "UNDO"}

        def execute(self, context):
            nonlocal syncing
            syncing = not syncing
            return {"FINISHED"}

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

    class VIEW3D_PT_roblox_sync(bpy.types.Panel):
        bl_space_type = "VIEW_3D"
        bl_region_type = "UI"
        bl_category = "Roblox"
        bl_label = "Roblox Sync"
        
        def draw(self, context):
            roblox_server.is_connected_area = context.area

            preferences = context.preferences
            addon_prefs = preferences.addons[utils.ROOT_PACKAGE].preferences

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
    
    return {
        "classes": (VIEW3D_OT_toggle_roblox_sync, VIEW3D_PT_roblox_sync,)
    }