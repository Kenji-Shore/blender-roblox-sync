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
    def get_color(instance, states, geometry_type):
        color = COLORS[instance.custom_object.tied_to_object.invisible_color].copy()
        if geometry_type == "faces":
            color.s *= 0.5
        return (color.r, color.g, color.b) + ((1 if geometry_type == "edges" else 0.2),)
    
    INVISIBLE_OBJECT = custom_objects.create_shader(
        vertex=INVISIBLE_VERT,
        fragment=INVISIBLE_FRAG,
        uniforms=(("color", {
            "type": "VEC4",
            "instance": True,
            "value": get_color,
        }),),
        interfaces={"color": ("flat", "VEC4")},
    )

    invisible_objects = utils.id_dict()
    def destroy_invisible_object(object):
        if object in invisible_objects:
            invisible_object = invisible_objects[object]
            invisible_object.destroy()
            del invisible_objects[object]
    def update_is_invisible(object, context):
        destroy_invisible_object(object)
        if object.is_invisible:
            invisible_object = custom_objects.CustomObject(
                object=object, 
                shader=INVISIBLE_OBJECT, 
                draw_geometry=("faces", "edges"),
                draw_order=-10,
                gpu_states={
                    "faces": {
                        "face_culling_set": "NONE",
                    },
                    "edges": {
                        "depth_test_set": "NONE",
                    },
                },
                
                tied_to_object=True,
            )
            invisible_objects[object] = invisible_object
    bpy.types.Object.is_invisible = bpy.props.BoolProperty(default=False, update=update_is_invisible)
    bpy.types.Object.invisible_color = bpy.props.EnumProperty(items=[(key, key, "") for key in COLORS.keys()], default="Red")

    def object_visibility_change(object, is_visible, object_exists):
        if is_visible:
            update_is_invisible(object, bpy.context)
        else:
            destroy_invisible_object(object)
    def draw(layout, context, currently_selected):
        if currently_selected:
            layout.prop(currently_selected, "is_invisible", text="Is Invisible")
            if currently_selected.is_invisible:
                layout.prop(currently_selected, "invisible_color", text="Color")
    return {
        "listeners": (utils.listen_object_visibility_change(object_visibility_change),),
        "draw": {
            "function": draw,
            "assign_to": "object_properties",
        },
    }