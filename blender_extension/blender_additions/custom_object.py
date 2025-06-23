import bpy, gpu, mathutils, pathlib
from gpu_extras.batch import batch_for_shader

def register(utils):

    # class CustomObject:
        
    #     def __init__(mesh, *, image=None, ):
    #         print()

    
    texture = None
    transform = None
    shader = None
    triangles_batch = None
    def draw_callback_3d():
        nonlocal transform
        if triangles_batch:
            gpu.state.face_culling_set("BACK")
            gpu.state.depth_test_set("LESS_EQUAL")

            transform = mathutils.Euler((0.05, 0, 0)).to_matrix().to_4x4() @ transform
            view_projection_matrix = bpy.context.region_data.perspective_matrix
            model_view_matrix = view_projection_matrix @ transform
            normal_matrix = transform.to_3x3().inverted().transposed()
            shader.uniform_float("modelViewMatrix", model_view_matrix)
            shader.uniform_float("normalMatrix", normal_matrix)
            shader.uniform_sampler("image", texture)
            triangles_batch.draw(shader)

            gpu.state.depth_test_set("NONE")
            gpu.state.face_culling_set("NONE")
    outline_handle_3d = bpy.types.SpaceView3D.draw_handler_add(draw_callback_3d, (), "WINDOW", "POST_VIEW")

    def unregister():
        nonlocal outline_handle_3d
        if outline_handle_3d:
            bpy.types.SpaceView3D.draw_handler_remove(outline_handle_3d, "WINDOW")
            outline_handle_3d = None

    KART_FILE_NAME = "BasicKart.blend"
    KART_FILE_PATH = str(pathlib.Path(__file__).parent.parent.joinpath(KART_FILE_NAME))
    def load_post(file):
        nonlocal triangles_batch
        nonlocal transform
        nonlocal texture
        nonlocal shader
        resources = utils.load_resources(KART_FILE_PATH, "objects")

        object = resources["objects"]["Chassis"]
        transform = object.matrix_world
        mesh = object.data

        pos_attributes = []
        normal_attributes = []
        uv_attributes = []

        vertices = mesh.vertices
        loop_uvs = mesh.uv_layers.active.uv
        for loop in mesh.loops:
            pos_attributes.append(vertices[loop.vertex_index].co)
            normal_attributes.append(loop.normal)
            uv_attributes.append(loop_uvs[loop.index].vector)

        triangles_indices = []
        for loop_triangle in mesh.loop_triangles:
            triangles_indices.append(tuple(loop_triangle.loops))
        
        texture = gpu.texture.from_image(resources["images"]["Basic Chassis.png"])
        vert_out = gpu.types.GPUStageInterfaceInfo("my_interface")
        vert_out.smooth("VEC3", "normalInterp")
        vert_out.smooth("VEC2", "uvInterp")

        shader_info = gpu.types.GPUShaderCreateInfo()
        shader_info.push_constant("MAT4", "modelViewMatrix")
        shader_info.push_constant("MAT3", "normalMatrix")
        shader_info.sampler(0, "FLOAT_2D", "image")
        shader_info.vertex_in(0, "VEC3", "pos")
        shader_info.vertex_in(1, "VEC3", "normal")
        shader_info.vertex_in(2, "VEC2", "uv")
        shader_info.vertex_out(vert_out)
        shader_info.fragment_out(0, "VEC4", "fragColor")

        shader_info.vertex_source(
            "void main()"
            "{"
            "  uvInterp = uv;"
            "  normalInterp = normalMatrix * normal;"
            "  gl_Position = modelViewMatrix * vec4(pos, 1.0f);"
            "}"
        )

        shader_info.fragment_source(
            "void main()"
            "{"
            "  fragColor = texture(image, uvInterp);"
            "  fragColor.xyz *= mix(vec3(0.53f, 1.0f, 0.56f), mix(vec3(1.0f, 0.85f, 0.5f), vec3(1.0f, 1.0f, 1.0f), 0.8f), clamp(dot(normalInterp, vec3(0.0f, 0.0f, 1.0f)), 0.0f, 1.0f));"
            "}"
        )

        shader = gpu.shader.create_from_info(shader_info)
        shader.bind()
        shader.uniform_sampler("image", texture)

        triangles_batch = batch_for_shader(shader, "TRIS", {
            "pos": pos_attributes,
            "normal": normal_attributes,
            "uv": uv_attributes
        }, indices=triangles_indices)

    def trigger_redraw():
        for area in bpy.context.window.screen.areas:
            if area.type == "VIEW_3D":
                area.tag_redraw()
        return 0.01
    return {
        "listeners": (
            utils.listen_handler("load_post", load_post),
            utils.listen_timer(trigger_redraw, persistent=True)
        ),
        "unregister": unregister
    }