"""Publish the illustrated LP, reusing the site's existing service components."""
from pathlib import Path
from copy import deepcopy
import hashlib
import html
import json
import re
import shutil
import tinycss2
from bs4 import BeautifulSoup
from PIL import Image
from io_retry import write_text

BASE = '/crystal-clean-home/'
PUBLIC = 'https://yasojima.github.io' + BASE


def art_image(root, name, alt, eager=False):
    path = root / 'brand/first-lp/art' / (name + '.webp')
    with Image.open(path) as image:
        width, height = image.size
    priority = 'fetchpriority="high"' if eager else 'loading="lazy"'
    revision = hashlib.sha256(path.read_bytes()).hexdigest()[:10]
    return f'<img src="{BASE}brand/first-lp/art/{path.name}?v={revision}" width="{width}" height="{height}" {priority} decoding="async" alt="{html.escape(alt, quote=True)}">'


def render_art(root, out):
    content = json.loads((root / 'brand/first-lp/art-content.json').read_text(encoding='utf-8'))
    shutil.copytree(root / 'brand/first-lp/art', out / 'art', dirs_exist_ok=True)
    (out / 'images').mkdir(exist_ok=True)
    shutil.copy2(root / 'brand/first-lp/images/hero.webp', out / 'images/hero.webp')
    tokens = {}
    for name, item in content['sections'].items():
        markup = art_image(root, name, item['alt'], name == 'opening')
        if item.get('mobile'):
            path = root / 'brand/first-lp/art' / (item['mobile'] + '.webp')
            with Image.open(path) as image:
                width, height = image.size
            revision = hashlib.sha256(path.read_bytes()).hexdigest()[:10]
            markup = f'<picture><source media="(max-width:600px)" srcset="{BASE}brand/first-lp/art/{path.name}?v={revision}" width="{width}" height="{height}">{markup}</picture>'
        token = name.upper().replace('-', '_')
        tokens['ART_' + token] = markup
    shared = BeautifulSoup((root / 'brand/estimate-cta/template.html').read_text(encoding='utf-8'), 'html.parser')
    button = shared.select_one('a')
    button.attrs.pop('role', None)
    button['class'] = button.get('class', []) + ['lp-estimate-button']
    button['aria-label'] = '無料お見積もり：清掃メニューを選ぶ'
    button.select_one('.c-double-icon-button__text').clear()
    button.select_one('.c-double-icon-button__text').append(BeautifulSoup('<span class="btn-free">無料お見積もり</span>', 'html.parser'))
    tokens['CTA_BUTTON'] = str(button)
    for name, item in content['ctas'].items():
        art = art_image(root, name, item['alt'])
        scene_button = deepcopy(button)
        if name == 'cta-final':
            scene_button['href'] = BASE + 'cart/'
            scene_button['aria-label'] = '無料見積もりを試す：見積もりカートへ'
            scene_button.select_one('.btn-free').string = '無料見積もりを試す'
        tokens[name.upper().replace('-', '_')] = f'<div class="lp-cta-scene {name}">{art}<div class="lp-cta-action">{scene_button}</div></div>'
    comparison = json.loads((root / 'brand/first-lp/comparison.json').read_text(encoding='utf-8'))
    heads = ''.join(f'<th scope="col">{html.escape(text)}</th>' for text in comparison['columns'])
    rows = ''.join('<tr><th scope="row">' + html.escape(row[0]) + '</th>' + ''.join(f'<td>{html.escape(value)}</td>' for value in row[1:]) + '</tr>' for row in comparison['rows'])
    tokens['COMPARISON_TABLE'] = f'<table><caption class="lp-sr">エアコンクリーニングの料金比較</caption><thead><tr>{heads}</tr></thead><tbody>{rows}</tbody></table>'
    return tokens


