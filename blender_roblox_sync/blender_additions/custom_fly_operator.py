import bpy, mathutils

def register(utils, package):
    FLY_DIRECTIONS = {
        "W": mathutils.Vector((0, 0, -1)),
        "S": mathutils.Vector((0, 0, 1)),
        "A": mathutils.Vector((-1, 0, 0)),
        "D": mathutils.Vector((1, 0, 0)),
        "Q": mathutils.Vector((0, -1, 0)),
        "E": mathutils.Vector((0, 1, 0)),
    }
    OFFSET = 0.1

    currently_running_operator = None
    class VIEW3D_OT_custom_fly(bpy.types.Operator):
        bl_idname = "view3d.custom_fly"
        bl_label = "Custom Fly Operator"
        bl_options = {"REGISTER", "GRAB_CURSOR", "BLOCKING"}

        fly_speed: bpy.props.FloatProperty(name="Some Floating Point", default=1.0)

        def stop_fly(self):
            nonlocal currently_running_operator
            currently_running_operator = None
            self.fly_running = False

            utils.unlisten(self.fly_handle_3d)
            bpy.context.window_manager.event_timer_remove(self.fly_timer)
            bpy.context.window.cursor_warp(*self.fly_mouse_pos)
            bpy.context.window.cursor_modal_restore()

            look_vec = self.region_3d.view_rotation @ mathutils.Vector((0, 0, -1))
            self.region_3d.view_location += look_vec * self.fly_original_distance
            self.region_3d.view_distance = self.fly_original_distance + OFFSET

        def modal(self, context, event):
            if (context.space_data.type != "VIEW_3D") or (event.type == "SPACE" and event.value == "PRESS"):
                self.stop_fly()

            if self.fly_running:
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
            else:
                return {'FINISHED'}

        def invoke(self, context, event):
            nonlocal currently_running_operator
            if context.space_data.type == "VIEW_3D":
                self.region_3d = context.space_data.region_3d
                self.region_3d.is_perspective = True
                self.region_3d.view_perspective = "PERSP"
                
                self.fly_original_distance = max(self.region_3d.view_distance, 0.1) - OFFSET
                look_vec = self.region_3d.view_rotation @ mathutils.Vector((0, 0, -1))
                self.region_3d.view_location -= look_vec * self.fly_original_distance
                self.region_3d.view_distance = OFFSET

                self.fly_mouse_pos = (event.mouse_x, event.mouse_y,)
                self.mouse_delta_x = 0
                self.mouse_delta_y = 0
                self.active_keys = []

                rot = self.region_3d.view_rotation
                rot_euler = rot.inverted().to_euler("ZXY")
                self.target_rot_z = rot_euler.z
                self.target_rot_x = rot_euler.x

                def draw_callback_3d(delta_time):
                    delta_x = self.mouse_delta_x
                    delta_y = self.mouse_delta_y
                    self.mouse_delta_x = 0
                    self.mouse_delta_y = 0

                    fly_vec = mathutils.Vector()
                    for key in self.active_keys:
                        if key in FLY_DIRECTIONS:
                            fly_vec += FLY_DIRECTIONS[key]
                    rot = self.region_3d.view_rotation        
                    self.region_3d.view_location += (rot @ fly_vec) * 40 * (0.3 if "LEFT_SHIFT" in self.active_keys else 1) * delta_time * self.fly_speed

                    if "RIGHTMOUSE" in self.active_keys:
                        x_delta = 2000 * (delta_x / context.area.width) * delta_time
                        y_delta = 1200 * (delta_y / context.area.height) * delta_time
                        self.target_rot_z += x_delta
                        self.target_rot_x = max(min(self.target_rot_x - y_delta, -0.2), -2.6)
                        target_euler = mathutils.Euler((self.target_rot_x, 0, self.target_rot_z), "ZXY")
                        target_rot = target_euler.to_quaternion().inverted().normalized()
                        self.region_3d.view_rotation = rot.slerp(target_rot, max(min(30 * delta_time, 1), 0))

                self.fly_handle_3d = utils.listen_draw(draw_callback_3d, is_pre_view=True)
                self.fly_timer = context.window_manager.event_timer_add(0.01, window=context.window)
                context.window_manager.modal_handler_add(self)
                context.window.cursor_modal_set("NONE")

                self.fly_running = True
                currently_running_operator = self
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
        if currently_running_operator:
            currently_running_operator.stop_fly()
        if keymap:
            keymap.keymap_items.remove(keymap_item)
    return {
        "classes": (VIEW3D_OT_custom_fly,),
        "unregister": unregister
    }