import bpy, time

def register(utils):
    process_mesh = utils.import_module("process_mesh")
    process_materials = utils.import_module("process_materials")

    def get_visible_mesh_objects():
        objects = []
        for object in bpy.context.visible_objects:
            if not (object.id_type == "OBJECT" and object.type == "MESH"):
                continue
            objects.append(object)
        return objects
    
    global process_assets
    def process_assets():
        overall_start = time.process_time()
        
        send_meshes = {}
        send_images = {}
        send_objects = {}

        if bpy.context.mode == "EDIT_MESH":
            for object in get_visible_mesh_objects():
                if object.mode == "EDIT":
                    object.update_from_editmode()
        depsgraph = bpy.context.evaluated_depsgraph_get()

        for object in get_visible_mesh_objects():
            object = object.evaluated_get(depsgraph)
            position, rotation, scale = object.matrix_world.decompose()
            scale, hashes = process_mesh(object.data, scale, send_meshes, process_materials(object.material_slots, send_images))
            send_object = (
                object.name,
                object.matrix_world.copy().freeze(),
                scale.freeze(),
                hashes
            )

            object_hash = hash(send_object)
            send_objects[object_hash] = send_object
        
        server.fire("sendObjects", send_meshes, send_images, send_objects)
        print("overall", time.process_time() - overall_start)