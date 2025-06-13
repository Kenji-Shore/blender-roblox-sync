import bpy, mathutils, time, math

def register(utils):
    
    fly_directions = {
        "W": mathutils.Vector((0, 0, -1)),
        "S": mathutils.Vector((0, 0, 1)),
        "A": mathutils.Vector((-1, 0, 0)),
        "D": mathutils.Vector((1, 0, 0)),
        "Q": mathutils.Vector((0, -1, 0)),
        "E": mathutils.Vector((0, 1, 0)),
    }

    OFFSET = 0.1

    fly_running = False
    fly_handle_3d = None
    fly_timer = None
    fly_cursor = None
    fly_original_distance = None
    fly_mouse_pos = None
    region_3d = None
    def stop_fly():
        nonlocal fly_running
        nonlocal fly_handle_3d
        nonlocal fly_timer
        nonlocal fly_cursor
        nonlocal fly_original_distance
        nonlocal fly_mouse_pos
        nonlocal region_3d

        fly_running = False
        if fly_handle_3d:
            bpy.types.SpaceView3D.draw_handler_remove(fly_handle_3d, 'WINDOW')
            fly_handle_3d = None
        if fly_timer:
            bpy.context.window_manager.event_timer_remove(fly_timer)
            fly_timer = None
        if fly_cursor:
            bpy.context.window_manager.draw_cursor_remove(fly_cursor)
            fly_cursor = None

        if region_3d:
            look_vec = region_3d.view_rotation @ mathutils.Vector((0, 0, -1))
            region_3d.view_location += look_vec * fly_original_distance
            region_3d.view_distance = fly_original_distance + OFFSET

            bpy.context.window.cursor_warp(*fly_mouse_pos)
            bpy.context.window.cursor_modal_restore()
            region_3d = None
            fly_original_distance = None
            fly_mouse_pos = None
        
    def draw_callback_3d(self, context):
        new_time = time.process_time()
        delta_time = new_time - self.last_time
        self.last_time = new_time

        delta_x = self.mouse_delta_x
        delta_y = self.mouse_delta_y
        self.mouse_delta_x = 0
        self.mouse_delta_y = 0

        region_3d = context.space_data.region_3d
        fly_vec = mathutils.Vector()
        for key in self.active_keys:
            if key in fly_directions:
                fly_vec += fly_directions[key]
        rot = region_3d.view_rotation        
        region_3d.view_location += (rot @ fly_vec) * 40 * (0.3 if "LEFT_SHIFT" in self.active_keys else 1) * delta_time * self.fly_speed

        if "RIGHTMOUSE" in self.active_keys:
            x_delta = 2000 * (delta_x / context.area.width) * delta_time
            y_delta = 1200 * (delta_y / context.area.height) * delta_time
            self.target_rot_z += x_delta
            self.target_rot_x = max(min(self.target_rot_x - y_delta, -0.2), -2.6)
            target_euler = mathutils.Euler((self.target_rot_x, 0, self.target_rot_z), "ZXY")
            target_rot = target_euler.to_quaternion().inverted().normalized()
            region_3d.view_rotation = rot.slerp(target_rot, max(min(30 * delta_time, 1), 0))

    class VIEW3D_OT_custom_fly(bpy.types.Operator):
        bl_idname = "view3d.custom_fly"
        bl_label = "Custom Fly Operator"
        bl_options = {"REGISTER", "GRAB_CURSOR", "BLOCKING"}

        fly_speed: bpy.props.FloatProperty(name="Some Floating Point", default=1.0)

        def modal(self, context, event):
            if (not fly_running) or (context.space_data.type != "VIEW_3D") or (event.type == "SPACE" and event.value == "PRESS"):
                stop_fly()
                return {'FINISHED'}

            key = event.type
            state = event.value
            if state == "PRESS":
                if not (key in self.active_keys):
                    self.active_keys.append(key)
            elif state == "RELEASE":
                if key in self.active_keys:
                    self.active_keys.remove(key)

            if key == "MOUSEMOVE":
                self.mouse_delta_x += event.mouse_x - event.mouse_prev_x
                self.mouse_delta_y += event.mouse_y - event.mouse_prev_y
            return {'RUNNING_MODAL'}

        def invoke(self, context, event):
            nonlocal fly_running
            nonlocal fly_handle_3d
            nonlocal fly_timer
            nonlocal fly_cursor
            nonlocal fly_original_distance
            nonlocal fly_mouse_pos
            nonlocal region_3d
            stop_fly()

            if context.space_data.type == "VIEW_3D":
                region_3d = context.space_data.region_3d
                region_3d.is_perspective = True
                region_3d.view_perspective = "PERSP"
                
                fly_original_distance = max(region_3d.view_distance, 0.1) - OFFSET
                look_vec = region_3d.view_rotation @ mathutils.Vector((0, 0, -1))
                region_3d.view_location -= look_vec * fly_original_distance
                region_3d.view_distance = OFFSET

                self.last_time = time.process_time()
                fly_mouse_pos = (event.mouse_x, event.mouse_y,)
                self.mouse_delta_x = 0
                self.mouse_delta_y = 0
                self.active_keys = []

                rot = region_3d.view_rotation
                rot_euler = rot.inverted().to_euler("ZXY")
                self.target_rot_z = rot_euler.z
                self.target_rot_x = rot_euler.x

                fly_running = True
                context.window_manager.modal_handler_add(self)
                fly_handle_3d = bpy.types.SpaceView3D.draw_handler_add(draw_callback_3d, (self, context), 'WINDOW', 'PRE_VIEW')
                fly_timer = context.window_manager.event_timer_add(0.01, window=context.window)
                context.window.cursor_modal_set("NONE")
                return {"RUNNING_MODAL"}
            else:
                return {"FINISHED"}

    window_manager = bpy.context.window_manager
    addon_keyconfig = window_manager.keyconfigs.addon

    keyconfig = window_manager.keyconfigs["Blender"]
    for keymap_item in keyconfig.keymaps["Frames"].keymap_items:
        if keymap_item.idname == "screen.animation_play":
            keymap_item.active = False

    if addon_keyconfig:
        keymap = addon_keyconfig.keymaps.new(name="3D View", space_type="VIEW_3D")
        keymap_item = keymap.keymap_items.new("view3d.custom_fly", type="SPACE", value="PRESS")
    
    def unregister():
        stop_fly()
        if keymap:
            keymap.keymap_items.remove(keymap_item)
    return {
        "classes": (VIEW3D_OT_custom_fly,),
        "unregister": unregister
    }