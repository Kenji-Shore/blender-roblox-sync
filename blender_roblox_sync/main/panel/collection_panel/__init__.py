import bpy

def register(utils, package):
    
    def draw(layout, context):
        panel_header, panel_body = layout.panel("collection")
        panel_header.label(text="Collection")
        if panel_body:
            utils.draw_layout("collection_panel", panel_body, context)
    return {
        "draw": {
            "function": draw, 
            "assign_to": "panel",
            "priority": 2
        },
    }