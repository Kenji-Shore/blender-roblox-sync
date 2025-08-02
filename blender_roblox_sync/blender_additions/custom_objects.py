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
    def get_default_shader(use_texture, use_color):
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
        return shader
        
    def float3x3_to_bytes(mat):
        col = mat.col
        return struct.pack("3f4x3f4x3f4x", *(col[0][:] + col[1][:] + col[2][:]))
    def float4x4_to_bytes(mat):
        col = mat.col
        return struct.pack("16f", *(col[0][:] + col[1][:] + col[2][:] + col[3][:]))
    
    custom_objects = []
    class CustomObjectInstance:
        def __init__(self, custom_object, matrix=None, object=None):
            self.__custom_object = custom_object
            self.object = object
            custom_object.instances.append(self)

            self.__transform = mathutils.Matrix.Identity(4)
            self.__scale = None
            self.__scale_matrix = None
            self.__matrix = None
            if object:
                set_visibility(object, False)
            else:
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
            if self.object:
                if not utils.object_exists(self.object):
                    self.destroy()
                    return
                
                value = self.object.matrix_world
                tied_matrix_get = self.__custom_object.tied_matrix_get
                if tied_matrix_get:
                    value = tied_matrix_get(value)
                return value
            else:
                return self.__matrix
        @matrix.setter
        def matrix(self, value):
            if value != self.__matrix:
                self.__matrix = value
                utils.trigger_redraw()

        def update_from_object(self):
            translation = self.tied_instance_object.matrix_world.decompose()
            self.transform = mathutils.Matrix.LocRotScale(translation, None, None)

        def destroy(self):
            if self.object:
                set_visibility(self.object, True)
            self.__custom_object.instances.remove(self)

    tied_to_properties = {}
    def update_object_property(object, tied_to_property):
        if getattr(object, tied_to_property):
            for custom_object in tied_to_properties[tied_to_property]:
                CustomObjectInstance(custom_object, object=object)
        else:
            for custom_object in tied_to_properties[tied_to_property]:
                for instance in custom_object.instances:
                    if instance.object == object:
                        instance.destroy()
    
    def object_visibility_change(object, is_visible):
        object = object.original
        for tied_to_property, tied_custom_objects in tied_to_properties.items():
            if getattr(object, tied_to_property):
                for custom_object in tied_custom_objects:
                    tied_instance = None
                    for instance in custom_object.instances:
                        if instance.object == object:
                            tied_instance = instance
                            break
                    if is_visible:
                        if not tied_instance:
                            CustomObjectInstance(custom_object, object=object)
                            custom_object
                    else:
                        if tied_instance:
                            tied_instance.destroy()

    global CustomObject
    class CustomObject:
        def __init__(self, *, 
            object, 
            image=None, 
            use_color=False, 
            shader=None, 

            draw_geometry=("faces",),
            draw_order=100, 
            gpu_states=None, 

            tied_to_object=False, 
            tied_to_property=None,
            tied_matrix_get=None,
        ):
            if not shader:
                shader = get_default_shader(
                    use_texture=(image != None),
                    use_color=use_color
                )

            self.__shader = shader["shader"]
            self.__vertex_attribs = shader["vertex_attribs"]
            self.__uniforms = shader["uniforms"]
            self.__init_texture(image, shader)

            self.__gpu_states = gpu_states
            self.draw_order = draw_order if draw_order > 0 else LARGE_INT + draw_order
            self.draw_geometry = draw_geometry

            self.instances = []
            self.tied_to_object = None
            self.tied_to_property = tied_to_property
            self.tied_matrix_get = tied_matrix_get
            if tied_to_property:
                if not tied_to_property in tied_to_properties:
                    tied_to_properties[tied_to_property] = []
                tied_to_properties[tied_to_property].append(self)
                setattr(bpy.types.Object, tied_to_property, bpy.props.BoolProperty(
                    default=False, update=lambda object, context: update_object_property(object, tied_to_property)
                ))
            if tied_to_object:
                self.tied_to_object = object.original
                CustomObjectInstance(self, object=object)
            self.generate_batch(object)
            self.is_destroyed = False
            custom_objects.append(self)
        
        def __init_texture(self, image, shader):
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

        def __generate_faces(self, mesh):
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

            load_attribs = {}
            for attrib in self.__vertex_attribs:
                if attrib in vertex_attribs:
                    load_attribs[attrib] = vertex_attribs[attrib]
            indices = []
            for loop_triangle in mesh.loop_triangles:
                indices.append(tuple(loop_triangle.loops))
            return batch_for_shader(self.__shader, "TRIS", load_attribs, indices=indices)
        
        def __generate_edges(self, mesh):
            load_attribs = {"pos": [v.co.copy() for v in mesh.vertices]}
            indices = []
            for edge in mesh.edges:
                indices.append(tuple(edge.vertices))
            return batch_for_shader(self.__shader, "LINES", load_attribs, indices=indices)

        def generate_batch(self, object):
            object.update_from_editmode()
            if self.tied_to_object:
                set_visibility(self.tied_to_object, False)

            generate_geometry = {
                "faces": self.__generate_faces,
                "edges": self.__generate_edges
            }
            
            mesh = object.data
            self.__batches = {}
            for geometry_type in self.draw_geometry:
                self.__batches[geometry_type] = generate_geometry[geometry_type](mesh)
            utils.trigger_redraw()

        def new(self, *, matrix=None, transform=mathutils.Matrix(), scale=mathutils.Vector((1, 1, 1))):
            if self.tied_to_object or self.tied_to_property:
                raise Exception("Attempted to create instance of a tied custom object")
            if not matrix:
                matrix = transform @ mathutils.Matrix.to_4x4(mathutils.Matrix.Diagonal(scale))
            new_instance = CustomObjectInstance(self, matrix=matrix)
            return new_instance
        
        def __prep_render(self, geometry_type, buf, common):
            self.__shader.uniform_block("my_struct", buf)
            if self.__uniforms:
                for uniform in self.__uniforms:
                    if type(uniform) is str:
                        uniform_name = uniform
                        uniform_info = COMMON_UNIFORMS[uniform]
                    else:
                        uniform_name, uniform_info = uniform

                    uniform_value = uniform_info["get_value"](self, geometry_type) if "get_value" in uniform_info else common[uniform_name]
                    getattr(self.__shader, uniform_info["set"])(uniform_name, uniform_value)
            if self.__texture:
                if type(self.__texture) is dict:
                    for slot_name, texture in self.__texture.items():
                        self.__shader.uniform_sampler(slot_name, texture)
                else:
                    self.__shader.uniform_sampler("image", self.__texture)
            
        def render(self, view_projection_matrix, common):
            if self.tied_to_object and (not utils.object_exists(self.tied_to_object)):
                self.destroy()
                return
            
            buf = b""
            draw_count = 0
            for instance in self.instances:
                mat = instance.matrix
                if mat:
                    buf += float4x4_to_bytes(view_projection_matrix @ mat)
                    buf += float3x3_to_bytes(mat.to_3x3().inverted().transposed())
                    draw_count += 1
            buf = gpu.types.GPUUniformBuf(buf)
            
            for geometry_type, batch in self.__batches.items():
                gpu_states = self.__gpu_states
                if gpu_states and (geometry_type in gpu_states):
                    gpu_states = gpu_states[geometry_type]
                self.__prep_render(geometry_type, buf, common)
                with utils.gpu_state(gpu_states):
                    batch.draw_instanced(self.__shader, instance_start=0, instance_count=draw_count)
        
        def destroy(self):
            for instance in self.instances:
                instance.destroy()
            if self.tied_to_property:
                tied_to_properties[self.tied_to_property].remove(self)
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
        for depsgraph_update in depsgraph.updates:
            id = depsgraph_update.id.original
            if (type(id) is bpy.types.Object) and depsgraph_update.is_updated_geometry:
                for custom_object in custom_objects:
                    if custom_object.tied_to_object == id:
                        custom_object.generate_batch(id)
                    
    def post_registration():
        bpy.types.Object.visible_settings = bpy.props.PointerProperty(type=VisibleSettings)
    return {
        "classes": (VisibleSettings,),
        "listeners": (
            utils.listen_draw(draw_callback_3d, priority=-1),
            utils.listen_depsgraph_update(depsgraph_update),
            utils.listen_object_visibility_change(object_visibility_change),
        ),
        "post_registration": post_registration,
    }