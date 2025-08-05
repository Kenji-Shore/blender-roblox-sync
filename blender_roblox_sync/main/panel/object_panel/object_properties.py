import bpy

def register(utils, package):
    loaded_draws = []
    global load_draw
    def load_draw(condition, draw_properties=None):
        loaded_draws.append((condition, draw_properties))

    def draw(layout, context):
        box = layout.box()
        col = box.column(align=True)
        currently_selected = context.active_object
        if currently_selected and not currently_selected.select_get():
            currently_selected = None
        col.label(text="Selected: " + (currently_selected.name if currently_selected else "None"))
        
        if currently_selected:
            col.separator(factor=1, type="LINE")
            flow = col.column_flow(align=True)

            for condition, draw_properties in loaded_draws:
                if condition(currently_selected):
                    if draw_properties:
                        draw_properties(flow, context, currently_selected)
                    return
            utils.draw_layout("object_properties", flow, context, currently_selected)
    return {
        "draw": {
            "function": draw, 
            "assign_to": "object_panel",
            "priority": 0
        },
    }