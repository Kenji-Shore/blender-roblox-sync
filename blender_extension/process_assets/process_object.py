import bpy

def register(utils):

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