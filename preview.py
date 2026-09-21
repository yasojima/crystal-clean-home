from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
ROOT = Path(__file__).resolve().parent / 'docs'
class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)
    def translate_path(self, path):
        if path.startswith('/crystal-clean-home/'):
            path = path[len('/crystal-clean-home'):]
        return super().translate_path(path)
ThreadingHTTPServer(('127.0.0.1', 8766), Handler).serve_forever()
