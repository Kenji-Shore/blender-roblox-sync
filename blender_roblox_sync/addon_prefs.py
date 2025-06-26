import bpy

def register(utils, package):
    manage_roblox_plugin = utils.import_module("manage_roblox_plugin")

    class SyncingAssetPrefs(bpy.types.PropertyGroup):
        name: bpy.props.StringProperty()
        file: bpy.props.StringProperty()
        asset_type_str: bpy.props.StringProperty()
        is_paused: bpy.props.BoolProperty()
    bpy.utils.register_class(SyncingAssetPrefs)

    class LoadExtensionPrefs(bpy.types.PropertyGroup):
        root_package: bpy.props.StringProperty()
        root_file_path_name: bpy.props.StringProperty()
    bpy.utils.register_class(LoadExtensionPrefs)

    class AddonPreferences(bpy.types.AddonPreferences):
        bl_idname = package

        last_dir: bpy.props.StringProperty(default="")
        plugins_dir: bpy.props.StringProperty(
            name="Local Plugin Path",
            description = "Roblox Studio Local Plugin Folder Path",
            default = manage_roblox_plugin.get_plugins_dir(),
            subtype = "DIR_PATH",
            update = manage_roblox_plugin.plugins_dir_update
        )

        extension_list: bpy.props.CollectionProperty(type=LoadExtensionPrefs)
        syncing_list: bpy.props.CollectionProperty(type=SyncingAssetPrefs)
        syncing_index: bpy.props.IntProperty(default=0)

        def draw(self, context):
            layout = self.layout
            row = layout.row()
            row.prop(self, "plugins_dir")
            
    bpy.utils.register_class(AddonPreferences)
    preferences = bpy.context.preferences
    global prefs
    prefs = preferences.addons[package].preferences

    def unregister():
        prefs.plugins_dir = "" #removes plugin
        bpy.utils.unregister_class(AddonPreferences)
        bpy.utils.unregister_class(SyncingAssetPrefs)
        bpy.utils.unregister_class(LoadExtensionPrefs)
    return {
        "unregister": unregister
    }