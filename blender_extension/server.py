import time, threading, struct, json, math, copy, sys
from pathlib import Path
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import mathutils

def transform_format(format_data, required_type = None):
    parsed_type = type(format_data)
    assert (not required_type) or (parsed_type is required_type)

    if parsed_type is str:
        if format_data in datatypes:
            format_data = struct.Struct("<" + datatypes[format_data]["python"])
        else:
            format_data = {"type": format_data}
    elif parsed_type is list:
        stack_datatype = None
        stack_count = 0
        merge_str = ""
        merge_count = 0

        list_len = len(format_data)
        list_index = 0
        while True:
            raw = format_data[list_index] if list_index < list_len else None
            datatype = datatypes[raw]["python"] if (type(raw) is str) and (raw in datatypes) else None
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
                    format_data[list_index] = transform_format(raw)
                list_index += 1

            if not raw:
                break
        
        if list_len == 1:
            format_data = format_data[0]
    elif type(format_data) is dict:
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
                format_data["count_format"] = struct.Struct(get_format_for_count(len(format_data["register_mask"])))
                format_data["type"] = "register_mask"

    return format_data

def get_format_for_count(count):
    return "<" + ("B", "H", "I")[min(math.ceil(math.log(2 * max(math.log(count, 256), 1), 2)) - 1, 2)]

message_formats = {}
message_id_format: str
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
        message_formats[i] = transform_format(message["data"])

    message_id_format = get_format_for_count(total_messages)
    send_limit = file_json["send_limit"]

YAW = 32767 / math.pi
PITCH = 32767 / (0.5 * math.pi)
send_queue = []

len_format = struct.Struct("<L").pack
pos_format = struct.Struct("<3f").pack
pos2d_format = struct.Struct("<2f").pack
cf_format = struct.Struct("<3d4h").pack
vec_format = struct.Struct("<2hf").pack
unitvec_format = struct.Struct("<2h").pack
hash_format = struct.Struct("<q").pack
col_format = struct.Struct("<3B").pack
buf_format = struct.Struct("<I").pack

