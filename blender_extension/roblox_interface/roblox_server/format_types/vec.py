import struct, math, mathutils

YAW = 32767 / math.pi
PITCH = 32767 / (0.5 * math.pi)
INV_YAW = 1 / YAW
INV_PITCH = 1 / PITCH

format = struct.Struct("<2hf")
format_size = format.size
unpack_from = format.unpack_from
pack = format.pack

def read(self, format_data, **masks):
	normal_yaw, normal_pitch, vel_mag = unpack_from(*self.__read_buffer(format_size))
	normal_yaw *= INV_YAW
	normal_pitch *= INV_PITCH
	horizontal = math.cos(normal_pitch)
	return (mathutils.Vector((math.sin(normal_yaw) * horizontal, math.cos(normal_yaw) * horizontal, math.sin(normal_pitch))) * vel_mag,)

def write(self, args, args_count, format_data, **masks):
	vec_value = args[args_count]
	vel_mag = vec_value.magnitude
	unit_vel = vec_value / vel_mag if vel_mag != 0 else mathutils.Vector(0, 1, 0)

	normal_yaw = math.atan2(unit_vel.x, unit_vel.y)
	normal_pitch = math.asin(unit_vel.z)
	self.__write_buffer(pack(
		round(normal_yaw * YAW),
		round(normal_pitch * PITCH),
		vel_mag
	), format_size)
	return args_count + 1