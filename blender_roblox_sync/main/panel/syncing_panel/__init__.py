import bpy

def register(utils, package):

    def draw(layout, context):
        panel_header, panel_body = layout.panel("syncing")
        panel_header.label(text="Syncing")
        if panel_body:
            utils.draw_layout("syncing_panel", panel_body, context)
    return {
        "draw": {
            "function": draw, 
            "assign_to": "panel",
            "priority": 0
        },
    }