def fire(message_name, *args):
    assert message_name in send_message_ids

    buffer = []
    def parse_args(format_data, *args, **masks):
        args_count = 0
        def parse(format_data, **masks):
            nonlocal args_count
            nonlocal buffer

            parsed_type = type(format_data)
            if parsed_type is list:
                for sub_format_data in format_data:
                    parse(sub_format_data, **masks)
            elif parsed_type is struct.Struct:
                buffer.append(format_data.pack(args[args_count]))
                args_count += 1
            else:
                match format_data["type"]:
                    case "register_mask":
                        register_masks = format_data["register_mask"]
                        mask_count = len(register_masks)
                        bools = args[args_count:args_count + mask_count]
                        bitmask = 0
                        for bool_value in bools:
                            bitmask <<= 1
                            bitmask += 1 if bool_value else 0
                        
                        for mask, bool_value in zip(register_masks, bools):
                            masks[mask] = bool_value
                        buffer.append(format_data["count_format"].pack(bitmask))
                        args_count += mask_count
                        parse(format_data["data"], **masks)
                    case "dict": #is dict
                        dict_items = args[args_count].items()
                        dict_len = len(dict_items)
                        buffer.append(len_format(dict_len))
                        if dict_len > 0:
                            test_value = next(iter(dict_items))[1]
                            values_type = type(test_value)
                            if (values_type is list) or (values_type is tuple):
                                for k, v in dict_items:
                                    parse_args(format_data["index"], k, **masks)
                                    parse_args(format_data["value"], *v, **masks)
                            else:
                                for k, v in dict_items:
                                    parse_args(format_data["index"], k, **masks)
                                    parse_args(format_data["value"], v, **masks)
                        args_count += 1
                    case "array": #is array
                        list_value = args[args_count]
                        list_len = len(list_value)
                        buffer.append(len_format(list_len))
                        if list_len > 0:
                            values_type = type(list_value[0])
                            if (values_type is list) or (values_type is tuple):
                                for v in list_value:
                                    parse_args(format_data["value"], *v, **masks)
                            else:
                                for v in list_value:
                                    parse_args(format_data["value"], v, **masks)
                        args_count += 1
                    case "format": #is a data chunk
                        data_count = format_data["count"]
                        buffer.append(format_data["format"].pack(*args[args_count:args_count + data_count]))
                        args_count += data_count
                    case "mask": #is masked data
                        mask = format_data["mask"]
                        if (mask in masks) and masks[mask]:
                            parse(format_data["data"], **masks)
                    case "repeat":#is repeated data
                        for _ in range(format_data["repeat"]):
                            parse(format_data["data"], **masks)
                    case "str": #is a string
                        str_value = args[args_count]
                        str_len = len(str_value)
                        buffer.append(struct.pack(f"<H{str_len}s", str_len, str_value.encode("utf-8")))
                        args_count += 1
                    case "pos":
                        pos_value = args[args_count]
                        buffer.append(pos_format(pos_value.y, pos_value.z, pos_value.x))
                        args_count += 1
                    case "pos2d":
                        pos_value = args[args_count]
                        buffer.append(pos2d_format(pos_value.x, pos_value.y))
                        args_count += 1
                    case "cf":
                        matrix_value = args[args_count]
                        (pos_value, quat_value, _) = matrix_value.decompose()
                        buffer.append(cf_format( 
                            pos_value.y, pos_value.z, pos_value.x,
                            round(32767 * quat_value.y), 
                            round(32767 * quat_value.z),
                            round(32767 * quat_value.x),
                            round(32767 * quat_value.w)
                        ))
                        args_count += 1
                    case "vec":
                        vec_value = args[args_count]
                        vel_mag = vec_value.magnitude
                        unit_vel = vec_value / vel_mag if vel_mag != 0 else mathutils.Vector(0, 1, 0)

                        normal_yaw = math.atan2(unit_vel.x, unit_vel.y)
                        normal_pitch = math.asin(unit_vel.z)
                        buffer.append(vec_format(
                            round(normal_yaw * YAW),
                            round(normal_pitch * PITCH),
                            vel_mag
                        ))
                        args_count += 1
                    case "unitvec":
                        vec_value = args[args_count]
                        normal_yaw = math.atan2(vec_value.x, vec_value.y)
                        normal_pitch = math.asin(vec_value.z)
                        buffer.append(unitvec_format(
                            round(normal_yaw * YAW),
                            round(normal_pitch * PITCH)
                        ))
                        args_count += 1
                    case "hash":
                        hash_value = args[args_count]
                        buffer.append(hash_format(hash_value))
                        args_count += 1
                    case "col":
                        col_value = args[args_count]
                        buffer.append(col_format(
                            round(255 * col_value.r), 
                            round(255 * col_value.g), 
                            round(255 * col_value.b)
                        ))
                        args_count += 1
                    case "buf":
                        buf_value = args[args_count]
                        buffer.append(buf_format(len(buf_value)))
                        buffer.append(buf_value)
                        args_count += 1
        parse(format_data, **masks)

    message_id = send_message_ids[message_name]
    buffer.append(struct.pack(message_id_format, message_id))
    parse_args(message_formats[message_id], *args)
    send_queue.append(b"".join(buffer))

