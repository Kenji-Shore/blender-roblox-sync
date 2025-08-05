import bpy

def register(utils, package):
    def poll(self, collection):
        return collection.is_editable and (collection in bpy.context.scene.collection.children_recursive)
    bpy.types.Scene.editing_collection = bpy.props.PointerProperty(type=bpy.types.Collection, poll=poll)
    def draw(layout, context):
        box = layout.box()
        col = box.column(align=True)
        col.prop_search(context.scene, "editing_collection", bpy.data, "collections", text="Edit")

        editing_collection = context.scene.editing_collection
        if editing_collection:
            col.separator(factor=1, type="LINE")
            flow = col.column_flow(align=True)
            utils.draw_layout("collection_properties", flow, context, editing_collection)
    return {
        "draw": {
            "function": draw, 
            "assign_to": "collection_panel",
            "priority": 0
        },
    }