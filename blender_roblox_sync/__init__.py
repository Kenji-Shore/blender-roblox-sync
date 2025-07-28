# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import bpy, queue, importlib, pathlib, inspect, uuid, sys, math, re
from contextlib import contextmanager

property_type = type(bpy.props.IntProperty())
def record_prefs(prefs):
    return_prefs = {}
    for pref_name, pref_annotation in prefs.__annotations__.items():
        if type(pref_annotation) is property_type:
            pref_value = getattr(prefs, pref_name)
            if isinstance(pref_value, bpy.types.bpy_prop_collection):
                new_pref_value = []
                for property_group in pref_value.values():
                    new_pref_value.append(record_prefs(property_group))
                pref_value = new_pref_value
            elif hasattr(pref_value, "__annotations__"):
                pref_value = record_prefs(pref_value)
            return_prefs[pref_name] = pref_value
    return return_prefs

def restore_prefs(prefs, recorded_prefs):
    for pref_name, pref_value in recorded_prefs.items():
        if hasattr(prefs, pref_name):
            match pref_value:
                case list():
                    collection_prop = getattr(prefs, pref_name)
                    for property_group in pref_value:
                        restore_prefs(collection_prop.add(), property_group)
                case dict():
                    restore_prefs(getattr(prefs, pref_name), pref_value)
                case _:
                    setattr(prefs, pref_name, pref_value)
            
