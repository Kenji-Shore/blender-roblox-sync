import bpy

def register(utils):

    global process
    def process(assets, object, is_root=False):
        object = object.evaluated_get(assets.depsgraph)
        transform = object.matrix_world
        _, _, scale = transform.decompose()

        if is_root:
            for child in object.children:
                assets.process(child)

        is_instance = object.is_instancer
        has_parent = object.parent != None
        has_mesh = (object.type == "MESH") and object.data

        send = (
            transform.copy().freeze(), 
            scale.freeze(),
            is_instance,
            has_parent,
            has_mesh,
        )

        if has_parent:
            send += assets.get_asset_name(object.parent)
        if is_instance:
            send += assets.process(object.instance_collection)
        if has_mesh:
            mesh = object.data

            material_slots = []
            for material_slot in object.material_slots:
                material = material_slot.material
                material_slots[material_slot.slot_index] = assets.process(material)
            send += (assets.process(mesh), material_slots,)
        return send