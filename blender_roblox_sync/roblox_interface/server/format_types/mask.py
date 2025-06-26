def read(self, format_data, **masks):
	mask = format_data["mask"]
	condition = (mask in masks) and masks[mask]
	if ("invert" in format_data) and format_data["invert"]:
		condition = not condition
	if condition:
		return self.parse(format_data["data"], **masks)
	else:
		return ()

def write(self, args, args_count, format_data, **masks):
	mask = format_data["mask"]
	condition = (mask in masks) and masks[mask]
	if ("invert" in format_data) and format_data["invert"]:
		condition = not condition
	if condition:
		args_count = self.parse(args, args_count, format_data["data"], **masks)
	return args_count