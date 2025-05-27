def read(self, format_data, **masks):
	format = format_data["format"]
	return format.unpack_from(*self.__read_buffer(format.size))

def write(self, args, args_count, format_data, **masks):
	data_count = format_data["count"]
	format = format_data["format"]
	self.__write_buffer(format.pack(*args[args_count:args_count + data_count]), format.size)
	return args_count + data_count