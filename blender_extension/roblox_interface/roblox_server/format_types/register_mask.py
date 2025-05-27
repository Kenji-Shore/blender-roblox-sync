def read(self, format_data, **masks):
	register_masks = format_data["register_mask"]
	format = format_data["count_format"]
	bitmask, = format.unpack_from(*self.__read_buffer(format.size))

	bools = []
	for _ in range(len(register_masks)):
		bools.insert(0, bool(bitmask & 0b1))
		bitmask >>= 1
		
	for mask, bool_value in zip(register_masks, bools):
		masks[mask] = bool_value

	args = tuple(bools)
	args += self.__parse(format_data["data"], **masks)
	return args

def write(self, args, args_count, format_data, **masks):
	register_masks = format_data["register_mask"]
	mask_count = len(register_masks)
	bools = args[args_count:args_count + mask_count]
	args_count += mask_count

	bitmask = 0
	for bool_value in bools:
		bitmask <<= 1
		bitmask += 1 if bool_value else 0
	
	for mask, bool_value in zip(register_masks, bools):
		masks[mask] = bool_value

	format = format_data["count_format"]
	self.__write_buffer(format.pack(bitmask), format.size)
	args_count = self.__parse(args, args_count, format_data["data"], **masks)
	return args_count