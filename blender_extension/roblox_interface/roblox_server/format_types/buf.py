import struct

format = struct.Struct("<I")
format_size = format.size
unpack_from = format.unpack_from
pack = format.pack

def read(self, format_data, **masks):
	buf_len, = unpack_from(*self.read_buffer(format_size))
	read_buffer, read_offset = self.read_buffer(buf_len)
	return (read_buffer[read_offset:read_offset + buf_len],)

def write(self, args, args_count, format_data, **masks):
	buf_value = args[args_count]
	data_size = len(buf_value)
	self.write_buffer(pack(data_size), format_size)
	self.write_buffer(buf_value, data_size)
	return args_count + 1