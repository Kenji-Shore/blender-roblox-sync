import struct

format = struct.Struct("<H")
format_size = format.size
unpack_from = format.unpack_from
pack = format.pack

def read(self, format_data, **masks):
	str_len, = unpack_from(*self.read_buffer(format_size))
	str_value, = struct.unpack_from(f"<{str_len}s", *self.read_buffer(str_len))
	return (str_value.decode("utf-8"),)

def write(self, args, args_count, format_data, **masks):
	str_value = args[args_count]
	str_len = len(str_value)
	self.write_buffer(pack(str_len), format_size)
	self.write_buffer(struct.pack(f"<{str_len}s", str_value.encode("utf-8")), str_len)
	return args_count + 1