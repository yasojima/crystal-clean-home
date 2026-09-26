"""Verify LP generation, source reuse, links, asset geometry and LP-only scope."""
from pathlib import Path
from urllib.parse import urlsplit
from bs4 import BeautifulSoup
from PIL import Image
import hashlib
import json
from first_lp import publish_first_lp
from product_wireframe import REVIEW_COPY, FLOW_COPY
from home_sections import homepage_questions

root = Path(__file__).resolve().parent
untouched = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in
             [root/'docs/index.html', root/'brand/header/floating.js',
              *[root/f'docs/house-cleaning/{c}/index.html' for c in
                ('aircon','pack','water','washer','kitchen','room','coating','others')]]}
publish_first_lp(root)
before = (root/'docs/first/index.html').read_bytes()
publish_first_lp(root)
assert before == (root/'docs/first/index.html').read_bytes(), 'Idempotence'
page = BeautifulSoup(before, 'html.parser')
main = page.select_one('#cch-first-lp')
source = BeautifulSoup((root/'source/first/index.html').read_text(encoding='utf-8'), 'html.parser')
assert str(main) == str(source.select_one('#cch-first-lp'))
assert len(main.select('h1')) == 1 and main.h1.img
assert not page.select('footer, .sec_cv')
assert not main.select('.lp-bridge, .lp-art-cta, .lp-contact')
art = json.loads((root/'brand/first-lp/art-content.json').read_text(encoding='utf-8'))
for entry in art['sections'].values():
    for copy in entry.get('transcript', []):
        assert copy in main.get_text()
assert len(main.select('.lp-art-section picture source')) == 3
assert len(main.select('.lp-estimate-button')) == 5
assert len(main.select('.lp-cta-scene')) == 4
assert len({i['src'] for i in main.select('.lp-cta-scene>img')}) == 4
for button in main.select('.lp-estimate-button'):
    assert button['href'] == '/crystal-clean-home/services/'
    assert not button.select('img,picture')
assert main.select_one('.lp-scroll-up')['href'] == '#first-introduction'
ids = [x['id'] for x in page.select('[id]')]
assert len(ids) == len(set(ids))
for link in main.select('a[href]'):
    href = link['href']
    if href.startswith('#'):
        assert page.find(id=href[1:])
    elif href.startswith('/crystal-clean-home/'):
        assert (root/'docs'/href.removeprefix('/crystal-clean-home/')/'index.html').exists()
for img in main.select('img'):
    path = root/'docs'/urlsplit(img['src']).path.removeprefix('/crystal-clean-home/')
    assert path.exists(), path
    assert 'alt' in img.attrs
    if path.suffix != '.svg':
        with Image.open(path) as image:
            assert image.size == (int(img['width']),int(img['height']))
for img in main.select('picture source'):
    path = root/'docs'/urlsplit(img['srcset']).path.removeprefix('/crystal-clean-home/')
    with Image.open(path) as image:
        assert image.size == (int(img['width']),int(img['height']))
data = json.loads((root/'brand/first-lp/materials.json').read_text(encoding='utf-8'))
assert len(main.select('.js-compare-image')) == 2
for i, item in enumerate(data['cases']):
    panel = main.select('.c-tab__panel')[i]
    tab = main.select('.c-tab__button')[i]
    assert tab['aria-controls'] == panel['id']
    assert panel['aria-labelledby'] == tab['id']
    for img, state in zip(panel.select('.c-compare-image img'),('before','after')):
        assert (root/item[state]).read_bytes() == (root/'docs'/img['src'].removeprefix('/crystal-clean-home/')).read_bytes()
for card, item in zip(main.select('.lp-voice'),data['reviews']):
    title, body = REVIEW_COPY[item['category']][item['index']]
    assert card.h3.get_text() == title
    assert card.select_one('.c-voice-card__text').get_text() == body
assert '実際のお客様の口コミ・評価ではありません' in main.get_text()
home = BeautifulSoup((root/'brand/service-cards/template.html').read_text(encoding='utf-8'),'html.parser')
assert [str(n) for n in main.select('.lp-services>a')] == [str(n) for n in home.select('.c-house-cleaning-links__link')]
assert len(main.select('.c-step-list__item')) == 5
for item, expected in zip(main.select('.c-step-list__item'),FLOW_COPY):
    assert expected['heading'] in item.get_text()
    assert expected['body'] in item.get_text()
faq = BeautifulSoup(homepage_questions(root), 'html.parser')
for item, index in zip(main.select('.lp-faq details'),data['faq_indices']):
    assert item.select_one('.cch-faq-answer').get_text() == faq.select('details')[index].select_one('.cch-faq-answer').get_text()
comparison = json.loads((root/'brand/first-lp/comparison.json').read_text(encoding='utf-8'))
assert [n.get_text() for n in main.select('thead th')] == comparison['columns']
assert [[n.get_text() for n in row.select('th,td')] for row in main.select('tbody tr')] == comparison['rows']
assert len(comparison['sources']) == 6
assert all(s['links'] for s in comparison['sources'])
assert not any(word in main.get_text() for word in ('架空の会社','比較用サンプル','仮設定'))
assert len(page.select('[data-cch-first-lp]')) == 2
assert len(page.select('[data-cch-lp-script]')) == 2
assert page.select_one('link[rel=canonical]')['href'] == 'https://yasojima.github.io/crystal-clean-home/first/'
assert not main.select('form, iframe')
for path, digest in untouched.items():
    assert hashlib.sha256(Path(path).read_bytes()).hexdigest() == digest, path
print('PASS: LP regeneration; source reuse; 5 button-only CTAs; 4 unique scenes; 3 mobile manga; 8 menus; 2 sliders; 3 review entries; 5 steps/FAQ; sourced comparison; LP-only footer removal.')
