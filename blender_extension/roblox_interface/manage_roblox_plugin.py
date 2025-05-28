import bpy, shutil, platform, pathlib

def register(utils):
    
    PLUGIN_NAME = "blender_roblox_sync.rbxm"
    PLUGIN_PATH = pathlib.Path(__file__).parent.joinpath(PLUGIN_NAME)

    def get_plugins_dir():
        plugins_dir = pathlib.Path.home()
        match platform.system():
            case "Darwin":
                plugins_dir = plugins_dir.joinpath("Documents", "Roblox", "Plugins")
            case "Windows":
                plugins_dir = plugins_dir.joinpath("AppData", "Local", "Roblox", "Plugins")

        return str(plugins_dir) if plugins_dir.is_dir() else ""

    def get_valid_path(dir):
        path = pathlib.Path(dir)
        if dir != "" and path.is_dir():
            return path.joinpath(PLUGIN_NAME)

    global is_valid_dir
    is_valid_dir = False
    def plugins_dir_update(self, context):
        global is_valid_dir
        is_valid_dir = False

        path = get_valid_path(self.plugins_dir)
        if path:
            try:
                shutil.copyfile(PLUGIN_PATH, path)
                is_valid_dir = True
            except:
                self.plugins_dir = ""
        
        if self.last_dir != self.plugins_dir:
            last_path = get_valid_path(self.last_dir)
            if last_path:
                last_path.unlink(missing_ok=True)
        self.last_dir = self.plugins_dir

    class CustomAddonPreferences(bpy.types.AddonPreferences):
        bl_idname = utils.ROOT_PACKAGE

        last_dir: bpy.props.StringProperty(default="")
        plugins_dir: bpy.props.StringProperty(
            name="Local Plugin pathlib.Path",
            description = "Roblox Studio Local Plugin Folder pathlib.Path",
            default="",
            subtype='DIR_PATH',
            update=plugins_dir_update
        )
    bpy.utils.register_class(CustomAddonPreferences)

    preferences = bpy.context.preferences
    addon_prefs = preferences.addons[utils.ROOT_PACKAGE].preferences
    addon_prefs.plugins_dir = get_plugins_dir() #adds plugin

    def unregister():
        preferences = bpy.context.preferences
        addon_prefs = preferences.addons[utils.ROOT_PACKAGE].preferences
        if addon_prefs:
            addon_prefs.plugins_dir = "" #removes plugin

    return {
        "classes": (CustomAddonPreferences,),
        "unregister": unregister
    }