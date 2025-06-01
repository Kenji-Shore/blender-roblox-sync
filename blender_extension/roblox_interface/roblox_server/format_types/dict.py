import struct

format = struct.Struct("<L")
format_size = format.size
unpack_from = format.unpack_from
pack = format.pack

def read(self, format_data, **masks):
	dict_len, = unpack_from(*self.read_buffer(format_size))
	dict_value = {}
	for _ in range(dict_len):
		k, = self.parse(format_data["index"], **masks)
		v = self.parse(format_data["value"], **masks)
		dict_value[k] = v if len(v) > 1 else v[0]
	return (dict_value,)

def write(self, args, args_count, format_data, **masks):
	dict_items = args[args_count].items()
	dict_len = len(dict_items)
	self.write_buffer(pack(dict_len), format_size)
	if dict_len > 0:
		test_value = next(iter(dict_items))[1]
		values_type = type(test_value)
		if (values_type is list) or (values_type is tuple):
			for k, v in dict_items:
				self.parse((k,), 0, format_data["index"], **masks)
				self.parse(v, 0, format_data["value"], **masks)
		else:
			for k, v in dict_items:
				self.parse((k,), 0, format_data["index"], **masks)
				self.parse((v,), 0, format_data["value"], **masks)
	return args_count + 1