"""Build a review-only HOME copy from the current published source."""
from pathlib import Path
from hashlib import sha256
import json
import re

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
SITE = ROOT / "source" / "site"

GUIDES = [
    {
        "eyebrow": "エアコンを選ぶ前に",
        "title": "機種と洗浄範囲で選ぶ",
        "description": "壁掛け・天井埋め込み、お掃除機能の有無を確認。通常の洗浄と完全分解洗浄の内容を見比べます。",
        "image": "/assets/images/cleaning-illustrations/aircon-disassembly.png",
        "alt": "分解した壁掛けエアコン",
        "points": ["エアコンのタイプ", "お掃除機能の有無", "洗浄する範囲"],
        "link": "/house-cleaning/aircon/",
        "action": "エアコンの内容・料金を見る",
    },
    {
        "eyebrow": "水まわり・キッチンを選ぶ前に",
        "title": "気になる場所から絞る",
        "description": "浴室のカビ、換気扇の油汚れ、シンクの水アカ。お掃除したい場所と、各メニューの対象範囲を確認します。",
        "image": "/assets/images/cleaning-illustrations/kitchen.png",
        "alt": "キッチンとレンジフード",
        "points": ["汚れが気になる場所", "清掃の対象範囲", "追加したいオプション"],
        "link": "/house-cleaning/kitchen/",
        "action": "キッチンの内容・料金を見る",
        "extraLink": "/house-cleaning/water/",
        "extraAction": "水まわりの内容・料金を見る",
    },
    {
        "eyebrow": "まとめて頼みたい方へ",
        "title": "暮らしの場面で選ぶ",
        "description": "引越し前・後のお掃除か、住みながらのお掃除か。パックサービスの違いから、ご希望に合う内容を選びます。",
        "image": "/assets/images/cleaning-illustrations/pack.png",
        "alt": "住まい全体のパックサービス",
        "points": ["引越し前・後", "在宅のお掃除", "まとめて頼む範囲"],
        "link": "/house-cleaning/pack/",
        "action": "パックサービスを見る",
    },
]

STEPS = [
    {"title": "内容を選んで試算", "text": "メニュー・数量・オプションを選び、見積もり金額を確認します。", "note": "まずは予算の目安を確認", "link": "/quick_cart/", "action": "シミュレーションへ"},
    {"title": "見積もり内容を確認", "text": "選んだ内容と合計を見直し、ご予算に合わせて数量やメニューを調整します。", "note": "追加・削除して見直せます", "link": "/cart/", "action": "見積もりの確認へ"},
    {"title": "ご希望を送信", "text": "お客様情報・作業先・ご希望を入力し、内容を確かめて見積もりを送信します。", "note": "希望内容をスタッフへ", "link": None, "action": None},
    {"title": "スタッフが現地へ", "text": "スタッフと訪問について相談し、現地で設置状況や作業範囲を確認します。", "note": "現地の状況も一緒に確認", "link": None, "action": None},
]

SECTIONS = [
    ("choose", "01", "メニュー選びを、もう少し分かりやすく。", "気になるサービスの違いを確認してから、内容と料金を見比べられます。", [("A", "大小の読み物"), ("B", "番号付きの横一覧"), ("C", "開いて読む案内")]),
    ("budget", "02", "頼みたいお掃除、いくらになる？", "代表的な３メニューで、数量を変えながら予算の目安を確かめられます。", [("A", "選択タイル＋合計帯"), ("B", "一覧＋明細"), ("C", "展開式＋結果パネル")]),
    ("flow", "03", "試算してから、スタッフの訪問まで。", "予算が合ったら見積もりへ。次に何をするかを、順番にご案内します。", [("A", "横につながる４段階"), ("B", "交互のタイムライン"), ("C", "お客様とスタッフの２面")]),
]


def section(key, number, title, description, variants):
    buttons = "".join(f'<button type="button" data-wf-choice="{letter}" aria-pressed="{str(letter == "A").lower()}" aria-controls="wf-{key}-{letter}"><b>{letter}</b> {label}</button>' for letter, label in variants)
    return f'''<section class="wf-section wf-section--{key}" id="wf-{key}" data-wf-section="{key}" aria-labelledby="wf-{key}-title">
<div class="wf-container">
<div class="wf-review wf-section-review"><span>追加セクション {number}・形の比較</span><div class="wf-options" role="group" aria-label="{title}の３案">{buttons}</div></div>
<header class="wf-heading"><span class="wf-kicker">{number}</span><div><h2 id="wf-{key}-title">{title}</h2><p>{description}</p></div></header>
<div data-wf-panels="{key}"></div>
</div></section>'''


