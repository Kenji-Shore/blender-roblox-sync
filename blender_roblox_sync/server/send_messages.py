from .pause_thread import PauseThread;

def register(utils, package):
    process_formats = utils.import_module("process_formats")

    class SendMessagesThread(PauseThread):
        def send_message(self, message_name, *args):
            self.args_queued.append((message_name,) + args)
            self.unpause()
        
        def write_buffer(self, data, data_size):
            self.buf_len += data_size
            if self.buf_len <= process_formats.SEND_LIMIT:
                self.buffer.append(data)
            else:
                overflow = self.buf_len - process_formats.SEND_LIMIT
                self.buffer.append(data[0:overflow])
                self.buffers_queued.append(b"".join(self.buffer))
                self.buffer = [data[overflow:]]
                self.buf_len = overflow
                
        def parse(self, args, args_count, format_data, **masks):
            parsed_type = type(format_data)
            if parsed_type is list:
                for sub_format_data in format_data:
                    args_count = self.parse(args, args_count, sub_format_data, **masks)
            else:
                args_count = process_formats.write_funcs[format_data["type"]](self, args, args_count, format_data, **masks)
            return args_count

        def run(self):
            self.buffer = []
            self.buf_len = 0
            self.args_queued = []
            self.buffers_queued = []

            self.stop_thread = False
            while not self.stop_thread:
                if len(self.args_queued) == 0:
                    self.pause()
                args = self.args_queued.pop(0)
                message_name = args[0]
                args_count = process_formats.write_funcs["str"](self, args, 0, None)
                self.parse(args, args_count, process_formats.message_formats[message_name])
                self.buffers_queued.append(b"".join(self.buffer))
                self.buffer = []
                self.buf_len = 0

    sendThread = SendMessagesThread(name = "blender_roblox_sync Send Messages Thread")
    global send_message
    def send_message(message_name, *args):
        sendThread.send_message(message_name, *args)

    global fetch_send_buffer
    def fetch_send_buffer():
        queue_len = len(sendThread.buffers_queued)
        if queue_len > 0:
            return sendThread.buffers_queued.pop(0)

    return {
        "threads": (sendThread,)
    }