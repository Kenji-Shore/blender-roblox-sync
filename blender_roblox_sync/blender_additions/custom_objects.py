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
    def set_visibility(object, is_visible):
        if utils.object_exists(object):
            if is_visible:
                for property_name, default_setting in VISIBLE_SETTINGS.items():
                    setattr(object, property_name, getattr(object.visible_settings, property_name))
            else:
                for property_name, default_setting in VISIBLE_SETTINGS.items():
                    setattr(object.visible_settings, property_name, getattr(object, property_name))
                    setattr(object, property_name, not default_setting)

    def get_world_lighting():
        world = bpy.context.scene.world
        world_color = mathutils.Color((0.8, 0.8, 0.8))
        if world.use_nodes:
            for node in world.node_tree.nodes:
                if type(node) is bpy.types.ShaderNodeBackground:
                    world_color = mathutils.Color(node.inputs[0].default_value[:3])
                    world_strength = node.inputs[1].default_value
                    world_color = world_color * world_strength
                    break
        else:
            world_color = world.color
        
        sun_dir = mathutils.Vector((0, 0, -1))
        sun_color = mathutils.Color((1, 1, 1))
        sun_energy = 0
        for object in bpy.context.scene.objects:
            if object.type == "LIGHT" and object.data.type == "SUN":
                light = object.data
                translation, rotation, scale = object.matrix_world.decompose()
                sun_dir = rotation.to_matrix().to_4x4() @ mathutils.Vector((0, 0, -1))
                sun_color = light.color
                sun_energy = light.energy
                sun_color = sun_color * sun_energy
                break
        return world_color, sun_color, sun_dir
    def get_view_dir():
        return bpy.context.space_data.region_3d.view_rotation @ mathutils.Vector((0, 0, -1))
    def get_common_values():
        common = {}
        common["world_color"], common["sun_color"], common["sun_dir"] = get_world_lighting()
        common["view_dir"] = get_view_dir()
        common["viewport"] = gpu.state.viewport_get()
        return common
    
    COMMON_UNIFORMS = {
        "viewport": {
            "type": "VEC4",
            "set": "uniform_float",
        },
        "view_dir": {
            "type": "VEC3",
            "set": "uniform_float",
        },
        "sun_dir": {
            "type": "VEC3",
            "set": "uniform_float",
        },
        "world_color": {
            "type": "VEC3",
            "set": "uniform_float",
        },
        "sun_color": {
            "type": "VEC3",
            "set": "uniform_float",
        },
    }

    global create_shader
    def create_shader(*, vertex, fragment, attribs=(), use_texture=False, texture_slots=("image",), uniforms=None, interfaces=None, define=None):
        shader_info = gpu.types.GPUShaderCreateInfo()
        shader_info.typedef_source((
            "struct MyStruct {"
            "   float4x4 modelViewMatrix;"
            "   float3x3 normalMatrix;"
            "};"
        ))
        shader_info.uniform_buf(0, "MyStruct", "my_struct[]")

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
            shader_info.define("USE_TEXTURE")
        if not "pos" in attribs:
            attribs = attribs + ("pos",)
        if "color" in attribs:
            shader_info.define("USE_COLOR")
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
    DEFAULT_SHADERS = {}
    DEFAULT_VERT = shaders_path.joinpath("default_vert.glsl").read_text()
    DEFAULT_FRAG = shaders_path.joinpath("default_frag.glsl").read_text()

    def float3x3_to_bytes(mat):
        col = mat.col
        return struct.pack("3f4x3f4x3f4x", *(col[0][:] + col[1][:] + col[2][:]))
    def float4x4_to_bytes(mat):
        col = mat.col
        return struct.pack("16f", *(col[0][:] + col[1][:] + col[2][:] + col[3][:]))
    
    custom_objects = []
    class CustomObjectInstance:
        def __init__(self, custom_object, matrix):
            self.__custom_object = custom_object
            custom_object.instances.append(self)

            self.__transform = mathutils.Matrix.Identity(4)
            self.__scale = None
            self.__scale_matrix = None
            self.__matrix = None
            translation, rotation, scale = matrix.decompose()
            self.scale = scale
            self.transform = mathutils.Matrix.LocRotScale(translation, rotation, None)

        @property
        def transform(self):
            return self.__transform
        @transform.setter
        def transform(self, value):
            if value != self.__transform:
                self.__transform = value
                self.__matrix = self.__transform @ self.__scale_matrix
                utils.trigger_redraw()

        @property
        def scale(self):
            return self.__scale
        @scale.setter
        def scale(self, value):
            if value != self.__scale:
                self.__scale = value
                self.__scale_matrix = mathutils.Matrix.to_4x4(mathutils.Matrix.Diagonal(value))
                self.__matrix = self.__transform @ self.__scale_matrix
                utils.trigger_redraw()

        @property
        def matrix(self):
            return self.__matrix
        @matrix.setter
        def matrix(self, value):
            if value != self.__matrix:
                self.__matrix = value
                utils.trigger_redraw()

        def destroy(self):
            self.__custom_object.instances.remove(self)

    global CustomObject
    class CustomObject:
        def __init__(self, *, object, image=None, shader=None, gpu_states=None, draw_order=100, use_color=False, draw_edges=False, tied_to_object=False):
            if not shader:
                use_texture = image != None
                default_shader_config = (use_texture, use_color)
                if default_shader_config in DEFAULT_SHADERS:
                    shader = DEFAULT_SHADERS[default_shader_config]
                else:
                    shader = create_shader(
                        vertex=DEFAULT_VERT,
                        fragment=DEFAULT_FRAG,
                        attribs=("normal", "uv") + (("color",) if use_color else ()),
                        use_texture=use_texture,
                        uniforms=("sun_dir", "world_color", "sun_color")
                    )
                    DEFAULT_SHADERS[default_shader_config] = shader

            self.__shader = shader["shader"]
            self.__vertex_attribs = shader["vertex_attribs"]
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
            self.draw_edges = draw_edges

            self.tied_object = None
            self.tied_instance = None
            if tied_to_object:
                set_visibility(object.original, False)
                self.tied_object = object.original
                self.tied_instance = CustomObjectInstance(self, object.matrix_world)
            self.generate_batch(object)
            self.is_destroyed = False
            custom_objects.append(self)
        
        def generate_batch(self, object):
            indices = []
            load_attribs = {}

            object.update_from_editmode()
            if self.tied_object:
                set_visibility(self.tied_object, False)
            mesh = object.data
            vertices = mesh.vertices
            if not self.draw_edges:
                pos_attribs = []
                color_attribs = []
                normal_attribs = []
                uv_attribs = []
                vertex_attribs = {
                    "pos": pos_attribs,
                    "color": color_attribs,
                    "normal": normal_attribs,
                    "uv": uv_attribs,
                }

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

                load_attribs = {}
                for attrib in self.__vertex_attribs:
                    if attrib in vertex_attribs:
                        load_attribs[attrib] = vertex_attribs[attrib]

                for loop_triangle in mesh.loop_triangles:
                    indices.append(tuple(loop_triangle.loops))
            else:
                load_attribs["pos"] = [v.co.copy() for v in vertices]
                for edge in mesh.edges:
                    indices.append(tuple(edge.vertices))
            self.__batch = batch_for_shader(self.__shader, "LINES" if self.draw_edges else "TRIS", load_attribs, indices=indices)
            utils.trigger_redraw()

        def new(self, *, matrix=None, transform=mathutils.Matrix(), scale=mathutils.Vector((1, 1, 1))):
            if self.tied_instance:
                raise Exception("Attempted to create instance of a tied custom object")
            if not matrix:
                matrix = transform @ mathutils.Matrix.to_4x4(mathutils.Matrix.Diagonal(scale))
            new_instance = CustomObjectInstance(self, matrix)
            return new_instance
        
        def render(self, view_projection_matrix, common):
            if self.tied_object and (not utils.object_exists(self.tied_object)):
                self.destroy()
                return
            
            buf = b""
            for instance in self.instances:
                mat = instance.matrix
                buf += float4x4_to_bytes(view_projection_matrix @ mat)
                buf += float3x3_to_bytes(mat.to_3x3().inverted().transposed())

            buf = gpu.types.GPUUniformBuf(buf)
            self.__shader.uniform_block("my_struct", buf)
            if self.__uniforms:
                for uniform in self.__uniforms:
                    if type(uniform) is str:
                        uniform_name = uniform
                        uniform_info = COMMON_UNIFORMS[uniform]
                    else:
                        uniform_name, uniform_info = uniform

                    uniform_value = uniform_info["get_value"](self) if "get_value" in uniform_info else common[uniform_name]
                    getattr(self.__shader, uniform_info["set"])(uniform_name, uniform_value)
            if self.__texture:
                if type(self.__texture) is dict:
                    for slot_name, texture in self.__texture.items():
                        self.__shader.uniform_sampler(slot_name, texture)
                else:
                    self.__shader.uniform_sampler("image", self.__texture)
            with utils.gpu_state(self.__gpu_states):
                self.__batch.draw_instanced(self.__shader, instance_start=0, instance_count=len(self.instances))
        
        def destroy(self):
            if self.tied_object:
                set_visibility(self.tied_object, True)
                self.tied_instance.destroy()
            self.is_destroyed = True
            custom_objects.remove(self)

    def draw_callback_3d(delta_time):
        common = get_common_values()
        with utils.gpu_state({
            "face_culling_set": "BACK",
            "depth_test_set": "LESS_EQUAL"
        }):
            view_projection_matrix = bpy.context.region_data.perspective_matrix

            custom_objects.sort(key = lambda custom_object: custom_object.draw_order)
            for custom_object in custom_objects:
                custom_object.render(view_projection_matrix, common)

    def depsgraph_update(depsgraph):
        updated_geometry = []
        updated_transform = []
        for depsgraph_update in depsgraph.updates:
            id = depsgraph_update.id
            if type(id) is bpy.types.Object:
                if depsgraph_update.is_updated_geometry:
                    updated_geometry.append(id.original)
                if depsgraph_update.is_updated_transform:
                    updated_transform.append(id.original)
        
        for custom_object in custom_objects:
            tied_object = custom_object.tied_object
            if tied_object:
                if tied_object in updated_geometry:
                    custom_object.generate_batch(tied_object)
                if tied_object in updated_transform:
                    custom_object.tied_instance.matrix = tied_object.matrix_world
    def post_registration():
        bpy.types.Object.visible_settings = bpy.props.PointerProperty(type=VisibleSettings)
    return {
        "classes": (VisibleSettings,),
        "listeners": (
            utils.listen_draw(draw_callback_3d, priority=-1),
            utils.listen_depsgraph_update(depsgraph_update),
        ),
        "post_registration": post_registration,
    }