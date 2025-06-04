import bpy

def register(utils):

	global process_object
	def process_object(object):
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