INV_YAW = math.pi / 32767
INV_PITCH = (0.5 * math.pi) / 32767
class ReceiveSignalThread(threading.Thread):
    def __pause(self):
        self.paused = True
        while self.paused:
            time.sleep(0.001)
            if self.stop_thread:
                sys.exit()

    def __unpause(self):
        self.paused = False
    
    def receive_signal(self, new_buffer):
        self.buffers_queued.append(new_buffer)
        self.__unpause()

    def __poll_buffer(self, byte_size):
        read_buffer = self.buffer
        read_offset = self.offset
        while self.buf_len < self.offset + byte_size:
            if len(self.buffers_queued) == 0:
                self.__pause()
            self.buffer = self.buffers_queued.pop(0)
            self.offset -= self.buf_len
            self.buf_len = len(self.buffer)
            read_buffer += self.buffer

        self.offset += byte_size
        return read_buffer, read_offset
    
    def __read_buffer(self, format_str):
        return struct.unpack_from(format_str, *self.__poll_buffer(struct.calcsize(format_str)))

    def __parse_args(self, format_data, *, masks = {}):
        masks = masks.copy()
        args = ()
        def parse(format_data):
            nonlocal args

            parsed_type = type(format_data)
            if parsed_type is list:
                for sub_format_data in format_data:
                    parse(sub_format_data)
            elif parsed_type is str:
                args += self.__read_buffer("<" + format_data)
            elif parsed_type is dict:
                if "value" in format_data: #is array or dict
                    if "index" in format_data: #is dict
                        len_dict, = self.__read_buffer("<L")
                        dict_value = {}
                        for _ in range(len_dict):
                            k, = self.__parse_args(format_data["index"], masks=masks)
                            v = self.__parse_args(format_data["value"], masks=masks)
                            dict_value[k] = v if len(v) > 1 else v[0]
                        args += (dict_value,)
                    else: #is array
                        len_list, = self.__read_buffer("<L")
                        list_value = []
                        for _ in range(len_list):
                            v = self.__parse_args(format_data["value"], masks=masks)
                            list_value.append(v if len(v) > 1 else v[0])
                        args += (list_value,)
                elif "format" in format_data: #is a data chunk
                    args += self.__read_buffer("<" + format_data["format"]) 
                elif "register_mask" in format_data:
                    register_masks = format_data["register_mask"]
                    register_masks = register_masks if type(register_masks) is list else (register_masks,)
                    mask_count = len(register_masks)
                    bools = []
                    bitmask, = self.__read_buffer(get_format_for_count(mask_count))
                    for _ in range(mask_count):
                        bools.insert(0, bool(bitmask & 0b1))
                        bitmask >>= 1
                        
                    for mask, bool_value in zip(register_masks, bools):
                        masks[mask] = bool_value
                    args += tuple(bools)
                elif "mask" in format_data: #is masked data
                    mask = format_data["mask"]
                    if (mask in masks) and masks[mask]:
                        parse(format_data["data"])
                elif "repeat" in format_data: #is repeated data
                    for _ in range(format_data["repeat"]):
                        parse(format_data["data"])
                else:
                    match format_data["type"]:
                        case "str": #is a string
                            str_len, = self.__read_buffer("<H")
                            str_value, = self.__read_buffer(f"<{str_len}s")
                            args += (str_value.decode("utf-8"),)
                        case "pos":
                            y, z, x = self.__read_buffer("<3f")
                            args += (mathutils.Vector((x, y, z)),)
                        case "pos2d":
                            args += (mathutils.Vector(self.__read_buffer("<2f")),)
                        case "cf":
                            y, z, x = self.__read_buffer("<3d")
                            qY, qZ, qX, qW = self.__read_buffer("<4h")
                            pos = mathutils.Vector((x, y, z))
                            quat = mathutils.Quaternion((qW / 32767, qX / 32767, qY / 32767, qZ / 32767))
                            args += (mathutils.Matrix.LocRotScale(pos, quat, None),)
                        case "vec":
                            normal_yaw = self.__read_buffer("<h")[0] * INV_YAW
                            normal_pitch = self.__read_buffer("<h")[0] * INV_PITCH
                            vel_mag, = self.__read_buffer("<f")
                            horizontal = math.cos(normal_pitch)
                            args += (mathutils.Vector((math.sin(normal_yaw) * horizontal, math.cos(normal_yaw) * horizontal, math.sin(normal_pitch))) * vel_mag,)
                        case "unitvec":
                            normal_yaw = self.__read_buffer("<h")[0] * INV_YAW
                            normal_pitch = self.__read_buffer("<h")[0] * INV_PITCH
                            horizontal = math.cos(normal_pitch)
                            args += (mathutils.Vector((math.sin(normal_yaw) * horizontal, math.cos(normal_yaw) * horizontal, math.sin(normal_pitch))),)
                        case "hash":
                            args += self.__read_buffer("<q")
                        case "col":
                            r, g, b = self.__read_buffer("<3B")
                            args += (mathutils.Color((r / 255, g / 255, b / 255)),)
                        case "buf":
                            buf_len, = self.__read_buffer("<I")
                            read_buffer, read_offset = self.__poll_buffer(buf_len)
                            args += (read_buffer[read_offset:read_offset + buf_len],)
        parse(format_data)
        return args
    
    def stop(self):
        self.stop_thread = True

    def run(self):
        self.buffers_queued = []
        self.buffer = bytearray()
        self.buf_len = 0
        self.offset = 0
        self.stop_thread = False

        while not self.stop_thread:
            message_id, = self.__read_buffer(message_id_format)
            args = self.__parse_args(message_formats[message_id])
            for callback in message_listeners[message_id]:
                thread = threading.Thread(target=callback, args=copy.deepcopy(args))
                thread.start()

