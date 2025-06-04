import bpy

def register(utils):
    manage_roblox_plugin = utils.import_module("manage_roblox_plugin")
    roblox_server = utils.import_module("roblox_server")

    syncing = False
    class VIEW3D_OT_toggle_roblox_sync(bpy.types.Operator):
        bl_idname = "view3d.toggle_roblox_sync"
        bl_label = "Toggle Roblox Sync"
        bl_options = {"REGISTER", "UNDO"}

        def execute(self, context):
            nonlocal syncing
            syncing = not syncing
            return {"FINISHED"}

    class VIEW3D_OT_OTHER_OPERATOR(bpy.types.Operator):
        bl_idname = "view3d.hgf_other_operator"
        bl_label = "HGF Other Operator"
        bl_options = {"REGISTER", "UNDO"}

        def execute(self, context):
            print(bpy.path.basename(bpy.context.blend_data.filepath))
            return {"FINISHED"}

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

            layout.operator("view3d.hgf_other_operator", text="test button")
    
    return {
        "classes": (VIEW3D_OT_toggle_roblox_sync, VIEW3D_PT_roblox_sync, VIEW3D_OT_OTHER_OPERATOR,)
    }