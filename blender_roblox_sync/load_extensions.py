import bpy

def register(utils, package):
    prefs = utils.import_module("addon_prefs").prefs
    
    class WM_OT_blender_roblox_sync_extension_changed(bpy.types.Operator):
        bl_idname = "wm.blender_roblox_sync_extension_changed"
        bl_label = "Extension added"

        def execute(self, context):
            utils.reload()
            return {'FINISHED'}
        
    for extension in prefs.extension_list.values():
        utils.load_addon(extension.root_package, extension.root_file_path_name)

    return {
        "classes": (WM_OT_blender_roblox_sync_extension_changed,),
    }