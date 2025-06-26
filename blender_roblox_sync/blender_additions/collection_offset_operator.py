import bpy, mathutils, math

def register(utils, package):
    AXES = {
        "x_offset": (mathutils.Euler((0, math.radians(90), 0)), mathutils.Vector((0, 1, 1)), mathutils.Color((1, 0, 0))),
        "y_offset": (mathutils.Euler((math.radians(-90), 0, 0)), mathutils.Vector((1, 0, 1)), mathutils.Color((0, 1, 0))),
        "z_offset": (mathutils.Euler(), mathutils.Vector((1, 1, 0)), mathutils.Color((0, 0, 1)))
    }
    def update_axis(collection, context):
        collection.instance_offset = mathutils.Vector((collection.x_offset, collection.y_offset, collection.z_offset))
    for axis in AXES.keys():
        setattr(bpy.types.Collection, axis, bpy.props.FloatProperty(default=0, update=update_axis))

    class TestClass():
        bl_label = "Test Light Widget"
        bl_space_type = 'VIEW_3D'
        bl_region_type = 'WINDOW'
        bl_options = {"3D", "PERSISTENT", "SCALE"}
        is_inner = False

        @classmethod
        def poll(cls, context):
            return context.collection != None

        def setup(self, context):
            self.target = context.collection
            self.arrows = {}

            instance_offset = self.target.instance_offset
            for axis, info in AXES.items():
                arrow = self.gizmos.new("GIZMO_GT_arrow_3d")
                orientation, mask, color = info
                offset = instance_offset.copy()
                if self.is_inner:
                    arrow.target_set_prop("offset", self.target, axis)
                    offset *= mask
                arrow.line_width = 6
                arrow.scale_basis = 1.5
                arrow.matrix_basis = mathutils.Matrix.LocRotScale(offset, orientation, None)
                arrow.draw_style = "NORMAL"

                new_color = color.copy()
                if self.is_inner:
                    new_color.s = 1
                    new_color.v = 0.4
                    arrow.alpha = 0.2
                else:
                    new_color.s = 0.8
                    new_color.v = 1
                    arrow.alpha = 1
                arrow.color = (new_color.r, new_color.g, new_color.b)

                if self.is_inner:
                    highlight_color = color.copy()
                    highlight_color.s = 0.3
                    highlight_color.v = 1
                    arrow.color_highlight = (highlight_color.r, highlight_color.g, highlight_color.b)
                    arrow.alpha_highlight = 0.4
                else:
                    arrow.select_bias = -math.inf
                self.arrows[axis] = arrow

        def refresh(self, context):
            instance_offset = self.target.instance_offset
            for axis, arrow in self.arrows.items():
                orientation, mask, _ = AXES[axis]
                offset = instance_offset.copy()
                if self.is_inner:
                    arrow.target_set_prop("offset", self.target, axis)
                    offset *= mask
                arrow.matrix_basis = mathutils.Matrix.LocRotScale(offset, orientation, None)
    
    class WidgetGroup(bpy.types.GizmoGroup, TestClass):
        bl_idname = "meowmeow"
        is_inner = True
    class WidgetGroup2(bpy.types.GizmoGroup, TestClass):
        bl_idname = "meowmeow2"
        bl_options = TestClass.bl_options | {"DEPTH_3D"}
    return {
        "classes": (WidgetGroup, WidgetGroup2,)
    }