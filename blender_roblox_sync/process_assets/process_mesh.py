import struct
from collections import deque
import numpy as np

def register(utils, package):
    
    global process
    def process(assets, mesh):
        vertices = mesh.vertices

        verts_keys = {}
        verts = deque()
        verts_index = 0
        tri_mat_indices = deque()
        tri_vis = deque()
        tri_normals = deque()
        all_tri_uvs = {}
        all_tri_colors = {}
            
        loops = mesh.loops
        for loop_triangle in mesh.loop_triangles:
            tri_mat_indices.append(loop_triangle.material_index)
            li1, li2, li3 = tuple(loop_triangle.loops)
            l1, l2, l3 = loops[li1], loops[li2], loops[li3]

            vi = l1.vertex_index
            if not vi in verts_keys:
                verts_keys[vi] = verts_index
                verts_index += 1

                vert = vertices[vi].co
                verts.append(vert.x)
                verts.append(vert.y)
                verts.append(vert.z)
            tri_vis.append(verts_keys[vi])

            vi = l2.vertex_index
            if not vi in verts_keys:
                verts_keys[vi] = verts_index
                verts_index += 1

                vert = vertices[vi].co
                verts.append(vert.x)
                verts.append(vert.y)
                verts.append(vert.z)
            tri_vis.append(verts_keys[vi])

            vi = l3.vertex_index
            if not vi in verts_keys:
                verts_keys[vi] = verts_index
                verts_index += 1

                vert = vertices[vi].co
                verts.append(vert.x)
                verts.append(vert.y)
                verts.append(vert.z)
            tri_vis.append(verts_keys[vi])
            
            normal = l1.normal
            tri_normals.append(normal.x)
            tri_normals.append(normal.y)
            tri_normals.append(normal.z)

            normal = l2.normal
            tri_normals.append(normal.x)
            tri_normals.append(normal.y)
            tri_normals.append(normal.z)

            normal = l3.normal
            tri_normals.append(normal.x)
            tri_normals.append(normal.y)
            tri_normals.append(normal.z)

        uv_layers = mesh.uv_layers
        active_uv_layer_name = ""
        for uv_layer in uv_layers:
            if uv_layer.active_render:
                active_uv_layer_name = uv_layer.name
                break   
        for uv_layer in uv_layers:
            tri_uvs = deque()
            loop_uvs = uv_layer.uv
            for loop_triangle in mesh.loop_triangles:
                li1, li2, li3 = tuple(loop_triangle.loops)

                uv = loop_uvs[li1].vector
                tri_uvs.append(uv.x)
                tri_uvs.append(uv.y)

                uv = loop_uvs[li2].vector
                tri_uvs.append(uv.x)
                tri_uvs.append(uv.y)

                uv = loop_uvs[li3].vector
                tri_uvs.append(uv.x)
                tri_uvs.append(uv.y)
            uv_bytes = np.array(tri_uvs, dtype=np.float32).data
            all_tri_uvs[uv_layer.name] = assets.hash_bytes(uv_bytes)

        for color_attribute in mesh.color_attributes:
            tri_colors = deque()
            loop_colors = color_attribute.data
            for loop_triangle in mesh.loop_triangles:
                li1, li2, li3 = tuple(loop_triangle.loops)

                color = loop_colors[li1].color_srgb
                tri_colors.append(color[0])
                tri_colors.append(color[1])
                tri_colors.append(color[2])
                tri_colors.append(color[3])

                color = loop_colors[li2].color_srgb
                tri_colors.append(color[0])
                tri_colors.append(color[1])
                tri_colors.append(color[2])
                tri_colors.append(color[3])

                color = loop_colors[li3].color_srgb
                tri_colors.append(color[0])
                tri_colors.append(color[1])
                tri_colors.append(color[2])
                tri_colors.append(color[3])
            tri_colors = np.array(tri_colors, dtype=np.float32)
            np.multiply(tri_colors, 255, out=tri_colors)
            color_bytes = tri_colors.astype(np.uint8).data
            all_tri_colors[color_attribute.name] = assets.hash_bytes(color_bytes)

        verts = np.array(verts, dtype=np.float32)
        tri_mat_indices = np.array(tri_mat_indices, dtype=np.uint16)
        tri_vis = np.array(tri_vis, dtype=np.uint16)
        tri_normals = np.array(tri_normals, dtype=np.float32)
        np.multiply(tri_normals, 127, out=tri_normals)
        mesh_bytes = b"".join((
            struct.pack("<H", verts_index),
            verts.data,
            struct.pack("<H", len(tri_vis) // 3),
            tri_vis.data,
            tri_normals.astype(np.int8).data
        ))

        return (assets.hash_bytes(mesh_bytes), active_uv_layer_name, all_tri_uvs, all_tri_colors,)