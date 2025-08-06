import bpy, bl_ui, mathutils

def register(utils, package):
    multi_vertex_paint = utils.import_module("multi_vertex_paint")
    custom_objects = utils.import_module("custom_objects")

    def get_node_setup(material):
        node_properties = {}
        if not material.use_image_transparency:
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
                    "Factor_Float": { "enabled": False, "default_value": 1 },
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
            "outputs": {
                "Alpha": { "enabled": material.use_image_transparency }
            }
        }
        node_properties["ShaderNodeBsdfPrincipled"] = {
            "properties": {
                "location": mathutils.Vector((510, -80)),
                "width": 240,
                "height": 100,
                "subsurface_method": "RANDOM_WALK",
                "distribution": "MULTI_GGX",
            },
            "inputs": {
                "Metallic": { "enabled": False, "default_value": 0 },
                "Roughness": { "enabled": False, "default_value": 1 },
                "IOR": { "enabled": False, "default_value": 1 },
                "Alpha": { "enabled": True, "default_value": 0 if material.use_scroll_texture else material.alpha },
                "Normal": { "enabled": False, "default_value": [0, 0, 0] },
                "Weight": { "enabled": False, "default_value": 0 },
                "Diffuse Roughness": { "enabled": False, "default_value": 0 },

                "Subsurface Weight": { "enabled": False, "default_value": 0 },
                "Subsurface Radius": { "enabled": False, "default_value": [1, 0.2, 0.1] },
                "Subsurface Scale": { "enabled": False, "default_value": 0.05 },
                "Subsurface IOR": { "enabled": False },
                "Subsurface Anisotropy": { "enabled": False, "default_value": 0 },

                "Specular IOR Level": { "enabled": False, "default_value": 0.5 },
                "Specular Tint": { "enabled": False, "default_value": [1, 1, 1, 1] },
                "Anisotropic": { "enabled": False, "default_value": 0 },
                "Anisotropic Rotation": { "enabled": False, "default_value": 0 },
                "Tangent": { "enabled": False, "default_value": [0, 0, 0] },
                "Transmission Weight": { "enabled": False, "default_value": 0 },

                "Coat Weight": { "enabled": False, "default_value": 0 },
                "Coat Roughness": { "enabled": False, "default_value": 0.03 },
                "Coat IOR": { "enabled": False, "default_value": 1.5 },
                "Coat Tint": { "enabled": False, "default_value": [1, 1, 1, 1] },
                "Coat Normal": { "enabled": False, "default_value": [0, 0, 0] },

                "Sheen Weight": { "enabled": False, "default_value": 0 },
                "Sheen Roughness": { "enabled": False, "default_value": 0.5 },
                "Sheen Tint": { "enabled": False, "default_value": [1, 1, 1, 1] },

                "Emission Color": { "enabled": False, "default_value": [1, 1, 1, 1] },
                "Emission Strength": { "enabled": False, "default_value": 0 },

                "Thin Film Thickness": { "enabled": False, "default_value": 0 },
                "Thin Film IOR": { "enabled": False, "default_value": 1.33 },
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
        if material.use_image_transparency:
            node_links.append((("ShaderNodeTexImage", "Color"), ("ShaderNodeBsdfPrincipled", "Base Color")))
            node_links.append((("ShaderNodeTexImage", "Alpha"), ("ShaderNodeBsdfPrincipled", "Alpha")))
        else:
            node_links.append((("ShaderNodeTexImage", "Color"), ("ShaderNodeMix", "A_Color")))
            node_links.append((("ShaderNodeVertexColor", "Color"), ("ShaderNodeMix", "B_Color")))
            node_links.append((("ShaderNodeMix", "Result_Color"), ("ShaderNodeBsdfPrincipled", "Base Color")))
        node_links.append((("ShaderNodeBsdfPrincipled", "BSDF"), ("ShaderNodeOutputMaterial", "Surface")))

        return node_properties, node_links

    def search_sockets(modify_nodes, socket_type, bl_idname, socket_identifier):
        for socket in getattr(modify_nodes.get(bl_idname), socket_type):
            if socket.identifier == socket_identifier:
                return socket
            
    custom_frame_name = "CustomMaterialFrame"
    def get_custom_material_label(material):
        return ("Transparent " if material.use_image_transparency else "") + "Image Material " + ("[Enabled]" if material.use_custom_material else "[Disabled]")

    def get_custom_material_frame(nodes):
        frame = nodes.get(custom_frame_name)
        if frame and (frame.bl_idname == "NodeFrame"):
            return frame

    def is_in_custom_material(nodes, node, frame=None):
        if not frame:
            frame = get_custom_material_frame(nodes)
        if frame:
            return node.parent == frame

    def disable_custom_material(material):
        if material.node_tree:
            nodes = material.node_tree.nodes
            frame = get_custom_material_frame(nodes)
            if frame:
                frame.label = get_custom_material_label(material)
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

    def init_custom_material(material):
        if material.node_tree:
            node_properties, node_links = get_node_setup(material)
            nodes = material.node_tree.nodes
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
            frame.label = get_custom_material_label(material)

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

            links = material.node_tree.links
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
            material = context.material

            box = layout.box()
            box.prop(material, "use_custom_material", text="Use Custom Material")

            if material.use_custom_material:
                nodes = material.node_tree.nodes
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
                
                layout.prop(material, "use_image_transparency", text="Use Image Transparency")
                layout.use_property_split = True
                if not material.use_image_transparency:
                    layout.prop(material, "alpha", text="Alpha")
                
                layout.use_property_split = False
                layout.prop(material, "use_scroll_texture", text="Use Scroll Texture")
                layout.use_property_split = True
                if material.use_scroll_texture:
                    layout.prop(material, "scroll_speed", text="Scroll Speed")
            else:
                super().draw(context)

    def update_use_custom_material(self, _=None):
        if self.use_custom_material:
            init_custom_material(self)
        else:
            disable_custom_material(self)

    objects_assigned_materials = utils.id_dict()
    materials_assignee_objects = utils.id_dict()
    scroll_materials = utils.id_dict()
    def update_scroll_material_objects(material, object, is_deleting):
        if is_deleting:
            if material in scroll_materials:
                scroll_material = scroll_materials[material]
                if object in scroll_material:
                    scroll_material[object].destroy()
                    del scroll_material[object]
                if len(scroll_material) == 0:
                    del scroll_materials[material]
        else:
            if not (material in scroll_materials):
                scroll_materials[material] = utils.id_dict()
            scroll_material = scroll_materials[material]
            if not (object in scroll_material):
                nodes = material.node_tree.nodes
                image_node = None
                for node in nodes:
                    if is_in_custom_material(nodes, node) and (type(node) is bpy.types.ShaderNodeTexImage):
                        image_node = node
                        break
                
                scroll_object = custom_objects.CustomObject(
                    object=object, 
                    image=image_node.image,
                    draw_geometry=("faces",),
                    tied_to_object=True,
                    tied_to_object_material=material
                )
                scroll_material[object] = scroll_object

    def update_scroll_material(material, _=None):
        if material in materials_assignee_objects:
            for object in materials_assignee_objects[material]:
                update_scroll_material_objects(material, object, not material.use_scroll_texture)
        update_use_custom_material(material)
    def update_transparency(material, _=None):
        if material.use_custom_material and (not (material.use_scroll_texture or material.use_image_transparency)):
            nodes = material.node_tree.nodes
            bsdf_node = None
            for node in nodes:
                if is_in_custom_material(nodes, node) and (type(node) is bpy.types.ShaderNodeBsdfPrincipled):
                    bsdf_node = node
                    break
            
            alpha_socket = None
            for socket in bsdf_node.inputs:
                if socket.identifier == "Alpha":
                    alpha_socket = socket
                    break
            if alpha_socket:
                alpha_socket.default_value = material.alpha

    bpy.types.Material.use_custom_material = bpy.props.BoolProperty(default=False, update=update_use_custom_material)
    bpy.types.Material.use_image_transparency = bpy.props.BoolProperty(default=False, update=update_use_custom_material)
    bpy.types.Material.alpha = bpy.props.FloatProperty(default=1, min=0, max=1, update=update_transparency)
    bpy.types.Material.use_scroll_texture = bpy.props.BoolProperty(default=False, update=update_scroll_material)
    bpy.types.Material.scroll_speed = bpy.props.FloatProperty(default=1, min=-10, max=10, update=update_use_custom_material)
    
    def update_object_material(object, is_visible=True):
        existing_materials = set()
        new_materials = set()
        if is_visible and (object.type == "MESH"):
            for material_slot in object.material_slots:
                material = material_slot.material
                if material:
                    new_materials.add(material.original)
        
        assigned_materials = None
        if object in objects_assigned_materials:
            assigned_materials = objects_assigned_materials[object]
            for assigned_material in assigned_materials:
                existing_materials.add(assigned_material)

            for material in (existing_materials - new_materials):
                update_scroll_material_objects(material, object, True)
                assignee_objects = materials_assignee_objects[material]
                assignee_objects.remove(object)
                assigned_materials.remove(material)
                if len(assignee_objects) == 0:
                    del materials_assignee_objects[material]

        if is_visible:
            if assigned_materials == None:
                assigned_materials = utils.id_list()
                objects_assigned_materials[object] = assigned_materials
            for material in (new_materials - existing_materials):
                if material.use_scroll_texture:
                    update_scroll_material_objects(material, object, False)
                assignee_objects = materials_assignee_objects[material] if material in materials_assignee_objects else utils.id_list()
                materials_assignee_objects[material] = assignee_objects
                assignee_objects.append(object)
                assigned_materials.append(material)
        if (assigned_materials != None) and (len(assigned_materials) == 0):
            del objects_assigned_materials[object]

    def depsgraph_update(depsgraph):
        for depsgraph_update in depsgraph.updates:
            id = depsgraph_update.id
            if (type(id) is bpy.types.Object):
                update_object_material(id)
    def object_visibility_change(object, is_visible, object_exists):
        update_object_material(object, is_visible)
    return {
        "classes": (EEVEE_MATERIAL_PT_surface,),
        "listeners": (
            utils.listen_depsgraph_update(depsgraph_update),
            utils.listen_object_visibility_change(object_visibility_change),
        ),
    }