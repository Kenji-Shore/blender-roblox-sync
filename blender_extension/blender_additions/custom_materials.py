import bpy, bl_ui, mathutils

def register(utils):
    multi_vertex_paint = utils.import_module("multi_vertex_paint")

    def get_node_setup(mat):
        node_properties = {}
        if mat.use_scroll_texture:
            node_properties["ShaderNodeUVMap"] = {
                "properties": {
                    "location": mathutils.Vector((-310, -100)),
                    "width": 140,
                    "height": 100,
                    "uv_map": "",
                    "show_options": False,
                },
            }
            node_properties["ShaderNodeMapping"] = {
                "properties": {
                    "location": mathutils.Vector((-140, -100)),
                    "width": 140,
                    "height": 100,
                    "vector_type": "POINT",
                    "show_options": False,
                },
                "inputs": {
                    "Rotation": {
                        "enabled": False,
                        "default_value": mathutils.Vector(),
                    },
                    "Scale": {
                        "enabled": False,
                        "default_value": mathutils.Vector((1, 1, 1)),
                    },
                },
            }
        if not mat.use_image_transparency:
            node_properties["ShaderNodeMix"] = {
                "properties": {
                    "location": mathutils.Vector((320, -100)),
                    "width": 140,
                    "height": 100,
                    "data_type": "RGBA",
                    "blend_type": "MULTIPLY",
                    "clamp_result": True,
                    "clamp_factor": True,
                    "factor_mode": "UNIFORM",
                    "show_options": False,
                },
                "inputs": {
                    "Factor_Float": {
                        "enabled": False,
                        "default_value": 1,
                    },
                },
            }
            node_properties["ShaderNodeVertexColor"] = {
                "properties": {
                    "location": mathutils.Vector((130, -350)),
                    "width": 140,
                    "height": 100,
                    "layer_name": multi_vertex_paint.VERTEX_COLOR_NAME,
                    "show_options": False,
                },
                "outputs": {
                    "Alpha": { "enabled": False }
                }
            }
        node_properties["ShaderNodeTexImage"] = {
            "properties": {
                "location": mathutils.Vector((30, -80)),
                "width": 240,
                "height": 100,
            },
            "inputs": {
                "Vector": { "enabled": mat.use_scroll_texture }
            },
            "outputs": {
                "Alpha": { "enabled": mat.use_image_transparency }
            }
        }
        node_properties["ShaderNodeBsdfPrincipled"] = {
            "properties": {
                "location": mathutils.Vector((510, -80)),
                "width": 240,
                "height": 100,
            },
            "inputs": {
                "Metallic": {
                    "enabled": False,
                    "default_value": 0
                },
                "Roughness": {
                    "enabled": False,
                    "default_value": 1
                },
                "IOR": {
                    "enabled": False,
                    "default_value": 1
                },
                "Alpha": { "enabled": True },
                "Normal": { "enabled": False },
                "Weight": { "enabled": False },
                "Diffuse Roughness": { "enabled": False },
                "Subsurface Weight": { "enabled": False },
                "Subsurface Radius": { "enabled": False },
                "Subsurface Scale": { "enabled": False },
                "Subsurface IOR": { "enabled": False },
                "Subsurface Anisotropy": { "enabled": False },
                "Specular IOR Level": { "enabled": False },
                "Specular Tint": { "enabled": False },
                "Anisotropic": { "enabled": False },
                "Anisotropic Rotation": { "enabled": False },
                "Tangent": { "enabled": False },
                "Transmission Weight": { "enabled": False },
                "Coat Weight": { "enabled": False },
                "Coat Roughness": { "enabled": False },
                "Coat IOR": { "enabled": False },
                "Coat Tint": { "enabled": False },
                "Coat Normal": { "enabled": False },
                "Sheen Weight": { "enabled": False },
                "Sheen Roughness": { "enabled": False },
                "Sheen Tint": { "enabled": False },
                "Emission Color": { "enabled": False },
                "Emission Strength": { "enabled": False },
                "Thin Film Thickness": { "enabled": False },
                "Thin Film IOR": { "enabled": False },
            },
        }
        node_properties["ShaderNodeOutputMaterial"] = {
            "properties": {
                "location": mathutils.Vector((790, -80)),
                "width": 140,
                "height": 100,
                "target": "EEVEE",
                "show_options": False,
                "is_active_output": True,
            },
            "inputs": {
                "Volume": { "enabled": False },
                "Displacement": { "enabled": False },
                "Thickness": { "enabled": False },
            }
        }

        node_links = []
        if mat.use_image_transparency:
            node_links.append((("ShaderNodeTexImage", "Color"), ("ShaderNodeBsdfPrincipled", "Base Color")))
            node_links.append((("ShaderNodeTexImage", "Alpha"), ("ShaderNodeBsdfPrincipled", "Alpha")))
        else:
            node_links.append((("ShaderNodeTexImage", "Color"), ("ShaderNodeMix", "A_Color")))
            node_links.append((("ShaderNodeVertexColor", "Color"), ("ShaderNodeMix", "B_Color")))
            node_links.append((("ShaderNodeMix", "Result_Color"), ("ShaderNodeBsdfPrincipled", "Base Color")))
        if mat.use_scroll_texture:
            node_links.append((("ShaderNodeUVMap", "UV"), ("ShaderNodeMapping", "Vector")))
            node_links.append((("ShaderNodeMapping", "Vector"), ("ShaderNodeTexImage", "Vector")))
        node_links.append((("ShaderNodeBsdfPrincipled", "BSDF"), ("ShaderNodeOutputMaterial", "Surface")))

        return node_properties, node_links

    def search_sockets(modify_nodes, socket_type, bl_idname, socket_identifier):
        for socket in getattr(modify_nodes.get(bl_idname), socket_type):
            if socket.identifier == socket_identifier:
                return socket
            
    custom_frame_name = "CustomMaterialFrame"
    def get_custom_material_label(mat):
        return ("Transparent " if mat.use_image_transparency else "") + "Image Material " + ("[Enabled]" if mat.use_custom_material else "[Disabled]")

    def get_custom_material_frame(nodes):
        frame = nodes.get(custom_frame_name)
        if frame and (frame.bl_idname == "NodeFrame"):
            return frame

    def is_in_custom_material(nodes, node, frame=None):
        if not frame:
            frame = get_custom_material_frame(nodes)
        if frame:
            return node.parent == frame

    def disable_custom_material(mat):
        nodes = mat.node_tree.nodes
        frame = get_custom_material_frame(nodes)
        if frame:
            frame.label = get_custom_material_label(mat)
            for node in nodes:
                if node.parent == frame and node.bl_idname == "ShaderNodeOutputMaterial":
                    nodes.remove(node)
        
        output_node_exists = False
        for node in nodes:
            if node.bl_idname == "ShaderNodeOutputMaterial":
                output_node_exists = True
                break
        if not output_node_exists:
            node = nodes.new(type="ShaderNodeOutputMaterial")
            node.location = mathutils.Vector((200, 160))

    def init_custom_material(mat):
        node_properties, node_links = get_node_setup(mat)
        if mat.node_tree:
            nodes = mat.node_tree.nodes
            frame = get_custom_material_frame(nodes)
            is_new = False
            if not frame:
                frame = nodes.new(type="NodeFrame")
                frame.name = custom_frame_name
                is_new = True
            frame.use_custom_color = True
            frame.label_size = 30
            frame.shrink = True
            frame.color = mathutils.Color((0.35, 0.35, 0.35))
            frame.location = mathutils.Vector((-500, -80))
            frame.label = get_custom_material_label(mat)

            modify_nodes = {}
            for node in nodes:
                if is_in_custom_material(nodes, node, frame):
                    if node.bl_idname in node_properties:
                        modify_nodes[node.bl_idname] = node
                    else:
                        nodes.remove(node)

            for bl_idname in node_properties.keys():
                if not bl_idname in modify_nodes:
                    node = nodes.new(type=bl_idname)
                    node.parent = frame
                    modify_nodes[bl_idname] = node

            links = mat.node_tree.links
            for link in links:
                if (link.from_node.parent == frame) or (link.to_node.parent == frame):
                    links.remove(link)
            for link in node_links:
                links.new(search_sockets(modify_nodes, "outputs", *link[0]), search_sockets(modify_nodes, "inputs", *link[1]))

            if is_new:
                image = None
                for node in nodes:
                    if node.parent != frame and node.bl_idname == "ShaderNodeTexImage":
                        image = node.image
                        break
                if image:
                    modify_nodes.get("ShaderNodeTexImage").image = image

            if mat.use_scroll_texture:
                location_socket = modify_nodes.get("ShaderNodeMapping").inputs.get("Location")
                driver = location_socket.driver_add("default_value", 1).driver
                driver.type = "SCRIPTED"
                driver.expression = f"frame * {-0.05 * mat.scroll_speed}"

            for bl_idname, node in modify_nodes.items():
                properties = node_properties.get(bl_idname)
                for k, v in properties["properties"].items():
                    setattr(node, k, v)
                
                input_properties = properties.get("inputs")
                if input_properties:
                    for input_socket in node.inputs:
                        socket_properties = input_properties.get(input_socket.identifier)
                        if socket_properties:
                            for k, v in socket_properties.items():
                                setattr(input_socket, k, v)

                output_properties = properties.get("outputs")
                if output_properties:
                    for output_socket in node.outputs:
                        socket_properties = output_properties.get(output_socket.identifier)
                        if socket_properties:
                            for k, v in socket_properties.items():
                                setattr(output_socket, k, v)

    class EEVEE_MATERIAL_PT_surface(bl_ui.properties_material.EEVEE_MATERIAL_PT_surface): #overwrite original panel
        def draw(self, context):
            layout = self.layout
            mat = context.material

            box = layout.box()
            box.prop(mat, "use_custom_material", text="Use Custom Material")

            if mat.use_custom_material:
                nodes = mat.node_tree.nodes
                image_node, bsdf_node = None, None
                for node in nodes:
                    if is_in_custom_material(nodes, node):
                        match type(node):
                            case bpy.types.ShaderNodeTexImage:
                                image_node = node
                            case bpy.types.ShaderNodeBsdfPrincipled:
                                bsdf_node = node
                
                if image_node.image and image_node.image.preview:
                    layout.template_icon(image_node.image.preview.icon_id, scale=4)
                layout.template_ID(image_node, "image", new="image.new", open="image.open")
                
                layout.prop(mat, "use_image_transparency", text="Use Image Transparency")
                layout.use_property_split = True
                if not mat.use_image_transparency:
                    alpha_socket = None
                    for socket in bsdf_node.inputs:
                        if socket.identifier == "Alpha":
                            alpha_socket = socket
                            break
                    layout.prop(alpha_socket, "default_value", text="Alpha")
                
                layout.use_property_split = False
                layout.prop(mat, "use_scroll_texture", text="Use Scroll Texture")
                layout.use_property_split = True
                if mat.use_scroll_texture:
                    layout.prop(mat, "scroll_speed", text="Scroll Speed")
            else:
                super().draw(context)

    def update_use_custom_material(self, _=None):
        if self.use_custom_material:
            init_custom_material(self)
        else:
            disable_custom_material(self)
    bpy.types.Material.use_custom_material = bpy.props.BoolProperty(default=True, update=update_use_custom_material)
    bpy.types.Material.use_image_transparency = bpy.props.BoolProperty(default=False, update=update_use_custom_material)
    bpy.types.Material.use_scroll_texture = bpy.props.BoolProperty(default=False, update=update_use_custom_material)
    bpy.types.Material.scroll_speed = bpy.props.FloatProperty(default=1, min=-10, max=10, update=update_use_custom_material)

    def material_added():
        update_use_custom_material(bpy.context.material)
    def load_post(file):
        bpy.context.scene.frame_start = 1
        bpy.context.scene.frame_end = 60
        bpy.ops.screen.animation_play()
        for mat in bpy.data.materials:
            update_use_custom_material(mat)
    return {
        "classes": (EEVEE_MATERIAL_PT_surface,),
        "listeners": (
            utils.listen_operator("MATERIAL_OT_new", material_added),
            utils.listen_handler("load_post", load_post),
        ),
    }