def render_materials(root, out):
    from home_sections import homepage_questions
    from product_wireframe import review_cards, common_flow
    settings = json.loads((root / 'brand/first-lp/materials.json').read_text(encoding='utf-8'))
    home = BeautifulSoup((root / 'brand/service-cards/template.html').read_text(encoding='utf-8'), 'html.parser')
    cards = ''.join(str(c) for c in home.select('.c-house-cleaning-links__link'))
    labels = {c['href'].rstrip('/').split('/')[-1]: c.h3.get_text(' ', strip=True) for c in home.select('.c-house-cleaning-links__link')}
    pack = BeautifulSoup((root / 'source/product-wireframe/pages/house-cleaning/pack/index.html').read_text(encoding='utf-8'), 'html.parser')
    tabs = deepcopy(pack.select_one('.c-compare-image').find_parent(class_='c-tab'))
    buttons = tabs.select('.c-tab__button')
    panels = tabs.select('.c-tab__panel')
    for extra in buttons[len(settings['cases']):] + panels[len(settings['cases']):]:
        extra.decompose()
    reused = out / 'reused'
    reused.mkdir(exist_ok=True)
    for i, item in enumerate(settings['cases']):
        button, panel = buttons[i], panels[i]
        button['id'] = f'lp-case-tab-{i}'
        button['aria-controls'] = f'lp-case-panel-{i}'
        button['aria-selected'] = 'true' if i == 0 else 'false'
        button['tabindex'] = '0' if i == 0 else '-1'
        button.string = item['category']
        panel['id'] = f'lp-case-panel-{i}'
        panel['aria-labelledby'] = button['id']
        panel['class'] = ['c-tab__panel'] + (['is-active'] if i == 0 else [])
        for image, state in zip(panel.select('.c-compare-image img'), ('before', 'after')):
            path = root / item[state]
            destination = reused / f'{item["key"]}-{state}.webp'
            shutil.copy2(path, destination)
            with Image.open(path) as asset:
                image['width'], image['height'] = map(str, asset.size)
            image['src'] = BASE + 'brand/first-lp/reused/' + destination.name
            image['alt'] = item['category'] + ('・清掃前のイメージ' if state == 'before' else '・清掃後のイメージ')
            image['loading'] = 'lazy'
        panel.select_one('.c-compare-image-tab__text').string = item['description']
        for note in panel.select('.c-note'):
            note.decompose()
        link_box = panel.select_one('.c-compare-image-tab__link-container')
        if link_box:
            link_box.decompose()
    closing_cases = []
    for item in settings['closing_cases']:
        pair = []
        for state, label in (('before', 'Before'), ('after', 'After')):
            path = root / item[state]
            destination = reused / f'{item["key"]}-{state}.webp'
            shutil.copy2(path, destination)
            with Image.open(path) as asset:
                width, height = asset.size
            pair.append(f'<figure class="lp-result-{state}"><figcaption>{label}</figcaption><img src="{BASE}brand/first-lp/reused/{destination.name}" width="{width}" height="{height}" loading="lazy" decoding="async" alt="{html.escape(item["category"])} {label}のイメージ"></figure>')
        closing_cases.append(f'<article class="lp-result-card"><h3>{html.escape(item["category"])}</h3><div class="lp-result-pair">{"".join(pair)}</div></article>')
    voices = []
    for item in settings['reviews']:
        original = review_cards(item['category'], None)
        card = deepcopy(original.select('.c-voice-card')[item['index']])
        card['class'] += ['lp-voice']
        label = BeautifulSoup(f'<p class="lp-service-label">{html.escape(labels[item["category"]])}</p>', 'html.parser')
        card.insert(1, label)
        card.append(BeautifulSoup(f'<a class="lp-related-menu" href="{BASE}house-cleaning/{item["category"]}/">この清掃メニューを見る <span aria-hidden="true">›</span></a>', 'html.parser'))
        voices.append(str(card))
    flow = common_flow().select_one('.c-step-list')
    for icon in flow.select('img'):
        icon['src'] = icon['src'].replace('_product-wireframe/', 'reference/product-pages/')
        with Image.open(root / 'source/product-wireframe/assets/flow' / icon['src'].split('/')[-1]) as asset:
            icon['width'], icon['height'] = map(str, asset.size)
    faq = BeautifulSoup(homepage_questions(root), 'html.parser')
    for i, item in enumerate(faq.select('details')):
        if i not in settings['faq_indices']:
            item.decompose()
    for i, item in enumerate(faq.select('.cch-faq-number'), 1):
        item.string = f'Q{i}.'
    return {'SERVICE_CARDS': cards, 'CASE_SLIDER': str(tabs), 'CLOSING_CASES': ''.join(closing_cases), 'REVIEW_CARDS': ''.join(voices),
            'FLOW': str(flow), 'FAQ': '<div class="lp-faq">' + str(faq.select_one('.cch-faq-list')) + '</div>'}


def reused_css(root, platform):
    """Scope the canonical component rules without forking their visual definitions."""
    families = ('.icv', '.c-compare-image', '.c-tab__', '.c-voice-card', '.c-step-list',
                '.cch-wf-voice', '.cch-wf-flow-icon', '.cch-faq', '#cch-faq',
                '.c-category-simple-card', '.c-ribbon-label-tag', '.c-illust')
    sources = ['reference/assets/css/common.css', 'product-wireframe/wireframe.css',
               'brand/prevention/style.css', 'brand/service-cards/style.css',
               'brand/header/category-cards.css']
    def scope(selector):
        selector = re.sub(r'html\[data-product-wireframe=["\']true["\']\]\s*', '', selector)
        selector = selector.replace('.cch-reference', '').replace('#cch-service-cards', '').replace('#cch-service-directory', '')
        selector = selector.replace('#cch-faq', '#first-faq')
        selector = re.sub(r'^\s*body\s+', '', selector)
        return '#cch-first-lp ' + selector.strip()
    def rules(items):
        result = []
        for rule in items:
            if rule.type == 'at-rule' and rule.content is not None and rule.lower_at_keyword in ('media', 'supports', 'layer'):
                nested = rules(tinycss2.parse_rule_list(rule.content, skip_whitespace=True, skip_comments=True))
                if nested:
                    result.append('@' + rule.lower_at_keyword + ' ' + tinycss2.serialize(rule.prelude) + '{' + nested + '}')
            elif rule.type == 'qualified-rule':
                groups = [[]]
                for token in rule.prelude:
                    if token.type == 'literal' and token.value == ',':
                        groups.append([])
                    else:
                        groups[-1].append(token)
                selectors = [tinycss2.serialize(group).strip() for group in groups]
                selectors = [scope(s) for s in selectors if any(f in s for f in families)]
                if selectors:
                    result.append(','.join(selectors) + '{' + tinycss2.serialize(rule.content) + '}')
        return '\n'.join(result)
    return '\n'.join(rules(tinycss2.parse_stylesheet((root / f'source/device/{platform}/css' / source).read_text(encoding='utf-8'), skip_comments=True, skip_whitespace=True)) for source in sources)


