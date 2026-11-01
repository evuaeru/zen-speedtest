#!/usr/bin/env python3
"""
Zen SpeedTest Local Server
Menyediakan endpoint benchmark throughput & latency berkecepatan tinggi tanpa hambatan CORS.
Dibuat khusus untuk kenyamanan Master Zay oleh Pelayan Ancellia.
"""

import sys
import os
import io
import socket
import time
import json
import urllib.parse
import webbrowser
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler

# Pastikan output konsol Windows aman dari UnicodeEncodeError (cp1252 / cp437)
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace', line_buffering=True)
    except Exception:
        pass
if hasattr(sys.stderr, 'reconfigure'):
    try:
        sys.stderr.reconfigure(encoding='utf-8', errors='replace', line_buffering=True)
    except Exception:
        pass

DEFAULT_PORT = 8080
CHUNK_SIZE = 64 * 1024  # 64 KB buffer per write/read
DUMMY_BUFFER = b'\x00' * CHUNK_SIZE

class SpeedTestHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, format, *args):
        # Meredam logging berlebih saat benchmark throughput tinggi
        if self.path.startswith('/api/download') or self.path.startswith('/api/upload') or self.path.startswith('/api/ping'):
            return
        super().log_message(format, *args)

    def send_cors_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, HEAD')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Range, Authorization, X-Requested-With, Cache-Control')
        self.send_header('Access-Control-Expose-Headers', 'Content-Length, Server-Timing, X-Response-Time')
        self.send_header('Access-Control-Allow-Private-Network', 'true')
        self.send_header('Timing-Allow-Origin', '*')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_cors_headers()
        self.send_header('Content-Length', '0')
        self.end_headers()

    def do_HEAD(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == '/api/ping':
            self.send_response(204)
            self.send_cors_headers()
            self.send_header('Content-Length', '0')
            self.end_headers()
        else:
            self.do_GET()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        # 1. Ping Endpoint
        if path == '/api/ping':
            self.send_response(204)
            self.send_cors_headers()
            self.send_header('Content-Length', '0')
            self.end_headers()
            return

        # 2. Server Info Endpoint
        if path == '/api/info':
            client_ip = self.client_address[0]
            data = {
                "status": "online",
                "mode": "local_server",
                "hostname": socket.gethostname(),
                "client_ip": client_ip,
                "server_time": time.time(),
                "node": "Localhost LAN Bridge"
            }
            body = json.dumps(data).encode('utf-8')
            self.send_response(200)
            self.send_cors_headers()
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        # 3. Download Throughput Benchmark Endpoint
        if path == '/api/download':
            query = urllib.parse.parse_qs(parsed.query)
            try:
                requested_bytes = int(query.get('bytes', [10 * 1024 * 1024])[0])
            except (ValueError, TypeError):
                requested_bytes = 10 * 1024 * 1024

            requested_bytes = max(1024, min(requested_bytes, 500 * 1024 * 1024))

            self.send_response(200)
            self.send_cors_headers()
            self.send_header('Content-Type', 'application/octet-stream')
            self.send_header('Content-Length', str(requested_bytes))
            self.end_headers()

            bytes_remaining = requested_bytes
            try:
                while bytes_remaining > 0:
                    chunk = DUMMY_BUFFER if bytes_remaining >= CHUNK_SIZE else DUMMY_BUFFER[:bytes_remaining]
                    self.wfile.write(chunk)
                    bytes_remaining -= len(chunk)
            except (ConnectionResetError, BrokenPipeError):
                pass
            return

        # 4. Melayani index.html statis
        if path in ('/', '/index.html'):
            html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'index.html')
            if os.path.exists(html_path):
                with open(html_path, 'rb') as f:
                    content = f.read()
                self.send_response(200)
                self.send_cors_headers()
                self.send_header('Content-Type', 'text/html; charset=utf-8')
                self.send_header('Content-Length', str(len(content)))
                self.end_headers()
                self.wfile.write(content)
                return

        # File tidak ditemukan
        self.send_response(404)
        self.send_cors_headers()
        self.send_header('Content-Type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'404 Not Found')

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        # Upload Benchmark Endpoint
        if path == '/api/upload':
            try:
                content_length = int(self.headers.get('Content-Length', 0))
            except (ValueError, TypeError):
                content_length = 0

            bytes_received = 0
            start_time = time.time()

            try:
                remaining = content_length
                while remaining > 0:
                    read_size = min(remaining, CHUNK_SIZE)
                    chunk = self.rfile.read(read_size)
                    if not chunk:
                        break
                    bytes_received += len(chunk)
                    remaining -= len(chunk)
            except Exception:
                pass

            duration = max(0.001, time.time() - start_time)
            resp = {
                "status": "success",
                "received_bytes": bytes_received,
                "duration_seconds": round(duration, 4),
                "speed_mbps": round((bytes_received * 8) / (duration * 1_000_000), 2)
            }
            body = json.dumps(resp).encode('utf-8')
            self.send_response(200)
            self.send_cors_headers()
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        self.send_response(404)
        self.send_cors_headers()
        self.end_headers()

def find_available_port(start_port=8080, max_attempts=20):
    for port in range(start_port, start_port + max_attempts):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('0.0.0.0', port))
                return port
            except OSError:
                continue
    return start_port

def run_server():
    port = find_available_port(DEFAULT_PORT)
    server_address = ('0.0.0.0', port)
    httpd = ThreadingHTTPServer(server_address, SpeedTestHandler)
    
    url = f"http://localhost:{port}"
    print("=" * 60)
    print("   [*] ZEN SPEEDTEST SERVER (Pelayan Ancellia)")
    print("=" * 60)
    print(f"[*] Server aktif di port       : {port}")
    print(f"[*] Akses Browser Lokal        : {url}")
    try:
        local_ip = socket.gethostbyname(socket.gethostname())
        print(f"[*] Akses Jaringan Lokal (LAN) : http://{local_ip}:{port}")
    except Exception:
        pass
    print("[*] Benchmark Endpoints        : /api/ping | /api/download | /api/upload")
    print("[*] Status CORS                : Fully Unlocked (*) + PNA Allowed")
    print("=" * 60)
    print("[i] Membuka antarmuka SpeedTest di browser Master Zay...")
    
    # Buka browser otomatis
    try:
        webbrowser.open(url)
    except Exception as e:
        print(f"[!] Gagal membuka browser otomatis: {e}")

    print("[*] Tekan Ctrl+C untuk menghentikan server.")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[*] Server dihentikan dengan aman. Salam hormat, Ancellia.")
        httpd.server_close()

if __name__ == '__main__':
    run_server()
