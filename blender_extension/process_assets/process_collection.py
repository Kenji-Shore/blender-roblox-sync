import bpy

def register(utils):

    def get_visible_mesh_objects():
        objects = []
        for object in bpy.context.visible_objects:
            if not (object.id_type == "OBJECT" and object.type == "MESH"):
                continue
            objects.append(object)
        return objects
    
    def process_collection(collection):
        # print("collection", collection.name)
        for object in collection.objects:
            if object.is_instancer:
                instance_collection = object.instance_collection
                # if instance_collection.library:
                #     print("library", bpy.path.basename(instance_collection.library.filepath))
            # print(object.name)
        for child_collection in collection.children:
            process_collection(child_collection)
            
    global process
    def process(assets, object):
        if object.type == "MESH":
            object = object.evaluated_get(assets.depsgraph)
            position, rotation, scale = object.matrix_world.decompose()

            mesh = object.data
            assets.process("mesh", mesh)

            material_slots = []
            for material_slot in object.material_slots:
                material = material_slot.material
                assets.process("material", material)
                material_slots[material_slot.slot_index] = material.name

            return (mesh.name, object.matrix_world.copy().freeze(), scale.freeze(), material_slots,)