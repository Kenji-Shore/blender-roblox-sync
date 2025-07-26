import bpy

def register(utils, package):
    manage_roblox_plugin = utils.import_module("manage_roblox_plugin")
    server = utils.import_module("server")

    global is_syncing
    is_syncing = False
    class VIEW3D_OT_toggle_roblox_sync(bpy.types.Operator):
        bl_idname = "view3d.toggle_roblox_sync"
        bl_label = "Toggle Roblox Sync"
        bl_options = {"REGISTER", "UNDO"}

        def execute(self, context):
            global is_syncing
            is_syncing = not is_syncing
            return {"FINISHED"}
    
    def draw(layout, context):
        server.is_connected_area = context.area

        can_sync = False
        sync_text = ""
        if not manage_roblox_plugin.is_valid_dir:
            sync_text = "Invalid Plugin Directory"
        elif not server.is_connected:
            sync_text = "Roblox Studio Not Open"
        else:
            sync_text = "Stop Sync" if is_syncing else "Start Sync"
            can_sync = True
        
        col2 = layout.column()
        row = col2.row()
        row.operator("view3d.toggle_roblox_sync", text=sync_text)
        row.enabled = can_sync
        
        row2 = col2.row()
        row2.progress(factor=0.5)
        row2.scale_y = 0.4

    return {
        "classes": (VIEW3D_OT_toggle_roblox_sync,),
        "draw": (draw, 1),
    }