def build():
    original = (SITE / "index.html").read_text(encoding="utf-8")
    catalogue_text = (SITE / "assets/js/cart-catalogue.js").read_text(encoding="utf-8")
    catalogue = json.loads(catalogue_text.split("=", 1)[1].strip().rstrip(";"))
    product_keys = ["product:1", "product:4", "product:666"]
    for key in product_keys:
        assert key in catalogue["items"]
    data = {"guides": GUIDES, "steps": STEPS, "productKeys": product_keys}
    for asset in [guide["image"] for guide in GUIDES] + [catalogue["items"][key]["image"] for key in product_keys]:
        assert (SITE / asset.lstrip("/")).is_file(), asset
    for route in [guide["link"] for guide in GUIDES] + ["/house-cleaning/water/", "/quick_cart/", "/cart/"]:
        assert (SITE / route.lstrip("/") / "index.html").is_file(), route
    additions = {row[0]: section(*row) for row in SECTIONS}
    page = original.replace("<title>Crystal Clean Home</title>", "<title>HOME ワイヤーフレーム比較 | Crystal Clean Home</title>")
    page = re.sub(r"<title>.*?</title>", "<title>HOME ワイヤーフレーム比較 | Crystal Clean Home</title>", page, count=1)
    page = page.replace("</head>", '<meta name="robots" content="noindex,nofollow">\n<link rel="stylesheet" href="/home-wireframe/wireframe.css">\n<script src="/home-wireframe/wireframe.js" defer></script>\n</head>', 1)
    page = page.replace('<body class="c-home">', '<body class="c-home wf-prototype wf-hide-floating">', 1)
    intro = '''<div class="wf-review wf-review-intro" id="wf-review-start"><div class="wf-container">
<p class="wf-review-tag">HOME 複製・ワイヤーフレーム比較</p><h1>既存のホームに、選ぶ・試算する・依頼する導線を追加。</h1>
<p>追加した３セクションを、それぞれＡ／Ｂ／Ｃで比較できます。各セクションで違う案を選んでも構いません。</p>
<div class="wf-review-actions"><div class="wf-presets" role="group" aria-label="まとめて比較"><button type="button" data-wf-preset="A">全体をＡ案に</button><button type="button" data-wf-preset="B">全体をＢ案に</button><button type="button" data-wf-preset="C">全体をＣ案に</button></div><button type="button" data-wf-clean>比較表示を隠す</button><button type="button" data-wf-floating aria-pressed="false">固定見積もりを表示</button></div>
<nav aria-label="追加セクションへ移動"><a href="#wf-choose">01 メニュー選び</a><a href="#wf-budget">02 予算の試算</a><a href="#wf-flow">03 訪問まで</a><a href="/">現在のホーム</a></nav>
<p class="wf-review-note">ローカルの検討用画面です。既存のホームは保持しています。比較しやすいよう固定見積もりを隠していますが、上のボタンで表示できます。訪問までの案内は予定する導線で、現在の見積もり機能は入力・確認までです。</p>
</div></div>'''
    selector = re.search(r'<section\b[^>]*id="home-cleaning-list"[^>]*>', page)
    assert selector
    page = page[:selector.start()] + intro + page[selector.start():]
    concerns = re.search(r'<section\b[^>]*id="tab-panel_02"[^>]*>', page)
    assert concerns
    page = page[:concerns.start()] + additions["choose"] + "\n" + page[concerns.start():]
    featured = re.search(r'<section\b[^>]*class="[^"]*c-featured-cleaning[^>]*>', page)
    assert featured
    page = page[:featured.start()] + additions["budget"] + "\n" + additions["flow"] + "\n" + page[featured.start():]
    encoded = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    page = page.replace("</body>", f'<script type="application/json" id="wf-data">{encoded}</script>\n<button type="button" class="wf-review-return" data-wf-return hidden>比較表示を戻す</button>\n</body>', 1)
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
    print("Built HOME copy: 3 new sections, 3 alternatives each; existing assets referenced.")


if __name__ == "__main__":
    build()
