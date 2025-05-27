import time, threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from . import process_formats, receive_messages, send_messages

def hook(message_name, callback):
    assert message_name in process_formats.receive_message_ids
    message_id = process_formats.receive_message_ids[message_name]
    process_formats.message_listeners[message_id].append(callback)

def unhook(message_name, callback):
    assert message_name in process_formats.receive_message_ids
    message_id = process_formats.receive_message_ids[message_name]
    process_formats.message_listeners[message_id].remove(callback)

timeout_duration = 1

is_connected = False
is_connected_callbacks = []
def set_is_connected(value):
    global is_connected
    if is_connected != value:
        is_connected = value
        for callback in is_connected_callbacks:
            callback(value)

server = None
receiveThread = None
sendThread = None
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
            receiveThread.receive_message(self.rfile.read(content_length))

        self.send_response(200)
        self.end_headers()

        queue_len = len(sendThread.buffers_queued)
        if queue_len > 0:
            self.wfile.write(sendThread.buffers_queued.pop(0))

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

def register(package):
    is_connected_callbacks.clear()
    global server
    global receiveThread
    global sendThread
    server = ServerThread(name = "blender_roblox_sync Server")
    receiveThread = receive_messages.ReceiveMessagesThread(name = "blender_roblox_sync Receive Messages Thread")
    sendThread = send_messages.SendMessagesThread(name = "blender_roblox_sync Send Messages Thread")
    server.start()
    receiveThread.start()
    sendThread.start()

def unregister(package):
    if server is not None:
        server.stop()
    if receiveThread is not None:
        receiveThread.stop()
    if sendThread is not None:
        sendThread.stop()