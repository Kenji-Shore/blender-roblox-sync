def read(self, format_data, **masks):
	mask = format_data["mask"]
	if (mask in masks) and masks[mask]:
		return self.parse(format_data["data"], **masks)
	else:
		return ()

def write(self, args, args_count, format_data, **masks):
	mask = format_data["mask"]
	if (mask in masks) and masks[mask]:
		args_count = self.parse(args, args_count, format_data["data"], **masks)
	return args_count