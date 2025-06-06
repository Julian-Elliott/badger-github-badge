#!/usr/bin/env python3
"""
Local test server for GitHub Pages data
Serves the public/ directory on localhost for testing
"""

import http.server
import socketserver
import os
import webbrowser
import time
from threading import Thread

PORT = 8080
DIRECTORY = "public"

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)
    
    def end_headers(self):
        # Add CORS headers for local testing
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        super().end_headers()

def start_server():
    """Start the local test server"""
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"🌐 Local GitHub Pages server running at:")
        print(f"   http://localhost:{PORT}/")
        print(f"   Badge data: http://localhost:{PORT}/api/badge_compact.json")
        print(f"   Simple data: http://localhost:{PORT}/api/badge_simple.txt")
        print()
        print("📱 Test URLs for Badger 2040 W:")
        print(f"   DATA_URL = \"http://192.168.1.XXX:{PORT}/api/badge_compact.json\"")
        print(f"   FALLBACK_URL = \"http://192.168.1.XXX:{PORT}/api/badge_simple.txt\"")
        print()
        print("Press Ctrl+C to stop the server")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 Server stopped")

if __name__ == "__main__":
    if not os.path.exists(DIRECTORY):
        print(f"❌ Directory '{DIRECTORY}' not found")
        print("Run 'python scripts/generate_badge_data.py' first")
        exit(1)
    
    start_server()
