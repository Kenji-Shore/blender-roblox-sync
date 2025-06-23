import bpy, gpu, mathutils
from gpu_extras.batch import batch_for_shader

def register(utils):

    COLORS = {
        "Red": mathutils.Color((1, 0, 0)),
        "Green": mathutils.Color((0, 1, 0)),
        "Blue": mathutils.Color((0, 0, 1)),
        "Purple": mathutils.Color((1, 0, 1)),
        "Yellow": mathutils.Color((1, 1, 0)),
        "Brown": mathutils.Color((0.5, 0.25, 0)),
        "White": mathutils.Color((1, 1, 1)),
    }

    VISIBLE_SETTINGS = {
        "show_in_front": False,
        "visible_shadow": True,
        "visible_volume_scatter": True,
        "visible_transmission": True,
        "visible_glossy": True,
        "visible_diffuse": True,
        "visible_camera": True
    }
    class VisibleSettings(bpy.types.PropertyGroup):
        pass
    for property_name, default_setting in VISIBLE_SETTINGS.items():
        VisibleSettings.__annotations__[property_name] = bpy.props.BoolProperty(default=default_setting)
    bpy.utils.register_class(VisibleSettings)
    bpy.types.Object.visible_settings = bpy.props.PointerProperty(type=VisibleSettings)

    def update_is_invisible(self, context):
        if self.is_invisible:
            for property_name, default_setting in VISIBLE_SETTINGS.items():
                setattr(self.visible_settings, property_name, getattr(self, property_name))
                setattr(self, property_name, not default_setting)
        else:
            for property_name, default_setting in VISIBLE_SETTINGS.items():
                setattr(self, property_name, getattr(self.visible_settings, property_name))
    bpy.types.Object.is_invisible = bpy.props.BoolProperty(default=False, update=update_is_invisible)
    bpy.types.Object.invisible_color = bpy.props.EnumProperty(items=[(key, key, "") for key in COLORS.keys()], default="Red")

    def build_batch(object):
        transform = object.matrix_world
        mesh = object.data
        pos_attributes = [transform @ v.co for v in mesh.vertices]

        triangles_indices = []
        edges_indices = []
        for loop_triangle in mesh.loop_triangles:
            triangles_indices.append(tuple(loop_triangle.vertices))
        for edge in mesh.edges:
            edges_indices.append(tuple(edge.vertices))
        
        triangles_shader = gpu.shader.from_builtin("UNIFORM_COLOR")
        triangles_shader.bind()
        triangles_batch = batch_for_shader(triangles_shader, "TRIS", {"pos": pos_attributes}, indices=triangles_indices)

        edges_shader = gpu.shader.from_builtin("UNIFORM_COLOR")
        edges_shader.bind()
        edges_batch = batch_for_shader(edges_shader, "LINES", {"pos": pos_attributes}, indices=edges_indices)
        return (triangles_shader, triangles_batch, edges_shader, edges_batch,)

    object_batches = {}
    def draw_callback_3d():
        nonlocal object_batches
        depsgraph = bpy.context.evaluated_depsgraph_get()

        new_object_batches = {}
        object = bpy.context.object
        for object in bpy.context.visible_objects:
            if object.is_invisible:
                new_object_batches[object] = object_batches[object] if object in object_batches else build_batch(object.evaluated_get(depsgraph))
        
        object_batches = new_object_batches
        for object, batches in object_batches.items():
            edge_color = COLORS[object.invisible_color]
            face_color = edge_color.copy()
            face_color.s *= 0.5

            triangles_shader, triangles_batch, edges_shader, edges_batch = batches

            gpu.state.depth_test_set("LESS_EQUAL")
            gpu.state.blend_set("ALPHA")
            triangles_shader.uniform_float("color", (face_color.r, face_color.g, face_color.b, 0.2,)) 
            triangles_batch.draw(triangles_shader)
            gpu.state.blend_set("NONE")
            gpu.state.depth_test_set("NONE")
            
            edges_shader.uniform_float("color", (edge_color.r, edge_color.g, edge_color.b, 1,)) 
            edges_batch.draw(edges_shader)
    outline_handle_3d = bpy.types.SpaceView3D.draw_handler_add(draw_callback_3d, (), "WINDOW", "POST_VIEW")

    def depsgraph_update_post(scene, depsgraph):
        for depsgraph_update in depsgraph.updates:
            id = depsgraph_update.id
            if (id.original in object_batches) and (depsgraph_update.is_updated_transform or depsgraph_update.is_updated_geometry):
                object_batches.pop(id.original)
    def unregister():
        nonlocal outline_handle_3d
        if outline_handle_3d:
            bpy.types.SpaceView3D.draw_handler_remove(outline_handle_3d, "WINDOW")
            outline_handle_3d = None
        bpy.utils.unregister_class(VisibleSettings)
    return {
        "listeners": (
            utils.listen_handler("depsgraph_update_post", depsgraph_update_post),
        ),
        "unregister": unregister
    }