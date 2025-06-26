import time, threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

def register(utils, package):
    process_formats = utils.import_module("process_formats")
    receive_messages = utils.import_module("receive_messages")
    send_messages = utils.import_module("send_messages")

    TIMEOUT_DURATION = 1

    global hook
    def hook(message_name, callback):
        assert message_name in process_formats.receive_message_ids
        message_id = process_formats.receive_message_ids[message_name]
        process_formats.listen_message(message_id, callback)
    global unhook
    def unhook(message_name, callback):
        assert message_name in process_formats.receive_message_ids
        message_id = process_formats.receive_message_ids[message_name]
        process_formats.unlisten_message(message_id, callback)
    global fire
    def fire(message_name, *args):
        send_messages.send_message(message_name, *args)

    global is_connected
    global is_connected_area
    is_connected = False
    is_connected_area = None
    def set_is_connected(value):
        global is_connected
        if is_connected != value:
            is_connected = value
            if is_connected_area:
                is_connected_area.tag_redraw()

    last_received = time.time()
    class ServerHandler(BaseHTTPRequestHandler):
        server_version = ""
        sys_version = ""

        def log_message(self, format, *args):
            if self.server.logging:
                BaseHTTPRequestHandler.log_message(self, format, *args)
        
        def do_POST(self):
            nonlocal last_received
            last_received = time.time()
            set_is_connected(True)

            content_length = int(self.headers['Content-Length'])
            if content_length > 0:
                receive_messages.receive_message(self.rfile.read(content_length))

            self.send_response(200)
            self.end_headers()

            send_buffer = send_messages.fetch_send_buffer()
            if send_buffer:
                self.wfile.write(send_buffer)
    class Server(ThreadingHTTPServer):
        request_queue_size = 128
        logging = False

        def service_actions(self):
            if time.time() - last_received >= TIMEOUT_DURATION:
                set_is_connected(False)    
    class ServerThread(threading.Thread):
        def run(self):
            self.server = Server(('localhost', 50520), ServerHandler)
            self.server.serve_forever()
        
        def stop(self):
            if hasattr(self, "server"):
                self.server.shutdown()
                self.server.server_close()

    return {
        "threads": (ServerThread(name = "blender_roblox_sync Server"),)
    }