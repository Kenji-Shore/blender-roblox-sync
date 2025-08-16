import bpy, gpu, mathutils, struct, sys, math, time
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
            "define": "USE_UV",
        },
        "color": {
            "type": "VEC3",
            "interface": "colorInterp",
            "define": "USE_COLOR",
        }
    }

    VISIBLE_SETTINGS = {
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
    bpy.types.Object.is_visible = bpy.props.BoolProperty(default=True)

    def set_visibility(object, is_visible):
        if utils.id_exists(object):
            if is_visible:
                for property_name, default_setting in VISIBLE_SETTINGS.items():
                    setattr(object, property_name, getattr(object.visible_settings, property_name))
            else:
                if object.is_visible:
                    for property_name, default_setting in VISIBLE_SETTINGS.items():
                        setattr(object.visible_settings, property_name, getattr(object, property_name))
                for property_name, default_setting in VISIBLE_SETTINGS.items():
                    setattr(object, property_name, not default_setting)
            object.is_visible = is_visible

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
    
    GLSL_ARRAY_STRUCT_ALIGNMENT = 16
    GLSL_TYPES = {
        "BOOL": {"alignment": 4, "set": "uniform_bool", "encode": lambda val: struct.pack("?3x", val)},
        "FLOAT": {"alignment": 4, "set": "uniform_float", "encode": lambda val: struct.pack("f", val)},
        "INT": {"alignment": 4, "set": "uniform_int", "encode": lambda val: struct.pack("i", val)},
        "UINT": {"alignment": 4, "set": "uniform_int", "encode": lambda val: struct.pack("I", val)},

        "VEC2": {"alignment": 8, "set": "uniform_float", "encode": lambda val: struct.pack("2f", *val[:])},
        "VEC3": {"alignment": 16, "set": "uniform_float", "encode": lambda val: struct.pack("3f4x", *val[:])},
        "VEC4": {"alignment": 16, "set": "uniform_float", "encode": lambda val: struct.pack("4f", *val[:])},

        "IVEC2": {"alignment": 8, "set": "uniform_int", "encode": lambda val: struct.pack("2i", *val[:])},
        "IVEC3": {"alignment": 16, "set": "uniform_int", "encode": lambda val: struct.pack("3i4x", *val[:])},
        "IVEC4": {"alignment": 16, "set": "uniform_int", "encode": lambda val: struct.pack("4i", *val[:])},

        "UVEC2": {"alignment": 8, "set": "uniform_int", "encode": lambda val: struct.pack("2I", *val[:])},
        "UVEC3": {"alignment": 16, "set": "uniform_int", "encode": lambda val: struct.pack("3I4x", *val[:])},
        "UVEC4": {"alignment": 16, "set": "uniform_int", "encode": lambda val: struct.pack("4I", *val[:])},

        "MAT3": {
            "alignment": 16,
            "set": "uniform_float",
            "encode": lambda val: struct.pack("3f4x3f4x3f4x", *(val.col[0][:] + val.col[1][:] + val.col[2][:]))
        },
        "MAT4": {
            "alignment": 16,
            "set": "uniform_float",
            "encode": lambda val: struct.pack("16f", *(val.col[0][:] + val.col[1][:] + val.col[2][:] + val.col[3][:]))
        }
    }

    UNIFORMS = {
        "viewport": {
            "type": "VEC4",
            "value": lambda object, states, geometry_type: states["viewport"]
        },
        "view_dir": {
            "type": "VEC3",
            "value": lambda object, states, geometry_type: states["view_dir"]
        },
        "sun_dir": {
            "type": "VEC3",
            "value": lambda object, states, geometry_type: states["sun_dir"]
        },
        "world_color": {
            "type": "VEC3",
            "value": lambda object, states, geometry_type: states["world_color"]
        },
        "sun_color": {
            "type": "VEC3",
            "value": lambda object, states, geometry_type: states["sun_color"]
        },
        "scale": {
            "type": "FLOAT",
            "value": lambda object, states, geometry_type: states["scale"]
        },
        "exponent": {
            "type": "FLOAT",
            "value": lambda object, states, geometry_type: states["exponent"]
        },
        "scroll_uvs": {
            "type": "VEC2",
            "value": lambda object, states, geometry_type: mathutils.Vector((0, (-object.tied_to_object_material.scroll_speed * time.time()) % 1))
        },
        "alpha": {
            "type": "FLOAT",
            "value": lambda object, states, geometry_type: object.alpha
        },

        "model_view_matrix": {
            "type": "MAT4",
            "instance": True,
            "value": lambda instance, states, geometry_type: states["view_projection_matrix"] @ instance.matrix
        },
        "normal_matrix": {
            "type": "MAT3",
            "instance": True,
            "value": lambda instance, states, geometry_type: instance.matrix.to_3x3().inverted().transposed()
        },
    }

    global create_shader
    def create_shader(*, 
        vertex,
        fragment, 
        attribs=(), 
        use_texture=False, 
        texture_slots=("image",), 
        uniforms=("normal_matrix",), 
        interfaces=None, 
        define=None,
        offset_depth=False,
    ):
        shader_info = gpu.types.GPUShaderCreateInfo()

        non_instance_uniforms = []
        instance_uniforms = []
        
        uniforms += ("model_view_matrix",)
        for uniform in uniforms:
            if type(uniform) is str:
                uniform_name = uniform
                uniform_info = UNIFORMS[uniform]
            else:
                uniform_name, uniform_info = uniform

            uniform_type = uniform_info["type"]
            glsl_type = GLSL_TYPES[uniform_type]
            if "instance" in uniform_info:
                instance_uniforms.append({
                    "name": uniform_name, 
                    "value": uniform_info["value"],
                    "type": uniform_type.lower(),
                    "alignment": glsl_type["alignment"], 
                    "encode": glsl_type["encode"], 
                })
            else:
                shader_info.push_constant(uniform_type, uniform_name)
                non_instance_uniforms.append({
                    "name": uniform_name, 
                    "value": uniform_info["value"],
                    "set": glsl_type["set"],
                })

        instance_uniforms.sort(key=lambda uniform: uniform["alignment"], reverse=True)
        if len(instance_uniforms) > 0:
            struct_strings = []
            for uniform in instance_uniforms:
                struct_strings.append(f"    {uniform['type']} {uniform['name']};")
            struct_strings.insert(0, "struct InstanceUniforms {")
            struct_strings.append("};")
            shader_info.typedef_source("\n".join(struct_strings))
            shader_info.uniform_buf(0, "InstanceUniforms", "instance_uniforms[]")

        if use_texture:
            index = 0
            for slot_name in texture_slots:
                shader_info.sampler(index, "FLOAT_2D", slot_name)
                index += 1
            shader_info.define("USE_TEXTURE")
        if not "pos" in attribs:
            attribs = attribs + ("pos",)
        if offset_depth:
            shader_info.define("OFFSET_DEPTH")
            shader_info.depth_write("LESS")
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
            if "define" in attrib_info:
                shader_info.define(attrib_info["define"])
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
            "non_instance_uniforms": non_instance_uniforms,
            "instance_uniforms": instance_uniforms,
        }

    shaders_path = utils.get_path(package, "shaders")
    DEFAULT_SHADERS = {}
    DEFAULT_VERT = shaders_path.joinpath("default_vert.glsl").read_text()
    DEFAULT_FRAG = shaders_path.joinpath("default_frag.glsl").read_text()
    def get_default_shader(use_texture, use_color, use_scroll_texture):
        default_shader_config = (use_texture, use_color, use_scroll_texture)
        if default_shader_config in DEFAULT_SHADERS:
            shader = DEFAULT_SHADERS[default_shader_config]
        else:
            attribs = ("normal",)
            if use_texture:
                attribs += ("uv",)
            if use_color:
                attribs += ("color",)

            shader = create_shader(
                vertex=DEFAULT_VERT,
                fragment=DEFAULT_FRAG,
                attribs=attribs,
                use_texture=use_texture,
                uniforms=("normal_matrix", "sun_dir", "world_color", "sun_color", "scale", "exponent", "alpha") + (("scroll_uvs",) if use_scroll_texture else ()),
                offset_depth=True,
            )
            DEFAULT_SHADERS[default_shader_config] = shader
        return shader
    
    custom_objects = []
    class CustomObjectInstance:
        def __init__(self, custom_object, matrix=None, object=None):
            self.custom_object = custom_object
            self.object = object.original if object else None
            self.visible = True
            custom_object.instances.append(self)

            self.__transform = mathutils.Matrix.Identity(4)
            self.__scale = None
            self.__scale_matrix = None
            self.__matrix = None
            if self.object:
                if not self.custom_object.tied_to_object_material:
                    set_visibility(self.object, False)
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
                value = bpy.context.view_layer.depsgraph.id_eval_get(self.object).matrix_world
                tied_matrix_get = self.custom_object.tied_matrix_get
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
            if self.object and (not self.custom_object.tied_to_object_material):
                set_visibility(self.object, True)
            if self in self.custom_object.instances:
                self.custom_object.instances.remove(self)

    tied_to_properties = {}
    def update_object_property(object, tied_to_property):
        if getattr(object, tied_to_property):
            for custom_object in tied_to_properties[tied_to_property]:
                CustomObjectInstance(custom_object, object=object)
        else:
            for custom_object in tied_to_properties[tied_to_property]:
                for instance in custom_object.instances.copy():
                    if instance.object == object.original:
                        instance.destroy()
    
    def object_visibility_change(object, is_visible, object_exists):
        if object_exists:
            for tied_to_property, tied_custom_objects in tied_to_properties.items():
                if getattr(object, tied_to_property):
                    for custom_object in tied_custom_objects:
                        tied_instance = None
                        for instance in custom_object.instances:
                            if instance.object == object.original:
                                tied_instance = instance
                                break
                        if not tied_instance:
                            CustomObjectInstance(custom_object, object=object)

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
            tied_to_object_material=None,
            tied_to_property=None,
            tied_matrix_get=None,
        ):
            if not shader:
                shader = get_default_shader(
                    use_texture=(image != None),
                    use_color=use_color,
                    use_scroll_texture=tied_to_object_material and tied_to_object_material.use_scroll_texture
                )

            self.__shader = shader["shader"]
            self.__vertex_attribs = shader["vertex_attribs"]
            self.__non_instance_uniforms = shader["non_instance_uniforms"]
            self.__instance_uniforms = shader["instance_uniforms"]
            self.__init_texture(image, shader)

            self.__gpu_states = gpu_states
            self.draw_order = draw_order if draw_order > 0 else LARGE_INT + draw_order
            self.draw_geometry = draw_geometry

            self.instances = []
            self.tied_to_object = None
            self.tied_to_object_material = None
            self.tied_to_property = tied_to_property
            self.tied_matrix_get = tied_matrix_get
            if tied_to_property:
                if not tied_to_property in tied_to_properties:
                    tied_to_properties[tied_to_property] = []
                tied_to_properties[tied_to_property].append(self)
                setattr(bpy.types.Object, tied_to_property, bpy.props.BoolProperty(
                    default=False, update=lambda object, context: update_object_property(object, tied_to_property)
                ))
            
            self.alpha = 1
            if tied_to_object:
                self.tied_to_object = object.original
                self.tied_to_object_material = tied_to_object_material
                CustomObjectInstance(self, object=object)
            self.generate_batch(object.original)
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

        def __get_tied_material_index(self, object):
            for material_slot in object.material_slots:
                material = material_slot.material
                if material == self.tied_to_object_material:
                    return material_slot.slot_index
                
        def __generate_faces(self, object, mesh):
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
            indices = []

            use_uvs = "uv" in self.__vertex_attribs
            use_colors = "color" in self.__vertex_attribs

            vertices = mesh.vertices
            loops = mesh.loops
            loop_uvs = mesh.uv_layers.active and mesh.uv_layers.active.uv
            loop_colors = mesh.color_attributes.active_color and mesh.color_attributes.active_color.data
            
            index = 0
            def process_loop(loop):
                nonlocal index
                loop_index = index
                index += 1

                pos_attribs.append(vertices[loop.vertex_index].co.copy())
                normal_attribs.append(loop.normal.copy())
                if use_uvs:
                    if loop_uvs:
                        uv_attribs.append(loop_uvs[loop.index].vector.copy())
                    else:
                        uv_attribs.append(mathutils.Vector((0, 0)))
                if use_colors:
                    if loop_colors:
                        color = loop_colors[loop.index].color_srgb
                        color_attribs.append(mathutils.Vector((color[0], color[1], color[2])))
                    else:
                        color_attribs.append(mathutils.Vector((1, 1, 1)))
                return loop_index

            if self.tied_to_object_material:
                material_index = self.__get_tied_material_index(object)
                for loop_triangle in mesh.loop_triangles:
                    if loop_triangle.material_index == material_index:
                        triangle_indices = ()
                        for loop_index in loop_triangle.loops:
                            triangle_indices += (process_loop(loops[loop_index]),)
                        indices.append(triangle_indices)
            else:
                for loop in loops:
                    process_loop(loop)
                for loop_triangle in mesh.loop_triangles:
                    indices.append(tuple(loop_triangle.loops))

            load_attribs = {}
            for attrib in self.__vertex_attribs:
                if attrib in vertex_attribs:
                    load_attribs[attrib] = vertex_attribs[attrib]
            return batch_for_shader(self.__shader, "TRIS", load_attribs, indices=indices)
        
        def __generate_edges(self, object, mesh):
            load_attribs = {}
            indices = []

            vertices = mesh.vertices
            load_attribs["pos"] = [v.co.copy() for v in vertices]
            for edge in mesh.edges:
                indices.append(tuple(edge.vertices))
            return batch_for_shader(self.__shader, "LINES", load_attribs, indices=indices)

        def generate_batch(self, object, depsgraph=None):
            object.update_from_editmode()
            mesh = object.data
            if depsgraph:
                mesh = object.to_mesh(preserve_all_data_layers=True, depsgraph=depsgraph)
            if self.tied_to_object and (not self.tied_to_object_material):
                set_visibility(self.tied_to_object, False)

            generate_geometry = {
                "faces": self.__generate_faces,
                "edges": self.__generate_edges
            }
            
            self.__batches = {}
            for geometry_type in self.draw_geometry:
                self.__batches[geometry_type] = generate_geometry[geometry_type](object, mesh)
            utils.trigger_redraw()

        def new(self, *, matrix=None, transform=mathutils.Matrix(), scale=mathutils.Vector((1, 1, 1))):
            if self.tied_to_object or self.tied_to_property:
                raise Exception("Attempted to create instance of a tied custom object")
            if not matrix:
                matrix = transform @ mathutils.Matrix.to_4x4(mathutils.Matrix.Diagonal(scale))
            new_instance = CustomObjectInstance(self, matrix=matrix)
            return new_instance
        
        def __get_uniform_value(self, uniform, object_or_instance, states, geometry_type):
            uniform_value = uniform["value"]
            if callable(uniform_value):
                uniform_value = uniform_value(object_or_instance, states, geometry_type)
            return uniform_value
        
        def __prep_instance_uniforms(self, states, geometry_type, instances):
            if len(self.__instance_uniforms) > 0:
                buf = b""
                def pad_buf(offset, alignment):
                    nonlocal buf
                    rounded_offset = alignment * math.ceil(offset / alignment)
                    pad_amount = rounded_offset - offset
                    if pad_amount > 0:
                        buf += struct.pack(f"{pad_amount}x")
                    return rounded_offset

                for instance in instances:
                    offset = 0
                    for uniform in self.__instance_uniforms:
                        offset = pad_buf(offset, uniform["alignment"])
                        encoded = uniform["encode"](self.__get_uniform_value(uniform, instance, states, geometry_type))
                        buf += encoded
                        offset += len(encoded)
                    offset = pad_buf(offset, GLSL_ARRAY_STRUCT_ALIGNMENT)

                self.__instance_buf = gpu.types.GPUUniformBuf(buf) #this python data must stay in memory until batch gets drawn
                self.__shader.uniform_block("instance_uniforms", self.__instance_buf)

        def __prep_render(self, states, geometry_type, instances):
            self.__prep_instance_uniforms(states, geometry_type, instances)
            for uniform in self.__non_instance_uniforms:
                getattr(self.__shader, uniform["set"])(uniform["name"], self.__get_uniform_value(uniform, self, states, geometry_type))

            if self.__texture:
                if type(self.__texture) is dict:
                    for slot_name, texture in self.__texture.items():
                        self.__shader.uniform_sampler(slot_name, texture)
                else:
                    self.__shader.uniform_sampler("image", self.__texture)
            
        def render(self, states, visible_objects):
            if (self.tied_to_object and (not utils.id_exists(self.tied_to_object))) or (self.tied_to_object_material and (not utils.id_exists(self.tied_to_object_material))):
                self.destroy()
                return
            if (self.tied_to_object and not (self.tied_to_object in visible_objects)):
                return
            
            instances = []
            for instance in self.instances.copy():
                if instance.object and (not utils.id_exists(instance.object)):
                    instance.destroy()
                elif instance.visible and not (instance.object and not (instance.object in visible_objects)):
                    instances.append(instance)

            if self.tied_to_object_material:
                self.alpha = self.tied_to_object_material.alpha
            instance_count = len(instances)
            if instance_count > 0:
                for geometry_type, batch in self.__batches.items():
                    gpu_states = self.__gpu_states
                    if gpu_states and (geometry_type in gpu_states):
                        gpu_states = gpu_states[geometry_type]
                    self.__prep_render(states, geometry_type, instances)
                    if self.tied_to_object_material and self.tied_to_object.mode == "EDIT":
                        gpu_states = gpu_states.copy() if gpu_states != None else {}
                        gpu_states["blend_set"] = "ADDITIVE"

                    with utils.gpu_state(gpu_states):
                        batch.draw_instanced(self.__shader, instance_start=0, instance_count=instance_count)
        
        def destroy(self):
            for instance in self.instances.copy():
                instance.destroy()
            if self.tied_to_property:
                tied_to_property_objects = tied_to_properties[self.tied_to_property]
                if self in tied_to_property_objects:
                    tied_to_property_objects.remove(self)
            self.is_destroyed = True
            if self in custom_objects:
                custom_objects.remove(self)

    def draw_callback_3d(delta_time):
        states = {}
        states["world_color"], states["sun_color"], states["sun_dir"] = get_world_lighting()
        states["view_dir"] = get_view_dir()
        states["viewport"] = gpu.state.viewport_get()
        states["view_projection_matrix"] = bpy.context.region_data.perspective_matrix

        color_managed_view_settings = bpy.context.scene.view_settings
        exposure = color_managed_view_settings.exposure
        gamma = color_managed_view_settings.gamma
        states["scale"] = 1 if exposure == 0 else pow(2, exposure)
        states["exponent"] = 1 if gamma == 1 else 1 / max(1.192092896e-07, gamma)
        
        visible_objects = bpy.context.visible_objects
        with utils.gpu_state({
            "blend_set": "ALPHA",
            "face_culling_set": "BACK",
            "depth_test_set": "LESS_EQUAL"
        }):
            custom_objects.sort(key = lambda custom_object: custom_object.draw_order)
            for custom_object in custom_objects.copy():
                custom_object.render(states, visible_objects)

    def depsgraph_update(depsgraph):
        for depsgraph_update in depsgraph.updates:
            id = depsgraph_update.id.original
            if (type(id) is bpy.types.Object) and depsgraph_update.is_updated_geometry:
                for custom_object in custom_objects:
                    if custom_object.tied_to_object == id:
                        custom_object.generate_batch(id, depsgraph)
     
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