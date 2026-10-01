"""Check service page structure, catalogue preservation and internal navigation."""
from pathlib import Path
from urllib.parse import urljoin, urlsplit, unquote
from collections import Counter
from datetime import datetime, timezone
import json
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / 'source/site'
DATA = ROOT / 'source/service-pages'
catalogue = json.loads((DATA / 'catalogue.json').read_text(encoding='utf-8'))
errors = []


def soup(value):
    return BeautifulSoup(value, 'html.parser')


def fail(route, reason):
    errors.append({'page':route,'reason':reason})


def prices(node):
    return [n.get_text(' ',strip=True) for n in node.select('.c-price__text')]


def options(node):
    return [(n.select_one('input[name="product-id"]')['value'], prices(n))
            for n in node.select('[data-product-card="option"]') if n.select_one('input[name="product-id"]')]


all_pages = {}
for path in SITE.rglob('*.html'):
    all_pages['/' + path.relative_to(SITE).as_posix().removesuffix('index.html')] = soup(path.read_text(encoding='utf-8'))

for route,page in catalogue['pages'].items():
    doc = all_pages[f'/house-cleaning/{route}/']
    main = doc.select_one('main[data-service-layout="shared-v1"]')
    if not main:
        fail(route,'shared layout missing'); continue
    ordered = ['.c-page-heading','.c-house-cleaning-mv','.p-page-anchors','.c-issue-list','.p-reasons','#apply','.c-voice-card','.c-faq-accordion','.c-step-list']
    descendants = list(main.descendants)
    positions = [descendants.index(main.select_one(sel)) if main.select_one(sel) else -1 for sel in ordered]
    if -1 in positions or positions != sorted(positions): fail(route,'section order')
    ids = [n['id'] for n in main.select('[id]')]
    if len(ids) != len(set(ids)): fail(route,'duplicate IDs')
    if len(main.select('.c-faq-accordion__item')) != 5: fail(route,'FAQ count')
    if len(main.select('.c-step-list__item')) != 5: fail(route,'flow count')
    if 'Visa' not in main.select_one('#service-faq').get_text() or 'Mastercard' not in main.select_one('#service-flow').get_text(): fail(route,'payments')
    for link in main.select('a[href^="#"]'):
        if link['href'] != '#' and link['href'][1:] not in ids: fail(route,'missing anchor '+link['href'])
    for node in main.select('a,button'):
        if '詳しく見る' in node.get_text(): fail(route,'detail CTA remains')
    for img in main.select('img[src]'):
        if img['src'].startswith('/') and not (SITE / unquote(img['src']).lstrip('/')).is_file(): fail(route,'missing image '+img['src'])
    for img in main.select('.c-house-cleaning-mv img,.c-lineup-card__image img,.c-reasons__bg,.c-service-photo img'):
        if '/service-scenes/' not in img['src']: fail(route,'unreplaced photograph '+img['src'])
    expected = [key for group in page['groups'] for key in group['products']]
    actual = [n['id'].removeprefix('product') for n in main.select('.c-lineup-product')]
    if actual != expected: fail(route,'product sequence '+repr(actual))
    for key in expected:
        n = main.select_one(f'[id="product{key}"]')
        before = soup(catalogue['products'][key].get('html',catalogue['products'][key].get('detail_html','')))
        old_card = before.select_one('[data-product-card="parent"]')
        new_card = n.select_one('[data-product-card="parent"]')
        if prices(old_card) != prices(new_card): fail(route,'parent prices changed '+key)
        if options(before) != options(n) and key not in ['1071','1073','1074']: fail(route,'options changed '+key)
        old_types = before.select_one('.js-room-types'); new_types = n.select_one('.js-room-types')
        if bool(old_types) != bool(new_types) or (old_types and [(o.get('value'),o.get_text()) for o in old_types.select('option')] != [(o.get('value'),o.get_text()) for o in new_types.select('option')]): fail(route,'variants changed '+key)
        if old_types:
            for target in ['prices','counters','options']:
                a = before.select_one(f'[data-switch-target="{target}"]')
                b = n.select_one(f'[data-switch-target="{target}"]')
                if a and (not b or len(a.find_all(recursive=False)) != len(b.find_all(recursive=False))): fail(route,'variant panels changed '+key+' '+target)
    if '特許' in main.get_text() or 'おそうじ本舗' in main.get_text(): fail(route,'former brand or proprietary claim')
    for key in page['offers']:
        old_offer = soup(catalogue['offers'][key])
        new_offer = main.find(attrs={'data-service-offer':key})
        if new_offer is None or prices(old_offer) != prices(new_offer): fail(route,'set-plan prices changed '+key)
        elif [n['value'] for n in old_offer.select('input[name="product-id"]')] != [n['value'] for n in new_offer.select('input[name="product-id"]')]: fail(route,'set-plan products changed '+key)

target_paths = {f'/house-cleaning/{r}/' for r in catalogue['pages']}
for path,doc in all_pages.items():
    for a in doc.select('a[href]'):
        u = urlsplit(urljoin('https://yasojima.github.io'+path,a['href']))
        if u.netloc != 'yasojima.github.io' or not u.fragment or u.path not in target_paths: continue
        target = all_pages.get(u.path)
        if target and not target.find(id=unquote(u.fragment)): fail(path,'missing destination '+u.path+'#'+u.fragment)

report = {'checked_at':datetime.now(timezone.utc).isoformat(),'pages':len(catalogue['pages']),'products':len(catalogue['products']),'errors':errors,'passed':not errors}
(ROOT / 'source/service-pages-verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,ensure_ascii=False))
raise SystemExit(bool(errors))
