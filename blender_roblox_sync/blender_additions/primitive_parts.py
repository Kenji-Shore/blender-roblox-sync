import bpy, bmesh, mathutils

def register(utils, package):
    PRIMITIVE_TYPES = {
        "Block": {
            "icon": "MESH_CUBE",
            "id": 0,
            "lock_scales": ()
        },
        "Wedge": {
            "icon": "MOD_LATTICE",
            "id": 1,
            "lock_scales": ()
        },
        "Cylinder": {
            "icon": "MESH_CYLINDER",
            "id": 2,
            "lock_scales": (0, 1)
        },
        "Sphere": {
            "icon": "MESH_UVSPHERE",
            "id": 3,
            "lock_scales": (0, 1, 2)
        }
    }

    def update_primitive_type(object, context):
        if object.is_primitive and object.mode == "OBJECT":
            PRIMITIVE_TYPES[object.primitive_type]["bmesh"].to_mesh(object.data)

    bpy.types.Object.is_primitive = bpy.props.BoolProperty(default=False)
    bpy.types.Object.primitive_type = bpy.props.EnumProperty(items=[(key, key, "", PRIMITIVE_TYPES[key]["icon"], PRIMITIVE_TYPES[key]["id"]) for key in PRIMITIVE_TYPES.keys()], default="Block", update=update_primitive_type)
    bpy.types.Object.primitive_lock_scale = bpy.props.FloatProperty()
    bpy.types.Scene.insert_primitive_type = bpy.props.EnumProperty(items=[(key, key, "", PRIMITIVE_TYPES[key]["icon"], PRIMITIVE_TYPES[key]["id"]) for key in PRIMITIVE_TYPES.keys()], default="Block")

    def primitive_update_transform(object):
        if utils.id_exists(object):
            with utils.pause_updates():
                translation, rotation, scale = object.matrix_world.decompose()
                lock_scale = object.primitive_lock_scale

                new_scale_avg = 0
                new_scale_count = 0
                for axis in PRIMITIVE_TYPES[object.primitive_type]["lock_scales"]:
                    new_scale = scale[axis]
                    if new_scale != lock_scale:
                        new_scale_avg += new_scale
                        new_scale_count += 1

                if new_scale_count > 0:
                    lock_scale = new_scale_avg / new_scale_count
                    object.primitive_lock_scale = lock_scale
                for axis in PRIMITIVE_TYPES[object.primitive_type]["lock_scales"]:
                    scale[axis] = lock_scale
                for axis in (0, 1, 2):
                    scale[axis] = abs(scale[axis])
                
                object.matrix_world = mathutils.Matrix.LocRotScale(translation, rotation, scale)
        
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

            scale = object.scale
            lock_scale = 0
            for axis in primitive_info["lock_scales"]:
                lock_scale = max(lock_scale, scale[axis])
            object.primitive_lock_scale = lock_scale
            primitive_update_transform(object)

            print("inserting", object)
            return {"FINISHED"}

    def primitive_part_updated(depsgraph):
        for depsgraph_update in depsgraph.updates:
            id = depsgraph_update.id.original
            if (type(id) is bpy.types.Object) and id.is_primitive and depsgraph_update.is_updated_transform:
                primitive_update_transform(id)
                utils.delay(primitive_update_transform, id)

    def exit_object_mode(new_mode):
        active_object = bpy.context.active_object
        for object in bpy.context.selected_objects:
            if object.is_primitive:
                bpy.context.view_layer.objects.active = object
                bpy.ops.object.mode_set(mode="OBJECT")
        bpy.context.view_layer.objects.active = active_object

    def post_registration_loaded():
        for resource_path in utils.get_path(package, "resources").glob("*.blend"):
            primitive_name = resource_path.stem
            if primitive_name in PRIMITIVE_TYPES:
                primitive_mesh = bmesh.new()
                with utils.load_resources(resource_path, "objects") as resources:
                    object = next(iter(resources["objects"].values()))
                    primitive_mesh.from_mesh(object.data)
                PRIMITIVE_TYPES[primitive_name]["bmesh"] = primitive_mesh

    # col = layout.column()
    # col.label(text="Insert Primitive:")
    # split = col.split(factor=0.6)
    # split.prop(context.scene, "insert_primitive_type", text="")
    # split.operator("view3d.insert_primitive", text="Insert")

    def draw(layout, context, currently_selected):
        if currently_selected.is_primitive:
            layout.prop(currently_selected, "is_primitive", text="Is Primitive")
            # split = layout.split(factor=0.5)
            # split.label(text="Primitive Type: ")
            layout.prop(currently_selected, "primitive_type", text="Shape")
    return {
        "classes": (VIEW3D_OT_insert_primitive,),
        "listeners": (
            utils.listen_mode(("OBJECT",), exit=exit_object_mode, priority=0),
            utils.listen_depsgraph_update(primitive_part_updated),
        ),
        "draw": {
            "function": draw,
            "assign_to": "object_properties",
        },
        "post_registration_loaded": post_registration_loaded
    }