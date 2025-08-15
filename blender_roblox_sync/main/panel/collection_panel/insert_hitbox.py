import bpy, mathutils, math, gpu

def register(utils, package):
    collection_properties = utils.import_module("collection_properties")
    primitive_parts = utils.import_module("primitive_parts")
    invisible_objects = utils.import_module("invisible_objects")

    def get_bounds(object, min_x, max_x, min_y, max_y, min_z, max_z):
        matrix_world = object.matrix_world
        for vert in object.data.vertices:
            pos = matrix_world @ vert.co
            x, y, z = pos.x, pos.y, pos.z
            if min_x == None:
                min_x = x
                max_x = x
                min_y = y
                max_y = y
                min_z = z
                max_z = z
            else:
                if x < min_x:
                    min_x = x
                if x > max_x:
                    max_x = x
                if y < min_y:
                    min_y = y
                if y > max_y:
                    max_y = y
                if z < min_z:
                    min_z = z
                if z > max_z:
                    max_z = z
        return min_x, max_x, min_y, max_y, min_z, max_z

    global insert_hitbox
    def insert_hitbox(collection):
        min_x, max_x, min_y, max_y, min_z, max_z = None, None, None, None, None, None
        for object in collection.all_objects:
            if object.type == "MESH":
                min_x, max_x, min_y, max_y, min_z, max_z = get_bounds(object, min_x, max_x, min_y, max_y, min_z, max_z)
        if min_x != None:
            min_bound = mathutils.Vector((min_x, min_y, min_z))
            max_bound = mathutils.Vector((max_x, max_y, max_z))
            size = 0.5 * (max_bound - min_bound)
            if (size.x > 0) and (size.y > 0) and (size.z > 0):
                pos = 0.5 * (max_bound + min_bound)
                hitbox = primitive_parts.insert_primitive("Block")
                hitbox.location = pos
                hitbox.scale = size
                hitbox.is_invisible = True
                hitbox.can_collide = True
                hitbox.name = "Hitbox"

    class VIEW3D_OT_insert_hitbox(bpy.types.Operator):
        bl_idname = "view3d.insert_hitbox"
        bl_label = "Insert Hitbox"
        bl_options = {"REGISTER", "UNDO"}

        def execute(self, context):
            insert_hitbox(collection_properties.currently_selected)
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