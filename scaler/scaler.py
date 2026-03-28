from http.server import BaseHTTPRequestHandler, HTTPServer
import subprocess
from gcp_utils import create_vm

class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == "/scale":
            print("Scaling triggered")

            ip = create_vm()
            print(f"New VM IP: {ip}")

            self.send_response(200)
            self.end_headers()

server = HTTPServer(("0.0.0.0", 6000), Handler)
print("Scaler running on port 6000")
server.serve_forever()