"""Check the eight main-site product pages against their approved source layout."""

import json
import re
from urllib.parse import urlsplit

from bs4 import BeautifulSoup

from integrated_product_pages import PUBLIC_ASSET_BASE, PUBLIC_BASE, public_markup
from product_wireframe import CATEGORIES, REVIEW_COPY, ROOT, category_page


catalog = json.loads((ROOT / "docs/reference/catalog.json").read_text(encoding="utf-8"))
catalog_data = json.dumps(catalog, ensure_ascii=False).replace("</", "<\\/")
variants = {variant["id"] for product in catalog["products"] for variant in product["variants"]}
assert {"ref-outerwall-base", "ref-outerwall-extra-sqm"} <= variants
card_counts = {"aircon": 38, "pack": 103, "water": 46, "washer": 20,
               "kitchen": 31, "room": 38, "coating": 11, "others": 10}
comparison_counts = {"aircon": 3, "pack": 2, "water": 3, "washer": 2,
                     "kitchen": 3, "room": 3, "coating": 2, "others": 2}

for category in CATEGORIES:
    expected_html, _ = category_page(category)
    expected = BeautifulSoup(public_markup(expected_html, catalog_data), "html.parser")
    destination = ROOT / "docs/house-cleaning" / category / "index.html"
    actual = BeautifulSoup(destination.read_text(encoding="utf-8"), "html.parser")
    assert str(actual.select_one(".cch-reference main")) == str(expected.select_one(".cch-reference main")), category
    assert json.loads(actual.select_one("#shop-catalog").text) == catalog, category
    assert "_product-wireframe" not in str(actual), category

    cards = actual.select(".js-product-card")
    assert len(cards) == card_counts[category], category
    assert len(actual.select(".c-compare-image")) == comparison_counts[category], category
    assert len(actual.select('[data-wireframe-slot="flow"] li')) == 5, category
    assert not actual.select('[data-product-card="option"] .js-modal-opener'), category
    assert len(actual.select('[data-product-card="parent"] .js-modal-opener')) == len(actual.select('[data-product-card="parent"]')), category
    for card in cards:
        for variant_id in json.loads(card["data-cch-variants"]):
            assert variant_id in variants, (category, variant_id)
    reviews = actual.select(".cch-wf-voice-card")
    assert len(reviews) == len(REVIEW_COPY[category]) == 6, category
    for card, (title, body) in zip(reviews, REVIEW_COPY[category]):
        assert card.select_one("h3").get_text(strip=True) == title, category
        assert card.select_one("p").get_text(strip=True) == body, category
        assert len(body) >= 100, (category, title)
    for image in actual.select(".cch-reference main img[src], .cch-wf-hero source[srcset]"):
        url = image.get("src") or image.get("srcset")
        if not url.startswith(PUBLIC_BASE):
            continue
        asset = ROOT / "docs" / urlsplit(url).path.removeprefix(PUBLIC_BASE)
        assert asset.exists(), (category, url)
    for stylesheet in actual.select('link[rel="stylesheet"][href^="/crystal-clean-home/reference/assets/"]'):
        relative = urlsplit(stylesheet["href"]).path.removeprefix(PUBLIC_BASE)
        assert (ROOT / "docs" / relative).exists(), (category, relative)
    for relative in re.findall(re.escape(PUBLIC_ASSET_BASE) + r"assets/([\w/.-]+)", str(actual)):
        assert (ROOT / "docs" / PUBLIC_ASSET_BASE.removeprefix(PUBLIC_BASE) / "assets" / relative).exists(), (category, relative)
    for link in actual.select(".cch-reference main a[href^='#']"):
        target = link["href"][1:]
        if target:
            assert actual.select_one("[id='" + target + "']"), (category, target)
    print(category, len(cards), "cards; 6 expanded sample reviews; exact main markup")

assert (ROOT / "docs/services/index.html").read_bytes() == (ROOT / "docs/house-cleaning/pack/index.html").read_bytes()
for device in ("desktop", "mobile"):
    assert (ROOT / "docs" / PUBLIC_ASSET_BASE.removeprefix(PUBLIC_BASE) / f"wireframe-{device}.css").exists()
print("PASS: eight integrated pages, links, assets, products, catalog, and reviews")
