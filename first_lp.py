"""Publish the image-led first-visit LP and its accessible text equivalents."""
from pathlib import Path
import hashlib
import html
import json
import re
import shutil
from bs4 import BeautifulSoup
from PIL import Image
from io_retry import write_text

BASE = '/crystal-clean-home/'
PUBLIC = 'https://yasojima.github.io' + BASE


def render_art(root, out):
    """Finished section art is the visual source. Do not recreate balloons in CSS.

    Mobile artwork is a deliberate recomposition, never a crop of dialogue.
    Text equivalents are available to every reader through ordinary disclosures.
    """
    content = json.loads((root / 'brand/first-lp/art-content.json').read_text(encoding='utf-8'))
    shutil.copytree(root / 'brand/first-lp/art', out / 'art', dirs_exist_ok=True)
    # Keep the original, text-free character art only as the social preview.
    (out / 'images').mkdir(exist_ok=True)
    shutil.copy2(root / 'brand/first-lp/images/hero.webp', out / 'images/hero.webp')

    def img(name, alt, eager=False):
        path = root / 'brand/first-lp/art' / (name + '.webp')
        with Image.open(path) as image:
            width, height = image.size
        priority = 'fetchpriority="high"' if eager else 'loading="lazy"'
        return f'<img src="{BASE}brand/first-lp/art/{path.name}" width="{width}" height="{height}" {priority} decoding="async" alt="{html.escape(alt, quote=True)}">'

    def picture(name, item):
        desktop = img(name, item['alt'], name == 'cover')
        if not item.get('mobile'):
            return desktop
        path = root / 'brand/first-lp/art' / (item['mobile'] + '.webp')
        with Image.open(path) as image:
            width, height = image.size
        return f'<picture><source media="(max-width: 600px)" srcset="{BASE}brand/first-lp/art/{path.name}" width="{width}" height="{height}">{desktop}</picture>'

    tokens = {}
    for name, item in content['sections'].items():
        tokens['ART_' + name.upper().replace('-', '_')] = picture(name, item)
        paragraphs = ''.join(f'<p>{html.escape(text)}</p>' for text in item.get('transcript', []))
        if paragraphs:
            tokens['TEXT_' + name.upper().replace('-', '_')] = f'<details class="lp-transcript"><summary>画像の内容を文章で読む</summary><div>{paragraphs}</div></details>'
    # The existing shared CTA determines the destination, even though this LP
    # uses finished image artwork for its label, icon, frame and background.
    shared = BeautifulSoup((root / 'brand/estimate-cta/template.html').read_text(encoding='utf-8'), 'html.parser')
    target = shared.select_one('a')['href']
    tokens['CTA_ART'] = f'<a class="lp-art-cta" href="{html.escape(target, quote=True)}" aria-label="無料お見積り：清掃メニューを選ぶ">{picture("cta-art", content["cta"])}</a>'
    comparison = content['comparison']
    heads = ''.join(f'<th scope="col">{html.escape(text)}</th>' for text in comparison['columns'])
    rows = ''.join('<tr><th scope="row">' + html.escape(row[0]) + '</th>' + ''.join(f'<td>{html.escape(value)}</td>' for value in row[1:]) + '</tr>' for row in comparison['rows'])
    tokens['COMPARISON_TABLE'] = f'<table><caption>料金比較サンプル（各1台・1箇所、税込・仮設定）</caption><thead><tr>{heads}</tr></thead><tbody>{rows}</tbody></table>'
    return tokens


