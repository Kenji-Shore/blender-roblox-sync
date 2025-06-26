import struct

format = struct.Struct("<L")
format_size = format.size
unpack_from = format.unpack_from
pack = format.pack

def read(self, format_data, **masks):
	list_len, = unpack_from(*self.read_buffer(format_size))
	list_value = []
	for _ in range(list_len):
		v = self.parse(format_data["value"], **masks)
		list_value.append(v if len(v) > 1 else v[0])
	return (list_value,)

def write(self, args, args_count, format_data, **masks):
	list_value = args[args_count]
	list_len = len(list_value)
	self.write_buffer(pack(list_len), format_size)
	if list_len > 0:
		values_type = type(list_value[0])
		if (values_type is list) or (values_type is tuple):
			for v in list_value:
				self.parse(v, 0, format_data["value"], **masks)
		else:
			for v in list_value:
				self.parse((v,), 0, format_data["value"], **masks)
	return args_count + 1