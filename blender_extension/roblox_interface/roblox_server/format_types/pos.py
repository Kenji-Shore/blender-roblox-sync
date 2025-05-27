import struct, mathutils

format = struct.Struct("<3f")
format_size = format.size
unpack_from = format.unpack_from
pack = format.pack

def read(self, format_data, **masks):
	y, z, x = unpack_from(*self.__read_buffer(format_size))
	return (mathutils.Vector((x, y, z)),)

def write(self, args, args_count, format_data, **masks):
	pos_value = args[args_count]
	self.__write_buffer(pack(pos_value.y, pos_value.z, pos_value.x), format_size)
	return args_count + 1