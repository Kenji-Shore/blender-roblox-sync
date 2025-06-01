import struct

format = struct.Struct("<q")
format_size = format.size
unpack_from = format.unpack_from
pack = format.pack

def read(self, format_data, **masks):
	return unpack_from(*self.read_buffer(format_size))

def write(self, args, args_count, format_data, **masks):
	hash_value = args[args_count]
	self.write_buffer(pack(hash_value), format_size)
	return args_count + 1