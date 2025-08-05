import bpy

def register(utils, package):
    
    def draw(layout, context):
        panel_header, panel_body = layout.panel("object")
        panel_header.label(text="Object")
        if panel_body:
            utils.draw_layout("object_panel", panel_body, context)
    return {
        "draw": {
            "function": draw, 
            "assign_to": "panel",
            "priority": 1
        },
    }