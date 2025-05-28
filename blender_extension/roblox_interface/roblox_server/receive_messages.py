import time, threading, copy, sys

def register(utils):
    process_formats = utils.import_module("process_formats")

    class ReceiveMessagesThread(threading.Thread):
        def __pause(self):
            self.paused = True
            while self.paused:
                time.sleep(0.001)
                if self.stop_thread:
                    sys.exit()

        def __unpause(self):
            self.paused = False
        
        def receive_message(self, new_buffer):
            self.buffers_queued.append(new_buffer)
            self.__unpause()

        def __read_buffer(self, data_size):
            read_buffer = self.buffer
            read_offset = self.offset
            while self.buf_len < self.offset + data_size:
                if len(self.buffers_queued) == 0:
                    self.__pause()
                self.buffer = self.buffers_queued.pop(0)
                self.offset -= self.buf_len
                self.buf_len = len(self.buffer)
                read_buffer += self.buffer

            self.offset += data_size
            return read_buffer, read_offset

        def __parse(self, format_data, **masks):
            parsed_type = type(format_data)
            if parsed_type is list:
                args = ()
                for sub_format_data in format_data:
                    args += self.__parse(sub_format_data, **masks)
                return args
            else:
                return process_formats.read_funcs[format_data["type"]](self, format_data, **masks)
        
        def stop(self):
            self.stop_thread = True

        def run(self):
            self.buffers_queued = []
            self.buffer = bytearray()
            self.buf_len = 0
            self.offset = 0
            self.stop_thread = False

            while not self.stop_thread:
                message_id, = process_formats.message_id_format.unpack_from(*self.__read_buffer(process_formats.message_id_format.size))
                args = self.__parse(process_formats.message_formats[message_id])
                for callback in process_formats.message_listeners[message_id]:
                    thread = threading.Thread(target=callback, args=copy.deepcopy(args))
                    thread.start()

    receiveThread = ReceiveMessagesThread(name = "blender_roblox_sync Receive Messages Thread")
    global receive_message
    def receive_message(*args):
        receiveThread.receive_message(*args)

    return {
        "threads": (receiveThread,)
    }