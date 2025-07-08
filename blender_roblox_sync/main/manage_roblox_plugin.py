import bpy, shutil, platform, pathlib

def register(utils, package):
    PLUGIN_NAME = "roblox_plugin.rbxm"
    PLUGINS_DIR = pathlib.Path.home()
    match platform.system():
        case "Darwin":
            PLUGINS_DIR = PLUGINS_DIR.joinpath("Documents", "Roblox", "Plugins")
        case "Windows":
            PLUGINS_DIR = PLUGINS_DIR.joinpath("AppData", "Local", "Roblox", "Plugins")
    PLUGINS_DIR = str(PLUGINS_DIR) if PLUGINS_DIR.is_dir() else ""

    def get_target_path(dir, target_name):
        path = pathlib.Path(dir)
        if dir != "" and path.is_dir():
            return path.joinpath(target_name + ".rbxm")

    global is_valid_dir
    is_valid_dir = False
    def append_plugins(self, _=None):
        global is_valid_dir
        is_valid_dir = True

        for addon_path in utils.addon_paths:
            addon_name = addon_path.stem
            plugin_path = addon_path.joinpath(PLUGIN_NAME)
            
            target_path = get_target_path(self.plugins_dir, addon_name)
            if target_path and plugin_path.is_file():
                try:
                    shutil.copyfile(plugin_path, target_path)
                except:
                    is_valid_dir = False
        
        if (not is_valid_dir) and (self.plugins_dir != PLUGINS_DIR):
            self.plugins_dir = PLUGINS_DIR
        
        if self.last_dir != self.plugins_dir:
            for addon_path in utils.addon_paths:
                addon_name = addon_path.stem
                last_path = get_target_path(self.last_dir, addon_name)
                if last_path:
                    last_path.unlink(missing_ok=True)
        self.last_dir = self.plugins_dir

    def prefs_draw(self, layout):
        row = layout.row()
        row.prop(self, "plugins_dir")

    def post_registration():
        append_plugins(utils.prefs)

    return {
        "prefs": {
            "last_dir": bpy.props.StringProperty(default=""),
            "plugins_dir": bpy.props.StringProperty(
                name="Local Plugin Path",
                description = "Roblox Studio Local Plugin Folder Path",
                default = PLUGINS_DIR,
                subtype = "DIR_PATH",
                update = append_plugins
            )
        },
        "prefs_draw": prefs_draw,
        "post_registration": post_registration
    }