def render_materials(root, out):
    """Reuse home category ownership and product samples without duplicating copy."""
    settings = json.loads((root / 'brand/first-lp/materials.json').read_text(encoding='utf-8'))
    home = BeautifulSoup((root / 'brand/service-cards/template.html').read_text(encoding='utf-8'), 'html.parser')
    css = (root / 'source/device/desktop/css/brand/header/category-cards.css').read_text(encoding='utf-8')
    reused = out / 'reused'
    reused.mkdir(exist_ok=True)

    def picture(path, name, alt, class_name=''):
        source = root / path
        destination = reused / (name + '.webp')
        with Image.open(source) as image:
            width, height = image.size
            if source.suffix == '.webp':
                shutil.copy2(source, destination)
            else:
                image.save(destination, 'WEBP', quality=90, method=6)
        return f'<img class="{class_name}" src="{BASE}brand/first-lp/reused/{destination.name}" width="{width}" height="{height}" loading="lazy" alt="{html.escape(alt, quote=True)}">'

    services = []
    scenes = {}
    for card in home.select('.c-house-cleaning-links__link'):
        marker = next(name for name in card.select_one('.c-illust')['class'] if name.startswith('c-illust--'))
        image_url = re.search(r'\.' + re.escape(marker) + r'\{[^}]*background-image:url\("([^"]+)"', css)[1]
        path = image_url.removeprefix(BASE)
        name = card['href'].rstrip('/').split('/')[-1]
        title = card.select_one('h3').get_text(' ', strip=True)
        scenes[name] = (path, name, title)
        services.append(f'<a class="lp-service-card" href="{card["href"]}">{picture(path, name, title)}<h3>{html.escape(title)}</h3><span>内容・料金を確認 <span aria-hidden="true">›</span></span></a>')

    cases = []
    for item in settings['cases']:
        pairs = ''.join(f'<figure>{picture(item[state], item["key"] + "-" + state, item["category"] + "：" + label)}<figcaption>{label}</figcaption></figure>' for state, label in [('before', '清掃前のイメージ'), ('after', '清掃後のイメージ')])
        cases.append(f'<article class="lp-case"><div class="lp-case-copy"><p class="lp-eyebrow">{html.escape(item["category"])}</p><h3>{html.escape(item["title"])}</h3><p>{html.escape(item["description"])}</p></div><div class="lp-case-pair">{pairs}</div></article>')

    reviews = json.loads((root / 'source/product-wireframe/review-copy.json').read_text(encoding='utf-8'))
    voices = []
    for index, item in enumerate(settings['reviews'], 1):
        title, body = reviews[item['category']][item['index']]
        voices.append(f'<article class="lp-voice"><p class="lp-voice-label">掲載用サンプル {index:02}</p><h3>{html.escape(title)}</h3><p>{html.escape(body)}</p></article>')
    return {'SERVICE_CARDS': ''.join(services), 'CASE_CARDS': ''.join(cases), 'REVIEW_CARDS': ''.join(voices), 'ROOM_SCENE': picture(*scenes['room'], class_name='lp-approach-image')}


def publish_first_lp(root):
    root = Path(root)
    template = root / 'brand/first-lp/template.html'
    if not template.exists():
        return
    main = template.read_text(encoding='utf-8').strip()
    out = root / 'docs/brand/first-lp'
    out.mkdir(parents=True, exist_ok=True)
    for name, markup in render_art(root, out).items():
        main = main.replace('{{' + name + '}}', markup)
    for name, markup in render_materials(root, out).items():
        main = main.replace('{{' + name + '}}', markup)
    if '{{' in main:
        raise ValueError('Unresolved first LP content placeholder')
    links = []
    for platform in ('desktop', 'mobile'):
        css = (root / f'source/device/{platform}/css/first-lp.css').read_text(encoding='utf-8')
        revision = hashlib.sha256(css.encode()).hexdigest()[:12]
        write_text(out / f'{platform}.css', css)
        media = '(min-width: 993px)' if platform == 'desktop' else '(max-width: 992px)'
        links.append(f'<link rel="stylesheet" href="{BASE}brand/first-lp/{platform}.css?v={revision}" media="{media}" data-cch-first-lp>')
    for relative in ('source/first/index.html', 'docs/first/index.html'):
        page = root / relative
        text = page.read_text(encoding='utf-8')
        text, count = re.subn(r'<main class="main_contents">.*?</main>', lambda _: main, text, count=1, flags=re.S)
        if count != 1:
            raise ValueError(f'Missing first main in {relative}')
        text = re.sub(r'(class="page_container)(?![^"\n]*\bcch-first-lp-page\b)', r'\1 cch-first-lp-page', text, count=1)
        text = re.sub(r'<link\b[^>]*data-cch-first-lp[^>]*>', '', text)
        text = re.sub(r'<title>.*?</title>', '<title>初めての方へ｜安心して相談できるハウスクリーニング｜クリスタルクリーンホーム</title>', text, count=1, flags=re.S)
        text = re.sub(r'<meta\b[^>]*(?:name=["\']description["\']|property=["\']og:[^"\']+["\'])[^>]*>', '', text)
        text = re.sub(r'<link\b[^>]*rel=["\']canonical["\'][^>]*>', '', text)
        desc = '初めてのハウスクリーニングを漫画でご案内。清掃方法の選定、作業前の説明、住まいの保護、衛生管理と仕上がり確認への取り組みをご紹介します。'
        metadata = f'<meta name="description" content="{desc}"><link rel="canonical" href="{PUBLIC}first/"><meta property="og:title" content="初めての方へ｜クリスタルクリーンホーム"><meta property="og:description" content="{desc}"><meta property="og:type" content="website"><meta property="og:url" content="{PUBLIC}first/"><meta property="og:image" content="{PUBLIC}brand/first-lp/images/hero.webp">'
        text = re.sub(r'\s*</head>', lambda _: '\n' + metadata + '\n'.join(links) + '\n</head>', text, count=1)
        if relative.startswith('source/'):
            # source/** is stored verbatim by Git; preserve its LF line endings.
            page.write_bytes(re.sub(r'[ \t]+$', '', text, flags=re.M).encode('utf-8'))
        else:
            write_text(page, text)


if __name__ == '__main__':
    from shared_ui import publish_shared_ui
    publish_shared_ui(Path(__file__).resolve().parent)
