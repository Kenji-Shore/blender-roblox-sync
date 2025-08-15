import bpy, mathutils, math, gpu

def register(utils, package):
    collection_properties = utils.import_module("collection_properties")
    primitive_parts = utils.import_module("primitive_parts")

    class VIEW3D_OT_insert_hitbox(bpy.types.Operator):
        bl_idname = "view3d.insert_hitbox"
        bl_label = "Insert Hitbox"
        bl_options = {"REGISTER", "UNDO"}

        def execute(self, context):
            hitbox = primitive_parts.insert_primitive("Block")
            return {"FINISHED"}

    def draw(layout, context, currently_selected):
        if currently_selected:    
            layout.operator("view3d.insert_hitbox", text="Insert Hitbox")
    
    return {
        "classes": (VIEW3D_OT_insert_hitbox,),
        "draw": {
            "function": draw,
            "assign_to": "collection_properties"
        },
    }