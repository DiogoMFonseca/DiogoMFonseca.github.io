#!/usr/bin/env python3
"""
Simple HTTP server for testing the frontend locally.
Serves the current directory with CORS enabled.
"""

import http.server
import socketserver
import os

PORT = 8000

class CORSRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        return super().end_headers()

    def log_message(self, format, *args):
        """Custom log format"""
        print(f"[{self.log_date_time_string()}] {format % args}")


if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    with socketserver.TCPServer(("", PORT), CORSRequestHandler) as httpd:
        print("=" * 60)
        print(f"🚀 Server running at http://localhost:{PORT}")
        print("=" * 60)
        print(f"\n📂 Serving directory: {os.getcwd()}\n")
        print("Press Ctrl+C to stop the server\n")

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\n👋 Server stopped")
