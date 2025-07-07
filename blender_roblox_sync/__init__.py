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

import bpy, queue, importlib, pathlib, inspect, uuid, sys
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
            self.__loaded_addons.append(root_package)
            self.addon_paths.append(root_file_path.parent)
            self.__lookup_package[root_file_path] = root_package
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

    def load_resources(self, file_path, *args):
        with bpy.data.libraries.load(file_path) as (data_from, data_to):
            for attr in args:
                setattr(data_to, attr, getattr(data_from, attr))

        resources = {}
        temp_dict = {}
        def add_resources(attr):
            if len(temp_dict) > 0:
                if not attr in resources:
                    resources[attr] = {}
                resources[attr].update(temp_dict)
                temp_dict.clear()

        for attr in dir(bpy.data):
            prop_collection = getattr(bpy.data, attr, None)
            if isinstance(prop_collection, bpy.types.bpy_prop_collection):
                for id in prop_collection:
                    if id.library_weak_reference and (id.library_weak_reference.filepath == file_path):
                        id.is_runtime_data = True
                        temp_dict[id.name] = id
                add_resources(attr)
        for attr in args:
            for id in getattr(data_to, attr):
                id.is_runtime_data = True
                temp_dict[id.name] = id
            add_resources(attr)
        return resources

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

    @contextmanager
    def pause_updates(self):
        try:
            self.__depsgraph_paused += 1
            yield True
        finally:
            self.__depsgraph_paused -= 1
        
    def register(self, recorded_prefs=None):
        self.addon_paths = []
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

        mode_updates = queue.Queue()
        def depsgraph_update_post(scene, depsgraph):
            if self.__depsgraph_paused == 0:
                for callback in self.__listen_depsgraph_updates.values():
                    callback()
                active_operator = bpy.context.active_operator
                if active_operator:
                    operator_name = active_operator.bl_idname
                    for listener in self.__listen_operators.values():
                        if listener["operator"] == operator_name:
                            listener["callback"]()
                if bpy.context.active_object:
                    mode_updates.put(bpy.context.active_object.mode)

        last_mode = None
        def deferred_mode_updates():
            nonlocal last_mode
            new_mode = None
            while not mode_updates.empty():
                new_mode = mode_updates.get()

            if new_mode and (new_mode != last_mode):
                store_last_mode = last_mode
                last_mode = new_mode
                
                for listener in self.__listen_modes.values():
                    modes = listener["modes"]
                    if (new_mode in modes) and not (store_last_mode in modes):
                        if ("enter" in listener) and listener["enter"]:
                            listener["enter"](store_last_mode)
                    elif not (new_mode in modes) and (store_last_mode in modes):
                        if ("exit" in listener) and listener["exit"]:
                            listener["exit"](new_mode)
            return 0.001

        self.__listeners = (
            self.listen_handler("depsgraph_update_post", depsgraph_update_post),
            self.listen_timer(deferred_mode_updates, persistent=True)
        )

        self.__prefs_props = {}
        self.__prefs_draws = []

        self.load_addon(__package__, __file__)
        if recorded_prefs:
            for extension in recorded_prefs["extension_list"]:
                self.load_addon(extension["root_package"], extension["root_file_path_name"])
        for module_name in self.__modules.keys():
            self.import_module(module_name)

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
        self.prefs = bpy.context.preferences.addons[__package__].preferences

        for returns in self.__registered_modules_returns:
            if "post_registration" in returns:
                returns["post_registration"]()

    def unregister(self):
        recorded_prefs = record_prefs(self.prefs) if self.prefs else None

        self.__reload_flag = None
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