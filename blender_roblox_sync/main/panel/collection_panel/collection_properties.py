import bpy

def register(utils, package):
    object_properties = utils.import_module("object_properties")

    def poll(self, collection):
        return collection.is_editable and (collection in bpy.context.scene.collection.children_recursive)
    bpy.types.Scene.editing_collection = bpy.props.PointerProperty(type=bpy.types.Collection, poll=poll)

    def get_object_collection(object):
        max_depth = 0
        closest_collection = None
        def scan_collection(collection, depth=0):
            nonlocal max_depth
            nonlocal closest_collection
            if (depth > max_depth) and (object.name in collection.objects):
                max_depth = depth
                closest_collection = collection
            for child_collection in collection.children:
                scan_collection(child_collection, depth + 1)
        scan_collection(bpy.context.scene.collection)
        return closest_collection
    
    class VIEW3D_OT_select_object_collection(bpy.types.Operator):
        bl_idname = "view3d.select_object_collection"
        bl_label = "Select Object Collection"
        bl_options = {"REGISTER", "UNDO"}

        def execute(self, context):
            context.scene.editing_collection = get_object_collection(object_properties.currently_selected)
            return {"FINISHED"}

    global currently_selected
    currently_selected = None 
    def draw(layout, context):
        global currently_selected
        currently_selected = context.scene.editing_collection

        box = layout.box()
        col = box.column(align=True)
        col.prop_search(context.scene, "editing_collection", bpy.data, "collections", text="")
        col.separator(factor=0.2, type="SPACE")

        selectable_collection = get_object_collection(object_properties.currently_selected) if object_properties.currently_selected else None
        select_text = f"Select: \"{selectable_collection.name}\"" if selectable_collection else "Select Object Collection"
        row = col.row()
        row.operator("view3d.select_object_collection", text=select_text)
        row.enabled = (selectable_collection != None) and (selectable_collection != currently_selected)
        
        if currently_selected:
            col.separator(factor=1, type="LINE")
            flow = col.column_flow(align=True)
            utils.draw_layout("collection_properties", flow, context, currently_selected)
        else:
            utils.draw_layout("collection_properties", None, context, None)
    return {
        "classes": (VIEW3D_OT_select_object_collection,),
        "draw": {
            "function": draw, 
            "assign_to": "collection_panel",
            "priority": 0
        },
    }