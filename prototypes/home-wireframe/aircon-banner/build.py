"""Build three local banner proposals using the existing aircon price source."""
from pathlib import Path
from hashlib import sha256
from html import escape
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'tools'))
from bs4 import BeautifulSoup
from build_cart_catalogue import prices

BASE = '/home-wireframe/aircon-banner/'
DESTINATION = '/house-cleaning/aircon/'
VARIANTS = (
    ('A', '4,400円お得！が主役', '最大サイズのお得額と黄色×青で、３案の中で最も強く目を引く販促型。'),
    ('B', '11,000円を一番に', '１台あたりの料金を圧倒的に大きく見せ、料金理解を最優先。'),
    ('C', '２台まとめて、お得にキレイ！', '大きな２台の文字に、リビング・寝室の親しみを添えた販促型。'),
)
CTA = 'エアコンクリーニングの料金を見る'


def pricing():
    data = json.loads((ROOT / 'source/service-pages/catalogue.json').read_text(encoding='utf-8'))
    product = BeautifulSoup(data['products']['1']['html'], 'html.parser')
    tiers = prices(product.select_one('.c-lineup-card__price'))['tiers']
    single = next(t['price'] for t in tiers if t['min'] == 1)
    multiple = next(t['price'] for t in tiers if t['min'] == 2)
    return dict(single=single, multiple=multiple, saving=single-multiple,
                total=multiple*2, totalSaving=(single-multiple)*2)


def banner(letter, p, prefix):
    condition = '壁掛けタイプ（お掃除機能なし）／同時に２台以上のご注文時／税込'
    art = f'<img class="ab-art" src="{BASE}assets/aircon-pair.png" width="1536" height="1024" alt="" decoding="async" loading="lazy">'
    action = '<span class="ab-action"><span class="ab-action-text"><span>エアコンクリーニングの</span><span>料金を見る</span></span><span class="ab-action-arrow" aria-hidden="true">→</span></span>'
    note = f'<p id="{prefix}-condition" class="ab-condition">{condition}</p>'
    category = '<p class="ab-tag">エアコンクリーニング</p>'
    if letter == 'A':
        copy = f'''<div class="ab-copy">{category}<span class="ab-promo">まとめてお得</span>
<h3 id="{prefix}-title" class="ab-title"><span class="ab-title-lead">２台まとめて</span><span class="ab-offer"><strong class="ab-main-number">{p['totalSaving']:,}</strong><span class="ab-offer-ending"><span>円</span><b>お得！</b></span></span></h3>
<p class="ab-support">１台あたり{p['saving']:,}円お得</p>{action}{note}</div>
<div class="ab-visual" aria-hidden="true"><span class="ab-visual-shape"></span>{art}<span class="ab-deco-star ab-deco-star--one"></span><span class="ab-deco-star ab-deco-star--two"></span></div>'''
    elif letter == 'B':
        copy = f'''<div class="ab-copy">{category}<span class="ab-promo">２台以上でお得</span>
<h3 id="{prefix}-title" class="ab-title"><span class="ab-title-lead">２台以上なら</span><span class="ab-unit-label">１台あたり</span><span class="ab-offer"><strong class="ab-main-number">{p['multiple']:,}</strong><span class="ab-offer-ending"><span>円</span><small>税込</small></span></span></h3>
<p class="ab-support">２台合計 <strong>{p['total']:,}円</strong>（税込）</p>{action}{note}</div>
<div class="ab-visual" aria-hidden="true"><span class="ab-visual-shape"></span>{art}<span class="ab-deco-star ab-deco-star--one"></span></div>'''
    else:
        copy = f'''<div class="ab-copy">{category}<span class="ab-promo">まとめてお得</span>
<h3 id="{prefix}-title" class="ab-title"><span class="ab-title-line"><strong class="ab-count">２台</strong><span>まとめて、</span></span><span class="ab-title-line ab-life-message">お得にキレイ！</span></h3>
<p class="ab-life-note">リビングも、寝室も。</p><p class="ab-support">２台合計 <strong>{p['total']:,}<span>円</span></strong><small>税込</small></p>{action}{note}</div>
<div class="ab-visual" aria-hidden="true"><span class="ab-visual-shape"></span>{art}<span class="ab-room ab-room--living">リビング</span><span class="ab-room ab-room--bed">寝室</span><span class="ab-deco-star ab-deco-star--one"></span></div>'''
    return f'''<a class="ab-banner ab-banner--{letter.lower()}" href="{DESTINATION}" aria-labelledby="{prefix}-title" aria-describedby="{prefix}-condition">
{copy}</a>'''


