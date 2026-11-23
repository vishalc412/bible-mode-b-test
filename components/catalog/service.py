"""Catalog HTTP API: other services read prices over HTTP.

Run: python3 -m components.catalog.service   (listens on 127.0.0.1:8001; CATALOG_HOST / CATALOG_PORT change it)
GET /price/<sku>  ->  200 {"sku": "SKU-1", "price": 24.0}  |  404 {"error": "unknown sku SKU-9"}
GET /health       ->  200 {"status": "ok"}
"""
import json
import os
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from components.catalog import catalog


class CatalogHandler(BaseHTTPRequestHandler):
    def _send(self, code, payload):
        body = json.dumps(payload).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = urllib.parse.urlsplit(self.path).path
        if path == "/health":
            return self._send(200, {"status": "ok"})
        if path.startswith("/price/"):
            sku = urllib.parse.unquote(path[len("/price/"):])
            try:
                return self._send(200, {"sku": sku, "price": catalog.price_of(sku)})
            except KeyError:
                return self._send(404, {"error": "unknown sku %s" % sku})
        return self._send(404, {"error": "not found"})

    def log_message(self, *args):
        pass


def make_server(host=None, port=None):
    host = host or os.environ.get("CATALOG_HOST", "127.0.0.1")
    port = int(port if port is not None else os.environ.get("CATALOG_PORT", "8001"))
    return ThreadingHTTPServer((host, port), CatalogHandler)


if __name__ == "__main__":
    server = make_server()
    print("catalog API on http://%s:%d" % server.server_address)
    server.serve_forever()
