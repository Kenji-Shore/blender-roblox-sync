import bpy, mathutils, math, gpu

def register(utils, package):
    custom_objects = utils.import_module("custom_objects")
    shaders_path = utils.get_path(package, "shaders")
    GRID_VERT = shaders_path.joinpath("uniform_color_vert.glsl").read_text()
    GRID_FRAG = shaders_path.joinpath("uniform_color_frag.glsl").read_text()

    def get_color(instance, states, geometry_type):
        return instance.color
    GRID = custom_objects.create_shader(
        vertex=GRID_VERT,
        fragment=GRID_FRAG,
        uniforms=(("color", {
            "type": "VEC4",
            "instance": True,
            "value": get_color,
        }),),
        interfaces={"color": ("flat", "VEC4")},
    )

    AXES = {
        "x_offset": (mathutils.Euler((0, math.radians(90), 0)), mathutils.Vector((0, 1, 1)), mathutils.Color((1, 0, 0))),
        "y_offset": (mathutils.Euler((math.radians(-90), 0, 0)), mathutils.Vector((1, 0, 1)), mathutils.Color((0, 1, 0))),
        "z_offset": (mathutils.Euler(), mathutils.Vector((1, 1, 0)), mathutils.Color((0, 0, 1)))
    }
    def update_axis(collection, context):
        collection.instance_offset = mathutils.Vector((collection.x_offset, collection.y_offset, collection.z_offset))
    for axis in AXES.keys():
        setattr(bpy.types.Collection, axis, bpy.props.FloatProperty(default=0, update=update_axis))

    class CollectionOffset(bpy.types.GizmoGroup):
        bl_idname = "OBJECT_GGT_collection_offset"
        bl_label = "Collection Offset Widget"
        bl_space_type = "VIEW_3D"
        bl_region_type = "WINDOW"
        bl_options = {"3D", "PERSISTENT", "SCALE"}
        is_inner = False

        @classmethod
        def poll(cls, context):
            return context.scene.editing_collection != None

        def setup(self, context):
            self.target = context.scene.editing_collection
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
            for grid_info in GRIDS.values():
                grid_instance = grid_info["grid_instance"]
                grid_instance.transform = mathutils.Matrix.LocRotScale(instance_offset, grid_info["rot"], None)
                grid_instance.visible = True

            for axis, arrow in self.arrows.items():
                orientation, mask, _ = AXES[axis]
                offset = instance_offset.copy()
                if self.is_inner:
                    arrow.target_set_prop("offset", self.target, axis)
                    offset *= mask
                arrow.matrix_basis = mathutils.Matrix.LocRotScale(offset, orientation, None)
    
    # class WidgetGroup(bpy.types.GizmoGroup, TestClass):
    #     bl_idname = "meowmeow"
    #     is_inner = True
    # class WidgetGroup2(bpy.types.GizmoGroup, TestClass):
    #     bl_idname = "meowmeow2"
    #     bl_options = TestClass.bl_options | {"DEPTH_3D"}

    GRID_SCALE = mathutils.Vector((0.5, 0.5, 0.5))
    GRIDS = {
        "xy": {
            "rot": mathutils.Euler((0, 0.5 * math.pi, 0)).to_quaternion(),
            "color": (0.9, 0.3, 0.3, 1),
        },
        "xz": {
            "rot": mathutils.Euler((0.5 * math.pi, 0, 0)).to_quaternion(),
            "color": (0.3, 0.9, 0.3, 1),
        },
        "yz": {
            "rot": mathutils.Euler((0, 0, 0)).to_quaternion(),
            "color": (0.3, 0.3, 0.9, 1),
        }
    }
    def post_registration_loaded():
        resources_path = utils.get_path(package, "resources")
        with utils.load_resources(resources_path.joinpath("Grid.blend"), "objects") as resources:
            grid = custom_objects.CustomObject(
                object=resources["objects"]["Grid"], 
                shader=GRID,
                draw_order=-10,
            )
        
        for grid_info in GRIDS.values():
            grid_instance = grid.new(
                transform=mathutils.Matrix.LocRotScale(mathutils.Vector(), grid_info["rot"], None),
                scale=GRID_SCALE
            )
            grid_instance.color = grid_info["color"]
            grid_instance.visible = False
            grid_info["grid_instance"] = grid_instance

    def draw(layout, context, editing_collection):
        layout.label(text="Currently Syncing:")
    
    return {
        "classes": (CollectionOffset,),
        "post_registration_loaded": post_registration_loaded,
        "draw": {
            "function": draw,
            "assign_to": "collection_properties"
        },
    }