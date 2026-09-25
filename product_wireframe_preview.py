"""Serve the locally generated site without publishing it."""

from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


DOCS = Path(__file__).resolve().parent / "docs"


class PreviewHandler(SimpleHTTPRequestHandler):
    def end_headers(self) -> None:
        self.send_header("Cache-Control", "no-store, must-revalidate")
        self.send_header("Pragma", "no-cache")
        super().end_headers()

    def translate_path(self, path: str) -> str:
        clean = path.split("?", 1)[0].split("#", 1)[0]
        relative = clean.removeprefix("/crystal-clean-home/").lstrip("/")
        target = (DOCS / relative).resolve()
        if not target.is_relative_to(DOCS.resolve()):
            return str(DOCS / "__not_found__")
        return str(target)


if __name__ == "__main__":
    server = ThreadingHTTPServer(("127.0.0.1", 8799), PreviewHandler)
    print("Local product page: http://127.0.0.1:8799/crystal-clean-home/house-cleaning/aircon/")
    server.serve_forever()
