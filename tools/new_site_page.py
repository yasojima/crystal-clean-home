"""Create a page with the shared Crystal Clean Home tab and contact settings."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "source/site"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("route", help="URL path, for example: /new-service/")
    parser.add_argument("title", help="Page title before the shared shop name")
    args = parser.parse_args()
    route = args.route.strip("/")
    if not route or any(part in (".", "..") for part in Path(route).parts):
        parser.error("Specify a new route below the site root")
    page = (SITE / route / "index.html").resolve()
    if not page.is_relative_to(SITE.resolve()) or page.exists():
        parser.error("The route is invalid or already exists")
    title = (args.title or "").strip()
    if not title or any(char in title for char in "<>&"):
        parser.error("Provide a plain-text title")
    page.parent.mkdir(parents=True, exist_ok=True)
    page.write_text(
        '<!doctype html>\n<html lang="ja">\n<head>\n'
        '<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        f'<title>{title}</title>\n<link rel="stylesheet" href="/assets/css/common.css">\n'
        '</head>\n<body>\n<main>\n'
        f'<h1>{title}</h1>\n'
        '</main>\n</body>\n</html>\n', encoding="utf-8")
    subprocess.run([sys.executable, "-X", "utf8", str(ROOT / "tools/apply_site_identity.py")],
                   cwd=ROOT, check=True)
    print(page)


if __name__ == "__main__":
    main()
