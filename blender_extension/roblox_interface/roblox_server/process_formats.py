import struct, json, math
from pathlib import Path
from ... import utils

def __transform_format(format_data, required_type = None):
    parsed_type = type(format_data)
    assert (not required_type) or (parsed_type is required_type)

    if parsed_type is dict:
        if "value" in format_data: #is array or dict
            if "index" in format_data:
                format_data["index"] = __transform_format(format_data["index"], str)
                format_data["type"] = "dict"
            else:
                format_data["type"] = "array"
            format_data["value"] = __transform_format(format_data["value"])
        elif "data" in format_data: #is masked data or repeated data
            format_data["data"] = __transform_format(format_data["data"])
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
            datatype = datatypes[raw]["python"] if is_str and (raw in datatypes) else None
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
                    format_data[list_index] = {"type": raw} if is_str else __transform_format(raw)
                list_index += 1

            if not raw:
                break
        
        if list_len == 1:
            format_data = format_data[0]
    return format_data

count_formats = (struct.Struct("<B"), struct.Struct("<H"), struct.Struct("<I"))
def get_format_for_count(count):
    return count_formats[min(math.ceil(math.log(2 * max(math.log(count, 256), 1), 2)) - 1, 2)]

message_formats = {}
send_message_ids = {}
receive_message_ids = {}
message_listeners = {}

with Path(__file__).parent.joinpath("message_formats.json").open() as message_formats_file:
    file_json = json.load(message_formats_file)
    messages = file_json["messages"]
    datatypes = file_json["datatypes"]
    
    total_messages = len(messages)
    for i in range(total_messages):
        message = messages[i]
        message_name = message["name"]
        if message["sender"] == "python":
            send_message_ids[message_name] = i
        else:
            receive_message_ids[message_name] = i
            message_listeners[i] = []
        message_formats[i] = __transform_format(message["data"])

    message_id_format = get_format_for_count(total_messages)
    send_limit = file_json["send_limit"]

read_funcs = {}
write_funcs = {}
for module_name, module_dict in utils.glob_from_parent(__file__, "format_types/*.py").items():
    read_funcs[module_name] = module_dict["read"]
    write_funcs[module_name] = module_dict["write"]