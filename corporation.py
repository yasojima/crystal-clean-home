"""Publish the independent corporate-service presentation from the captured page."""

from pathlib import Path
from bs4 import BeautifulSoup
import shutil


BASE = "/crystal-clean-home/"
OLD_IMAGES = BASE + "wp/wp-content/themes/original_theme/img/"
NEW_IMAGES = BASE + "brand/corporation/images/"

BODY_COPY = {
    "main .area_corporation-lead p": [
        "オフィスや店舗など、多くの方が利用する建物では、場所ごとに汚れの種類や清掃の優先順位が異なります。私たちは施設の用途と利用状況を伺い、日常の業務に配慮した清掃内容をご案内します。",
        "作業前に対象の材質や汚れの状態を確認し、必要な範囲と方法を整理します。見た目だけでなく、利用する方が気持ちよく過ごせる環境を目指し、一箇所ずつ丁寧に取り組みます。",
    ],
    "main .area_corporation-difference .text p": [
        "業務用エアコンは、設置場所や稼働状況によって内部にほこりや汚れが蓄積します。機種と状態を確かめたうえで、フィルターや外装、必要に応じた内部の清掃範囲をご提案します。定期的なお手入れについてもご相談ください。",
        "人の出入りが多い床には、砂ぼこりや靴の跡などが少しずつ残ります。カーペットのシミや床材の汚れは、素材と状態を確認してから清掃方法を選びます。日常のお手入れでは届きにくい箇所も、必要な範囲を丁寧に整えます。",
        "共用部や利用頻度の高い箇所の除菌清掃、光触媒コーティングについてもご相談いただけます。対象となる素材や作業条件を確認し、施設の使い方に合う内容をご案内します。",
        "改修や入退去に伴う引き渡し前の清掃では、工事後の粉じんや設備まわりの汚れなど、現場ごとに確認すべき点が変わります。対象範囲と仕上げのご希望を伺い、作業内容を明確にしたうえで進めます。規模の大きな現場も、まずはご相談ください。",
    ],
    "main .area_corporation-difference-annotation p": [
        "法人施設の清掃に加え、住まいのハウスクリーニングについてもご相談を承ります。場所ごとの使われ方に目を向け、必要な清掃をわかりやすくご案内します。"
    ],
}


def publish_corporation(root):
    root = Path(root)
    page = root / "docs/service/corporation/index.html"
    soup = BeautifulSoup(page.read_text(encoding="utf-8"), "html.parser")
    main = soup.find("main", class_="main_contents")
    if main is None:
        raise ValueError("Corporate main section not found")

    title = main.find("h1", recursive=False)
    if title is None or title.get_text(strip=True) != "法人向けサービス":
        raise ValueError("Corporate page title changed")
    title["class"] = ["cch-corporation-title-band"]
    soup.body["class"] = list(dict.fromkeys([*soup.body.get("class", []), "cch-corporation"]))

    for selector, paragraphs in BODY_COPY.items():
        nodes = main.select(selector.removeprefix("main "))
        if len(nodes) != len(paragraphs):
            raise ValueError(f"Corporate copy shape changed: {selector}: {len(nodes)}")
        for node, copy in zip(nodes, paragraphs):
            node.clear()
            node.append(copy)

    for img in main.find_all("img"):
        for attr in ("src", "data-src"):
            value = img.get(attr, "")
            if value.startswith(OLD_IMAGES) and "corporate_img" in value:
                img[attr] = NEW_IMAGES + Path(value).stem + ".png"
    for noscript in main.find_all("noscript"):
        inner = str(noscript)
        for name in [f"corporate_img{i:03d}" for i in range(1, 18)] + ["sp_corporate_img001"]:
            inner = inner.replace(OLD_IMAGES + name + ".jpg", NEW_IMAGES + name + ".png")
        noscript.replace_with(BeautifulSoup(inner, "html.parser"))

    if not soup.select_one('link[data-cch-corporation-desktop]'):
        for platform in ("desktop", "mobile"):
            link = soup.new_tag("link", rel="stylesheet")
            link["href"] = BASE + "brand/corporation/" + platform + ".css"
            link["data-cch-corporation-" + platform] = ""
            link["media"] = "(min-width: 993px)" if platform == "desktop" else "(max-width: 992px)"
            soup.head.append(link)

    out = root / "docs/brand/corporation"
    out.mkdir(parents=True, exist_ok=True)
    shutil.copytree(root / "brand/corporation/images", out / "images", dirs_exist_ok=True)
    for platform in ("desktop", "mobile"):
        shutil.copy2(root / f"source/device/{platform}/css/corporation.css", out / f"{platform}.css")
    page.write_text(str(soup), encoding="utf-8")


if __name__ == "__main__":
    publish_corporation(Path(__file__).resolve().parent)
    from shared_ui import publish_shared_ui
    publish_shared_ui(Path(__file__).resolve().parent)
