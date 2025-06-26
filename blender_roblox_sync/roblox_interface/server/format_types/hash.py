format_size = 32
def read(self, format_data, **masks):
	read_buffer, read_offset = self.read_buffer(format_size)
	return (read_buffer[read_offset:read_offset + format_size],)

def write(self, args, args_count, format_data, **masks):
	hash_value = args[args_count]
	self.write_buffer(hash_value, format_size)
	return args_count + 1