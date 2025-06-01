import struct, mathutils

format = struct.Struct("<3d4h")
format_size = format.size
unpack_from = format.unpack_from
pack = format.pack

def read(self, format_data, **masks):
	y, z, x, qY, qZ, qX, qW = unpack_from(*self.read_buffer(format_size))
	pos = mathutils.Vector((x, y, z))
	quat = mathutils.Quaternion((qW / 32767, qX / 32767, qY / 32767, qZ / 32767))
	return (mathutils.Matrix.LocRotScale(pos, quat, None),)

def write(self, args, args_count, format_data, **masks):
	matrix_value = args[args_count]
	(pos_value, quat_value, _) = matrix_value.decompose()
	self.write_buffer(pack(
		pos_value.y, pos_value.z, pos_value.x,
		round(32767 * quat_value.y), 
		round(32767 * quat_value.z),
		round(32767 * quat_value.x),
		round(32767 * quat_value.w)
	), format_size)
	return args_count + 1