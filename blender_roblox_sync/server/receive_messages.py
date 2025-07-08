import threading, copy
from .pause_thread import PauseThread;

def register(utils, package):
    process_formats = utils.import_module("process_formats")

    class ReceiveMessagesThread(PauseThread):
        def receive_message(self, new_buffer):
            self.buffers_queued.append(new_buffer)
            self.unpause()

        def read_buffer(self, data_size):
            read_buffer = self.buffer
            read_offset = self.offset
            while self.buf_len < self.offset + data_size:
                if len(self.buffers_queued) == 0:
                    self.pause()
                self.buffer = self.buffers_queued.pop(0)
                self.offset -= self.buf_len
                self.buf_len = len(self.buffer)
                read_buffer += self.buffer

            self.offset += data_size
            return read_buffer, read_offset

        def parse(self, format_data, **masks):
            parsed_type = type(format_data)
            if parsed_type is list:
                args = ()
                for sub_format_data in format_data:
                    args += self.parse(sub_format_data, **masks)
                return args
            else:
                return process_formats.read_funcs[format_data["type"]](self, format_data, **masks)

        def run(self):
            self.buffers_queued = []
            self.buffer = bytearray()
            self.buf_len = 0
            self.offset = 0

            self.stop_thread = False
            while not self.stop_thread:
                message_name, = process_formats.read_funcs["str"](self, None)
                args = self.parse(process_formats.message_formats[message_name])
                for callback in process_formats.message_listeners[message_name]:
                    thread = threading.Thread(target=callback, args=copy.deepcopy(args))
                    thread.start()

    receiveThread = ReceiveMessagesThread(name = "blender_roblox_sync Receive Messages Thread")
    global receive_message
    def receive_message(*args):
        receiveThread.receive_message(*args)

    return {
        "threads": (receiveThread,)
    }