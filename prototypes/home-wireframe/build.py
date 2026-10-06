"""Build a review-only HOME copy from the current published source."""
from pathlib import Path
from hashlib import sha256
import json
import re

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
SITE = ROOT / "source" / "site"

BANNERS = [
    {
        "key": "aircon",
        "label": "まとめてお得に",
        "title": ["エアコン２台、", "まとめてお得に。"],
        "description": "",
        "image": "/assets/images/cleaning-illustrations/aircon.png",
        "link": "/house-cleaning/aircon/",
        "action": "まとめて頼む料金を見る",
    },
    {
        "key": "coating",
        "label": "お掃除の、その先へ",
        "title": ["日々の手入れを、", "もっとしやすく。"],
        "description": "水まわりや床の表面を整える、コーティングのご案内。",
        "image": "/assets/images/cleaning-illustrations/coating.png",
        "link": "/house-cleaning/coating/",
        "action": "コーティングを詳しく見る",
    },
    {
        "key": "pack",
        "label": "新生活の準備に",
        "title": ["引越しの前後に、", "住まいを整える。"],
        "description": "お荷物の搬出後・入居前に、住まいのお掃除をまとめて。",
        "image": "/assets/images/cleaning-illustrations/pack.png",
        "link": "/house-cleaning/pack/",
        "action": "引越し前後のお掃除を見る",
    },
]

NEWS = [
    {"id": "hours", "date": "20XX.XX.XX", "category": "営業案内", "title": "営業日・受付時間のご案内", "summary": "営業日・受付時間についてお知らせします。", "body": "営業日・受付時間に関するお知らせの掲載例です。正式な日付と本文は、運用時に登録します。"},
    {"id": "services", "date": "20XX.XX.XX", "category": "サービス", "title": "サービス内容の更新について", "summary": "対応メニューの変更点をご案内します。", "body": "サービス内容の更新を伝えるための掲載例です。正式な変更内容と適用日は、運用時に登録します。"},
    {"id": "information", "date": "20XX.XX.XX", "category": "お知らせ", "title": "見積もりに関するご案内", "summary": "見積もり受付についてお知らせします。", "body": "見積もり受付についての掲載例です。実際の案内内容は、運用時に登録します。"},
]

SECTIONS = [
    ("pickup", "特集枠", "暮らしに合わせたお掃除特集", [("A", "横長バナー・１訴求"), ("B", "手動スライド・３訴求"), ("C", "大小バナー・３訴求")]),
    ("news", "追加セクション", "最新のお知らせ", [("A", "日付・見出しの一覧"), ("B", "注目１件＋ほか２件"), ("C", "３枚のカード")]),
]


def section(key, number, title, variants):
    curve = '<span aria-hidden="true" class="c-section-curve c-section-curve--up" style="--curve-color:#e3f1fc;"></span>' if key == "news" else ""
    extra = " c-curved-section c-curved-section--up" if key == "news" else ""
    note = '<p class="wf-news-draft">表示例・仮原稿（日付と内容は未確定）</p>' if key == "news" else ""
    label = "NEWS" if key == "news" else "PICK UP"
    buttons = "".join(f'<button type="button" data-wf-choice="{letter}" aria-pressed="{str(letter == "A").lower()}" aria-controls="wf-{key}-{letter}"><b>{letter}</b> {label}</button>' for letter, label in variants)
    return f'''<section class="wf-section wf-section--{key}{extra}" id="wf-{key}" data-wf-section="{key}" aria-labelledby="wf-{key}-title">{curve}
<div class="wf-container">
<div class="wf-review wf-section-review"><span>{number}・形の比較</span><div class="wf-options" role="group" aria-label="{title}の３案">{buttons}</div></div>
<header class="wf-section-heading"><span>{label}</span><h2 id="wf-{key}-title">{title}</h2></header>{note}
<div data-wf-panels="{key}"></div>
</div></section>'''


