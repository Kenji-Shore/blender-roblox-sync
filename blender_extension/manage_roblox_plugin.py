import platform
from pathlib import Path

import bpy
import shutil

plugin_name = "blender_roblox_sync.rbxm"

"DFIntUserHttpRequestsPerMinuteLimitZ"
def get_plugins_dir():
    plugins_dir = Path.home()
    match platform.system():
        case "Darwin":
            plugins_dir = plugins_dir.joinpath("Documents", "Roblox", "Plugins")
        case "Windows":
            plugins_dir = plugins_dir.joinpath("AppData", "Local", "Roblox", "Plugins")

    return str(plugins_dir) if plugins_dir.is_dir() else ""

plugin_path = Path(__file__).parent.joinpath(plugin_name)
is_valid_dir = False

def get_valid_path(dir):
    path = Path(dir)
    if dir != "" and path.is_dir():
        return path.joinpath(plugin_name)

def plugins_dir_update(self, context):
    global is_valid_dir
    is_valid_dir = False

    path = get_valid_path(self.plugins_dir)
    if path:
        try:
            shutil.copyfile(plugin_path, path)
            is_valid_dir = True
        except:
            self.plugins_dir = ""
    
    last_path = get_valid_path(self.last_dir)
    if last_path:
        last_path.unlink(missing_ok=True)
    
    self.last_dir = self.plugins_dir

class CustomAddonPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__

    last_dir: bpy.props.StringProperty(default="")
    plugins_dir: bpy.props.StringProperty(
        name="Local Plugin Path",
        description = "Roblox Studio Local Plugin Folder Path",
        default="",
        subtype='DIR_PATH',
        update=plugins_dir_update
    )

classes = (CustomAddonPreferences,)
def register():
    preferences = bpy.context.preferences
    addon_prefs = preferences.addons[__package__].preferences
    addon_prefs.plugins_dir = get_plugins_dir() #adds plugin

def unregister():
    preferences = bpy.context.preferences
    addon_prefs = preferences.addons[__package__].preferences
    addon_prefs.plugins_dir = "" #removes plugin