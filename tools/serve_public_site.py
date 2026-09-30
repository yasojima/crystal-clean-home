"""Serve the captured public responses without rewriting their contents."""
import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / 'source' / 'site'
manifest = json.loads((ROOT / 'source' / 'manifest.json').read_text(encoding='utf-8'))
responses = {}
for url, record in manifest['files'].items():
    parts = urlsplit(url)
    responses[(unquote(parts.path), parts.query)] = record
    responses.setdefault((unquote(parts.path), ''), record)


class SnapshotHandler(BaseHTTPRequestHandler):
    def serve(self, body=True):
        parts = urlsplit(self.path)
        path = unquote(parts.path)
        record = responses.get((path, parts.query)) or responses.get((path, ''))
        if record is None and not path.endswith('/') and (path + '/', '') in responses:
            self.send_response(301)
            self.send_header('Location', parts.path + '/' + (('?' + parts.query) if parts.query else ''))
            self.send_header('Content-Length', '0')
            self.end_headers()
            return
        if record is None and path.endswith('/'):
            record = responses.get((path.rstrip('/'), ''))
        if record is None:
            self.send_error(404, 'Not included in the captured public responses')
            return
        effective = urlsplit(record['effective_url'])
        if unquote(effective.path) != path:
            self.send_response(302)
            self.send_header('Location', effective.path + (('?' + effective.query) if effective.query else ''))
            self.send_header('Content-Length', '0')
            self.end_headers()
            return
        target = (SITE / record['path']).resolve()
        if not target.is_relative_to(SITE.resolve()) or not target.is_file():
            self.send_error(404)
            return
        self.send_response(200)
        self.send_header('Content-Type', record['content_type'])
        self.send_header('Content-Length', str(target.stat().st_size))
        self.send_header('Cache-Control', 'no-cache')
        self.end_headers()
        if body:
            with target.open('rb') as file:
                while chunk := file.read(1024 * 1024):
                    self.wfile.write(chunk)

    def do_GET(self):
        self.serve()

    def do_HEAD(self):
        self.serve(body=False)

    def do_POST(self):
        self.send_error(501, 'Server connections are not implemented in this frontend snapshot')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', type=int, default=8769)
    args = parser.parse_args()
    with ThreadingHTTPServer(('127.0.0.1', args.port), SnapshotHandler) as server:
        print(f'Preview: http://127.0.0.1:{args.port}/', flush=True)
        print('Stop: Ctrl+C. Cart, reservation and form submissions are not connected.', flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
