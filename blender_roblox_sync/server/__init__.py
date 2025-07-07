import time, threading, http.server

def register(utils, package):
    process_formats = utils.import_module("process_formats")
    receive_messages = utils.import_module("receive_messages")
    send_messages = utils.import_module("send_messages")

    PORT = 50520
    TIMEOUT_DURATION = 1

    global hook
    global unhook
    global fire
    def hook(message_name, callback):
        process_formats.message_listeners[message_name].append(callback)
    def unhook(message_name, callback):
        process_formats.message_listeners[message_name].remove(callback)
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
    class ServerHandler(http.server.BaseHTTPRequestHandler):
        server_version = ""
        sys_version = ""

        def log_message(self, format, *args):
            if self.server.logging:
                http.server.BaseHTTPRequestHandler.log_message(self, format, *args)
        
        def do_POST(self):
            nonlocal last_received
            last_received = time.time()
            set_is_connected(True)

            content_length = int(self.headers["Content-Length"])
            if content_length > 0:
                receive_messages.receive_message(self.rfile.read(content_length))

            self.send_response(200)
            self.end_headers()

            send_buffer = send_messages.fetch_send_buffer()
            if send_buffer:
                self.wfile.write(send_buffer)
    class Server(http.server.HTTPServer):
        request_queue_size = 128
        logging = False

        def service_actions(self):
            if time.time() - last_received >= TIMEOUT_DURATION:
                set_is_connected(False)    
    class ServerThread(threading.Thread):
        def run(self):
            self.server = Server(("localhost", PORT), ServerHandler)
            self.server.serve_forever()
        
        def stop(self):
            if hasattr(self, "server"):
                self.server.shutdown()
                self.server.server_close()

    return {
        "threads": (ServerThread(name = "blender_roblox_sync Server"),)
    }