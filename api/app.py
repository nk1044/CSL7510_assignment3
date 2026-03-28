from http.server import BaseHTTPRequestHandler, HTTPServer
import socket

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        hostname = socket.gethostname()

        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()

        self.wfile.write(f"Response from {hostname}".encode())

if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", 5000), Handler)
    print("App running on port 5000")
    server.serve_forever()