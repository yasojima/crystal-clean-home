"""Check regeneration, readable static content, old anchors and asset integrity."""
from pathlib import Path
from bs4 import BeautifulSoup
from PIL import Image
import json
from first_lp import publish_first_lp

root = Path(__file__).resolve().parent
publish_first_lp(root)
before = (root / 'docs/first/index.html').read_bytes()
publish_first_lp(root)
assert before == (root / 'docs/first/index.html').read_bytes(), 'Publisher must be idempotent'
page = BeautifulSoup(before, 'html.parser')
source = BeautifulSoup((root / 'source/first/index.html').read_text(encoding='utf-8'), 'html.parser')
main = page.select_one('#cch-first-lp')
assert str(main) == str(source.select_one('#cch-first-lp'))
assert len(main.select('h1')) == 1
art = json.loads((root / 'brand/first-lp/art-content.json').read_text(encoding='utf-8'))
for chapter in ('first-comic', 'first-work', 'first-finish'):
    assert main.select_one('#' + chapter + ' picture source[media="(max-width: 600px)"]')
assert not main.select('.lp-bubble, .lp-comic'), 'Do not recreate illustrated scenes as CSS cards'
assert len(main.select('.lp-flow > li')) == 5
assert len(main.select('.lp-faq details')) == 5
for section, item in art['sections'].items():
    for paragraph in item.get('transcript', []):
        assert paragraph in main.get_text(), 'Image text equivalent must be available to readers'
assert len(main.select('thead th')) == 7
assert [x.get_text(strip=True) for x in main.select('thead th')[2:]] == ['A社','B社','C社','D社','E社']
assert [[c.get_text() for c in tr.select('th,td')] for tr in main.select('tbody tr')] == art['comparison']['rows']
assert '架空の会社' in main.get_text()
assert '実際のお客様の体験談ではありません' in main.get_text()
ids = [x['id'] for x in page.select('[id]')]
assert len(ids) == len(set(ids)), 'Duplicate IDs'
for name in ('first-introduction', 'cleaning-approach', 'infection-prevention'):
    assert page.find(id=name)
for a in main.select('a[href]'):
    href = a['href']
    if href.startswith('#'):
        assert page.find(id=href[1:])
    elif href.startswith('/crystal-clean-home/'):
        assert (root / 'docs' / href.removeprefix('/crystal-clean-home/') / 'index.html').exists()
for img in main.select('img'):
    assert img.get('alt') and img.get('width') and img.get('height')
    path = root / 'docs' / img['src'].removeprefix('/crystal-clean-home/')
    with Image.open(path) as image:
        assert image.size == (int(img['width']), int(img['height']))
for source_img in main.select('picture source'):
    path = root / 'docs' / source_img['srcset'].removeprefix('/crystal-clean-home/')
    with Image.open(path) as image:
        assert image.size == (int(source_img['width']), int(source_img['height']))
    assert source_img.find_next_sibling('img')
assert page.select_one('link[rel="canonical"]')['href'] == 'https://yasojima.github.io/crystal-clean-home/first/'
assert len(page.select('meta[name="description"]')) == 1
assert len(page.select('[data-cch-first-lp]')) == 2
assert not main.select('form, iframe, script, [hidden]')
assert all(a['href'] == '/crystal-clean-home/services/' for a in main.select('.lp-art-cta'))
assert len(main.select('.lp-art-cta')) == 5
assert all(a.get('aria-label') and a.select_one('picture source') for a in main.select('.lp-art-cta'))
home = BeautifulSoup((root / 'brand/service-cards/template.html').read_text(encoding='utf-8'), 'html.parser')
cards = main.select('.lp-service-card')
originals = home.select('.c-house-cleaning-links__link')
assert len(cards) == len(originals) == 8
assert [(a['href'], a.h3.get_text(' ', strip=True)) for a in cards] == [(a['href'], a.h3.get_text(' ', strip=True)) for a in originals]
settings = json.loads((root / 'brand/first-lp/materials.json').read_text(encoding='utf-8'))
assert len(main.select('.lp-case')) == len(settings['cases']) == 2
for case, setting in zip(main.select('.lp-case'), settings['cases']):
    for img, state in zip(case.select('img'), ('before', 'after')):
        derivative = root / 'docs' / img['src'].removeprefix('/crystal-clean-home/')
        assert derivative.read_bytes() == (root / setting[state]).read_bytes(), 'Before/after must preserve existing image'
reviews = json.loads((root / 'source/product-wireframe/review-copy.json').read_text(encoding='utf-8'))
assert len(main.select('.lp-voice')) == len(settings['reviews']) == 3
for voice, setting in zip(main.select('.lp-voice'), settings['reviews']):
    title, body = reviews[setting['category']][setting['index']]
    assert voice.h3.get_text() == title
    assert voice.select('p')[-1].get_text() == body
assert '実際の施工写真ではありません' in main.get_text()
assert '実際のお客様の口コミ・評価ではありません' in main.get_text()
assert '{{' not in str(main)
print('PASS: regeneration, canonical body, 3 image manga chapters, mobile art, accessible text/table, 8 linked menus, 2 before/after pairs, 3 source reviews, 5 CTAs, anchors, SEO and image dimensions')
