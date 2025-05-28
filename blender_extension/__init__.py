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

import bpy, queue, importlib, pathlib
from contextlib import contextmanager

class Utils:
    ROOT_PACKAGE = __package__
    def glob_from_parent(self, file_path_name, glob_str):
        file_path = pathlib.Path(file_path_name)
        parent_path = file_path.parent
        modules = {}
        for module_path in parent_path.glob(glob_str):
            if module_path != file_path:
                relative_path = module_path.relative_to(__file__)
                module_name = relative_path.stem
                parts = (self.ROOT_PACKAGE,) + relative_path.parts[:-1] + (module_name,)
                if module_name == "__init__":
                    module_name = parts[-2]
                modules[module_name] = importlib.import_module(".".join(parts))
        return modules
    
    __listen_operators = {}
    def listen_operator(self, operator_name, callback):
        key = ()
        self.__listen_operators[key] = {"operator": operator_name, "callback": callback}
        return key

    __listen_modes = {}
    def listen_mode(self, modes, **kwargs):
        key = ()
        self.__listen_modes[key] = {"modes": modes, **kwargs}
        return key

    __listen_depsgraph_updates = {}
    def listen_depsgraph_update(self, callback):
        key = ()
        self.__listen_depsgraph_updates[key] = callback
        return key

    __listen_handlers = {}
    def listen_handler(self, handler_name, callback):
        @bpy.app.handlers.persistent
        def wrapped_callback(*args):
            return callback(*args)
        
        key = ()
        self.__listen_handlers[key] = (handler_name, wrapped_callback)
        getattr(bpy.app.handlers, handler_name).append(wrapped_callback)
        return key

    __listen_timers = {}
    def listen_timer(self, callback, **kwargs): #only use for repeating timers, not one-time timers
        bpy.app.timers.register(callback, **kwargs)

        key = ()
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

    __depsgraph_paused = 0
    @contextmanager
    def pause_updates(self):
        try:
            self.__depsgraph_paused += 1
            yield True
        finally:
            self.__depsgraph_paused -= 1

    def import_module(self, module_name):
        if module_name in self.__modules:
            module = self.__modules[module_name]
            if not (module_name in self.__registered_modules):
                if module_name in self.__dependency_stack:
                    raise Exception("Circular module import detected!")
                
                self.__dependency_stack.append(module_name)
                if hasattr(module, "register"):
                    returns = getattr(module, "register")(utils)
                    if returns:
                        if "classes" in returns:
                            for cls in returns["classes"]:
                                bpy.utils.register_class(cls)
                        if "threads" in returns:
                            for thread in returns["threads"]:
                                thread.start()
                        self.__registered_modules_returns.append(returns)
                self.__registered_modules.append(module_name)
                self.__dependency_stack.remove(module_name)
            return module
        
    def __init__(self):
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
            self.listen_timer(deferred_mode_updates, persistent=True),
        )

        self.__modules = self.glob_from_parent(__file__, "**/*.py")
        self.__registered_modules = []
        self.__registered_modules_returns = []
        self.__dependency_stack = []
        for module_name in self.__modules.keys():
            self.import_module(module_name)

    def __del__(self):
        for listener in self.__listeners:
            self.unlisten(listener)
        self.__registered_modules_returns.reverse()
        for returns in self.__registered_modules_returns:
            if "unregister" in returns:
                returns["unregister"]()
            if "classes" in returns:
                for cls in returns["classes"]:
                    bpy.utils.register_class(cls)
            if "threads" in returns:
                for thread in returns["threads"]:
                    thread.stop()
            if "listeners" in returns:
                for listener in returns["listeners"]:
                    self.unlisten(listener)

def register():
    global utils
    utils = Utils()

def unregister():
    del utils