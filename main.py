"""
Kaafeh Doosti Bot Service
All bots have been permanently migrated to the dedicated Iranian VPS.
This service is kept idle to maintain Render service health checks.
"""
import os
import http.server
import socketserver

PORT = int(os.environ.get("PORT", 8080))

class HealthHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"Kaafeh Doosti bots migrated permanently to dedicated VPS. TeamTalk connections disabled here.\n")

    def log_message(self, format, *args):
        pass

if __name__ == "__main__":
    print(f"Health server listening on port {PORT}. Zero TeamTalk connections active.")
    with socketserver.TCPServer(("", PORT), HealthHandler) as httpd:
        httpd.serve_forever()