def hook(message_name, callback):
    assert message_name in receive_message_ids
    message_id = receive_message_ids[message_name]
    message_listeners[message_id].append(callback)

def unhook(message_name, callback):
    assert message_name in receive_message_ids
    message_id = receive_message_ids[message_name]
    message_listeners[message_id].remove(callback)

timeout_duration = 1

is_connected = False
is_connected_callbacks = []
def set_is_connected(value):
    global is_connected
    if is_connected != value:
        is_connected = value
        for callback in is_connected_callbacks:
            callback(value)

signalReceiver = None
last_received = time.time()
class ServerHandler(BaseHTTPRequestHandler):
    server_version = ""
    sys_version = ""

    def log_message(self, format, *args):
        if self.server.logging:
            BaseHTTPRequestHandler.log_message(self, format, *args)
    
    def do_POST(self):
        global last_received
        last_received = time.time()
        set_is_connected(True)

        content_length = int(self.headers['Content-Length'])
        if content_length > 0:
            signalReceiver.receive_signal(self.rfile.read(content_length))

        self.send_response(200)
        self.end_headers()

        queue_len = len(send_queue)
        if queue_len > 0:
            send_buffer = bytearray()
            send_size = 0
            while (queue_len > 0) and (send_size < send_limit):
                buffer = send_queue.pop(0)
                buffer_size = len(buffer)
                send_size += buffer_size
                queue_len -= 1
                if send_size <= send_limit:
                    send_buffer += buffer
                else:
                    overflow = send_size - send_limit
                    send_buffer += buffer[0:overflow]
                    send_queue.insert(0, buffer[overflow:])

            self.wfile.write(send_buffer)

class Server(ThreadingHTTPServer):
    request_queue_size = 128
    logging = False

    def service_actions(self):
        if time.time() - last_received >= timeout_duration:
            set_is_connected(False)
            

class ServerThread(threading.Thread):
    def run(self):
        self.server = Server(('localhost', 50520), ServerHandler)
        self.server.serve_forever()
    
    def stop(self):
        if hasattr(self, "server"):
            self.server.shutdown()
            self.server.server_close()

server = None
def register():
    is_connected_callbacks.clear()
    global server
    global signalReceiver
    server = ServerThread(name = "blender_roblox_sync Server")
    server.start()
    signalReceiver = ReceiveSignalThread(name = "blender_roblox_sync Signal Receiver")
    signalReceiver.start()

def unregister():
    if server is not None:
        server.stop()
    if signalReceiver is not None:
        signalReceiver.stop()