import bpy, struct
import numpy as np

def register(utils, package):

    def output_socket_is_connected(output_socket):
        for link in output_socket.links:
            if link.is_valid and (not link.is_muted) and node_is_connected(link.to_node, link.to_socket):
                return True
        return False

    def node_is_connected(node, input_socket):
        if type(node) is bpy.types.ShaderNodeOutputMaterial:
            return node.is_active_output
                
        if node.mute:
            for internal_link in node.internal_links:
                if internal_link.is_valid and (internal_link.from_socket == input_socket):
                    if output_socket_is_connected(internal_link.to_socket):
                        return True
        else:
            for output_socket in node.outputs:
                if output_socket_is_connected(output_socket):
                    return True
        return False

    def process_image(assets, image):
        width, height = tuple(image.size)
        if width == 0 and height == 0:
            return None
        
        pixels = np.empty(width * height * 4, dtype=np.float32)
        image.pixels.foreach_get(pixels)
        np.multiply(pixels, 255, out=pixels)
        image_bytes = struct.pack("<2H", width, height) + pixels.astype(np.uint8).data
        return assets.hash_bytes(image_bytes)

    global process
    def process(assets, material):
        if material.node_tree:
            uv_map = ""
            color_attribute = ""

            image_node = None
            bsdf_node = None
            for node in material.node_tree.nodes:
                match type(node):
                    case bpy.types.ShaderNodeTexImage:
                        if output_socket_is_connected(node.outputs.get("Color")) and node.image:
                            image_node = node
                    case bpy.types.ShaderNodeVertexColor:
                        if output_socket_is_connected(node.outputs.get("Color")):
                            color_attribute = node.layer_name
                    case bpy.types.ShaderNodeBsdfPrincipled:
                        if output_socket_is_connected(node.outputs.get("BSDF")):
                            bsdf_node = node
                    case bpy.types.ShaderNodeUVMap:
                        if output_socket_is_connected(node.outputs.get("UV")):
                            uv_map = node.uv_map

            use_image = image_node != None
            use_image_transparency = False 
            use_scroll_texture = material.use_custom_material and material.use_scroll_texture

            if use_image and bsdf_node:
                for link in bsdf_node.inputs.get("Alpha").links:
                    if link.is_valid and (not link.is_muted) and (link.from_node == image_node):
                        use_image_transparency = True
                        break
            
            send = (uv_map, color_attribute, use_image, use_image_transparency, use_scroll_texture,)
            if use_image:
                send += (process_image(assets, image_node.image),)
            if not use_image_transparency:
                send += (round((bsdf_node.inputs.get("Alpha").default_value if bsdf_node else 1) * 255),)
            if use_scroll_texture:
                send += (material.scroll_speed,)
            return send