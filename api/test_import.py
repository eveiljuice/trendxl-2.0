from http.server import BaseHTTPRequestHandler
import json
import sys
import traceback


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # Try to import main
            from main import app

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            message = json.dumps({
                'status': 'ok',
                'message': 'main.py imported successfully!',
                'app_type': str(type(app)),
                'path': self.path
            })
            self.wfile.write(message.encode())
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            message = json.dumps({
                'status': 'error',
                'message': f'Failed to import main: {str(e)}',
                'traceback': traceback.format_exc(),
                'path': self.path
            })
            self.wfile.write(message.encode())
        return
