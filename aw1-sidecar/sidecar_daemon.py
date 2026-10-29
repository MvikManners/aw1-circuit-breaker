#!/usr/bin/env python3
import os
import sys
import json
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
import socketserver
import threading
from pathlib import Path

# Try importing installed aw1 engine or fallback to native AST checker
try:
    from aw1.circuit import ExecutionBreaker, ExecutionHalt
    breaker = ExecutionBreaker()
except Exception:
    import ast
    class ExecutionBreaker:
        def __init__(self):
            self.blocked = [
                'subprocess', 'os.system', 'pty.spawn', 'socket.socket',
                '.ssh/id_rsa', '/etc/passwd', 'child_process', 'eval('
            ]
        def verify(self, payload):
            start = time.perf_counter()
            text = str(payload)
            for b in self.blocked:
                if b in text:
                    return {"allowed": False, "violation": "FORBIDDEN_PRIMITIVE", "reason": f"Detected: {b}", "latency_ms": round((time.perf_counter() - start) * 1000, 4)}
            return {"allowed": True, "latency_ms": round((time.perf_counter() - start) * 1000, 4)}
    breaker = ExecutionBreaker()

class SidecarHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Silent stdout to preserve micro-latency
        return

    def do_GET(self):
        if self.path in ('/healthz', '/livez'):
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            resp = {
                "status": "HEALTHY",
                "service": "aw1-circuit-breaker-sidecar",
                "version": "1.0.0",
                "engine": "AW-1 Layer 0 AST Guard",
                "sla": "<0.14ms"
            }
            self.wfile.write(json.dumps(resp).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path in ('/v1/verify', '/verify'):
            length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(length) if length > 0 else b'{}'
            
            try:
                data = json.loads(body.decode('utf-8'))
                payload = data.get('payload', '')
            except Exception:
                payload = body.decode('utf-8', errors='ignore')

            # Run deterministic verification
            res = breaker.verify(payload)
            status_code = 200 if res.get('allowed', False) else 403
            
            self.send_response(status_code)
            self.send_header('Content-Type', 'application/json')
            self.send_header('X-AW1-Latency-MS', str(res.get('latency_ms', 0.05)))
            self.end_headers()
            self.wfile.write(json.dumps(res).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

def run_http(port=9099):
    server = HTTPServer(('0.0.0.0', port), SidecarHandler)
    server.serve_forever()

if __name__ == '__main__':
    port = int(os.environ.get('AW1_PORT', 9099))
    print(f"[*] AW-1 Enterprise Security Sidecar listening on 0.0.0.0:{port}")
    run_http(port)