def build():
    original = (SITE / "index.html").read_text(encoding="utf-8")
    catalogue_text = (SITE / "assets/js/cart-catalogue.js").read_text(encoding="utf-8")
    catalogue = json.loads(catalogue_text.split("=", 1)[1].strip().rstrip(";"))
    product = catalogue["items"]["product:1"]
    assert product["tiers"][0]["price"] > next(t["price"] for t in product["tiers"] if t["min"] == 2)
    data = {"banners": BANNERS, "news": NEWS}
    for asset in [banner["image"] for banner in BANNERS]:
        assert (SITE / asset.lstrip("/")).is_file(), asset
    for route in [banner["link"] for banner in BANNERS]:
        assert (SITE / route.lstrip("/") / "index.html").is_file(), route
    additions = {row[0]: section(*row) for row in SECTIONS}
    page = original.replace("<title>Crystal Clean Home</title>", "<title>HOME ワイヤーフレーム比較 | Crystal Clean Home</title>")
    page = re.sub(r"<title>.*?</title>", "<title>HOME ワイヤーフレーム比較 | Crystal Clean Home</title>", page, count=1)
    page = page.replace("</head>", '<meta name="robots" content="noindex,nofollow">\n<link rel="stylesheet" href="/home-wireframe/wireframe.css">\n<script src="/home-wireframe/wireframe.js" defer></script>\n</head>', 1)
    page = page.replace('<body class="c-home">', '<body class="c-home wf-prototype wf-hide-floating">', 1)
    intro = '''<div class="wf-review wf-review-intro" id="wf-review-start"><div class="wf-container">
<p class="wf-review-tag">HOME 複製・ワイヤーフレーム比較</p><h1>最新のお知らせ・３パターンの比較。</h1>
<p>既存バナーを残し、お悩み・ご要望別と末尾の８項目の間に、お知らせの枠を追加しています。</p>
<div class="wf-review-actions"><button type="button" data-wf-clean>比較表示を隠す</button><button type="button" data-wf-floating aria-pressed="false">固定見積もりを表示</button></div>
<nav aria-label="比較画面の移動"><a href="#wf-news">お知らせの３案へ</a><a href="#wf-pickup">特集バナーの３案へ</a><a href="/">現在のホーム</a></nav>
<p class="wf-review-note">ローカルの検討用画面です。お知らせの原稿・掲載日は仮です。案の採用と公開は未決定です。固定見積もりは上のボタンで表示できます。</p>
</div></div>'''
    selector = re.search(r'<section\b[^>]*id="home-cleaning-list"[^>]*>', page)
    assert selector
    page = page[:selector.start()] + intro + additions["pickup"] + "\n" + page[selector.start():]
    bottom = re.search(r'<section\b[^>]*class="[^"]*c-featured-cleaning[^>]*>', page)
    assert bottom
    page = page[:bottom.start()] + additions["news"] + "\n" + page[bottom.start():]
    encoded = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    page = page.replace("</body>", f'<script type="application/json" id="wf-data">{encoded}</script>\n<dialog class="wf-news-dialog" aria-labelledby="wf-news-dialog-title"><button type="button" class="wf-news-close" data-wf-news-close aria-label="お知らせを閉じる">×</button><div data-wf-news-detail></div></dialog>\n<button type="button" class="wf-review-return" data-wf-return hidden>比較表示を戻す</button>\n</body>', 1)
    preserved = {}
    for name, pattern in {
        "sharedHeader": r'<header class="c-header">.*?</header>',
        "sharedFooter": r'<footer\b.*?</footer>',
        "videoSection": r'<section\b[^>]*class="home-first-view".*?</section>',
        "topEightCategories": r'<section\b[^>]*id="home-cleaning-list".*?</section>',
        "guideBanners": r'<section\b[^>]*class="[^"]*home-first-guide-section[^>]*>.*?</section>',
        "reasons": r'<section\b[^>]*id="home-reasons".*?</section>',
        "concerns": r'<section\b[^>]*id="tab-panel_02".*?</section>',
        "bottomEightCategories": r'<section\b[^>]*class="[^"]*c-featured-cleaning[^>]*>.*?</section>',
    }.items():
        match = re.search(pattern, original, re.DOTALL)
        assert match and match.group(0) in page, name
        preserved[name] = True
    (HERE / "index.html").write_text(page, encoding="utf-8", newline="\n")
    (HERE / "build-info.json").write_text(json.dumps({"source": "source/site/index.html", "sourceSha256": sha256((SITE / "index.html").read_bytes()).hexdigest(), "sections": [row[0] for row in SECTIONS], "variantsPerSection": 3, "assetsCopied": 0, "preservedMarkup": preserved, "newLinksAndAssetsExist": True}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print("Built HOME copy: existing banners preserved; three news layouts added before the bottom categories.")


if __name__ == "__main__":
    build()
