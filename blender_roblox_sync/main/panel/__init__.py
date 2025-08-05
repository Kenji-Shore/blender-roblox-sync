import bpy

def register(utils, package):

    def draw(layout, context):
        col = layout.column()
        utils.draw_layout("panel", col, context)
    return {
        "draw": {
            "function": draw,
            "priority": 0
        },
    }