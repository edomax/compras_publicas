"""Simple HTTP server to serve the LM Studio interface and proxy API calls."""
import json
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import urllib.request
import urllib.error


class CORSHTTPRequestHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        if self.path.startswith('/api/'):
            self.proxy_to_lmstudio()
        else:
            super().do_GET()

    def do_POST(self):
        if self.path.startswith('/api/'):
            self.proxy_to_lmstudio()
        else:
            super().do_POST()

    def proxy_to_lmstudio(self):
        try:
            # Remove /api prefix and forward to LM Studio
            lm_path = self.path.replace('/api', '')
            lm_url = f'http://localhost:1234{lm_path}'
            
            if self.command == 'GET':
                with urllib.request.urlopen(lm_url) as response:
                    data = response.read()
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(data)
            
            elif self.command == 'POST':
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                
                req = urllib.request.Request(lm_url, data=post_data)
                req.add_header('Content-Type', 'application/json')
                
                with urllib.request.urlopen(req) as response:
                    data = response.read()
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(data)
                    
        except urllib.error.URLError as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            error_response = json.dumps({
                'error': f'Cannot connect to LM Studio: {str(e)}'
            }).encode()
            self.wfile.write(error_response)
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            error_response = json.dumps({
                'error': f'Server error: {str(e)}'
            }).encode()
            self.wfile.write(error_response)


if __name__ == '__main__':
    server_address = ('localhost', 8080)
    httpd = HTTPServer(server_address, CORSHTTPRequestHandler)
    print("Server running on http://localhost:8080")
    print("Open http://localhost:8080/lmstudio_interface.html in your browser")
    print("Make sure LM Studio is running on http://localhost:1234")
    httpd.serve_forever()