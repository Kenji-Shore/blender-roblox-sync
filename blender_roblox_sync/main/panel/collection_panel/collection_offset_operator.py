import bpy, mathutils, math

def register(utils, package):
    collection_properties = utils.import_module("collection_properties")
    custom_objects = utils.import_module("custom_objects")
    shaders_path = utils.get_path(package, "shaders")
    GRID_VERT = shaders_path.joinpath("uniform_color_vert.glsl").read_text()
    GRID_FRAG = shaders_path.joinpath("uniform_color_frag.glsl").read_text()

    def get_color(instance, states, geometry_type):
        color = instance.color.copy()
        if geometry_type == "edges":
            color.v *= 0.5
        return (color.r, color.g, color.b) + ((1 if geometry_type == "edges" else instance.alpha * 0.7),)
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
    ARROWS = {}
    def update_axis(collection, context):
        collection.instance_offset = mathutils.Vector((collection.x_offset, collection.y_offset, collection.z_offset))
    for axis in AXES.keys():
        setattr(bpy.types.Collection, axis, bpy.props.FloatProperty(default=0, update=update_axis))

    GRID_SCALE = mathutils.Vector((0.8, 0.8, 0.8))
    GRIDS = {
        "xy": {
            "rot": mathutils.Euler((0, 0.5 * math.pi, 0)).to_quaternion(),
            "color": mathutils.Color((1, 0, 0)),
        },
        "xz": {
            "rot": mathutils.Euler((0.5 * math.pi, 0, 0)).to_quaternion(),
            "color": mathutils.Color((0, 1, 0)),
        },
        "yz": {
            "rot": mathutils.Euler((0, 0, 0)).to_quaternion(),
            "color": mathutils.Color((0, 0, 1)),
        }
    }

    gizmo_running = False
    target_collection = None
    def gizmo_run():
        nonlocal target_collection
        nonlocal gizmo_running
        if collection_properties.currently_selected != None:
            gizmo_running = True
            target_collection = collection_properties.currently_selected
    def gizmo_cleanup():
        nonlocal target_collection
        nonlocal gizmo_running
        gizmo_running = False
        target_collection = None
        
        for grid_info in GRIDS.values():
            grid_instance = grid_info["grid_instance"]
            grid_instance.visible = False
    
    class VIEW3D_OT_toggle_collection_offset(bpy.types.Operator):
        bl_idname = "view3d.toggle_collection_offset"
        bl_label = "Toggle Collection Offset"
        bl_options = {"REGISTER", "UNDO"}

        def execute(self, context):
            nonlocal gizmo_running
            if gizmo_running:
                gizmo_cleanup()
            else:
                gizmo_run()
            return {"FINISHED"}

    class CollectionOffset(bpy.types.GizmoGroup):
        bl_idname = "OBJECT_GGT_collection_offset"
        bl_label = "Collection Offset Widget"
        bl_space_type = "VIEW_3D"
        bl_region_type = "WINDOW"
        bl_options = {"3D", "PERSISTENT", "SCALE"}

        @classmethod
        def poll(cls, context):
            can_run = (target_collection != None) and (target_collection == collection_properties.currently_selected) and utils.id_exists(target_collection)
            if gizmo_running and (not can_run):
                gizmo_cleanup()
            return gizmo_running and can_run

        def setup(self, context):
            for axis, info in AXES.items():
                arrow = self.gizmos.new("GIZMO_GT_arrow_3d")
                _, _, color = info

                arrow.line_width = 6
                arrow.scale_basis = 1.5
                arrow.draw_style = "NORMAL"

                new_color = color.copy()
                new_color.s = 0.8
                new_color.v = 1
                arrow.alpha = 1
                arrow.color = (new_color.r, new_color.g, new_color.b)

                highlight_color = color.copy()
                highlight_color.s = 0.6
                highlight_color.v = 1
                arrow.color_highlight = (highlight_color.r, highlight_color.g, highlight_color.b)
                ARROWS[axis] = arrow

        def refresh(self, context):
            instance_offset = target_collection.instance_offset
            for axis, arrow in ARROWS.items():
                orientation, mask, _ = AXES[axis]
                offset = instance_offset.copy()
                arrow.target_set_prop("offset", target_collection, axis)
                offset *= mask
                arrow.matrix_basis = mathutils.Matrix.LocRotScale(offset, orientation, None)

    grid_loaded = False
    def post_registration_loaded():
        nonlocal grid_loaded
        resources_path = utils.get_path(package, "resources")
        with utils.load_resources(resources_path.joinpath("Grid.blend"), "objects") as resources:
            grid = custom_objects.CustomObject(
                object=resources["objects"]["Grid"], 
                shader=GRID,
                draw_geometry=("faces", "edges"),
                draw_order=-6,
            )
        
        for grid_info in GRIDS.values():
            grid_instance = grid.new(
                transform=mathutils.Matrix.Identity(4),
                scale=GRID_SCALE,
            )
            grid_instance.visible = False
            grid_info["grid_instance"] = grid_instance
        grid_loaded = True

    def draw(layout, context, currently_selected):
        if currently_selected:    
            layout.operator("view3d.toggle_collection_offset", text="Stop Edit Offset" if gizmo_running else "Edit Offset")

        if grid_loaded:
            if currently_selected:
                instance_offset = currently_selected.instance_offset
                for grid_info in GRIDS.values():
                    grid_instance = grid_info["grid_instance"]
                    color = grid_info["color"].copy()
                    if currently_selected != target_collection:
                        color.s *= 0.5
                        grid_instance.alpha = 0.2
                    else:
                        grid_instance.alpha = 1
                    grid_instance.color = color
                    grid_instance.transform = mathutils.Matrix.LocRotScale(instance_offset, grid_info["rot"], None)
                    grid_instance.visible = True
            else:
                for grid_info in GRIDS.values():
                    grid_instance = grid_info["grid_instance"]
                    grid_instance.visible = False
    
    return {
        "classes": (CollectionOffset, VIEW3D_OT_toggle_collection_offset),
        "post_registration_loaded": post_registration_loaded,
        "draw": {
            "function": draw,
            "assign_to": "collection_properties"
        },
    }