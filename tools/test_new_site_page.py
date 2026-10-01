"""Exercise the page generator without leaving a test page in the site."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "source/manifest.json"
PAGE_DIR = ROOT / "source/site/__identity_probe__"
PAGE = PAGE_DIR / "index.html"


def main() -> None:
    if PAGE_DIR.exists():
        raise SystemExit("Probe route already exists; refusing to overwrite it")
    original_manifest = MANIFEST.read_bytes()
    try:
        subprocess.run([sys.executable, "-X", "utf8", str(ROOT / "tools/new_site_page.py"),
                        "/__identity_probe__/", "検査用"], cwd=ROOT, check=True,
                       stdout=subprocess.DEVNULL)
        html = PAGE.read_text(encoding="utf-8")
        assert "<title>Crystal Clean Home</title>" in html
        assert 'href="/favicon/crystal-clean-home.svg"' in html
        assert 'src="/assets/js/demo-contact.js"' in html
        assert 'src="/assets/js/shared-translation-control.js"' in html
        assert 'href="/assets/css/site-typography.css?v=20261001"' in html
        assert 'family=Zen+Kaku+Gothic+New:wght@400;500;700' in html
        print("new page identity generation: PASS")
    finally:
        if PAGE.exists():
            PAGE.unlink()
        if PAGE_DIR.exists():
            PAGE_DIR.rmdir()
        MANIFEST.write_bytes(original_manifest)


if __name__ == "__main__":
    main()