def design_notes(letter, p):
    common_structure = 'a要素全体をリンクにし、CSS Gridで左64％／右36％。左はラベル→h3→価格補足→CTA→条件、右は文字なしのimgとCSS装飾。すべての文字は静的HTML。'
    notes = {
        'A': [
            ('狙い', 'お得額が見た瞬間に分かる、最も販促感の強い案。画像より大きい数字と、黄色・青の強い対比で目を引きます。'),
            ('レイアウト', '左に「２台まとめて」→最大サイズの4,400→円お得！→CTA→条件。右のエアコン２台は小さめにまとめ、青い斜めパネルで分離します。'),
            ('配色', '黄色#ffdf32×濃い青#06439d。お得ラベルとCTAはオレンジ、数字は白い縁取り。ドット・放射は薄く、文字の背面を優先。'),
            ('メインコピー', f'２台まとめて {p["totalSaving"]:,}円お得！'),
            ('価格の見せ方', f'{p["totalSaving"]:,}をPC最大158pxで主役に。１台あたり{p["saving"]:,}円お得は小さく補足。'),
            ('CTA', CTA), ('HTML/CSS構造', common_structure)],
        'B': [
            ('狙い', 'いくらで頼めるかを最短で伝える案。１台あたりの11,000円を最も大きくし、２台合計は補助情報に留めます。'),
            ('レイアウト', '左に「２台以上なら」→１台あたり→大きな11,000円（税込）→小さな２台合計→CTA→条件。右は２台の画像と青い丸背景。'),
            ('配色', '白・水色#eaf7ff×濃い青#06439d。料金の円と販促ラベルにオレンジ、帯に黄色。数値部分は無地で読みやすく。'),
            ('メインコピー', f'２台以上なら、１台あたり{p["multiple"]:,}円（税込）'),
            ('価格の見せ方', f'{p["multiple"]:,}をPC最大138px。２台合計{p["total"]:,}円（税込）は下に小さく表示し、情報の強弱を明確に。'),
            ('CTA', CTA), ('HTML/CSS構造', common_structure)],
        'C': [
            ('狙い', 'まとめて注文するメリットに暮らしの親しみを添える案。２台の文字を大きくし、リビング・寝室は補助情報として扱います。'),
            ('レイアウト', '左に大きな「２台」→「まとめて、お得にキレイ！」→生活場面→２台合計料金→CTA→条件。右は２台の画像と部屋名ラベル。'),
            ('配色', 'クリーム#fff0d4×サイトの濃い青。オレンジの帯と黄色の下線で販促感を加え、温かさと視認性を両立。'),
            ('メインコピー', '２台まとめて、お得にキレイ！'),
            ('価格の見せ方', f'２台の文字はPC最大114px。２台合計{p["total"]:,}円（税込）は最大42pxで、メインコピーの次に見せます。'),
            ('CTA', CTA), ('HTML/CSS構造', common_structure)],
    }
    return notes[letter]


def notes_markup(letter, p):
    rows = ''.join(f'<dt>{escape(label)}</dt><dd>{escape(value)}</dd>' for label, value in design_notes(letter, p))
    return f'<details class="ab-design-notes" open><summary>この案の狙い・レイアウト・実装</summary><dl>{rows}</dl></details>'


