from http.server import BaseHTTPRequestHandler, HTTPServer
import threading

class SimpleWebShellHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        print(f"[HTTP] GET from {self.client_address[0]}: {self.path}")
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        print(f"[HTTP] POST from {self.client_address[0]}: {post_data.decode(errors='ignore')}")
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

class WebListener:
    def __init__(self, ip='0.0.0.0', port=8080):
        self.ip = ip
        self.port = port
        self.server = HTTPServer((self.ip, self.port), SimpleWebShellHandler)
        self.thread = None

    def start(self):
        print(f"[*] Starting HTTP listener on {self.ip}:{self.port}")
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def stop(self):
        self.server.shutdown()
        print("[*] HTTP listener stopped.") 