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
voice_profiles = json.loads((DATA / 'voices.json').read_text(encoding='utf-8'))['pages']
added_options = json.loads((DATA / 'additional-options.json').read_text(encoding='utf-8'))['products']
errors = []
voice_headings = {}
voice_bodies = {}


def soup(value):
    return BeautifulSoup(value, 'html.parser')


def fail(route, reason):
    errors.append({'page':route,'reason':reason})


def prices(node):
    return [n.get_text(' ',strip=True) for n in node.select('.c-price__text,.c-plan-price__text')]


def options(node):
    return [(n.select_one('input[name="product-id"]')['value'], prices(n))
            for n in node.select('[data-product-card="option"]') if n.select_one('input[name="product-id"]')]


all_pages = {}
for path in SITE.rglob('*.html'):
    all_pages['/' + path.relative_to(SITE).as_posix().removesuffix('index.html')] = soup(path.read_text(encoding='utf-8'))

for route,page in catalogue['pages'].items():
    doc = all_pages[f'/house-cleaning/{route}/']
    main = doc.select_one('main[data-service-layout="shared-v2"]')
    if not main:
        fail(route,'shared layout missing'); continue
    if main.select('.c-lineup-card__image[href],.c-lineup-card__heading a[href]'):
        fail(route,'product image or heading still links to another page')
    ordered = [
        '.c-house-cleaning-mv','.p-page-anchors','.c-issue-list','.p-reasons',
        '#apply','.c-voice-card','.c-faq-accordion','.c-step-list']
    descendants = list(main.descendants)
    positions = [descendants.index(main.select_one(sel)) if main.select_one(sel) else -1 for sel in ordered]
    if -1 in positions or positions != sorted(positions): fail(route,'section order')
    if doc.select_one('.c-breadcrumbs') or main.select_one('.c-page-heading'):
        fail(route,'breadcrumb or pre-hero heading remains')
    if len(doc.select('#first-view')) != 1 or not main.select_one('.c-house-cleaning-mv--check h1'):
        fail(route,'first view or semantic page heading')
    if route not in voice_profiles or len(voice_profiles[route]) != 6:
        fail(route,'service voice profile')
    reason_items = main.select('.c-reasons__item')
    if len(reason_items) != 3 or not main.select_one('.c-reasons--navy') or any(
        len(item.select('.c-reasons__navy')) != 1 or item.select_one('.c-reasons__bg') or
        item.select_one('.c-reasons__navy img') for item in reason_items
    ):
        fail(route,'three plain navy panels')
    ids = [n['id'] for n in main.select('[id]')]
    if len(ids) != len(set(ids)): fail(route,'duplicate IDs')
    if len(main.select('.c-faq-accordion__item')) != 5: fail(route,'FAQ count')
    voice_section = main.select_one('.c-voice-card').find_parent('section') if main.select_one('.c-voice-card') else None
    expected_voice_heading = 'ご利用いただいたお客様の声'
    if not voice_section or voice_section.select_one('.c-section-heading__subtitle').get_text(strip=True) != expected_voice_heading:
        fail(route,'voice heading')
    elif len(voice_section.select('.c-voice-card')) != 6 or voice_section.select_one('.mt20'):
        fail(route,'voice card count or subtitle')
    elif any(not card.select_one('h3').get_text(strip=True) or not card.select_one('p').get_text(strip=True)
             for card in voice_section.select('.c-voice-card')):
        fail(route,'empty voice card')
    else:
        for card in voice_section.select('.c-voice-card'):
            if len(card.select_one('h3').get_text(strip=True)) > 22:
                fail(route,'voice heading too long beside logo')
            for value, seen, kind in ((card.select_one('h3').get_text(strip=True),voice_headings,'heading'),
                                      (card.select_one('p').get_text(strip=True),voice_bodies,'body')):
                if value in seen: fail(route,f'duplicate voice {kind} with {seen[value]}')
                seen[value] = route
    preview = voice_section and 'c-voice-section--bubble-preview' in voice_section.get('class', [])
    preview_css = doc.select_one('link[href^="/assets/css/aircon-voice-bubbles.css?v="]')
    if not preview or not preview_css or not voice_section.select_one('.c-voice-bubbles'):
        fail(route,'shared voice bubbles missing')
    else:
        profiles = voice_section.select('.c-voice-card__profile')
        ratings = [node.get('aria-label') for node in voice_section.select('.c-voice-card__stars')]
        if len(profiles) != 6 or ratings != [f"5つ星中{r['rating']}つ星" for r in voice_profiles[route]]:
            fail(route,'sample profile and rating layout')
        if voice_section.select_one('.c-voice-bubbles__note'):
            fail(route,'obsolete voice note remains')
        for card,record in zip(voice_section.select('.c-voice-card'),voice_profiles[route]):
            if card.select_one('h3').get_text(strip=True) != record['title'] or card.select_one('p').get_text(strip=True) != record['body'] or card.select_one('.c-voice-card__nickname').get_text(strip=True) != record['nickname']:
                fail(route,'voice source mismatch')
    concerns = main.select('.c-issue-card__text')
    if len(concerns) != 3 or any(len(node.select('br')) != 1 or not node.get_text().endswith('...') for node in concerns):
        fail(route,'concerns not two lines ending ...')
    introduction_heading = main.select_one('#service-introduction .p-content-box__heading')
    if not introduction_heading or len(introduction_heading.select('br')) != 1 or not introduction_heading.get_text().endswith('！'):
        fail(route,'introduction heading punctuation')
    for node in main.select('.c-product-additional-card__description'):
        if node.select('br,p') or not node.get_text(strip=True): fail(route,'option description format')
    for question in main.select('.c-faq-accordion__trigger'):
        value = question.get_text(strip=True)
        if value.endswith('か') or value.endswith(('。','、')): fail(route,'FAQ punctuation '+value)
    if len(main.select('.c-step-list__item')) != 5: fail(route,'flow count')
    faq_text = main.select_one('#service-faq').get_text()
    flow_text = main.select_one('#service-flow').get_text()
    if not all(method in faq_text for method in ('Visa', 'Mastercard')) or 'お支払い' not in flow_text: fail(route,'payments')
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
        expected_options = options(before)
        if key in added_options:
            variants = len(n.select('.js-room-types option')) or 1
            expected_options += [(record['id'], [f"{record['price']:,}"])
                                 for _ in range(variants) for record in added_options[key]]
        if expected_options != options(n) and key not in ['1071','1073','1074']: fail(route,'options changed '+key)
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
        # CHG-035 keeps at most two product tabs; the legacy sets occupy a tab
        # only when the page has fewer than two normal product choices.
        if page['category'] != 'aircon' and len(set(expected)) >= 2:
            if new_offer is not None: fail(route,'legacy sets exceed the two-tab limit '+key)
            continue
        if new_offer is None or prices(old_offer) != prices(new_offer): fail(route,'set-plan prices changed '+key)
        elif [n['value'] for n in old_offer.select('input[name="product-id"]')] != [n['value'] for n in new_offer.select('input[name="product-id"]')]: fail(route,'set-plan products changed '+key)
    if route == 'aircon':
        plan = main.select_one('#service-sets.l-section--blue-bubbles')
        panels = plan.select('.recommend-plan__tab .c-tab__panel') if plan else []
        if len(panels) != 2 or [len(panel.select('.recommend-plan-cards > .c-plan-card')) for panel in panels] != [2, 1]:
            fail(route,'offer card layout')

