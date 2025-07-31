import bpy, gpu, mathutils, struct, sys
from gpu_extras.batch import batch_for_shader

def register(utils, package):
    LARGE_INT = sys.maxsize
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
        "color": {
            "type": "VEC3",
            "interface": "colorInterp",
        }
    }

    def get_view_dir(object):
        return bpy.context.space_data.region_3d.view_rotation @ mathutils.Vector((0, 0, -1))
    COMMON_UNIFORMS = {
        "view_dir": {
            "type": "VEC3",
            "set": "uniform_float",
            "get_value": get_view_dir,
        }
    }

    global create_shader
    def create_shader(*, vertex, fragment, attribs, use_texture=False, texture_slots=("image",), uniforms=None, interfaces=None, define=None):
        shader_info = gpu.types.GPUShaderCreateInfo()
        shader_info.typedef_source((
            "struct MyStruct {"
            "   float4x4 modelViewMatrix;"
            "   float3x3 normalMatrix;"
            "};"
        ))
        shader_info.uniform_buf(0, "MyStruct", "my_struct[]")
        shader_info.push_constant("VEC4", "viewport")
        if uniforms:
            for uniform in uniforms:
                if type(uniform) is str:
                    uniform_name = uniform
                    uniform_info = COMMON_UNIFORMS[uniform]
                else:
                    uniform_name, uniform_info = uniform
                shader_info.push_constant(uniform_info["type"], uniform_name)
        if use_texture:
            index = 0
            for slot_name in texture_slots:
                shader_info.sampler(index, "FLOAT_2D", slot_name)
                index += 1
        if define:
            for variable, value in define.items():
                shader_info.define(variable, value)

        vert_out = gpu.types.GPUStageInterfaceInfo("my_interface")
        index = 0
        for attrib in attribs:
            attrib_info = VERTEX_ATTRIB_TYPES[attrib]
            attrib_type = attrib_info["type"]
            shader_info.vertex_in(index, attrib_type, attrib)
            if "interface" in attrib_info:
                vert_out.smooth(attrib_type, attrib_info["interface"])
            index += 1
        if interfaces:
            for interface_name, interface_info in interfaces.items():
                getattr(vert_out, interface_info[0])(interface_info[1], interface_name)
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
            "texture_slots": texture_slots,
            "uniforms": uniforms,
        }

    shaders_path = utils.get_path(package, "shaders")
    DEFAULT_SHADER = create_shader(
        vertex=shaders_path.joinpath("default_vert.glsl").read_text(),
        fragment=shaders_path.joinpath("default_frag.glsl").read_text(),
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
        def __init__(self, custom_object, transform, scale):
            utils.trigger_redraw()
            self.__custom_object = custom_object
            self.__transform = transform
            self.__scale = scale
            self.__scale_matrix = mathutils.Matrix.to_4x4(mathutils.Matrix.Diagonal(scale))

        @property
        def transform(self):
            return self.__transform
        @transform.setter
        def transform(self, value):
            if value != self.__transform:
                utils.trigger_redraw()
                self.__transform = value

        @property
        def scale(self):
            return self.__scale
        @scale.setter
        def scale(self, value):
            if value != self.__scale:
                utils.trigger_redraw()
                self.__scale = value
                self.__scale_matrix = mathutils.Matrix.to_4x4(mathutils.Matrix.Diagonal(value))

        def get_matrix(self):
            return self.__transform @ self.__scale_matrix

        def destroy(self):
            self.__custom_object.instances.remove(self)
    global CustomObject
    class CustomObject:
        def __init__(self, *, object, image=None, shader=DEFAULT_SHADER, gpu_states=None, draw_order=100):
            pos_attribs = []
            normal_attribs = []
            uv_attribs = []
            color_attribs = []
            vertex_attribs = {
                "pos": pos_attribs,
                "normal": normal_attribs,
                "uv": uv_attribs,
                "color": color_attribs,
            }
            
            mesh = object.data
            vertices = mesh.vertices
            loop_uvs = mesh.uv_layers.active and mesh.uv_layers.active.uv
            loop_colors = mesh.color_attributes.active_color and mesh.color_attributes.active_color.data
            for loop in mesh.loops:
                pos_attribs.append(vertices[loop.vertex_index].co.copy())
                normal_attribs.append(loop.normal.copy())
                if loop_uvs:
                    uv_attribs.append(loop_uvs[loop.index].vector.copy())
                if loop_colors:
                    color = loop_colors[loop.index].color_srgb
                    color_attribs.append(mathutils.Vector((color[0], color[1], color[2])))

            triangles_indices = []
            for loop_triangle in mesh.loop_triangles:
                triangles_indices.append(tuple(loop_triangle.loops))

            load_attribs = {}
            for attrib in shader["vertex_attribs"]:
                load_attribs[attrib] = vertex_attribs[attrib]
            self.__batch = batch_for_shader(shader["shader"], "TRIS", load_attribs, indices=triangles_indices)
            self.__shader = shader["shader"]
            self.__uniforms = shader["uniforms"]
            if image and shader["use_texture"]:
                self.__texture = {}
                if type(image) is dict:
                    for slot_name in shader["texture_slots"]:
                        self.__texture[slot_name] = gpu.texture.from_image(image[slot_name])
                else:
                    texture = gpu.texture.from_image(image)
                    for slot_name in shader["texture_slots"]:
                        self.__texture[slot_name] = texture
            else:
                self.__texture = None
            self.__gpu_states = gpu_states
            self.instances = []
            self.draw_order = draw_order if draw_order > 0 else LARGE_INT + draw_order

            custom_objects.append(self)
        
        def new(self, transform=mathutils.Matrix(), scale=mathutils.Vector((1, 1, 1))):
            new_instance = CustomObjectInstance(self, transform, scale)
            self.instances.append(new_instance)
            return new_instance
        
        def render(self, view_projection_matrix, viewport):
            buf = b""
            for instance in self.instances:
                mat = instance.get_matrix()
                buf += float4x4_to_bytes(view_projection_matrix @ mat)
                buf += float3x3_to_bytes(mat.to_3x3().inverted().transposed())

            buf = gpu.types.GPUUniformBuf(buf)
            self.__shader.uniform_float("viewport", viewport)
            self.__shader.uniform_block("my_struct", buf)
            if self.__uniforms:
                for uniform in self.__uniforms:
                    if type(uniform) is str:
                        uniform_name = uniform
                        uniform_info = COMMON_UNIFORMS[uniform]
                    else:
                        uniform_name, uniform_info = uniform
                    getattr(self.__shader, uniform_info["set"])(uniform_name, uniform_info["get_value"](self))
            if self.__texture:
                if type(self.__texture) is dict:
                    for slot_name, texture in self.__texture.items():
                        self.__shader.uniform_sampler(slot_name, texture)
                else:
                    self.__shader.uniform_sampler("image", self.__texture)
            with utils.gpu_state(self.__gpu_states):
                self.__batch.draw_instanced(self.__shader, instance_start=0, instance_count=len(self.instances))

    def draw_callback_3d(delta_time):
        with utils.gpu_state({
            "face_culling_set": "BACK",
            "depth_test_set": "LESS_EQUAL"
        }):
            viewport = gpu.state.viewport_get()
            view_projection_matrix = bpy.context.region_data.perspective_matrix

            custom_objects.sort(key = lambda custom_object: custom_object.draw_order)
            for custom_object in custom_objects:
                custom_object.render(view_projection_matrix, viewport)
    return {
        "listeners": (utils.listen_draw(draw_callback_3d, priority=-1),),
    }