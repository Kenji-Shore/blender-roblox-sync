import bpy, mathutils

def register(utils, package):
    custom_objects = utils.import_module("custom_objects")
    
    shaders_path = utils.get_path(package, "shaders")
    INVISIBLE_VERT = shaders_path.joinpath("uniform_color_vert.glsl").read_text()
    INVISIBLE_FRAG = shaders_path.joinpath("uniform_color_frag.glsl").read_text()

    COLORS = {
        "Red": mathutils.Color((1, 0, 0)),
        "Green": mathutils.Color((0, 1, 0)),
        "Blue": mathutils.Color((0, 0, 1)),
        "Purple": mathutils.Color((1, 0, 1)),
        "Yellow": mathutils.Color((1, 1, 0)),
        "Brown": mathutils.Color((0.5, 0.25, 0)),
        "White": mathutils.Color((1, 1, 1)),
    }
    def get_color(custom_object):
        color = COLORS[custom_object.tied_object.invisible_color].copy()
        if not custom_object.draw_edges:
            color.s *= 0.5
        return (color.r, color.g, color.b) + ((1 if custom_object.draw_edges else 0.2),)
    
    INVISIBLE_OBJECT = custom_objects.create_shader(
        vertex=INVISIBLE_VERT,
        fragment=INVISIBLE_FRAG,
        uniforms=(("color", {
            "type": "VEC4",
            "set": "uniform_float",
            "get_value": get_color,
        }),)
    )

    invisible_objects = {}
    def destroy_invisible_object(object):
        if object.original in invisible_objects:
            invisible_faces, invisible_edges = invisible_objects[object.original]
            invisible_faces.destroy()
            invisible_edges.destroy()
            del invisible_objects[object.original]
    def update_is_invisible(object, context):
        destroy_invisible_object(object)
        if object.is_invisible:
            invisible_faces = custom_objects.CustomObject(
                object=object, 
                shader=INVISIBLE_OBJECT, 
                gpu_states={
                    "blend_set": "ALPHA",
                    "face_culling_set": "NONE",
                },
                draw_order=-10,
                tied_to_object=True,
            )
            invisible_edges = custom_objects.CustomObject(
                object=object, 
                shader=INVISIBLE_OBJECT, 
                gpu_states={
                    "depth_test_set": "NONE",
                },
                draw_order=-9,
                draw_edges=True,
                tied_to_object=True,
            )
            invisible_objects[object.original] = (invisible_faces, invisible_edges)
    bpy.types.Object.is_invisible = bpy.props.BoolProperty(default=False, update=update_is_invisible)
    bpy.types.Object.invisible_color = bpy.props.EnumProperty(items=[(key, key, "") for key in COLORS.keys()], default="Red")

    def object_visibility_change(object, is_visible):
        if is_visible:
            update_is_invisible(object, bpy.context)
        else:
            destroy_invisible_object(object)
    def draw(layout, context):
        box = layout.box()
        active_object = bpy.context.object
        if active_object:
            row = box.row()
            row.prop(active_object, "is_invisible", text="Is Invisible")
            if active_object.is_invisible:
                row = box.row()
                row.prop(active_object, "invisible_color", text="Color")
    return {
        "listeners": (utils.listen_object_visibility_change(object_visibility_change),),
        "draw": draw,
    }