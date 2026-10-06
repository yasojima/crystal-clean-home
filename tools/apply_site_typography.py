"""Apply the shared heading/body font links to all saved HTML pages."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "source/site"
MANIFEST = ROOT / "source/manifest.json"
CSS_PATH = "assets/css/site-typography.css"
FONT_LINK = (
    '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?'
    'family=Noto+Sans+JP:wght@400;500;700&amp;'
    'family=Zen+Kaku+Gothic+New:wght@400;500;700&amp;display=swap">'
)
CSS_LINK = '<link rel="stylesheet" href="/assets/css/site-typography.css?v=2026100601">'


def add_typography_links(html: str) -> str:
    """Refresh the shared version and insert missing links without duplicates."""
    html = re.sub(r'<link\b[^>]*href="/assets/css/site-typography\.css(?:\?[^\"]*)?"[^>]*>',
                  lambda _: CSS_LINK, html)
    additions = []
    if FONT_LINK not in html:
        additions.append(FONT_LINK)
    if CSS_LINK not in html:
        additions.append(CSS_LINK)
    if not additions:
        return html
    newline = "\r\n" if "\r\n" in html else "\n"
    result, count = re.subn(
        r"</head\s*>",
        lambda match: newline.join(additions) + newline + match.group(),
        html,
        count=1,
        flags=re.I,
    )
    if count != 1:
        raise ValueError("HTML page has no closing head element")
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Check links and manifest without writing")
    args = parser.parse_args()
    pages = sorted(SITE.rglob("*.html"))
    changed: dict[str, bytes] = {}
    for page in pages:
        before = page.read_bytes()
        after = add_typography_links(before.decode("utf-8")).encode("utf-8")
        if after != before:
            changed[page.relative_to(SITE).as_posix()] = after

    css = (SITE / CSS_PATH).read_bytes()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    indexed = {record["path"]: record for record in manifest["files"].values()}
    stale = [rel for rel in [CSS_PATH, *(page.relative_to(SITE).as_posix() for page in pages)]
             if rel not in indexed or indexed[rel]["sha256"] != hashlib.sha256(
                 changed.get(rel, (SITE / rel).read_bytes())).hexdigest()]
    if args.check:
        if changed or stale:
            raise SystemExit(f"Typography sync required: {len(changed)} pages, {len(stale)} manifest entries")
        print(json.dumps({"pages_checked": len(pages), "typography_current": True}))
        return

    for rel, data in changed.items():
        (SITE / rel).write_bytes(data)
    for rel in sorted(set(changed) | set(stale) | {CSS_PATH}):
        data = changed.get(rel)
        if data is None:
            data = css if rel == CSS_PATH else (SITE / rel).read_bytes()
        if rel in indexed:
            indexed[rel].setdefault("source_sha256", indexed[rel]["sha256"])
            indexed[rel]["sha256"] = hashlib.sha256(data).hexdigest()
            indexed[rel]["bytes"] = len(data)
        else:
            url = manifest["origin"].rstrip("/") + "/" + rel
            manifest["files"][url] = {
                "path": rel, "effective_url": url, "status": 200,
                "content_type": "text/css" if rel.endswith(".css") else "text/html",
                "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest(),
                "origin_type": "local-site-typography",
            }
    unique = {record["path"]: record for record in manifest["files"].values()}
    manifest["counts"].update(urls=len(manifest["files"]), unique_paths=len(unique),
                              bytes=sum(record["bytes"] for record in unique.values()))
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"pages": len(pages), "updated_pages": len(changed),
                      "manifest_entries": len(stale)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
