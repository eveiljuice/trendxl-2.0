#!/usr/bin/env python3
"""
Simple debug server to provide backend status information
Runs on port 9999 to not conflict with main backend
"""
import subprocess
import socket
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import datetime
import threading
import time

class DebugHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/debug-status':
            try:
                status = self.get_backend_status()
                self.send_response(200)
                self.send_header('Content-Type', 'text/plain')
                self.end_headers()
                self.wfile.write(status.encode('utf-8'))
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'text/plain')
                self.end_headers()
                self.wfile.write(f"Error getting backend status: {e}".encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()
    
    def get_backend_status(self):
        """Collect comprehensive backend status"""
        status_lines = []
        status_lines.append("=== BACKEND DEBUG STATUS ===")
        status_lines.append(f"Timestamp: {datetime.datetime.now().isoformat()}")
        status_lines.append("")
        
        # Check port 8000
        status_lines.append("=== PORT 8000 STATUS ===")
        try:
            result = subprocess.run(['netstat', '-tuln'], capture_output=True, text=True, timeout=5)
            if ':8000' in result.stdout:
                lines = [line for line in result.stdout.split('\n') if ':8000' in line]
                status_lines.extend(lines)
            else:
                status_lines.append("❌ Nothing listening on port 8000")
        except Exception as e:
            status_lines.append(f"❌ Failed to check port: {e}")
        
        status_lines.append("")
        
        # Check Python processes
        status_lines.append("=== PYTHON PROCESSES ===")
        try:
            result = subprocess.run(['ps', 'aux'], capture_output=True, text=True, timeout=5)
            python_lines = []
            for line in result.stdout.split('\n'):
                if any(term in line.lower() for term in ['python', 'uvicorn', 'fastapi']) and 'grep' not in line:
                    python_lines.append(line)
            
            if python_lines:
                status_lines.extend(python_lines)
            else:
                status_lines.append("❌ No Python processes found")
        except Exception as e:
            status_lines.append(f"❌ Failed to check processes: {e}")
        
        status_lines.append("")
        
        # Check supervisor status
        status_lines.append("=== SUPERVISOR STATUS ===")
        try:
            result = subprocess.run([
                'supervisorctl', '-c', '/etc/supervisor/conf.d/supervisord.conf', 'status'
            ], capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                status_lines.extend(result.stdout.strip().split('\n'))
            else:
                status_lines.append(f"❌ Supervisor error: {result.stderr.strip()}")
        except Exception as e:
            status_lines.append(f"❌ Failed to get supervisor status: {e}")
        
        status_lines.append("")
        
        # Backend logs
        status_lines.append("=== BACKEND LOGS (last 10 lines) ===")
        try:
            result = subprocess.run(['tail', '-10', '/var/log/supervisor/backend.log'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0 and result.stdout.strip():
                status_lines.extend(result.stdout.strip().split('\n'))
            else:
                status_lines.append("❌ No backend stdout log available")
        except Exception as e:
            status_lines.append(f"❌ Failed to read backend log: {e}")
        
        status_lines.append("")
        
        # Backend error logs  
        status_lines.append("=== BACKEND ERRORS (last 10 lines) ===")
        try:
            result = subprocess.run(['tail', '-10', '/var/log/supervisor/backend_error.log'],
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0 and result.stdout.strip():
                status_lines.extend(result.stdout.strip().split('\n'))
            else:
                status_lines.append("❌ No backend error log available")
        except Exception as e:
            status_lines.append(f"❌ Failed to read backend error log: {e}")
            
        return '\n'.join(status_lines)
    
    def log_message(self, format, *args):
        # Suppress default logging
        pass

def start_debug_server():
    """Start debug server on port 9999"""
    try:
        server = HTTPServer(('127.0.0.1', 9999), DebugHandler)
        print("Debug server starting on port 9999...")
        server.serve_forever()
    except Exception as e:
        print(f"Debug server failed to start: {e}")

if __name__ == '__main__':
    start_debug_server()
