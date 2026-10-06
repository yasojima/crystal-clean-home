"""Serve the prototype and existing site from one local process."""
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlsplit
import argparse

HERE = Path(__file__).resolve().parent
SITE = HERE.parents[1] / "source" / "site"


class Handler(SimpleHTTPRequestHandler):
    def translate_path(self, path):
        route = unquote(urlsplit(path).path)
        if route == "/home-wireframe":
            route += "/"
        if route.startswith("/home-wireframe/"):
            base, relative = HERE, route.removeprefix("/home-wireframe/")
        else:
            base, relative = SITE, route.lstrip("/")
        resolved = (base / relative).resolve()
        if not resolved.is_relative_to(base):
            return str(base / "__not_found__")
        return str(resolved)

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def log_message(self, *_):
        pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8773)
    args = parser.parse_args()
    server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    print(f"http://127.0.0.1:{args.port}/home-wireframe/", flush=True)
    server.serve_forever()
