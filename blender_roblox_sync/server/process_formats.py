import struct, json, math

def register(utils, package):
    global SEND_LIMIT
    SEND_LIMIT = 20000000
    MESSAGE_FORMATS_NAME = "message_formats"
    DATA_TYPES = {
        "u8": "B",
        "i8": "b",
        "u16": "H",
        "i16": "h",
        "u32": "I",
        "i32": "i",
        "f32": "f",
        "f64": "d",
    }
    
    count_formats = (struct.Struct("<B"), struct.Struct("<H"), struct.Struct("<I"))
    def get_format_for_count(count):
        return count_formats[min(math.ceil(math.log(2 * max(math.log(count, 256), 1), 2)) - 1, 2)]
    def transform_format(format_data, required_type = None):
        parsed_type = type(format_data)
        assert (not required_type) or (parsed_type is required_type)

        if parsed_type is dict:
            if "value" in format_data: #is array or dict
                if "index" in format_data:
                    format_data["index"] = transform_format(format_data["index"], str)
                    format_data["type"] = "dict"
                else:
                    format_data["type"] = "array"
                format_data["value"] = transform_format(format_data["value"])
            elif "data" in format_data: #is masked data or repeated data
                format_data["data"] = transform_format(format_data["data"])
                if "mask" in format_data:
                    format_data["type"] = "mask"
                elif "repeat" in format_data:
                    format_data["type"] = "repeat"
                elif "register_mask" in format_data:
                    register_mask = format_data["register_mask"]
                    format_data["register_mask"] = tuple(register_mask) if type(register_mask) is list else (register_mask,)
                    format_data["count_format"] = get_format_for_count(len(format_data["register_mask"]))
                    format_data["type"] = "register_mask"
        else:
            if parsed_type is str:
                format_data = [format_data]

            stack_datatype = None
            stack_count = 0
            merge_str = ""
            merge_count = 0

            list_len = len(format_data)
            list_index = 0
            while True:
                raw = format_data[list_index] if list_index < list_len else None
                is_str = type(raw) is str
                datatype = DATA_TYPES[raw] if is_str and (raw in DATA_TYPES) else None
                if datatype == stack_datatype:
                    stack_count += 1
                else:
                    if stack_datatype:
                        merge_str += (str(stack_count) + stack_datatype) if stack_count > 1 else stack_datatype
                        merge_count += stack_count
                    stack_datatype = datatype
                    stack_count = 1
                    
                if datatype:
                    format_data.pop(list_index)
                    list_len -= 1
                else:
                    if merge_str != "":
                        format_data.insert(list_index, {
                            "count": merge_count, 
                            "format": struct.Struct("<" + merge_str),
                            "type": "format"
                        })
                        merge_str = ""
                        merge_count = 0
                        list_len += 1
                        list_index += 1

                    if raw:
                        format_data[list_index] = {"type": raw} if is_str else transform_format(raw)
                    list_index += 1

                if not raw:
                    break
            
            if list_len == 1:
                format_data = format_data[0]
        return format_data

    global message_formats
    global message_listeners
    message_formats = {}
    message_listeners = {}

    global read_funcs
    global write_funcs
    read_funcs = {}
    write_funcs = {}
    for module_name, module in utils.glob_from_parent(__file__, "format_types/*.py").items():
        module_dict = module.__dict__
        read_funcs[module_name] = module_dict["read"]
        write_funcs[module_name] = module_dict["write"]

    def load_message_format(message_format_path):
        message_name = message_format_path.stem
        with message_format_path.open() as message_format_file:
            message_listeners[message_name] = []
            message_formats[message_name] = transform_format(json.load(message_format_file))

    def post_registration():
        for addon_path in utils.addon_paths:
            message_formats_path = addon_path.joinpath(MESSAGE_FORMATS_NAME)
            if message_formats_path.is_dir():
                for message_format_path in message_formats_path.glob("**/*.json"):
                    load_message_format(message_format_path)
    return {
        "post_registration": post_registration
    }