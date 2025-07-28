import bpy, bmesh

def register(utils, package):
    PRIMITIVE_TYPES = {
        "Block": {
            "icon": "MESH_CUBE",
            "id": 0,
        },
        "Wedge": {
            "icon": "MOD_LATTICE",
            "id": 1,
        },
        "Cylinder": {
            "icon": "MESH_CYLINDER",
            "id": 2,
        },
        "Sphere": {
            "icon": "MESH_UVSPHERE",
            "id": 3,
        }
    }
    bpy.types.Object.is_primitive = bpy.props.BoolProperty(default=False)
    bpy.types.Object.primitive_type = bpy.props.EnumProperty(items=[(key, key, "") for key in PRIMITIVE_TYPES.keys()], default="Block")
    bpy.types.Scene.insert_primitive_type = bpy.props.EnumProperty(items=[(key, key, "", PRIMITIVE_TYPES[key]["icon"], PRIMITIVE_TYPES[key]["id"]) for key in PRIMITIVE_TYPES.keys()], default="Block")

    class VIEW3D_OT_insert_primitive(bpy.types.Operator):
        bl_idname = "view3d.insert_primitive"
        bl_label = "Insert Primitive"
        bl_options = {"REGISTER", "UNDO"}

        def execute(self, context):
            primitive_type = context.scene.insert_primitive_type
            primitive_info = PRIMITIVE_TYPES[primitive_type]

            bpy.ops.object.add(type="MESH")
            object = context.active_object
            object.is_primitive = True
            object.primitive_type = primitive_type
            object.name = primitive_type
            primitive_info["bmesh"].to_mesh(object.data)

            print("inserting", object)
            return {"FINISHED"}
        
    def draw(layout, context):
        box = layout.box()
        col = box.column()
        col.label(text="Insert Primitive:")
        split = col.split(factor=0.6)
        split.prop(context.scene, "insert_primitive_type", text="")
        split.operator("view3d.insert_primitive", text="Insert")

    def primitive_part_updated(depsgraph):
        for depsgraph_update in depsgraph.updates:
            object = depsgraph_update.id
            if (type(object) is bpy.types.Object) and object.is_primitive:
                if depsgraph_update.is_updated_transform:
                    object.matrix_world = object.matrix_world.normalized()
                    translation, rotation, scale = object.matrix_world.decompose()
                    object.scale = scale
                #depsgraph_update.is_updated_geometry)

    def post_registration_loaded():
        for resource_path in utils.get_resources_path(package).glob("*.blend"):
            primitive_name = resource_path.stem
            primitive_mesh = bmesh.new()
            with utils.load_resources(resource_path, "objects") as resources:
                object = next(iter(resources["objects"].values()))
                primitive_mesh.from_mesh(object.data)
            PRIMITIVE_TYPES[primitive_name]["bmesh"] = primitive_mesh
    return {
        "classes": (VIEW3D_OT_insert_primitive,),
        "listeners": (
            # utils.listen_mode(("VERTEX_PAINT", "SCULPT"), enter=enter_vertex_paint, exit=exit_vertex_paint), 
            utils.listen_depsgraph_update(primitive_part_updated),
        ),
        "draw": draw,
        "post_registration_loaded": post_registration_loaded,
    }