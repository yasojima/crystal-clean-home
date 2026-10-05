"""Audit every published HTML page for identity and old contact destinations."""

from __future__ import annotations

import json
import re
from html.parser import HTMLParser
from pathlib import Path

SITE = Path(__file__).resolve().parents[1] / "source/site"
BRAND = "クリスタルクリーンホーム"
TAB_BRAND = "Crystal Clean Home"
ICON = "/favicon/crystal-clean-home.svg"
SCRIPT = "/assets/js/demo-contact.js?v=2026100601"
TRANSLATION_SCRIPT = "/assets/js/shared-translation-control.js"
OLD_NAME = re.compile(r"おそうじ本舗|お掃除本舗|オソウジホンポ")
OLD_PHONE = re.compile(r"0120[-‐‑–—ー ]?24[-‐‑–—ー ]?1000|03[-‐‑–—ー ]?6630[-‐‑–—ー ]?6104|0120241000")
EMAIL = re.compile(r"[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}", re.I)
FORMER_LINK = re.compile(r"(?:osoujihonpo|hitowa\.com|lin\.ee/|line\.me/R/ti/p/)", re.I)
OBSOLETE_ASSET = re.compile(r"(?:/assets/images/logo\.webp|/assets/images/footer/footer-tel-"
                            r"|img-app750\.webp|/line_bnr\.webp)", re.I)


class Page(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.title = ""
        self.in_title = False
        self.icons = []
        self.scripts = []
        self.bad_links = []
        self.mail_or_phone_links = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr = dict(attrs)
        if tag == "title":
            self.in_title = True
        if tag == "link" and "icon" in (attr.get("rel") or ""):
            self.icons.append(attr.get("href"))
        if tag == "script":
            self.scripts.append(attr.get("src"))
        if tag == "a":
            href = attr.get("href") or ""
            if FORMER_LINK.search(href):
                self.bad_links.append(href)
            if href.lower().startswith(("mailto:", "tel:")):
                self.mail_or_phone_links.append(href)

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self.in_title = False

    def handle_data(self, data: str) -> None:
        if self.in_title:
            self.title += data


def main() -> None:
    pages = sorted(SITE.rglob("*.html"))
    failures = []
    for path in pages:
        text = path.read_text(encoding="utf-8")
        page = Page()
        page.feed(text)
        reasons = []
        if page.title != TAB_BRAND:
            reasons.append("tab title")
        if page.icons != [ICON]:
            reasons.append("favicon")
        if page.scripts.count(SCRIPT) != 1:
            reasons.append("demo script")
        if page.scripts.count(TRANSLATION_SCRIPT) != 1:
            reasons.append("translation script")
        if OLD_NAME.search(text):
            reasons.append("former shop name")
        if OLD_PHONE.search(text):
            reasons.append("former phone")
        if EMAIL.search(text):
            reasons.append("email address")
        if page.bad_links:
            reasons.append(f"former-brand links ({len(page.bad_links)})")
        if page.mail_or_phone_links:
            reasons.append(f"mailto/tel links ({len(page.mail_or_phone_links)})")
        if OBSOLETE_ASSET.search(text):
            reasons.append("obsolete brand/contact image")
        if reasons:
            failures.append({"path": path.relative_to(SITE).as_posix(), "reasons": reasons})
    for path in SITE.rglob("*.js"):
        text = path.read_text(encoding="utf-8")
        reasons = []
        if OLD_NAME.search(text) or OLD_PHONE.search(text):
            reasons.append("former shop name or phone")
        if OBSOLETE_ASSET.search(text):
            reasons.append("obsolete brand/contact image")
        if reasons:
            failures.append({"path": path.relative_to(SITE).as_posix(), "reasons": reasons})
    result = {"pages_checked": len(pages), "failed_pages": len(failures),
              "issues": failures[:30]}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
