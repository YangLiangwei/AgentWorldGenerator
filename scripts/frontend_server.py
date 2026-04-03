from __future__ import annotations

import json
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib import error, request

ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / "web"
API_BASE = "http://127.0.0.1:8787"


def _send(handler: BaseHTTPRequestHandler, code: int, body: bytes, ctype: str):
    handler.send_response(code)
    handler.send_header("Content-Type", ctype)
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


class Handler(BaseHTTPRequestHandler):
    def do_HEAD(self):
        if self.path.startswith('/api/'):
            target = API_BASE + self.path[len('/api'):]
            req = request.Request(target, method='HEAD')
            try:
                with request.urlopen(req) as resp:
                    return _send(self, resp.getcode(), b"", resp.headers.get('Content-Type', 'application/json; charset=utf-8'))
            except Exception:
                return _send(self, 502, b"", 'text/plain')
        path = WEB / ('index.html' if self.path == '/' else self.path.lstrip('/'))
        if path.exists() and path.is_file():
            return _send(self, 200, b"", 'text/html; charset=utf-8')
        return _send(self, 404, b"", 'text/plain')

    def do_GET(self):
        if self.path.startswith('/api/'):
            return self._proxy('GET')
        path = WEB / ('index.html' if self.path == '/' else self.path.lstrip('/'))
        if path.exists() and path.is_file():
            return _send(self, 200, path.read_bytes(), 'text/html; charset=utf-8')
        return _send(self, 404, b'not found', 'text/plain')

    def do_POST(self):
        if self.path.startswith('/api/'):
            return self._proxy('POST')
        return _send(self, 404, b'not found', 'text/plain')

    def _proxy(self, method: str):
        target = API_BASE + self.path[len('/api'):]
        body = None
        if method == 'POST':
            n = int(self.headers.get('Content-Length', '0'))
            body = self.rfile.read(n) if n else b'{}'
        req = request.Request(target, data=body, method=method, headers={'Content-Type': 'application/json'})
        try:
            with request.urlopen(req) as resp:
                data = resp.read()
                ctype = resp.headers.get('Content-Type', 'application/json; charset=utf-8')
                return _send(self, resp.getcode(), data, ctype)
        except error.HTTPError as e:
            data = e.read() if hasattr(e, 'read') else json.dumps({'error': str(e)}).encode('utf-8')
            ctype = e.headers.get('Content-Type', 'application/json; charset=utf-8') if getattr(e, 'headers', None) else 'application/json; charset=utf-8'
            return _send(self, e.code, data, ctype)
        except Exception as e:
            err = json.dumps({'error': str(e)}).encode('utf-8')
            return _send(self, 502, err, 'application/json; charset=utf-8')


def run(port: int = 8788):
    srv = HTTPServer(('0.0.0.0', port), Handler)
    print(f'frontend server listening on :{port}')
    srv.serve_forever()


if __name__ == '__main__':
    run()