def publish_first_lp(root):
    root = Path(root)
    template = root / 'brand/first-lp/template.html'
    if not template.exists():
        return
    main = template.read_text(encoding='utf-8-sig').strip()
    out = root / 'docs/brand/first-lp'
    out.mkdir(parents=True, exist_ok=True)
    for name, markup in (render_art(root, out) | render_materials(root, out)).items():
        main = main.replace('{{' + name + '}}', markup)
    if '{{' in main:
        raise ValueError('Unresolved first LP content placeholder')
    links = []
    for platform in ('desktop', 'mobile'):
        css = reused_css(root, platform) + '\n' + (root / f'source/device/{platform}/css/first-lp.css').read_text(encoding='utf-8')
        revision = hashlib.sha256(css.encode()).hexdigest()[:12]
        write_text(out / f'{platform}.css', css)
        media = '(min-width: 993px)' if platform == 'desktop' else '(max-width: 992px)'
        links.append(f'<link rel="stylesheet" href="{BASE}brand/first-lp/{platform}.css?v={revision}" media="{media}" data-cch-first-lp>')
    script = root / 'brand/first-lp/interaction.js'
    shutil.copy2(script, out / script.name)
    revision = hashlib.sha256(script.read_bytes()).hexdigest()[:12]
    scripts = f'<script defer src="{BASE}reference/assets/js/common.js" data-cch-lp-script></script><script defer src="{BASE}brand/first-lp/interaction.js?v={revision}" data-cch-lp-script></script>'
    for relative in ('source/first/index.html', 'docs/first/index.html'):
        page = root / relative
        text = page.read_text(encoding='utf-8')
        text, count = re.subn(r'<main class="main_contents">.*?</main>', lambda _: main, text, count=1, flags=re.S)
        if count != 1:
            raise ValueError(f'Missing first main in {relative}')
        text = re.sub(r'(class="page_container)(?![^"\n]*\bcch-first-lp-page\b)', r'\1 cch-first-lp-page', text, count=1)
        text = re.sub(r'<section\b[^>]*class="sec_cv"[^>]*>.*?</section>', '', text, flags=re.S)
        # The shared floating bar only mounts when a footer exists.
        text = re.sub(r'<footer\b[^>]*>.*?</footer>', '', text, flags=re.S)
        text = re.sub(r'<link\b[^>]*data-cch-first-lp[^>]*>', '', text)
        text = re.sub(r'<script\b[^>]*data-cch-lp-script[^>]*>.*?</script>', '', text, flags=re.S)
        text = re.sub(r'<title>.*?</title>', '<title>初めての方へ｜安心して相談できるハウスクリーニング｜クリスタルクリーンホーム</title>', text, count=1, flags=re.S)
        text = re.sub(r'<meta\b[^>]*(?:name=["\']description["\']|property=["\']og:[^"\']+["\'])[^>]*>', '', text)
        text = re.sub(r'<link\b[^>]*rel=["\']canonical["\'][^>]*>', '', text)
        desc = '初めてのハウスクリーニングを漫画でご案内。清掃方法の選定、作業前の説明、住まいの保護、衛生管理と仕上がり確認への取り組みをご紹介します。'
        metadata = f'<meta name="description" content="{desc}"><link rel="canonical" href="{PUBLIC}first/"><meta property="og:title" content="初めての方へ｜クリスタルクリーンホーム"><meta property="og:description" content="{desc}"><meta property="og:type" content="website"><meta property="og:url" content="{PUBLIC}first/"><meta property="og:image" content="{PUBLIC}brand/first-lp/images/hero.webp">'
        text = re.sub(r'\s*</head>', lambda _: '\n' + metadata + '\n'.join(links) + scripts + '\n</head>', text, count=1)
        if relative.startswith('source/'):
            page.write_bytes(re.sub(r'[ \t]+$', '', text, flags=re.M).encode('utf-8'))
        else:
            write_text(page, text)


if __name__ == '__main__':
    from shared_ui import publish_shared_ui
    publish_shared_ui(Path(__file__).resolve().parent)
