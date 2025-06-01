import struct, mathutils

format = struct.Struct("<3B")
format_size = format.size
unpack_from = format.unpack_from
pack = format.pack

def read(self, format_data, **masks):
	r, g, b = unpack_from(*self.read_buffer(format_size))
	return (mathutils.Color((r / 255, g / 255, b / 255)),)

def write(self, args, args_count, format_data, **masks):
	col_value = args[args_count]
	self.write_buffer(pack(
		round(255 * col_value.r), 
		round(255 * col_value.g), 
		round(255 * col_value.b)
	), format_size)
	return args_count + 1