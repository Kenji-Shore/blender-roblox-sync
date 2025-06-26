import struct, math, mathutils

YAW = 32767 / math.pi
PITCH = 32767 / (0.5 * math.pi)
INV_YAW = 1 / YAW
INV_PITCH = 1 / PITCH

format = struct.Struct("<2h")
format_size = format.size
unpack_from = format.unpack_from
pack = format.pack

def read(self, format_data, **masks):
	normal_yaw, normal_pitch = unpack_from(*self.read_buffer(format_size))
	normal_yaw *= INV_YAW
	normal_pitch *= INV_PITCH
	horizontal = math.cos(normal_pitch)
	return (mathutils.Vector((math.sin(normal_yaw) * horizontal, math.cos(normal_yaw) * horizontal, math.sin(normal_pitch))),)

def write(self, args, args_count, format_data, **masks):
	vec_value = args[args_count]
	normal_yaw = math.atan2(vec_value.x, vec_value.y)
	normal_pitch = math.asin(vec_value.z)
	self.write_buffer(pack(
		round(normal_yaw * YAW),
		round(normal_pitch * PITCH)
	), format_size)
	return args_count + 1