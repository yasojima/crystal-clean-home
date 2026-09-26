"""Check the generated corporate page and its canonical local assets."""

from pathlib import Path
from bs4 import BeautifulSoup

from corporation import BODY_COPY, publish_corporation


ROOT = Path(__file__).resolve().parent
PAGE = ROOT / "docs/service/corporation/index.html"


def check():
    publish_corporation(ROOT)
    first = PAGE.read_text(encoding="utf-8")
    publish_corporation(ROOT)
    assert PAGE.read_text(encoding="utf-8") == first, "corporate publisher is not idempotent"

    soup = BeautifulSoup(first, "html.parser")
    main = soup.find("main", class_="main_contents")
    assert main is not None
    assert main.find("h1", recursive=False).get_text(strip=True) == "法人向けサービス"
    assert main.find("h1", recursive=False).has_attr("class")
    assert len(soup.select('link[data-cch-corporation-desktop]')) == 1
    assert len(soup.select('link[data-cch-corporation-mobile]')) == 1

    for selector, copies in BODY_COPY.items():
        actual = [node.get_text(strip=True) for node in main.select(selector.removeprefix("main "))]
        assert actual == copies, selector

    urls = {value for img in main.find_all("img") for value in (img.get("src"), img.get("data-src")) if value and "/brand/corporation/images/" in value}
    names = {Path(url).name for url in urls}
    expected = {f"corporate_img{i:03d}.png" for i in range(1, 18)} | {"sp_corporate_img001.png"}
    assert names == expected, names ^ expected
    for name in expected:
        assert (ROOT / "brand/corporation/images" / name).is_file(), name
        assert (ROOT / "docs/brand/corporation/images" / name).is_file(), name
    assert not any("/wp/wp-content/themes/original_theme/img/corporate_img" in str(img) for img in main.find_all("img"))
    for platform in ("desktop", "mobile"):
        assert (ROOT / f"docs/brand/corporation/{platform}.css").read_bytes() == (ROOT / f"source/device/{platform}/css/corporation.css").read_bytes()
    print("PASS: corporate title, seven paragraphs, 18 images, two stylesheets, idempotent publishing")


if __name__ == "__main__":
    check()
