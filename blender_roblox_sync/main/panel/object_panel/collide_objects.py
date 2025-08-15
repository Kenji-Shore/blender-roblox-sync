import bpy

def register(utils, package):
    bpy.types.Object.can_touch = bpy.props.BoolProperty(default=False)
    bpy.types.Object.can_collide = bpy.props.BoolProperty(default=False)

    def draw(layout, context, currently_selected):
        if currently_selected:
            layout.prop(currently_selected, "can_collide", text="Can Collide")
            if not currently_selected.can_collide:
                layout.prop(currently_selected, "can_touch", text="Can Touch")
    return {
        "draw": {
            "function": draw,
            "assign_to": "object_properties",
        },
    }