def build():
    p = pricing()
    articles = ''.join(f'''<article class="ab-proposal" id="proposal-{letter}">
<header class="ab-proposal-heading"><div><span class="ab-letter">{letter}</span><h2>{label}</h2></div><p>{description}</p><a href="context.html?banner={letter}#home-pickup-banner">HOMEで見る <span aria-hidden="true">↗</span></a></header>
{banner(letter, p, 'gallery-'+letter)}{notes_markup(letter,p)}</article>''' for letter, label, description in VARIANTS)
    page = f'''<!doctype html>
<html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="robots" content="noindex,nofollow"><title>エアコン２台バナー・３案 | Crystal Clean Home</title><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Zen+Kaku+Gothic+New:wght@700;900&amp;display=swap"><link rel="stylesheet" href="{BASE}banner.css"></head>
<body class="ab-review"><header class="ab-review-header"><a class="ab-brand" href="/home-wireframe/">Crystal Clean Home</a><span>バナー・３案比較</span></header>
<main class="ab-review-main"><section class="ab-intro"><p class="ab-kicker">エアコン２台・まとめてお得</p><h1>数字が主役の、販促バナー。</h1><p>左に訴求と料金、右に２台のエアコン。情報の強弱をつけて、３案を再構成しました。</p><nav aria-label="３案の移動"><a href="#proposal-A">A お得額</a><a href="#proposal-B">B 料金</a><a href="#proposal-C">C ２台まとめて</a></nav></section>
{articles}<footer class="ab-review-note"><p>ローカルの比較用です。掲載する案は未決定です。</p><p>文言・金額・条件はHTMLで表示しています。３案とも既存のエアコンページへつながります。</p><a href="/home-wireframe/">HOMEの比較画面に戻る</a></footer></main></body></html>'''
    (HERE / 'index.html').write_text(page, encoding='utf-8', newline='\n')
    original = (ROOT / 'source/site/index.html').read_text(encoding='utf-8')
    match = re.search(r'<section\b[^>]*id="home-pickup-banner"[^>]*>.*?</section>', original, re.S)
    assert match
    panels = ''.join(f'<div data-ab-panel="{letter}"'+(' hidden' if letter != 'A' else '')+f'>{banner(letter,p,"context-"+letter)}</div>' for letter,_,_ in VARIANTS)
    controls = ''.join(f'<button type="button" data-ab-choice="{letter}" aria-pressed="'+('true' if letter == 'A' else 'false')+f'">{letter} {label}</button>' for letter,label,_ in VARIANTS)
    replacement = f'''<section class="home-pickup home-pickup--banner" id="home-pickup-banner" aria-labelledby="home-pickup-banner-title"><div class="home-pickup__inner"><div class="ab-context-review"><p>上部バナー・３案比較</p><div role="group" aria-label="バナーの３案">{controls}</div><a href="{BASE}">３案を並べて見る</a></div><header class="home-pickup__heading"><span>PICK UP</span><h2 id="home-pickup-banner-title">まとめて頼むお掃除</h2></header>{panels}</div></section>'''
    context = original[:match.start()] + replacement + original[match.end():]
    context = re.sub(r'<title>.*?</title>', '<title>HOMEのエアコンバナー比較 | Crystal Clean Home</title>', context, count=1)
    context = context.replace('</head>', f'<meta name="robots" content="noindex,nofollow"><link rel="stylesheet" href="{BASE}banner.css"><script src="{BASE}context.js" defer></script></head>', 1)
    (HERE / 'context.html').write_text(context, encoding='utf-8', newline='\n')
    preservation = {}
    for name, pattern in {
        'header': r'<header class="c-header">.*?</header>',
        'footer': r'<footer\b.*?</footer>',
        'laterPickupSlots': r'<section\b[^>]*id="home-pickup".*?</section>',
        'video': r'<section\b[^>]*class="home-first-view".*?</section>',
        'guideBanners': r'<section\b[^>]*class="[^"]*home-first-guide-section[^>]*>.*?</section>',
    }.items():
        fragment = re.search(pattern, original, re.S)
        assert fragment and fragment.group(0) in context, name
        preservation[name] = True
    metadata = dict(priceSource='source/service-pages/catalogue.json: products.1',
                    priceParser='tools/build_cart_catalogue.py: prices', prices=p,
                    revision=2, designNotes={letter:dict(design_notes(letter,p)) for letter,_,_ in VARIANTS},
                    variants=[v[0] for v in VARIANTS], destination=DESTINATION,
                    textRendering='static HTML; CSS decorations; raster artwork contains no text',
                    prototypeOnly=True, published=False, preservedMarkup=preservation,
                    sourceHomeSha256=sha256((ROOT / 'source/site/index.html').read_bytes()).hexdigest())
    (HERE / 'build-info.json').write_text(json.dumps(metadata, ensure_ascii=False, indent=2)+'\n',encoding='utf-8',newline='\n')
    brief = ['## 再提案３案の設計説明', '', '３案とも左に訴求・価格・CTA・条件、右に２台の画像を置きます。販促ラベルは「まとめてお得」「２台以上」を使用します。', '']
    for letter, label, _ in VARIANTS:
        brief.extend([f'### {letter}案：{label}', ''])
        brief.extend(f'- **{key}**：{value}' for key, value in design_notes(letter, p))
        brief.append('')
    marker_start, marker_end = '<!-- proposal-notes:start -->', '<!-- proposal-notes:end -->'
    section = marker_start + '\n' + '\n'.join(brief) + marker_end
    readme_path = HERE / 'README.md'
    readme = readme_path.read_text(encoding='utf-8')
    if marker_start in readme:
        readme = re.sub(re.escape(marker_start) + r'.*?' + re.escape(marker_end), lambda _: section, readme, flags=re.S)
    else:
        readme += '\n' + section + '\n'
    readme_path.write_text(readme, encoding='utf-8', newline='\n')
    print(json.dumps(dict(revision=metadata['revision'], prices=p, variants=metadata['variants'], preserved=preservation)))


if __name__ == '__main__':
    build()