if set(voice_profiles) != set(catalogue['pages']): fail('voices','profile routes do not match pages')

reason_pages = {path:doc for path,doc in all_pages.items() if doc.select_one('.p-reasons')}
if len(reason_pages) != len(catalogue['pages']) + 4: fail('reasons','service pages and four shared reason sections expected')
for path,doc in reason_pages.items():
    cards = doc.select('.c-reasons--navy .c-reasons__item')
    if len(cards) != 3 or doc.select('.c-reasons__bg') or any(
        len(card.select('.c-reasons__navy')) != 1 or card.select_one('.c-reasons__navy img')
        for card in cards
    ) or not doc.select_one('link[href="/assets/css/reasons-navy.css?v=2026100211"]'):
        fail(path,'sitewide plain navy reason section')

target_paths = {f'/house-cleaning/{r}/' for r in catalogue['pages']}
for path,doc in all_pages.items():
    if doc.select('.c-footer-bottom-nav__copyright,.business-footer__copyright'):
        fail(path,'footer site name remains')
    for a in doc.select('a[href]'):
        u = urlsplit(urljoin('https://yasojima.github.io'+path,a['href']))
        if u.netloc != 'yasojima.github.io' or not u.fragment or u.path not in target_paths: continue
        target = all_pages.get(u.path)
        if target and not target.find(id=unquote(u.fragment)): fail(path,'missing destination '+u.path+'#'+u.fragment)

report = {'checked_at':datetime.now(timezone.utc).isoformat(),'pages':len(catalogue['pages']),'reason_pages':len(reason_pages),'products':len(catalogue['products']),'errors':errors,'passed':not errors}
(ROOT / 'source/service-pages-verification.json').write_bytes((json.dumps(report,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
print(json.dumps(report,ensure_ascii=False))
raise SystemExit(bool(errors))
