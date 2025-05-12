import bpy
from contextlib import contextmanager
import queue

def get_loop_uvs(uv_layers):
    for uv_layer in uv_layers:
        if uv_layer.active_render:
            return uv_layer.uv

__listen_operators = {}
def listen_operator(operator_name, callback):
    key = ()
    __listen_operators[key] = {"operator": operator_name, "callback": callback}
    return key

__mode_updates = queue.Queue()
__listen_modes = {}
def listen_mode(modes, **kwargs):
    key = ()
    __listen_modes[key] = {"modes": modes, **kwargs}
    return key

__listen_depsgraph_updates = {}
def listen_depsgraph_update(callback):
    key = ()
    __listen_depsgraph_updates[key] = callback
    return key

def unlisten(key):
    if key in __listen_operators:
        __listen_operators.pop(key)
    elif key in __listen_modes:
        __listen_modes.pop(key)
    elif key in __listen_depsgraph_updates:
        __listen_depsgraph_updates.pop(key)

__last_mode = None
@bpy.app.handlers.persistent
def depsgraph_update_post(scene, depsgraph):
    for callback in __listen_depsgraph_updates.values():
        callback()

    active_operator = bpy.context.active_operator
    if active_operator:
        operator_name = active_operator.bl_idname
        for listener in __listen_operators.values():
            if listener["operator"] == operator_name:
                listener["callback"]()

    global __last_mode
    if bpy.context.active_object:
        __mode_updates.put(bpy.context.active_object.mode)

def register_depsgraph_updates():
    bpy.app.handlers.depsgraph_update_post.append(depsgraph_update_post)
def unregister_depsgraph_updates():
    if depsgraph_update_post in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.remove(depsgraph_update_post)
        return True

__depsgraph_paused = 0
@contextmanager
def pause_updates():
    global __depsgraph_paused
    depsgraph_update_existed = False
    try:
        if __depsgraph_paused == 0:
            depsgraph_update_existed = unregister_depsgraph_updates()
        __depsgraph_paused += 1
        yield True
    finally:
        __depsgraph_paused -= 1
        if (__depsgraph_paused == 0) and depsgraph_update_existed:
            register_depsgraph_updates()

def deferred_mode_updates():
    global __last_mode
    new_mode = None
    while not __mode_updates.empty():
        new_mode = __mode_updates.get()

    if new_mode and (new_mode != __last_mode):
        store_last_mode = __last_mode
        __last_mode = new_mode
        
        for listener in __listen_modes.values():
            modes = listener["modes"]
            if (new_mode in modes) and not (store_last_mode in modes):
                if ("enter" in listener) and listener["enter"]:
                    listener["enter"](store_last_mode)
            elif not (new_mode in modes) and (store_last_mode in modes):
                if ("exit" in listener) and listener["exit"]:
                    listener["exit"](new_mode)
    return 0.001

def register():
    bpy.app.timers.register(deferred_mode_updates, persistent=True)
    register_depsgraph_updates()
def unregister():
    if bpy.app.timers.is_registered(deferred_mode_updates):
        bpy.app.timers.unregister(deferred_mode_updates)
    unregister_depsgraph_updates()