class Utils:
    def load_addon(self, root_package, root_file_path_name):
        if not root_package in self.__loaded_addons:
            root_file_path = pathlib.Path(root_file_path_name)
            addon_path = root_file_path.parent

            self.__loaded_addons.append(root_package)
            self.addon_paths[root_package] = addon_path
            self.__lookup_package[root_file_path] = root_package
            self.__addon_draws[root_package] = []
            for module_name, module in self.glob_from_parent(root_file_path_name, "**/*.py").items():
                if hasattr(module, "register"):
                    if module_name in self.__modules:
                        raise Exception("Duplicate module name detected!")
                    self.__modules[module_name] = (module, root_package)

    def import_module(self, module_name):
        if module_name in self.__modules:
            module, root_package = self.__modules[module_name]
            if not (module_name in self.__registered_modules):
                if module_name in self.__dependency_stack:
                    raise Exception("Circular module import detected!")
                
                self.__dependency_stack.append(module_name)
                returns = getattr(module, "register")(self, root_package)
                if returns:
                    if "classes" in returns:
                        for cls in returns["classes"]:
                            bpy.utils.register_class(cls)
                    if "threads" in returns:
                        for thread in returns["threads"]:
                            thread.start()
                    if "prefs" in returns:
                        for pref_name, property_def in returns["prefs"].items():
                            self.__prefs_props[pref_name] = property_def
                    if "prefs_draw" in returns:
                        self.__prefs_draws.append(returns["prefs_draw"])
                    if "draw" in returns:
                        draw = returns["draw"]
                        addon_draws = self.__addon_draws[root_package]
                        if not type(draw) is tuple:
                            draw = (draw, math.inf)
                        priority = draw[1]
                        list_len = len(addon_draws)
                        for i in range(list_len + 1):
                            if i == list_len or priority <= addon_draws[i][1]:
                                addon_draws.insert(i, draw)
                                break
                    self.__registered_modules_returns.append(returns)
                self.__registered_modules.append(module_name)
                self.__dependency_stack.remove(module_name)
            return module
        
    def glob_from_parent(self, file_path_name, glob_str):
        file_path = pathlib.Path(file_path_name)
        file_package = (self.__lookup_package[file_path],)
        parent_path = file_path.parent

        modules = {}
        for module_path in parent_path.glob(glob_str):
            if module_path != file_path:
                relative_path = module_path.relative_to(parent_path)
                parts = file_package + relative_path.parts[:-1]
                module_package = ".".join(parts)
                module_stem = module_path.stem
                module_name = parts[-1] if module_stem == "__init__" else module_stem
                self.__lookup_package[module_path] = module_package
                modules[module_name] = importlib.import_module(".".join((module_package, module_stem)))
        return modules
    
    def listen_operator(self, operator_name, callback):
        key = uuid.uuid4()
        self.__listen_operators[key] = {"operator": operator_name, "callback": callback}
        return key

    def listen_mode(self, modes, **kwargs):
        key = uuid.uuid4()
        self.__listen_modes[key] = {"modes": modes, **kwargs}
        return key

    def listen_depsgraph_update(self, callback):
        key = uuid.uuid4()
        self.__listen_depsgraph_updates[key] = callback
        return key

    def listen_handler(self, handler_name, callback):
        args_count = len(inspect.signature(callback).parameters)
        @bpy.app.handlers.persistent
        def wrapped_callback(*args):
            return callback(*args[:args_count])
        
        key = uuid.uuid4()
        self.__listen_handlers[key] = (handler_name, wrapped_callback)
        getattr(bpy.app.handlers, handler_name).append(wrapped_callback)
        return key

    def listen_timer(self, callback, **kwargs): #only use for repeating timers, not one-time timers
        bpy.app.timers.register(callback, **kwargs)

        key = uuid.uuid4()
        self.__listen_timers[key] = callback
        return key

    def unlisten(self, key):
        if key in self.__listen_operators:
            self.__listen_operators.pop(key)
        elif key in self.__listen_modes:
            self.__listen_modes.pop(key)
        elif key in self.__listen_depsgraph_updates:
            self.__listen_depsgraph_updates.pop(key)
        elif key in self.__listen_handlers:
            listener = self.__listen_handlers.pop(key)
            if listener[1] in getattr(bpy.app.handlers, listener[0]):
                getattr(bpy.app.handlers, listener[0]).remove(listener[1])
        elif key in self.__listen_timers:
            callback = self.__listen_timers.pop(key)
            if bpy.app.timers.is_registered(callback):
                bpy.app.timers.unregister(callback)

    def get_resources_path(self, package):
        addon_path = self.addon_paths[package]
        resources_path = addon_path.joinpath("resources")
        if resources_path.is_dir():
            return resources_path
    
    @contextmanager
    def load_resources(self, file_path, *args):
        file_path_str = str(file_path)
        id_names_dict = {}
        with bpy.data.libraries.load(file_path_str) as (data_from, data_to):
            for attr in args:
                id_names_dict[attr] = getattr(data_from, attr).copy()
                setattr(data_to, attr, getattr(data_from, attr))

        resources = {}
        def add_resource(attr, id_name, id):
            resources[attr] = {} if not attr in resources else resources[attr]
            resources[attr][id_name] = id

        def iterate_ids(func):
            for attr in dir(bpy.data):
                prop_collection = getattr(bpy.data, attr, None)
                if isinstance(prop_collection, bpy.types.bpy_prop_collection):
                    for id in prop_collection:
                        ref = id.library_weak_reference
                        if ref and (ref.filepath == file_path_str):
                            func(attr, id, ref, prop_collection)

        iterate_ids(lambda attr, id, ref, prop_collection: add_resource(attr, ref.id_name[2:], id))
        for attr, id_names in id_names_dict.items():
            loaded_ids = getattr(data_to, attr)
            for i in range(len(loaded_ids)):
                add_resource(attr, id_names[i], loaded_ids[i])
        try:
            yield resources
        finally:
            iterate_ids(lambda attr, id, ref, prop_collection: prop_collection.remove(id))
    
    @contextmanager
    def pause_updates(self):
        try:
            self.__depsgraph_paused += 1
            yield True
        finally:
            self.__depsgraph_paused -= 1
    
    def __create_panel(self, root_package_name, addon_draws):
        store_addon_draws = addon_draws.copy()
        def panelDraw(self, context):
            layout = self.layout
            for draw, _ in store_addon_draws:
                draw(layout, context)
        panelClass = type(f"VIEW3D_PT_{root_package_name}", (bpy.types.Panel,), {
            "bl_space_type": "VIEW_3D",
            "bl_region_type": "UI",
            "bl_category": root_package_name,
            "bl_label": root_package_name,
            "draw": panelDraw
        })
        self.__addon_panels.append(panelClass)

    def register(self, recorded_prefs=None):
        self.addon_paths = {}
        self.__loaded_addons = []
        self.__lookup_package = {}
        self.__modules = {}
        self.__registered_modules = []
        self.__registered_modules_returns = []
        self.__dependency_stack = []

        self.__listen_operators = {}
        self.__listen_modes = {}
        self.__listen_depsgraph_updates = {}
        self.__listen_handlers = {}
        self.__listen_timers = {}
        self.__depsgraph_paused = 0

        def depsgraph_update_post(scene, depsgraph):
            active_operator = bpy.context.active_operator
            if active_operator:
                operator_name = active_operator.bl_idname
                for listener in self.__listen_operators.values():
                    if listener["operator"] == operator_name:
                        listener["callback"]()
            if self.__depsgraph_paused == 0:
                for callback in self.__listen_depsgraph_updates.values():
                    callback(depsgraph)

        last_mode = "OBJECT"
        def deferred_mode_updates():
            nonlocal last_mode
            if self.__depsgraph_paused == 0:
                new_mode = "OBJECT"
                if bpy.context.active_object:
                    new_mode = bpy.context.active_object.mode

                if new_mode != last_mode:
                    for listener in self.__listen_modes.values():
                        modes = listener["modes"]
                        if (new_mode in modes) and not (last_mode in modes):
                            if ("enter" in listener) and listener["enter"]:
                                listener["enter"](last_mode)
                        elif not (new_mode in modes) and (last_mode in modes):
                            if ("exit" in listener) and listener["exit"]:
                                listener["exit"](new_mode)
                    last_mode = new_mode
            return 0.001
        
        def load_post(file):
            nonlocal last_mode
            last_mode = "OBJECT"

        self.__listeners = (
            self.listen_handler("depsgraph_update_post", depsgraph_update_post),
            self.listen_timer(deferred_mode_updates, persistent=True),
            self.listen_handler("load_post", load_post),
        )

        self.__prefs_props = {}
        self.__prefs_draws = []

        self.__addon_draws = {}
        self.__addon_panels = []

        self.load_addon(__package__, __file__)
        if recorded_prefs:
            for extension in recorded_prefs["extension_list"]:
                self.load_addon(extension["root_package"], extension["root_file_path_name"])
        for module_name in self.__modules.keys():
            self.import_module(module_name)

        for root_package, addon_draws in self.__addon_draws.items():
            if len(addon_draws) > 0:
                match = re.search("[^\.]*$", root_package)
                self.__create_panel(match.group(0) if match else "", addon_draws)
        self.__addon_draws = None

        prefs_draws = self.__prefs_draws
        class AddonPrefs(bpy.types.AddonPreferences):
            bl_idname = __package__
            def draw(self, context):
                layout = self.layout
                for draw_func in prefs_draws:
                    draw_func(self, layout)
        for pref_name, property_def in self.__prefs_props.items():
            AddonPrefs.__annotations__[pref_name] = property_def
        self.__prefs_props = None
        self.__prefs_draws = None
        self.__addon_prefs_class = AddonPrefs

        bpy.utils.register_class(self.__addon_prefs_class)
        for addon_panel in self.__addon_panels:
            bpy.utils.register_class(addon_panel)
        self.prefs = bpy.context.preferences.addons[__package__].preferences

        for returns in self.__registered_modules_returns:
            if "post_registration" in returns:
                returns["post_registration"]()

        post_registration_load_flag = uuid.uuid4()
        self.__post_registration_load_flag = post_registration_load_flag
        def post_registration_loaded():
            if self.__post_registration_load_flag == post_registration_load_flag:
                for returns in self.__registered_modules_returns:
                    if "post_registration_loaded" in returns:
                        returns["post_registration_loaded"]()
        bpy.app.timers.register(post_registration_loaded)

    def unregister(self):
        self.__post_registration_load_flag = None
        self.__reload_flag = None
        recorded_prefs = record_prefs(self.prefs) if self.prefs else None

        for listener in self.__listeners:
            self.unlisten(listener)
        self.__registered_modules_returns.reverse()
        for returns in self.__registered_modules_returns:
            if "unregister" in returns:
                returns["unregister"]()
            if "classes" in returns:
                for cls in returns["classes"]:
                    bpy.utils.unregister_class(cls)
            if "threads" in returns:
                for thread in returns["threads"]:
                    thread.stop()
            if "listeners" in returns:
                for listener in returns["listeners"]:
                    self.unlisten(listener)
        
        if self.__addon_prefs_class:
            bpy.utils.unregister_class(self.__addon_prefs_class)
            for addon_panel in self.__addon_panels:
                bpy.utils.unregister_class(addon_panel)
        return recorded_prefs

    def reload(self):
        reload_flag = uuid.uuid4()
        self.__reload_flag = reload_flag
        def delayed_reload():
            if self.__reload_flag == reload_flag:
                recorded_prefs = self.unregister()
                for loaded_module_name in tuple(sys.modules):
                    for package_name in self.__loaded_addons:
                        if loaded_module_name.startswith(package_name) and (package_name != package_name):
                            del sys.modules[loaded_module_name]
                            break
                self.register(recorded_prefs)
        bpy.app.timers.register(delayed_reload)

def register():
    global utils
    utils = Utils()
    utils.register()
    bpy.context.preferences.use_preferences_save = True #this is necessary to get programmatically-set addonprefs to save on close

def unregister():
    global utils
    utils.unregister()
    utils = None