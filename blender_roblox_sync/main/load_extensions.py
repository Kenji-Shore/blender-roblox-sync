import bpy

def register(utils, package):
    class WM_OT_blender_roblox_sync_extension_changed(bpy.types.Operator):
        bl_idname = "wm.blender_roblox_sync_extension_changed"
        bl_label = "Extension added"
        def execute(self, context):
            utils.reload()
            return {'FINISHED'}
    
    class LoadExtensionPrefs(bpy.types.PropertyGroup):
        root_package: bpy.props.StringProperty()
        root_file_path_name: bpy.props.StringProperty()

    return {
        "classes": (
            LoadExtensionPrefs,
            WM_OT_blender_roblox_sync_extension_changed,
        ),
        "prefs": {
            "extension_list": bpy.props.CollectionProperty(type=LoadExtensionPrefs)
        },
    }