import time, threading, sys

def register(utils):
    process_formats = utils.import_module("process_formats")

    class SendMessagesThread(threading.Thread):
        def __pause(self):
            self.paused = True
            while self.paused:
                time.sleep(0.001)
                if self.stop_thread:
                    sys.exit()

        def __unpause(self):
            self.paused = False
        
        def send_message(self, message_name, *args):
            assert message_name in process_formats.send_message_ids
            message_id = process_formats.send_message_ids[message_name]
            self.args_queued.append((message_id,) + args)
            self.__unpause()
        
        def __write_buffer(self, data, data_size):
            self.buf_len += data_size
            if self.buf_len <= process_formats.SEND_LIMIT:
                self.buffer.append(data)
            else:
                overflow = self.buf_len - process_formats.SEND_LIMIT
                self.buffer.append(data[0:overflow])
                self.buffers_queued.append(b"".join(self.buffer))
                self.buffer = [data[overflow:]]
                
        def __parse(self, args, args_count, format_data, **masks):
            parsed_type = type(format_data)
            if parsed_type is list:
                for sub_format_data in format_data:
                    args_count = self.__parse(args, args_count, sub_format_data, **masks)
            else:
                args_count = process_formats.write_funcs[format_data["type"]](self, args, args_count, format_data, **masks)
        
        def stop(self):
            self.stop_thread = True

        def run(self):
            self.buffer = []
            self.buf_len = 0
            self.args_queued = []
            self.buffers_queued = []
            self.stop_thread = False

            while not self.stop_thread:
                if len(self.args_queued) == 0:
                    self.__pause()
                args = self.args_queued.pop(0)
                message_id = args[0]
                self.__write_buffer(process_formats.message_id_format.pack(message_id), process_formats.message_id_format.size)
                self.__parse(args, 1, process_formats.message_formats[message_id])

    sendThread = SendMessagesThread(name = "blender_roblox_sync Send Messages Thread")
    global send_message
    def send_message(*args):
        sendThread.send_message(*args)

    return {
        "threads": (sendThread,)
    }