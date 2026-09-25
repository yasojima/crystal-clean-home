"""Build isolated product-page wireframes from exact copies of current output."""

from __future__ import annotations

import hashlib
import json
import re
from copy import deepcopy
from html import escape
from pathlib import Path

from bs4 import BeautifulSoup, Comment, NavigableString, Tag


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "source/product-wireframe/pages/house-cleaning"
BASE = "/crystal-clean-home/_product-wireframe/"
STYLE_SOURCES = {
    device: ROOT / f"source/device/{device}/css/product-wireframe/wireframe.css"
    for device in ("desktop", "mobile")
}
ASSET_SOURCE = ROOT / "source/product-wireframe/assets"
REVIEW_COPY_SOURCE = ROOT / "source/product-wireframe/review-copy.json"
FAQ_COPY_SOURCE = ROOT / "source/product-wireframe/faq-copy.json"
FLOW_COPY_SOURCE = ROOT / "source/product-wireframe/flow-copy.json"
SERVICE_COPY_SOURCE = ROOT / "source/product-wireframe/service-copy.json"
OPTION_BRIEFS_SOURCE = ROOT / "source/product-wireframe/option-brief-copy.json"
STYLE_VERSION = hashlib.sha256(b"".join(path.read_bytes() for path in STYLE_SOURCES.values())).hexdigest()[:12]
CATEGORIES = (
    "aircon", "pack", "water", "washer", "kitchen", "room", "coating", "others"
)
REVIEW_COPY = json.loads(REVIEW_COPY_SOURCE.read_text(encoding="utf-8"))
FAQ_COPY = json.loads(FAQ_COPY_SOURCE.read_text(encoding="utf-8"))
FLOW_COPY = json.loads(FLOW_COPY_SOURCE.read_text(encoding="utf-8"))
SERVICE_COPY = json.loads(SERVICE_COPY_SOURCE.read_text(encoding="utf-8"))
OPTION_BRIEFS = json.loads(OPTION_BRIEFS_SOURCE.read_text(encoding="utf-8"))
# (sheet, column, row, columns, rows). Order follows the existing parent cards.
PRODUCT_PHOTO_LAYOUT = {
    "aircon": [("product-sheet.png", i % 2, i // 2, 2, 2) for i in range(3)],
    "pack": [("product-sheet.png", 0, i, 1, 2) for i in range(2)],
    "water": [("product-sheet.png", i % 2, i // 2, 2, 3) for i in range(6)],
    "kitchen": [("product-sheet.png", i % 2, i // 2, 2, 2) for i in range(4)],
    "room": [(f"product-sheet-{i // 6 + 1}.png", (i % 6) % 3, (i % 6) // 3, 3, 2) for i in range(17)],
    "coating": [(f"product-sheet-{i // 4 + 1}.png", (i % 4) % 2, (i % 4) // 2, 2, 2) for i in range(7)],
    "others": [("product-sheet.png", i % 2, i // 2, 2, 2) for i in range(4)],
}
SERVICE_ICON_ASSETS = {
    "aircon-wall.webp": "service-icons/wall-aircon.png",
    "aircon-ceil.webp": "aircon/ceiling-cassette-front.png",
    "disassemble.png": "service-icons/disassembled-ac.png",
    "ac-coat.png": "service-icons/ac-coat.png",
    "outdoor-unit.png": "service-icons/outdoor-unit.png",
    "cap.png": "service-icons/bug-cap.png",
    "eco.png": "service-icons/eco-detergent.png",
    "steam.png": "service-icons/steam-cleaner.png",
    "air-cleaner.png": "room/air-purifier.png",
    "intake-exhaust-port.png": "service-icons/intake-vent.png",
    "filter.png": "service-icons/vent-filter.png",
    "four-way-machine.png": "aircon/ceiling-cassette-front.png",
    "four-way.png": "aircon/ceiling-cassette-front.png",
    "kitchen-fan.webp": "kitchen/range-hood-front.png",
    "kitchen.webp": "service-icons/kitchen-unit.png",
    "bath.webp": "service-icons/bathtub.png",
    "bath-fan.webp": "water/bathroom-dryer-front.png",
    "sink.webp": "water/lavatory-front.png",
    "pipe.webp": "water/reheating-pipes-front.png",
    "ulblo.webp": "water/ultrabubble-fixture-front.png",
    "wallpaper-dyeing-option-five.png": "room/wallpaper-dyeing-front.png",
    "wallpaper-dyeing-option-ten.png": "room/wallpaper-dyeing-front.png",
    "cleaning-wax.png": "service-icons/floor-wax.png",
    "cleaning-wax1.png": "service-icons/floor-wax.png",
    "peeling-wax10.png": "service-icons/wax-strip.png",
    "peeling-wax.png": "service-icons/wax-strip.png",
    "toilet.webp": "water/toilet-front.png",
    "wallpaper-dyeing-cloth.webp": "room/wallpaper-dyeing-front.png",
    "op-coating.png": "service-icons/surface-coating.png",
    "mirror-film-option.png": "service-icons/bathroom-mirror.png",
    "drier.png": "water/bathroom-dryer-front.png",
    "descaling-blue.png": "service-icons/mineral-stain.png",
    "pipe.png": "water/reheating-pipes-front.png",
    "ti-coat.png": "service-icons/anti-mold-bath.png",
    "apron-high-pressure.png": "service-icons/bath-apron.png",
    "apron.png": "service-icons/bath-apron.png",
    "mirror.png": "service-icons/bathroom-mirror.png",
    "bathroom-addition-option.png": "service-icons/bathtub.png",
    "ulblo-op.png": "water/ultrabubble-fixture-front.png",
    "lavatory-set.png": "water/lavatory-front.png",
    "intake-exhaust-port-filter.png": "service-icons/vent-filter.png",
    "toilet-ventilation-fan.png": "service-icons/toilet-fan.png",
    "add-toilet-bowl.png": "water/toilet-front.png",
    "descaling.png": "service-icons/mineral-stain.png",
    "wax.png": "service-icons/floor-wax.png",
    "bathroom-set.png": "service-icons/bathtub.png",
    "lavatory-large-size.png": "water/lavatory-front.png",
    "cooking-stove-set.png": "service-icons/cooking-stove.png",
    "dishwasher-set.png": "kitchen/dishwasher-front.png",
    "kitchen-set.png": "service-icons/kitchen-unit.png",
    "fan-with-cleaning-option.png": "kitchen/range-hood-front.png",
    "fan-island-type.png": "service-icons/island-hood.png",
    "fan-set.png": "kitchen/range-hood-front.png",
    "kitchen-large-size.png": "service-icons/kitchen-unit.png",
    "sink-polishing.png": "service-icons/sink-polish.png",
    "rei-large-size.png": "kitchen/refrigerator-front.png",
    "screen-door.png": "service-icons/screen-door.png",
    "shutter.png": "service-icons/rain-shutter.png",
    "white-wood.png": "room/unfinished-wood-front.png",
    "tatami.png": "room/tatami-front.png",
    "air-purifier-complete-disassembly.png": "service-icons/air-purifier-disassembly.png",
    "flooring-repair.png": "service-icons/floor-repair.png",
    "photocatalyst-addition-option.png": "service-icons/exterior-wall.png",
    "exterior-addition-option.png": "service-icons/exterior-wall.png",
    "efro-removal.png": "service-icons/efflorescence-tile.png",
}
WASHER_TYPES = ("top", "front", "side")
WASHER_LINEUP = (
    ("washer-top", "縦型洗濯機のお掃除"),
    ("washer-front", "ドラム式洗濯機のお掃除"),
    ("washer-side", "ドラム式乾燥機能のお掃除"),
)
LABELS = {
    "aircon": "エアコンクリーニング",
    "pack": "まるごとクリーニング",
    "water": "水まわり・浴室",
    "washer": "洗濯機",
    "kitchen": "キッチン",
    "room": "お部屋",
    "coating": "コーティング",
    "others": "外壁洗浄・その他",
}
ISSUES = {
    "washer": (
        "洗ったばかりの洗濯物からイヤなニオイがする…",
        "洗濯物に細かなゴミがつく…",
        "洗濯槽クリーナーを使っても、奥の汚れが気になる…",
    ),
    "coating": ("水まわりや床のお手入れをしやすくしたい", "素材に合う施工方法を知りたい", "清掃とコーティングの違いを確認したい"),
    "others": ("外壁や屋外の汚れが気になる", "清掃できる範囲を確認したい", "場所に合うサービスを選びたい"),
}

ISSUE_FOLLOWUPS = {
    "pack": ("キッチンや窓まわりなど、気になる箇所をまとめて確認し、お部屋に合う清掃プランを選べます。", "まるごとクリーニングはクリスタルクリーンホームにお任せください！"),
    "water": ("浴室のカビや水アカ、トイレや洗面台の汚れなど、水まわりの箇所に合わせて清掃します。", "水まわりの清掃はクリスタルクリーンホームにお任せください！"),
    "washer": ("洗濯物のニオイや細かなゴミが気になるときは、洗濯機の種類に合う清掃サービスをお選びいただけます。", "洗濯機の清掃はクリスタルクリーンホームにお任せください！"),
    "kitchen": ("レンジフードの油汚れやコンロ・シンクの汚れなど、キッチンの気になる箇所に合わせて清掃します。", "キッチンの清掃はクリスタルクリーンホームにお任せください！"),
    "room": ("床やカーペット、壁紙など、お部屋の素材と汚れに合わせてサービスを選べます。", "お部屋の清掃はクリスタルクリーンホームにお任せください！"),
    "coating": ("浴室の小さなキズやくすみ、床のお手入れなど、素材と用途に合わせた施工をご案内します。", "コーティングはクリスタルクリーンホームにお任せください！"),
    "others": ("外壁やベランダの汚れ、お墓のお掃除など、場所に合わせたサービスをご案内します。", "外壁洗浄・その他のお掃除はクリスタルクリーンホームにお任せください！"),
}
SELECTORS = {
    "aircon": (("壁掛けタイプ", "#lineup01"), ("天井埋め込みタイプ", "#lineup02")),
    "pack": (("お得なセット", "#anchor00"), ("お引越し前後", "#anchor01"), ("在宅中", "#anchor02")),
    "water": (("お風呂", "#anchor01"), ("追い焚き配管", "#anchor02"), ("ウルブロ取り付け", "#anchor06"), ("浴室乾燥機", "#anchor03"), ("トイレ", "#anchor04"), ("洗面台", "#anchor05")),
    "washer": (("縦型洗濯機", "#washer-top"), ("ドラム式洗濯機", "#washer-front"), ("ドラム式乾燥機", "#washer-side")),
    "kitchen": (("レンジフード・換気扇", "#anchor01"), ("キッチン", "#anchor02"), ("冷蔵庫", "#anchor03"), ("食器洗い乾燥機", "#anchor04")),
    "room": (("フローリング", "#anchor01"), ("マットレス", "#anchor12"), ("ソファ・椅子", "#anchor02"), ("カーペット", "#anchor03"), ("壁紙染色", "#anchor04"), ("壁紙", "#anchor05"), ("ガラス・サッシ", "#anchor06"), ("白木", "#anchor09"), ("畳", "#anchor10"), ("玄関床", "#anchor11"), ("換気ダクト", "#anchor07"), ("空気清浄機", "#anchor08")),
    "coating": (("リニューアルコーティング", "#coating02"), ("フロアコーティング", "#coating03")),
    "others": (("外壁手洗い洗浄", "#anchor04"), ("光触媒コーティング", "#anchor01"), ("ベランダ・外回り", "#anchor02"), ("お墓", "#anchor03")),
}
BRAND_ILLUSTRATIONS = "/crystal-clean-home/brand/category-illustrations-v2/"
SELECTOR_IMAGES = {
    "aircon": {"#lineup01": BRAND_ILLUSTRATIONS + "aircon.webp", "#lineup02": BASE + "assets/aircon/ceiling-cassette-front.png"},
    "pack": {"#anchor00": BASE + "assets/pack/bundle-front.png", "#anchor01": BASE + "assets/pack/moving-front.png", "#anchor02": BASE + "assets/pack/lived-in-front.png"},
    "water": {"#anchor01": BRAND_ILLUSTRATIONS + "water.png", "#anchor02": BASE + "assets/water/reheating-pipes-front.png", "#anchor06": BASE + "assets/water/ultrabubble-fixture-front.png", "#anchor03": BASE + "assets/water/bathroom-dryer-front.png", "#anchor04": BASE + "assets/water/toilet-front.png", "#anchor05": BASE + "assets/water/lavatory-front.png"},
    "washer": {"#washer-top": BASE + "assets/washer/top-loading-front.png", "#washer-front": BRAND_ILLUSTRATIONS + "washing.png", "#washer-side": BASE + "assets/washer/drum-dryer-front.png"},
    "kitchen": {"#anchor01": BASE + "assets/kitchen/range-hood-front.png", "#anchor02": BRAND_ILLUSTRATIONS + "kitchen.png", "#anchor03": BASE + "assets/kitchen/refrigerator-front.png", "#anchor04": BASE + "assets/kitchen/dishwasher-front.png"},
    "room": {"#anchor01": BRAND_ILLUSTRATIONS + "room.png", "#anchor12": BASE + "assets/room/mattress-front.png", "#anchor02": BASE + "assets/room/sofa-chairs.png", "#anchor03": BASE + "assets/room/carpet-front.png", "#anchor04": BASE + "assets/room/wallpaper-dyeing-front.png", "#anchor05": BASE + "assets/room/wallpaper-cleaning-front.png", "#anchor06": BASE + "assets/room/window-sash-front.png", "#anchor09": BASE + "assets/room/unfinished-wood-front.png", "#anchor10": BASE + "assets/room/tatami-front.png", "#anchor11": BASE + "assets/room/entryway-floor-front.png", "#anchor07": BASE + "assets/room/ventilation-duct-front.png", "#anchor08": BASE + "assets/room/air-purifier.png"},
    "coating": {"#coating02": BASE + "assets/coating/renewal-front.png", "#coating03": BRAND_ILLUSTRATIONS + "coating.png"},
    "others": {"#anchor04": BRAND_ILLUSTRATIONS + "other.png", "#anchor01": BASE + "assets/others/photocatalyst-front.png", "#anchor02": BASE + "assets/others/balcony-pressure-wash-front.png", "#anchor03": BASE + "assets/others/grave-cleaning.png"},
}


def fragment(soup: BeautifulSoup, markup: str) -> Tag:
    return BeautifulSoup(markup, "html.parser").find()


def slot(node: Tag, name: str) -> Tag:
    node["data-wireframe-slot"] = name
    return node


def nearest_section(heading: Tag | None) -> Tag | None:
    return heading.find_parent("section") if heading else None


def source_section(main: Tag, token: str) -> Tag | None:
    for heading in main.find_all("h2"):
        if token in heading.get_text(" ", strip=True):
            section = nearest_section(heading)
            if section and section.find_parent(id="cch-shared-footer") is None:
                return section
    return None


def placeholder(soup: BeautifulSoup, category: str, kind: str) -> Tag:
    if kind == "pain":
        if category in {"washer", "coating", "others"}:
            section = fragment(soup, '<section class="l-section l-section--limited l-section--blue-wave l-section--blue-bubbles" style="--bg-color: #e3f1fc;" data-wireframe-slot="pain"><div class="l-section-inner l-section-inner--limited"><div class="u-width-pc-1024"></div></div></section>')
            section.select_one(".u-width-pc-1024").append(issue_card_list("こんなお悩みはありませんか？", ISSUES[category]))
            return section
        cards = "".join(f"<li>{text}</li>" for text in ISSUES[category])
        return fragment(soup, f'<section class="cch-wf-section cch-wf-pain" data-wireframe-slot="pain"><h2>こんなお悩みはありませんか？</h2><ul>{cards}</ul></section>')
    if kind == "proof":
        return fragment(soup, '<section class="cch-wf-section cch-wf-pending" data-wireframe-slot="proof"><h2>クリーニング事例（ビフォーアフター）</h2><div class="cch-wf-before-after"><div>Before<br><span>このサービスの施工前写真を掲載</span></div><div>After<br><span>同じ施工事例の施工後写真を掲載</span></div></div><p>実際の施工写真が確認できるまで、画像は掲載しません。</p></section>')
    if kind == "plan":
        return fragment(soup, '<section class="cch-wf-section cch-wf-pending" data-wireframe-slot="plan"><h2>おすすめプラン</h2><p>対象商品と組み合わせを確認してから掲載します。商品名・料金・割引を仮定していません。</p></section>')
    if kind == "reviews":
        return fragment(soup, '<section class="cch-wf-section cch-wf-pending" data-wireframe-slot="reviews"><h2>ご利用いただいたお客様の声</h2><p>このサービスに対応する実際の感想を確認後に掲載します。</p></section>')
    if kind == "faq":
        return fragment(soup, '<section class="cch-wf-section cch-wf-pending" data-wireframe-slot="faq"><h2>よくあるご質問</h2><p>対応範囲・料金・作業条件を確認後に回答を掲載します。</p></section>')
    if kind == "flow":
        return fragment(soup, '<section class="cch-wf-section cch-wf-pending" data-wireframe-slot="flow"><h2>ご利用・お支払いまでの流れ</h2><ol><li>商品と数量を選び、概算を確認</li><li>お問い合わせ窓口で内容を確認</li><li>訪問・作業・お支払いの条件を確定</li></ol><p>このワイヤーフレームから実予約・送信はできません。</p></section>')
    raise ValueError(kind)


def replace_compare_photos(section: Tag, category: str) -> None:
    """Retain the source tabs, slider, copy and image dimensions; swap image files only."""
    comparisons = section.select(".c-compare-image")
    for index, comparison in enumerate(comparisons, 1):
        images = comparison.select("img.c-compare-image__item")
        assert len(images) == 2, (category, index)
        for image, phase in zip(images, ("before", "after")):
            asset = ASSET_SOURCE / category / f"case-{index}-{phase}.webp"
            assert asset.exists(), asset
            image["src"] = BASE + f"assets/{category}/{asset.name}"


def completed_proof(soup: BeautifulSoup, category: str) -> Tag:
    """Reuse the existing comparison tabs and slider for original example photos."""
    assert category in {"washer", "others", "coating"}
    source = BeautifulSoup((SOURCE / "aircon/index.html").read_text(encoding="utf-8"), "html.parser")
    section = nearest_section(source.select_one(".c-compare-image"))
    assert section is not None
    section = slot(section.extract(), "proof")
    section.select_one(".p-content-box__heading").string = (
        "コーティングの施工事例（ビフォーアフター）" if category == "coating"
        else f"{LABELS[category]}のクリーニング事例（ビフォーアフター）"
    )
    subjects = {
        "washer": ("洗濯槽まわり", "ドラム式のドアパッキン"),
        "others": ("外壁", "ベランダ"),
        "coating": ("浴槽の表面", "フローリング"),
    }[category]
    buttons = section.select(".c-tab__button")
    panels = section.select(".c-tab__panel")
    assert len(buttons) == len(panels) == 3
    buttons[-1].decompose()
    panels[-1].decompose()
    for index, (label, button, panel) in enumerate(zip(subjects, buttons[:2], panels[:2]), 1):
        button.string = label
        button_id = f"compare-image_{category}_button_{index:02d}"
        panel_id = f"compare-image_{category}_panel_{index:02d}"
        button["id"], button["aria-controls"] = button_id, panel_id
        panel["id"], panel["aria-labelledby"] = panel_id, button_id
        images = panel.select("img.c-compare-image__item")
        assert len(images) == 2
        for image, phase, phase_label in zip(images, ("before", "after"), ("施工前", "施工後")):
            asset = ASSET_SOURCE / category / f"case-{index}-{phase}.png"
            assert asset.exists(), asset
            image["src"] = BASE + f"assets/{category}/{asset.name}"
            image["alt"] = f"{label}の{phase_label}イメージ"
    notes = section.select(".c-note")
    assert len(notes) >= 2
    notes[-1].string = "画像は構成確認用に生成したイメージであり、実際の施工写真ではありません。"
    return section


CURATED_PLANS = {
    "washer": (
        ("縦型洗濯機クリーニング", "洗濯槽まわりの汚れが気になる方に。洗濯機本体の内側と外側、脱水槽を分解せずに洗浄します。", "11,550", "台", "#washer-top", "washer/top-loading-front.png"),
        ("ドラム式洗濯機クリーニング", "ドアパッキンやドラムまわりの汚れを確認したい方に。対象機種と作業範囲は下の商品一覧でご案内します。", "18,150", "台", "#washer-front", BRAND_ILLUSTRATIONS + "washing.png"),
    ),
    "others": (
        ("ベランダ・外回り高圧洗浄", "床や外回りの汚れをまとめて確認したい方に。対象となる場所と追加範囲は商品一覧でご確認ください。", "11,000", "式", "#anchor02", "others/balcony-pressure-wash-front.png"),
        ("お墓のお掃除", "墓石の汚れや周辺の清掃が気になる方に。作業内容と対象範囲は商品一覧でご確認ください。", "19,800", "基", "#anchor03", "others/grave-cleaning.png"),
    ),
    "coating": (
        ("浴室リニューアルコーティング", "浴室の細かなキズやくすみを整え、浴槽などの表面をコーティングします。施工範囲と追加条件をご確認ください。", "71,500", "式", "#coating02", "coating/renewal-front.png"),
        ("フロアコーティング（1帖あたり）", "床材の表面を保護し、お手入れしやすい状態を目指します。料金は1帖あたりの表示です。", "8,800", "帖", "#coating03", BRAND_ILLUSTRATIONS + "coating.png"),
    ),
}

CURATED_PLAN_PRODUCTS = {
    "washer": ("ref-card-8", "ref-card-9"),
    "others": ("ref-card-702", "ref-card-703"),
    "coating": ("ref-card-800", "ref-card-804"),
}


def completed_plan(soup: BeautifulSoup, category: str) -> Tag:
    """Use the existing recommendation card, with the same catalog IDs as its product."""
    water = BeautifulSoup((SOURCE / "water/index.html").read_text(encoding="utf-8"), "html.parser")
    plan = deepcopy(water.select_one(".c-recommend-plan"))
    template = plan.select_one(".c-set-plan-card")
    cards = plan.select_one(".c-recommend-plan__cards")
    assert template and cards
    cards.clear()
    catalog = json.loads(soup.select_one("script#shop-catalog").string)
    products = {product["id"]: product for product in catalog["products"]}
    for (title, description, price, unit, _href, image), product_id in zip(CURATED_PLANS[category], CURATED_PLAN_PRODUCTS[category]):
        product = products[product_id]
        variant = product["variants"][0]
        assert variant["price"] == int(price.replace(",", "")) and variant["unit"] == unit, (category, title)
        card = deepcopy(template)
        card["data-cch-card"] = product_id
        card["data-cch-variants"] = json.dumps([variant["id"]], ensure_ascii=False)
        card.select_one('input[name="product-id"]')["value"] = variant["sourceId"]
        card.select_one(".c-set-plan-card__heading").string = title
        card.select_one(".c-set-plan-card__description").string = description
        card.select_one(".c-set-plan-card__label").decompose()  # No unverified set discount.
        images = card.select(".c-set-plan-card__image")
        images[0]["src"] = image if image.startswith("/") else BASE + "assets/" + image
        images[0]["alt"] = title
        for extra in images[1:]:
            extra.decompose()
        for comment in card.find_all(string=lambda value: isinstance(value, Comment)):
            comment.extract()
        card.select_one(".c-set-plan-card__price .c-price__text").string = price
        card.select_one(".c-set-plan-card__price .c-price__unit").string = f"(税込)／{unit}"
        note = card.select_one(".c-set-plan-card__main .c-note")
        if note:
            note.decompose()
        cards.append(card)
    plan.select_one(".c-recommend-plan__text").string = "ご希望の清掃箇所に合わせてお選びいただけます。"
    for comment in plan.find_all(string=lambda value: isinstance(value, Comment)):
        comment.extract()
    return slot(plan, "plan")


def washer_lineup(soup: BeautifulSoup) -> list[Tag]:
    """Fill copies of the existing lineup/option cards with washer detail data."""
    water = BeautifulSoup((SOURCE / "water/index.html").read_text(encoding="utf-8"), "html.parser")
    product_template = water.select_one(".c-lineup-product")
    option_template = water.select_one(".c-product-additional-card[data-product-card='option']")
    assert product_template and option_template
    products = []
    illustrations = (BASE + "assets/washer/top-loading-front.png", BRAND_ILLUSTRATIONS + "washing.png", BASE + "assets/washer/drum-dryer-front.png")
    descriptions = (
        "洗濯機本体の外側・内側と脱水槽を、分解を伴わない方法で洗浄します。",
        "ドアパッキンやドラムまわりなど、ドラム式ならではの汚れに対応します。",
        "乾燥機能に関わる部品を分解して清掃する、対象機種限定のサービスです。",
    )
    option_icons = {
        "完全分解洗浄": "washer/top-loading-front.png",
        "日立製": "washer/top-loading-front.png",
        "空気清浄機クリーニング": "room/air-purifier.png",
        "洗濯パン": "washer/top-loading-front.png",
        "かさ上げ台設置": "washer/drum-dryer-front.png",
        "給気口クリーニング": "service-icons/intake-vent.png",
        "給気口クリーニング　フィルター交換付き": "service-icons/vent-filter.png",
    }
    for kind, illustration, description in zip(WASHER_TYPES, illustrations, descriptions):
        source = BeautifulSoup((SOURCE / "washer" / kind / "index.html").read_text(encoding="utf-8"), "html.parser")
        original = source.select_one('[data-product-card="parent"]')
        assert original is not None
        source_id = original.select_one('input[name="product-id"]')["value"]
        product = deepcopy(product_template)
        product["id"] = "product" + source_id
        card = product.select_one('[data-product-card="parent"]')
        card["data-cch-card"] = original["data-cch-card"]
        card["data-cch-variants"] = original["data-cch-variants"]
        card.select_one('input[name="product-id"]')["value"] = source_id
        title = original.select_one(".c-product-card__heading").get_text(" ", strip=True)
        card.select_one(".c-lineup-card__heading a").string = title
        image = card.select_one(".c-lineup-card__image img")
        image["src"] = illustration
        image["alt"] = title
        image["class"] = list(dict.fromkeys(image.get("class", []) + ["cch-wf-washer-photo"]))
        card.select_one(".c-lineup-card__description").string = description
        card.select_one(".c-lineup-card__time-description").string = original.select_one(".c-product-card-list__time").get_text(" ", strip=True) + "／台"
        price = card.select_one(".c-lineup-card__price-item")
        price.clear()
        price.append(deepcopy(original.select_one(".c-product-card-list__price-item").find(recursive=False)))
        options = product.select_one(".c-lineup-options")
        panel = options.select_one(".c-lineup-options__accordion-contents")
        panel["id"] = "lineup-accordion_washer_" + source_id
        options.select_one(".c-lineup-options__accordion-trigger")["aria-controls"] = panel["id"]
        grid = product.select_one(".c-lineup-option-list__contents")
        grid.clear()
        for original_option in source.select('[data-product-card="option"]'):
            option = deepcopy(option_template)
            option["data-cch-card"] = original_option["data-cch-card"]
            option["data-cch-variants"] = original_option["data-cch-variants"]
            option.select_one('input[name="product-id"]')["value"] = original_option.select_one('input[name="product-id"]')["value"]
            name = original_option.select_one(".c-option-card__heading").get_text(" ", strip=True)
            option.select_one(".c-product-additional-card__heading").string = name
            icon_asset = option_icons[name]
            assert (ASSET_SOURCE / icon_asset).exists(), icon_asset
            icon = option.select_one(".c-product-additional-card__image")
            icon["src"] = BASE + "assets/" + icon_asset
            icon["alt"] = name
            icon["class"] = list(dict.fromkeys(icon.get("class", []) + ["cch-wf-service-icon"]))
            option.select_one(".c-additional-option-card__description").string = original_option.select_one(".c-option-card__description").get_text(" ", strip=True)
            option_price = option.select_one(".c-product-additional-card__price")
            option_price.clear()
            option_price.append(deepcopy(original_option.select_one(".c-option-card__price").find(recursive=False)))
            grid.append(option)
        products.append(product)
    return products


def replace_product_photos(lineup: Tag, category: str) -> None:
    """Replace only existing primary product photos; keep product behavior and options."""
    if category == "washer":
        return  # The category has no photographed product cards yet.
    cards = lineup.select('[data-product-card="parent"]')
    layout = PRODUCT_PHOTO_LAYOUT[category]
    assert len(cards) == len(layout), (category, len(cards), len(layout))
    for card, (sheet, col, row, columns, rows) in zip(cards, layout):
        img = card.select_one(".c-lineup-card__image img")
        assert img is not None, (category, card.get("id"))
        x = f"{col * 100 / (columns - 1):g}%" if columns > 1 else "0%"
        y = f"{row * 100 / (rows - 1):g}%" if rows > 1 else "0%"
        label = card.select_one("h3") or card.select_one("h4")
        alt = label.get_text(" ", strip=True) if label else img.get("alt", "商品")
        photo = fragment(BeautifulSoup("", "html.parser"),
            f'<span class="cch-wf-product-photo cch-wf-product-photo--{columns}x{rows}" '
            f'role="img" aria-label="{escape(alt, quote=True)}のイメージ写真" '
            f'style="background-image:url(\'{BASE}assets/{category}/{sheet}\');'
            f'background-position:{x} {y}"></span>')
        img.replace_with(photo)


def replace_service_icons(section: Tag, selector: str) -> None:
    """Replace only plan and option-card icons; leave product/modal photos intact."""
    for icon in section.select(selector):
        source_name = icon.get("src", "").rsplit("/", 1)[-1]
        asset = SERVICE_ICON_ASSETS.get(source_name)
        assert asset is not None, (source_name, section.get("data-wireframe-slot"))
        assert (ASSET_SOURCE / asset).exists(), asset
        icon["src"] = BASE + "assets/" + asset
        icon["class"] = list(dict.fromkeys(icon.get("class", []) + ["cch-wf-service-icon"]))


def replace_service_descriptions(section: Tag, category: str, kind: str) -> None:
    """Rewrite card bodies while keeping headings, non-IP notes and card behavior."""
    selectors = {
        "plan": (".c-plan-card, .c-set-plan-card", ".c-plan-card__heading, .c-set-plan-card__heading", ".c-plan-card__description, .c-set-plan-card__description"),
        "parent": ('[data-product-card="parent"]', ".c-lineup-card__heading", ".c-lineup-card__description"),
        "option": ('[data-product-card="option"]', ".c-product-additional-card__heading", ".c-additional-option-card__description"),
    }
    card_selector, heading_selector, body_selector = selectors[kind]
    copy = SERVICE_COPY.get(category, {}).get(kind, {})
    for card in section.select(card_selector):
        heading = card.select_one(heading_selector)
        body = card.select_one(body_selector)
        if heading is None or body is None or not body.get_text(" ", strip=True):
            continue
        title = re.sub(r"\s+", " ", heading.get_text(" ", strip=True))
        assert title in copy, (category, kind, title)
        new_text = copy[title]
        assert new_text and new_text.endswith("。"), (category, kind, title)
        first_text = next((node for node in body.children if isinstance(node, NavigableString) and node.strip()), None)
        assert first_text is not None, (category, kind, title)
        first_text.replace_with(new_text)
        for node in list(body.children):
            if not isinstance(node, NavigableString) or not node.strip().startswith("※"):
                continue
            if not any(term in node for term in ("登録商標", "商標登録", "特許")):
                continue
            previous = node.previous_sibling
            if isinstance(previous, Tag) and previous.name == "br":
                previous.decompose()
            node.extract()


def remove_ip_notices(section: Tag) -> None:
    """Remove standalone trademark/patent notes from service cards only."""
    for note in section.select(".c-plan-card .c-note, .c-set-plan-card .c-note, [data-product-card='parent'] .c-lineup-card__note"):
        if any(term in note.get_text(" ", strip=True) for term in ("登録商標", "商標登録", "特許")):
            note.decompose()


def remove_ip_catalog_notices(soup: BeautifulSoup) -> None:
    """Keep the local cart catalog usable without stale trademark/patent footnotes."""
    script = soup.select_one("script#shop-catalog")
    if script is None or script.string is None:
        return
    catalog = json.loads(script.string)
    for product in catalog.get("products", []):
        description = product.get("description")
        if not isinstance(description, str):
            continue
        product["description"] = re.sub(r"※[^。]*?(?:登録商標|商標登録|特許)[^。]*。", "", description)
    script.string.replace_with(json.dumps(catalog, ensure_ascii=False))


def unlink_product_details(lineup: Tag) -> None:
    """Keep product-card content and cart controls without copied detail-page links."""
    for card in lineup.select('[data-product-card="parent"]'):
        image_link = card.select_one("a.c-lineup-card__image")
        detail_link = card.select_one("a.c-lineup-card__detail-button")
        heading_link = card.select_one(".c-lineup-card__heading a")
        assert image_link and detail_link and heading_link, card.get("id")
        image_link.name = "div"
        detail_link.name = "button"
        detail_link["type"] = "button"
        heading_link.name = "span"
        for node in (image_link, detail_link, heading_link):
            del node["href"]


def remove_option_details(lineup: Tag) -> list[str]:
    """Remove only self-contained option detail controls and their private dialogs."""
    kept = []
    for card in lineup.select('[data-product-card="option"]'):
        button = card.select_one(".c-product-additional-card__detail-button")
        if button is None:
            continue
        target = button.get("data-target-modal-id")
        dialog = card.find("dialog", id=target) if target else None
        # A shared or externally referenced dialog must stay intact.
        references = lineup.find_all(attrs={"data-target-modal-id": target}) if target else []
        if dialog is None or references != [button]:
            kept.append(card.get("data-cch-card", card.get_text(" ", strip=True)[:40]))
            continue
        button.decompose()
        dialog.decompose()
    return kept


def shorten_option_descriptions(lineup: Tag, category: str) -> None:
    """Keep option copy within three rendered lines; review any new overflow with a human."""
    # Future option copy must fit within three lines even on narrow phones. If that would
    # omit service conditions or require a fourth line, confirm the wording with a human.
    briefs = OPTION_BRIEFS.get(category, {})
    shared_briefs = OPTION_BRIEFS.get("*", {})
    for card in lineup.select('[data-product-card="option"]'):
        title = card.select_one(".c-product-additional-card__heading")
        body = card.select_one(".c-additional-option-card__description")
        if title is None or body is None:
            continue
        heading = re.sub(r"\s+", " ", title.get_text(" ", strip=True))
        key = card.get("data-cch-card") if category == "washer" else heading
        copy = briefs.get(key, shared_briefs.get(heading))
        if copy:
            body.clear()
            body.string = copy


def add_parent_detail_dialogs(soup: BeautifulSoup, lineup: Tag) -> None:
    """Show the demo notice only when a parent product's detail button is opened."""
    # For a real client package, retain the parent detail CTA only when verified special
    # terms, distinctive techniques or rights need explanation. Otherwise remove that CTA
    # and leave only quantity + add-to-cart, preserving product IDs, prices and cart data.
    note = "※デモンストレーションのサンプル表示のため、「詳しく見る」のパッケージはありません。"
    # Keep the exact wording while allowing line breaks only at meaningful phrase boundaries.
    note_markup = ('<span class="cch-wf-parent-detail-dialog__line">'
                   '<span>※デモンストレーションの</span><span>サンプル表示のため、</span></span>'
                   '<span class="cch-wf-parent-detail-dialog__line">'
                   '<span>「詳しく見る」の</span><span>パッケージはありません。</span></span>')
    assert BeautifulSoup(note_markup, "html.parser").get_text() == note
    for index, card in enumerate(lineup.select('[data-product-card="parent"]'), start=1):
        detail = card.select_one(".c-lineup-card__detail-button")
        assert detail is not None and detail.name == "button", card.get("data-cch-card")
        modal_id = f"cch-wf-parent-detail-{index}"
        detail["class"] = [*detail.get("class", []), "js-modal-opener"]
        detail["data-target-modal-id"] = modal_id
        detail["aria-haspopup"] = "dialog"
        detail["aria-controls"] = modal_id
        dialog = fragment(soup, f'''<dialog class="c-modal js-modal cch-wf-parent-detail-dialog" id="{modal_id}" aria-label="詳しく見るについて">
            <div class="c-modal__backdrop js-modal-closer"></div>
            <div class="c-modal__main">
              <button class="c-modal-closer js-modal-closer" type="button" aria-label="閉じる">モーダルを閉じる</button>
              <p class="cch-wf-parent-detail-dialog__message">{note_markup}</p>
            </div>
        </dialog>''')
        card.append(dialog)
    # The imported modal handler unlocks scrolling on its close button, but not on Escape.
    cleanup = soup.new_tag("script")
    cleanup.string = """document.addEventListener('close', function (event) {
      const dialog = event.target;
      if (!dialog.matches || !dialog.matches('.cch-wf-parent-detail-dialog')) return;
      dialog.setAttribute('aria-hidden', 'true');
      if (!document.querySelector('.c-modal[open]')) document.body.classList.remove('is-fixed');
    }, true);"""
    soup.body.append(cleanup)


def enable_outerwall_cart(soup: BeautifulSoup, lineup: Tag) -> None:
    """The imported outer-wall CTA uses an external form, not the local cart."""
    card = next((item for item in lineup.select('[data-product-card="parent"]')
                 if item.select_one(".c-lineup-card__heading").get_text(" ", strip=True) == "外壁手洗い洗浄"), None)
    assert card is not None and not card.get("data-cch-card")
    # The imported source reuses product702 for a later card; give this row a unique anchor.
    card.parent["id"] = "productOuterwall"
    price = int(card.select_one(".c-price__text").get_text(strip=True).replace(",", ""))
    assert price == 44000  # The imported card's base price for one wall of at most 40 m².
    card["data-cch-card"] = "ref-card-outerwall-base"
    card["data-cch-variants"] = '["ref-outerwall-base"]'
    water = BeautifulSoup((SOURCE / "water/index.html").read_text(encoding="utf-8"), "html.parser")
    quantity_template = water.select_one('[data-product-card="parent"] .js-product-quantity')
    assert quantity_template is not None
    cta = card.select_one(".c-lineup-card__foot .js-add-cart")
    assert cta is not None and cta.name == "a"
    cta.insert_before(deepcopy(quantity_template))
    cta.name = "button"
    for attr in ("href", "rel", "target"):
        cta.attrs.pop(attr, None)
    cta["type"] = "button"
    cta.select_one(".c-button__text").string = "カートに追加"
    card.append(fragment(soup, '<input name="product-id" type="hidden" value="outerwall-base">'))
    # The source also states a 990-yen charge for each square metre above 40 m².
    # Copy the same native option accordion/card used by the other product rows.
    options = deepcopy(water.select_one(".c-lineup-product .c-lineup-options"))
    option = deepcopy(water.select_one('.c-product-additional-card[data-product-card="option"]'))
    assert options is not None and option is not None
    panel = options.select_one(".c-lineup-options__accordion-contents")
    panel["id"] = "lineup-accordion_outerwall"
    options.select_one(".c-lineup-options__accordion-trigger")["aria-controls"] = panel["id"]
    option["data-cch-card"] = "ref-card-outerwall-extra-sqm"
    option["data-cch-variants"] = '["ref-outerwall-extra-sqm"]'
    option.select_one('input[name="product-id"]')["value"] = "outerwall-extra-sqm"
    option.select_one(".c-product-additional-card__heading").string = "外壁手洗い洗浄 追加1㎡（40㎡超の部分）"
    option.select_one(".c-additional-option-card__description").string = "外壁1面が40㎡を超える場合、超過面積1㎡ごとの追加料金です。"
    icon = option.select_one(".c-product-additional-card__image")
    icon["src"] = BASE + "assets/others/hero-exterior.png"
    icon["alt"] = "外壁手洗い洗浄"
    icon["class"] = list(dict.fromkeys(icon.get("class", []) + ["cch-wf-service-icon"]))
    option.select_one(".c-product-additional-card__price .c-price__text").string = "990"
    option.select_one(".c-product-additional-card__price .c-price__unit").string = " (税込)／㎡"
    option.select_one(".js-product-quantity")["data-unit"] = "㎡"
    grid = options.select_one(".c-lineup-option-list__contents")
    grid.clear()
    grid.append(option)
    card.parent.append(options)


def ensure_outerwall_catalog(soup: BeautifulSoup) -> None:
    """Keep the newly cart-enabled source item when moving among product pages."""
    script = soup.select_one("script#shop-catalog")
    assert script is not None and script.string
    catalog = json.loads(script.string)
    add_outerwall_products(catalog)
    script.string.replace_with(json.dumps(catalog, ensure_ascii=False))


def add_outerwall_products(catalog: dict, image_base: str = BASE) -> None:
    """Add the outer-wall products to the shared estimate catalog exactly once."""
    known = {product["id"] for product in catalog["products"]}
    additions = [{
        "id": "ref-card-outerwall-base", "category": "reference", "name": "外壁手洗い洗浄",
        "description": "外壁の汚れを確認しながら、専用の器材を使って手洗いで丁寧に洗浄します。",
        "images": [image_base + "assets/others/hero-exterior.png"],
        "variants": [{"id": "ref-outerwall-base", "name": "外壁1面（40㎡以下）", "price": 44000,
                      "unit": "面", "max": 30}],
        "detail": None,
    }, {
        "id": "ref-card-outerwall-extra-sqm", "category": "reference", "name": "外壁手洗い洗浄 追加1㎡（40㎡超の部分）",
        "description": "外壁1面が40㎡を超える場合の追加面積です。",
        "images": [image_base + "assets/others/hero-exterior.png"],
        "variants": [{"id": "ref-outerwall-extra-sqm", "name": "追加1㎡", "price": 990,
                      "unit": "㎡", "max": 30, "requires": "ref-outerwall-base"}],
        "detail": None,
    }]
    catalog["products"].extend(product for product in additions if product["id"] not in known)


def selector(soup: BeautifulSoup, main: Tag, category: str) -> Tag:
    """Use the copied water-page frame with each category's original links and copy."""
    template = BeautifulSoup((SOURCE / "water/index.html").read_text(encoding="utf-8"), "html.parser")
    anchors = template.select_one(".p-page-anchors")
    section = anchors.find_parent(class_="l-section")
    grid = anchors.select_one(".p-page-anchors__cards")
    grid.clear()
    original = main.select(".p-page-anchors .c-page-anchors__anchor")
    assert not original or len(original) == len(SELECTORS[category]), category
    if original:
        for link in original:
            grid.append(deepcopy(link))
    else:
        for label, href in SELECTORS[category]:
            link = fragment(soup, f'<a class="c-category-simple-card c-category-simple-card--icon-down c-page-anchors__anchor" href="{escape(href, quote=True)}"><div class="c-category-simple-card__top"></div><div class="c-category-simple-card__bottom"><h3 class="c-category-simple-card__text">{escape(label)}</h3></div></a>')
            grid.append(link)
    heading = "洗濯機の種類を選ぶ" if category == "washer" else "清掃箇所・サービスを選ぶ"
    anchors.select_one(".p-page-anchors__heading").string = heading
    grid.attrs.pop("tabindex", None)
    grid.attrs.pop("role", None)
    grid.attrs.pop("aria-label", None)
    links = section.select(".c-page-anchors__anchor")
    assert len(links) == len(SELECTOR_IMAGES[category]), category
    for link in links:
        src = SELECTOR_IMAGES[category][link["href"]]
        top = link.select_one(".c-category-simple-card__top")
        assert top is not None
        top.clear()
        image = soup.new_tag("img", src=src, alt="", loading="lazy")
        image["class"] = "cch-wf-location-image"
        top.append(image)
        if not link["href"].startswith("#"):
            link["class"].append("cch-wf-link-card")
    anchors.append(fragment(soup, '<a class="cch-wf-next-section" href="#cch-wf-pain" aria-label="次のセクションへ進む"></a>'))
    return slot(section, "selector")


def hero(soup: BeautifulSoup, main: Tag, category: str) -> Tag:
    image_alts = {
        "aircon": ("hero-cleaning.png", "壁掛けエアコンの内部を養生して洗浄する作業イメージ"),
        "pack": ("hero-living-room.png", "清掃後の明るいリビングとキッチンのイメージ"),
        "water": ("hero-bathroom.png", "清掃後の明るい浴室のイメージ"),
        "washer": ("hero-laundry.png", "清潔なランドリー空間に置かれた正面向きの洗濯機のイメージ"),
        "kitchen": ("hero-kitchen.png", "シンクとコンロを正面から見た清潔なキッチンのイメージ"),
        "room": ("hero-empty-room.png", "床と壁が清潔に整った明るいお部屋のイメージ"),
        "coating": ("hero-washstand.png", "清潔で光沢のある洗面台のイメージ"),
        "others": ("hero-exterior.png", "住宅の外壁を正面から清掃する作業イメージ"),
    }
    if category in image_alts:
        filename, alt = image_alts[category]
        wide_filename = filename.removesuffix(".png") + "-wide.png"
        wide_source = (f'<source media="(min-width: 768px)" '
                       f'srcset="{BASE}assets/{category}/{wide_filename}">') if category != "aircon" else ""
        return fragment(soup, f'<section class="cch-wf-hero cch-wf-hero--{category}" data-wireframe-slot="hero" aria-label="{LABELS[category]}のイメージ画像">'
                        f'<picture>{wide_source}<img src="{BASE}assets/{category}/{filename}" alt="{alt}" fetchpriority="high"></picture></section>')
    return fragment(soup, '<section class="cch-wf-hero" data-wireframe-slot="hero" aria-label="画像または動画の配置位置">'
                    '<div class="cch-wf-media-placeholder"><strong>IMAGE / VIDEO</strong><span>画像・動画を配置する仮の枠</span></div></section>')


def rewrite_draft_links(soup: BeautifulSoup) -> None:
    for link in soup.select('a[href^="/crystal-clean-home/cart/"], a[href^="/crystal-clean-home/estimate/"]'):
        href = link["href"]
        link["href"] = BASE + href.removeprefix("/crystal-clean-home/")
    for link in soup.select('a[href^="/crystal-clean-home/house-cleaning/"]'):
        href = link.get("href", "")
        rest = href.removeprefix("/crystal-clean-home/house-cleaning/")
        category = rest.split("/", 1)[0]
        if category in CATEGORIES:
            link["href"] = BASE + rest
    for link in soup.select('a[data-demo-action="phone"], a[href^="tel:"]'):
        number_line = link.find_parent("p", class_="num")
        (number_line or link).decompose()
    for link in soup.select('a[href*="osoujihonpo.com"], a[href*="iekire.com"]'):
        note = link.find_parent("li")
        if note and "対応している店舗が限られ" in note.get_text():
            note.decompose()
            continue
        link["href"] = "/crystal-clean-home/contact/"
        link.attrs.pop("target", None)
        link.attrs.pop("rel", None)
        if "js-add-cart" in link.get("class", []):
            link["class"] = [name for name in link["class"] if name != "js-add-cart"]


def append_styles(soup: BeautifulSoup) -> None:
    for device, media in (("desktop", "(min-width: 993px)"), ("mobile", "(max-width: 992px)")):
        stylesheet = soup.new_tag("link", rel="stylesheet", href=BASE + f"wireframe-{device}.css?v=" + STYLE_VERSION, media=media)
        soup.head.append(stylesheet)
    soup.html["data-product-wireframe"] = "true"


def issue_card_list(heading: str, worries: tuple[str, ...] | list[str]) -> Tag:
    pack = BeautifulSoup((SOURCE / "pack/index.html").read_text(encoding="utf-8"), "html.parser")
    cards = pack.select_one(".c-issue-list")
    assert cards is not None
    for comment in cards.find_all(string=lambda node: isinstance(node, Comment)):
        comment.extract()
    card_texts = cards.select(".c-issue-card__text")
    assert len(card_texts) == len(worries) == 3
    cards.select_one(".c-issue-list__heading").string = heading
    for text_node, worry in zip(card_texts, worries):
        text_node.string = worry
    return cards.extract()


def aircon_issue_as_cards(issue: Tag) -> None:
    """Use the pack page's issue-card pattern without altering either source copy."""
    feature_grid = issue.select_one(".p-cleaning-menu__contents")
    heading = issue.select_one(".p-content-box__heading")
    assert feature_grid is not None and heading is not None
    worries = []
    for feature in feature_grid.select(".c-feature__heading"):
        label = deepcopy(feature)
        for line_break in label.select("br"):
            line_break.replace_with(" ")
        worries.append(re.sub(r"\s+", " ", label.get_text()).strip())
    assert len(worries) == 3

    content_box = heading.find_parent(class_="p-content-box")
    assert content_box is not None
    content_box.insert_before(issue_card_list(heading.get_text(strip=True), worries))
    heading.decompose()
    feature_grid.decompose()
    for anchor_nav in issue.select(".anchor-nav"):
        anchor_nav.decompose()


def add_issue_followup(soup: BeautifulSoup, issue: Tag, category: str) -> None:
    cards = issue.select_one(".c-issue-list")
    assert cards is not None and category in ISSUE_FOLLOWUPS, category
    explanation, closing = ISSUE_FOLLOWUPS[category]
    followup = fragment(soup, '<div class="p-content-box cch-wf-issue-followup">'
        f'<p>{escape(explanation)}</p>'
        f'<h3 class="c-heading-level-3 p-content-box__heading">{escape(closing)}</h3>'
        '<a class="c-button c-button--large c-button--fill-red p-content-box__button" href="#apply">'
        '<span class="c-button__text">お見積り（無料）はこちら</span>'
        '<span class="c-icon c-icon--caret-down c-button__icon" aria-hidden="true"></span>'
        '</a></div>')
    cards.insert_after(followup)


def review_cards(category: str, original_id: str | None) -> Tag:
    """Reuse the copied pack review layout with clearly marked sample copy."""
    pack = BeautifulSoup((SOURCE / "pack/index.html").read_text(encoding="utf-8"), "html.parser")
    section = source_section(pack.select_one(".cch-reference main"), "ご利用いただいたお客様の声")
    assert section is not None
    section = slot(section.extract(), "reviews")
    section["id"] = original_id or "review"
    for comment in section.find_all(string=lambda node: isinstance(node, Comment)):
        comment.extract()
    heading = section.select_one(".p-content-box__heading")
    intro = section.select_one("p.tac")
    grid = section.select_one(".c-grid")
    assert heading and intro and grid
    heading.string = "ご利用いただいたお客様の声"
    intro.string = "掲載用サンプル文です。実際のお客様の口コミではありません。"
    intro["class"] = ["tac", "mt10", "cch-wf-review-notice"]
    grid.clear()
    entries = REVIEW_COPY[category]
    assert len(entries) == 6, category
    for title, body in entries:
        card = fragment(pack, '<div class="c-voice-card cch-wf-voice-card">'
            '<img class="cch-wf-voice-logo" src="/crystal-clean-home/wp/wp-content/themes/original_theme/img/logo.svg" alt="クリスタルクリーンホーム" loading="lazy">'
            f'<h3 class="c-voice-card__heading">{escape(title)}</h3>'
            f'<p class="c-voice-card__text">{escape(body)}</p></div>')
        grid.append(card)
    return section


def faq_cards(category: str, original_id: str | None) -> Tag:
    """Keep the copied accordion controls, replacing all third-party answers."""
    water = BeautifulSoup((SOURCE / "water/index.html").read_text(encoding="utf-8"), "html.parser")
    section = source_section(water.select_one(".cch-reference main"), "よくある質問")
    assert section is not None
    section = slot(section.extract(), "faq")
    section["id"] = original_id or "faq"
    for comment in section.find_all(string=lambda node: isinstance(node, Comment)):
        comment.extract()
    heading = section.select_one(".p-content-box__heading")
    accordion = section.select_one(".c-faq-accordion")
    assert heading and accordion
    heading.string = f"{LABELS[category]}に関するよくある質問"
    notice = fragment(water, '<p class="cch-wf-faq-notice">回答は構成確認用の案です。受付条件・支払い方法は公開前に確認します。</p>')
    heading.insert_after(notice)
    items = accordion.select(":scope > .c-faq-accordion__item")
    assert len(items) == 5
    entries = [
        ("どのような支払い方法を利用できますか？", "現金、Visa・Mastercardのクレジットカード、電子決済を予定しています。電子決済の種類や最終的な受付可否は、公開前に確認してご案内します。"),
        ("見積り以外の費用が必要になる場合はありますか？", "設備の状態や追加の作業範囲によって費用が変わる場合は、作業前に内容と金額を確認します。出張・駐車に関する条件もお見積り時にご案内します。"),
        *FAQ_COPY[category],
    ]
    assert len(entries) == 5, category
    for index, (item, (question, answer)) in enumerate(zip(items, entries), 1):
        answer_id = f"faq-{category}-{index:02d}"
        trigger = item.select_one(".c-faq-accordion__trigger")
        content = item.select_one(".c-faq-accordion__content")
        answer_text = content.select_one(".c-faq-accordion__text") if content else None
        assert trigger and content and answer_text
        trigger.string = question
        trigger["aria-controls"] = answer_id
        content["id"] = answer_id
        answer_text.clear()
        answer_text.string = answer
    for empty_link_container in section.select(".p-content-box__link-container"):
        if not empty_link_container.get_text(strip=True) and not empty_link_container.find(True):
            empty_link_container.decompose()
    return section


def common_flow() -> Tag:
    """Use one copied step-list frame and one source of copy for every category."""
    original = BeautifulSoup((SOURCE / "aircon/index.html").read_text(encoding="utf-8"), "html.parser")
    section = original.select_one("#flow")
    assert section is not None
    section = slot(section.extract(), "flow")
    section["class"] = [*section.get("class", []), "cch-wf-flow"]
    heading = section.select_one(".p-content-box__heading")
    assert heading is not None
    heading.clear()
    heading.string = "ご利用・お支払いまでの流れ"
    items = section.select(".c-step-list__item")
    assert len(items) == len(FLOW_COPY) == 5
    for index, (item, entry) in enumerate(zip(items, FLOW_COPY), 1):
        item.select_one(".c-step-list-item__heading-step").string = f"STEP {index:02d}"
        item.select_one(".c-step-list-item__heading-main").string = entry["heading"]
        item.select_one(".c-step-list-item__text p").string = entry["body"]
        icon_box = item.select_one(".c-step-list-item__icon-box")
        icon_box.clear()
        icon_box.append(fragment(original, f'<img class="cch-wf-flow-icon" src="{BASE}assets/flow/{entry["icon"]}" alt="" loading="lazy">'))
        note = item.select_one(".c-step-list-item__note")
        if note:
            note.decompose()
    note = fragment(original, '<p class="cch-wf-flow-note">ご利用条件とお支払い方法は、公開前に確認してご案内します。このワイヤーフレームから実際の予約・送信はできません。</p>')
    section.select_one(".c-step-list").insert_after(note)
    return section


def category_page(category: str) -> tuple[str, dict]:
    source = SOURCE / category / "index.html"
    html = source.read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "html.parser")
    main = soup.select_one(".cch-reference main")
    assert main is not None
    card_count = len(main.select(".js-product-card"))
    heading = main.find("h1", recursive=False)
    floating = main.select_one("#js-floating")
    dialog = main.select_one("#add-cart-modal")
    cross = source_section(main, "クリスタルクリーンホームのハウスクリーニング")
    if cross is None:
        cross_soup = BeautifulSoup((SOURCE / "aircon/index.html").read_text(encoding="utf-8"), "html.parser")
        cross = source_section(cross_soup.select_one(".cch-reference main"), "クリスタルクリーンホームのハウスクリーニング")
    issue = main.select_one(":scope > .l-section--blue-wave") if category != "washer" else None
    if category == "aircon" and issue:
        aircon_issue_as_cards(issue)
    proof = None
    if issue and issue.select_one(".c-compare-image"):
        proof = issue
    else:
        compare = main.select_one(".c-compare-image")
        proof = nearest_section(compare) if compare else None
    plans = []
    for plan in main.select(".recommend-plan, .c-recommend-plan"):
        outer = plan.find_parent("section", id="plan") or plan
        if outer not in plans:
            plans.append(outer)
    reviews = source_section(main, "ご利用いただいたお客様の声")
    faq = source_section(main, "よくある質問")
    flow = source_section(main, "ご利用までの流れ")
    lineup_selector = ".c-lineup-heading, .c-lineup-products, .c-lineup-issue"
    if category == "coating":
        lineup_selector += ", h2.category-heading, .coating-contents"
    lineup_nodes = [node for node in main.select(lineup_selector) if not node.find_parent(class_="c-recommend-plan")]
    for nested in list(lineup_nodes):
        if any(parent is not nested and nested in parent.descendants for parent in lineup_nodes):
            lineup_nodes.remove(nested)
    banner = hero(soup, main, category)
    new_main = soup.new_tag("main")
    first_view = soup.new_tag("div", attrs={"class": "cch-wf-first-view"})
    first_view.append(banner)
    if heading:
        first_view.append(heading.extract())
    else:
        first_view.append(fragment(soup, f'<h1 class="c-page-heading">{LABELS[category]}</h1>'))
    first_view.append(selector(soup, main, category))
    new_main.append(first_view)
    pain_section = slot(issue.extract(), "pain" + (" proof" if issue is proof else "")) if issue else placeholder(soup, category, "pain")
    if proof is issue and proof is not None:
        replace_compare_photos(pain_section, category)
    pain_section["id"] = "cch-wf-pain"
    if category != "aircon":
        add_issue_followup(soup, pain_section, category)
    new_main.append(pain_section)
    if proof and proof is not issue:
        proof_section = slot(proof.extract(), "proof")
        replace_compare_photos(proof_section, category)
        new_main.append(proof_section)
    elif proof is None:
        new_main.append(completed_proof(soup, category) if category in {"washer", "others", "coating"} else placeholder(soup, category, "proof"))
    if plans:
        for plan in plans:
            plan_section = slot(plan.extract(), "plan")
            replace_service_icons(plan_section, "img")
            replace_service_descriptions(plan_section, category, "plan")
            remove_ip_notices(plan_section)
            new_main.append(plan_section)
    else:
        new_main.append(completed_plan(soup, category) if category in {"washer", "others", "coating"} else placeholder(soup, category, "plan"))
    lineup = fragment(soup, '<section class="cch-wf-lineup" data-wireframe-slot="lineup" id="apply"><div class="cch-wf-section-heading"><h2>サービス・商品一覧</h2><p>各商品の概要とオプションを続けて確認できます。</p></div></section>')
    for node in lineup_nodes:
        lineup.append(node.extract())
    for heading_image in lineup.select(".c-lineup-heading__image"):
        heading_image.decompose()
    replace_product_photos(lineup, category)
    replace_service_icons(lineup, "img.c-product-additional-card__image")
    replace_service_descriptions(lineup, category, "parent")
    replace_service_descriptions(lineup, category, "option")
    remove_ip_notices(lineup)
    unlink_product_details(lineup)
    if category == "others":
        enable_outerwall_cart(soup, lineup)
    if category == "washer":
        for (anchor, heading), product in zip(WASHER_LINEUP, washer_lineup(soup)):
            lineup.append(fragment(soup,
                f'<h2 class="c-lineup-heading" id="{anchor}">'
                f'<span class="c-lineup-heading__contain">{escape(heading)}'
                '<span class="c-lineup-heading__sub-text">LINEUP</span></span></h2>'))
            products = fragment(soup, '<div class="c-lineup-products js-products"></div>')
            products.append(product)
            lineup.append(products)
        unlink_product_details(lineup)
    kept_option_details = remove_option_details(lineup)
    shorten_option_descriptions(lineup, category)
    add_parent_detail_dialogs(soup, lineup)
    new_main.append(lineup)
    new_main.append(review_cards(category, reviews.get("id") if reviews else None))
    new_main.append(faq_cards(category, faq.get("id") if faq else None))
    new_main.append(common_flow())
    if cross:
        cross = slot(cross.extract(), "cross-sell")
        menu_index_links = [link for link in cross.select(".p-content-box__link-container > a.c-icon-link-text")
                            if link.get_text(strip=True).startswith("ハウスクリーニングのメニュー一覧はこちら")]
        for link in menu_index_links:
            link.parent.decompose()
        new_main.append(cross)
    if floating:
        new_main.append(floating.extract())
    if dialog:
        new_main.append(dialog.extract())
    # The first-view link already marks the transition into pain. Keep the
    # existing bubble arrows; fill only major section starts that lack one.
    seen_plan = False
    for section in new_main.find_all(recursive=False):
        kind = section.get("data-wireframe-slot")
        if kind not in {"proof", "plan", "lineup", "cross-sell"}:
            continue
        if kind == "plan":
            if seen_plan:
                continue
            seen_plan = True
        if "l-section--blue-bubbles" not in section.get("class", []):
            section["class"] = [*section.get("class", []), "cch-wf-arrow-boundary"]
    main.replace_with(new_main)
    ensure_outerwall_catalog(soup)
    remove_ip_catalog_notices(soup)
    append_styles(soup)
    rewrite_draft_links(soup)
    result = str(soup)
    preview_count = len(BeautifulSoup(result, "html.parser").select(".cch-reference main .js-product-card"))
    added_cards = (18 if category == "washer" else 0) + (2 if category in CURATED_PLANS else 0) + (1 if category == "others" else 0)
    assert preview_count == card_count + added_cards, (category, card_count, preview_count)
    return result, {"cards": card_count, "slots": [el.get("data-wireframe-slot") for el in new_main.select("[data-wireframe-slot]")], "sha256": hashlib.sha256(source.read_bytes()).hexdigest(), "kept_option_details": kept_option_details}
