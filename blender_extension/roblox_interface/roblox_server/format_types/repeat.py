def read(self, format_data, **masks):
	args = ()
	for _ in range(format_data["repeat"]):
		args += self.__parse(format_data["data"], **masks)
	return args

def write(self, args, args_count, format_data, **masks):
	for _ in range(format_data["repeat"]):
		args_count = self.__parse(args, args_count, format_data["data"], **masks)
	return args_count