"""Verify removal of detail routes without altering the retained purchase UI."""
import json
import subprocess
from pathlib import Path
from urllib.parse import urljoin, urlsplit
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / 'source/site'
DATA = ROOT / 'source/service-pages'
BASELINE = '479de41'
catalogue = json.loads((DATA / 'catalogue.json').read_text(encoding='utf-8'))
before = json.loads(subprocess.check_output(['git', 'show', f'{BASELINE}:source/service-pages/catalogue.json']))
removed = {f'/house-cleaning/{r}/' for r in before['pages'] if '/' in r}
assert len(catalogue['pages']) == 8 and not any('/' in r for r in catalogue['pages'])
scope = json.loads((ROOT / 'source/scope.json').read_text(encoding='utf-8'))
assert removed <= set(scope['excluded_exact_paths'])
for route in removed:
    assert not (SITE / route.strip('/') / 'index.html').exists(), route

destinations = {}
products = 0
for route in catalogue['pages']:
    rel = f'house-cleaning/{route}/index.html'
    old = BeautifulSoup(subprocess.check_output(['git','show',f'{BASELINE}:source/site/{rel}']), 'html.parser')
    new = BeautifulSoup((SITE / rel).read_bytes(), 'html.parser')
    assert not new.select('.c-lineup-card__image[href],.c-lineup-card__heading a[href]')
    for link in old.select('.c-lineup-card__image[href],.c-lineup-card__heading a[href]'):
        link.name = 'span'
        del link['href']
    assert str(old.main) == str(new.main), (route, 'content beyond image/title links changed')
    products += len(new.select('.c-lineup-card'))
    destinations[f'/house-cleaning/{route}/'] = new

checked_links = 0
pages = list(SITE.rglob('*.html'))
for path in pages:
    text = path.read_text(encoding='utf-8')
    doc = BeautifulSoup(text, 'html.parser')
    base = 'https://yasojima.github.io/' + path.relative_to(SITE).as_posix()
    for link in doc.select('[href]'):
        url = urlsplit(urljoin(base, link['href']))
        if url.netloc not in ['yasojima.github.io','www.osoujihonpo.com']: continue
        assert url.path not in removed, (str(path),link['href'])
        if url.path in destinations and url.fragment:
            assert destinations[url.path].find(id=url.fragment), (str(path),link['href'])
            checked_links += 1
    assert not any(r in text for r in removed), (str(path),'removed route remains in raw HTML')
assert not any(r in (SITE / 'sitemap.xml').read_text(encoding='utf-8') for r in removed)
assert (DATA / 'detail-faq.json').exists() is False
old_voices = json.loads(subprocess.check_output(['git','show',f'{BASELINE}:source/service-pages/voices.json']))['pages']
voices = json.loads((DATA / 'voices.json').read_text(encoding='utf-8'))['pages']
assert voices == {r:old_voices[r] for r in catalogue['pages']}
report = dict(passed=True, servicePages=8, removedDetailPages=len(removed), publicHtml=len(pages),
              preservedProducts=products, preservedReviews=sum(map(len,voices.values())), checkedAnchorLinks=checked_links,
              purchaseContentUnchanged=True, baseline=BASELINE)
out = ROOT / 'evidence/2026-10-04/category-only/static.json'
out.parent.mkdir(parents=True,exist_ok=True)
out.write_bytes((json.dumps(report,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
print(json.dumps(report))
