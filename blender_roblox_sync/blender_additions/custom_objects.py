import bpy, gpu, mathutils, struct
from gpu_extras.batch import batch_for_shader

def register(utils, package):
    VERTEX_ATTRIB_TYPES = {
        "pos": {
            "type": "VEC3",
        },
        "normal": {
            "type": "VEC3",
            "interface": "normalInterp",
        },
        "uv": {
            "type": "VEC2",
            "interface": "uvInterp",
        },
    }

    global create_shader
    def create_shader(*, vertex, fragment, attribs, use_texture=False):
        shader_info = gpu.types.GPUShaderCreateInfo()
        shader_info.typedef_source((
            "struct MyStruct {"
            "   float4x4 modelViewMatrix;"
            "   float3x3 normalMatrix;"
            "};"
        ))
        shader_info.uniform_buf(0, "MyStruct", "my_struct[]")
        if use_texture:
            shader_info.sampler(0, "FLOAT_2D", "image")

        vert_out = gpu.types.GPUStageInterfaceInfo("my_interface")
        index = 0
        for attrib in attribs:
            attrib_info = VERTEX_ATTRIB_TYPES[attrib]
            attrib_type = attrib_info["type"]
            shader_info.vertex_in(index, attrib_type, attrib)
            if "interface" in attrib_info:
                vert_out.smooth(attrib_type, attrib_info["interface"])
            index += 1
        shader_info.vertex_out(vert_out)
        shader_info.fragment_out(0, "VEC4", "fragColor")
        
        shader_info.vertex_source(vertex)
        shader_info.fragment_source(fragment)
        
        shader = gpu.shader.create_from_info(shader_info)
        shader.bind()

        return {
            "shader": shader,
            "vertex_attribs": attribs,
            "use_texture": use_texture,
        }

    DEFAULT_SHADER = create_shader(
        vertex=(
            "void main()"
            "{"
            "  uvInterp = uv;"
            "  normalInterp = my_struct[gl_InstanceID].normalMatrix * normal;"
            "  gl_Position = my_struct[gl_InstanceID].modelViewMatrix * vec4(pos, 1.0f);"
            "}"
        ),
        fragment=(
            "void main()"
            "{"
            "  fragColor = texture(image, uvInterp);"
            "  fragColor.xyz *= mix(vec3(0.53f, 1.0f, 0.56f), mix(vec3(1.0f, 0.85f, 0.5f), vec3(1.0f, 1.0f, 1.0f), 0.8f), clamp(dot(normalInterp, vec3(0.0f, 0.0f, 1.0f)), 0.0f, 1.0f));"
            "}"
        ),
        attribs=("pos", "normal", "uv"),
        use_texture=True
    )

    def float3x3_to_bytes(mat):
        col = mat.col
        return struct.pack("3f4x3f4x3f4x", *(col[0][:] + col[1][:] + col[2][:]))
    def float4x4_to_bytes(mat):
        col = mat.col
        return struct.pack("16f", *(col[0][:] + col[1][:] + col[2][:] + col[3][:]))
    
    custom_objects = []
    class CustomObjectInstance:
        def __init__(self, custom_object, transform):
            self.__custom_object = custom_object
            self.transform = transform
        def destroy(self):
            print("deletoes")
            self.__custom_object.instances.remove(self)
    global CustomObject
    class CustomObject:
        def __init__(self, *, object, image, shader=DEFAULT_SHADER):
            pos_attribs = []
            normal_attribs = []
            uv_attribs = []
            vertex_attribs = {
                "pos": pos_attribs,
                "normal": normal_attribs,
                "uv": uv_attribs
            }
            
            mesh = object.data
            vertices = mesh.vertices
            loop_uvs = mesh.uv_layers.active.uv
            for loop in mesh.loops:
                pos_attribs.append(vertices[loop.vertex_index].co.copy())
                normal_attribs.append(loop.normal.copy())
                uv_attribs.append(loop_uvs[loop.index].vector.copy())

            triangles_indices = []
            for loop_triangle in mesh.loop_triangles:
                triangles_indices.append(tuple(loop_triangle.loops))

            load_attribs = {}
            for attrib in shader["vertex_attribs"]:
                load_attribs[attrib] = vertex_attribs[attrib]
            self.__batch = batch_for_shader(shader["shader"], "TRIS", load_attribs, indices=triangles_indices)
            self.__shader = shader["shader"]
            self.instances = []
            if image and shader["use_texture"]:
                self.__texture = gpu.texture.from_image(image)
            
            custom_objects.append(self)
        
        def new(self, transform=mathutils.Matrix()):
            new_instance = CustomObjectInstance(self, transform)
            self.instances.append(new_instance)
            return new_instance
        
        def render(self, view_projection_matrix):
            gpu.state.face_culling_set("BACK")
            gpu.state.depth_test_set("LESS_EQUAL")

            buf = b""
            for instance in self.instances:
                transform = instance.transform
                buf += float4x4_to_bytes(view_projection_matrix @ transform)
                buf += float3x3_to_bytes(transform.to_3x3().inverted().transposed())

            buf = gpu.types.GPUUniformBuf(buf)
            self.__shader.uniform_block("my_struct", buf)
            if self.__texture:
                self.__shader.uniform_sampler("image", self.__texture)
            self.__batch.draw_instanced(self.__shader, instance_start=0, instance_count=2)
            
            gpu.state.depth_test_set("NONE")
            gpu.state.face_culling_set("NONE")

    def draw_callback_3d():
        view_projection_matrix = bpy.context.region_data.perspective_matrix
        for custom_object in custom_objects:
            custom_object.render(view_projection_matrix)
    outline_handle_3d = bpy.types.SpaceView3D.draw_handler_add(draw_callback_3d, (), "WINDOW", "POST_VIEW")

    def unregister():
        nonlocal outline_handle_3d
        if outline_handle_3d:
            bpy.types.SpaceView3D.draw_handler_remove(outline_handle_3d, "WINDOW")
            outline_handle_3d = None

    def trigger_redraw():
        for area in bpy.context.window.screen.areas:
            if area.type == "VIEW_3D":
                area.tag_redraw()
        return 0.01
    return {
        "listeners": (utils.listen_timer(trigger_redraw, persistent=True),),
        "unregister": unregister
    }