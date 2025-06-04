import struct, mathutils
from collections import deque
import numpy as np

def register(utils):
    
    def get_loop_colors(mesh, assigned_materials):
        material_loop_colors = {}
        color_attributes = mesh.color_attributes
        for material_index, material_group in assigned_materials.items():
            if material_group["color_attribute_name"] != None:
                color_attribute = color_attributes.get(material_group["color_attribute_name"])
                if color_attribute:
                    material_loop_colors[material_index] = color_attribute.data
                else:
                    all_color_attributes = color_attributes.values()
                    material_loop_colors[material_index] = all_color_attributes[0].data if len(all_color_attributes) > 0 else None
        return material_loop_colors
    
    def get_loop_uvs(uv_layers):
        for uv_layer in uv_layers:
            if uv_layer.active_render:
                return uv_layer.uv
            
    class SeparatedMesh():
        def __init__(self, loop_uvs, loop_colors):
            self.loop_uvs = loop_uvs
            self.loop_colors = loop_colors

            self.verts = ({}, deque())
            self.verts_index = 0
            self.tris = (deque(), deque(), deque(), deque())

    class SeparatedMeshes(dict):
        def __getitem__(self, material_index):
            material_index = material_index if material_index in self.assigned_materials else 0
            try:
                return dict.__getitem__(self, material_index)
            except KeyError:
                separated_mesh = SeparatedMesh(self.loop_uvs, self.material_loop_colors.get(material_index))
                dict.__setitem__(self, material_index, separated_mesh)
                return separated_mesh
        
        def __init__(self, mesh, assigned_materials):
            self.loop_uvs = get_loop_uvs(mesh.uv_layers)
            self.assigned_materials = assigned_materials
            self.material_loop_colors = get_loop_colors(mesh, assigned_materials)
            super(SeparatedMeshes, self).__init__()

    global process_mesh   
    def process_mesh(mesh, scale, send_meshes, assigned_materials):
        vertices = mesh.vertices
        sign_x = 1 if scale.x >= 0 else -1
        sign_y = 1 if scale.y >= 0 else -1
        sign_z = 1 if scale.z >= 0 else -1
        flip_winding = sign_x * sign_y * sign_z < 0
        sign = mathutils.Vector((sign_x, sign_y, sign_z))
        scale *= sign

        separated_meshes = SeparatedMeshes(mesh, assigned_materials)
        loops = mesh.loops
        for loop_triangle in mesh.loop_triangles:
            s_mesh = separated_meshes[loop_triangle.material_index]
            loop_uvs, loop_colors = s_mesh.loop_uvs, s_mesh.loop_colors

            tri_vis, tri_normals, tri_uvs, tri_colors = s_mesh.tris
            verts_keys, verts = s_mesh.verts
            
            if flip_winding:
                li3, li2, li1 = tuple(loop_triangle.loops)
                l3, l2, l1 = loops[li3], loops[li2], loops[li1]
            else:
                li1, li2, li3 = tuple(loop_triangle.loops)
                l1, l2, l3 = loops[li1], loops[li2], loops[li3]

            vi = l1.vertex_index
            if not vi in verts_keys:
                verts_keys[vi] = s_mesh.verts_index
                s_mesh.verts_index += 1

                vert = vertices[vi].co * sign
                verts.append(vert.x)
                verts.append(vert.y)
                verts.append(vert.z)
            tri_vis.append(verts_keys[vi])

            vi = l2.vertex_index
            if not vi in verts_keys:
                verts_keys[vi] = s_mesh.verts_index
                s_mesh.verts_index += 1

                vert = vertices[vi].co * sign
                verts.append(vert.x)
                verts.append(vert.y)
                verts.append(vert.z)
            tri_vis.append(verts_keys[vi])

            vi = l3.vertex_index
            if not vi in verts_keys:
                verts_keys[vi] = s_mesh.verts_index
                s_mesh.verts_index += 1

                vert = vertices[vi].co * sign
                verts.append(vert.x)
                verts.append(vert.y)
                verts.append(vert.z)
            tri_vis.append(verts_keys[vi])
            
            normal = l1.normal * sign
            tri_normals.append(normal.x)
            tri_normals.append(normal.y)
            tri_normals.append(normal.z)

            normal = l2.normal * sign
            tri_normals.append(normal.x)
            tri_normals.append(normal.y)
            tri_normals.append(normal.z)

            normal = l3.normal * sign
            tri_normals.append(normal.x)
            tri_normals.append(normal.y)
            tri_normals.append(normal.z)

            if loop_uvs:
                uv = loop_uvs[li1].vector
                tri_uvs.append(uv.x)
                tri_uvs.append(uv.y)

                uv = loop_uvs[li2].vector
                tri_uvs.append(uv.x)
                tri_uvs.append(uv.y)

                uv = loop_uvs[li3].vector
                tri_uvs.append(uv.x)
                tri_uvs.append(uv.y)

            if loop_colors:
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

        hashes = []
        for material_index, s_mesh in separated_meshes.items():
            tri_vis, tri_normals, tri_uvs, tri_colors = s_mesh.tris
            _, verts = s_mesh.verts
            verts_index = s_mesh.verts_index
            flags = int(bool(s_mesh.loop_uvs))
            flags <<= flags
            flags += int(bool(s_mesh.loop_colors))

            tris_len = len(tri_vis) // 3
            verts = np.array(verts, dtype=np.float32)
            tri_vis = np.array(tri_vis, dtype=np.uint16)
            tri_normals = np.array(tri_normals, dtype=np.float32)
            tri_uvs = np.array(tri_uvs, dtype=np.float32)
            tri_colors = np.array(tri_colors, dtype=np.float32)

            np.multiply(tri_normals, 127, out=tri_normals)
            np.multiply(tri_colors, 255, out=tri_colors)

            mesh_bytes = b"".join((
                bytes((flags,)),
                struct.pack("<H", verts_index),
                verts.data,
                struct.pack("<H", tris_len),
                tri_vis.data,
                tri_normals.astype(np.int8).data,
                tri_uvs.data,
                tri_colors.astype(np.uint8).data
            ))
            mesh_hash = hash(mesh_bytes)
            if not mesh_hash in send_meshes:
                send_meshes[mesh_hash] = mesh_bytes
            
            assigned_material = assigned_materials[material_index]
            image_hash = assigned_material["image_hash"]

            has_image = image_hash != None
            mesh_image = (has_image, assigned_material["use_image_transparency"], mesh_hash, round(assigned_material["alpha"] * 255))
            if has_image:
                mesh_image += (image_hash,)
            hashes.append(mesh_image)
        return scale, tuple(hashes)