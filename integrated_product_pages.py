"""Publish the eight approved product layouts at their live site routes."""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from urllib.parse import urlsplit

from bs4 import BeautifulSoup

from product_wireframe import ASSET_SOURCE, BASE as DRAFT_BASE, CATEGORIES, ROOT, STYLE_SOURCES, category_page


PUBLIC_BASE = "/crystal-clean-home/"
PUBLIC_ASSET_BASE = PUBLIC_BASE + "reference/product-pages/"


def public_markup(draft_html: str, catalog_json: str, root: Path = ROOT) -> str:
    """Keep the approved markup while changing only its delivery paths/catalog."""
    markup = draft_html.replace(DRAFT_BASE + "assets/", PUBLIC_ASSET_BASE + "assets/")
    for device in STYLE_SOURCES:
        markup = markup.replace(
            DRAFT_BASE + f"wireframe-{device}.css",
            PUBLIC_ASSET_BASE + f"wireframe-{device}.css",
        )
    for category in CATEGORIES:
        markup = markup.replace(DRAFT_BASE + category + "/", PUBLIC_BASE + "house-cleaning/" + category + "/")
    for page in ("cart", "estimate"):
        markup = markup.replace(DRAFT_BASE + page + "/", PUBLIC_BASE + page + "/")
    if DRAFT_BASE in markup:
        raise ValueError("A draft URL remains in the integrated product page")
    soup = BeautifulSoup(markup, "html.parser")
    for stylesheet in soup.select('link[rel="stylesheet"][href^="/crystal-clean-home/reference/assets/"]'):
        relative = urlsplit(stylesheet["href"]).path.removeprefix(PUBLIC_BASE)
        if not (root / "docs" / relative).exists():
            stylesheet.decompose()
    embedded = soup.select_one("script#shop-catalog")
    if embedded is None:
        raise ValueError("Product page has no estimate catalog")
    embedded.string = catalog_json
    return str(soup)


def publish_integrated_product_pages(root: Path = ROOT, catalog: dict | None = None) -> None:
    root = Path(root)
    if catalog is None:
        catalog = json.loads((root / "docs/reference/catalog.json").read_text(encoding="utf-8"))
    catalog_json = json.dumps(catalog, ensure_ascii=False).replace("</", "<\\/")
    asset_output = root / "docs/reference/product-pages"
    asset_output.mkdir(parents=True, exist_ok=True)
    for device, source in STYLE_SOURCES.items():
        shutil.copy2(source, asset_output / f"wireframe-{device}.css")
    shutil.copytree(ASSET_SOURCE, asset_output / "assets", dirs_exist_ok=True)
    for category in CATEGORIES:
        draft_html, _ = category_page(category)
        markup = public_markup(draft_html, catalog_json, root)
        destination = root / "docs/house-cleaning" / category / "index.html"
        destination.write_text(markup, encoding="utf-8")
        if category == "pack":
            (root / "docs/services/index.html").write_text(markup, encoding="utf-8")


if __name__ == "__main__":
    publish_integrated_product_pages()
