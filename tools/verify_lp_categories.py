"""Verify category ownership and PC/mobile estimate entry consistency."""
from pathlib import Path
import json
import re
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / 'source/site'
canonical = BeautifulSoup((ROOT / 'source/service-pages/templates/categories.html').read_bytes(), 'html.parser')

def cards(nodes, quick=False):
    return [dict(label=n.select_one('h3').get_text('', strip=True),
                 illustration=next(c for c in n.select_one('.c-illust')['class'] if c.startswith('c-illust--')),
                 href=n['href'].replace('/quick_cart/', '/house-cleaning/') if quick else n['href'],
                 badge=n.select_one('.c-ribbon-label-tag')['aria-label'] if n.select_one('.c-ribbon-label-tag') else None)
            for n in nodes]

expected = cards(canonical.select('a.c-category-simple-card'))
assert len(expected) == 8
lp = BeautifulSoup((SITE / 'beginner/index.html').read_bytes(), 'html.parser')
quick = BeautifulSoup((SITE / 'quick_cart/index.html').read_bytes(), 'html.parser')
assert cards(lp.select('.lp-services a.c-category-simple-card')) == expected
assert cards(quick.select('a.step__card'), True) == expected
ctas = lp.select('a.lp-estimate-button')
assert len(ctas) == 6 and all(n['href'] == '/quick_cart/' for n in ctas)
for name in ['first-lp-desktop.css', 'first-lp-mobile.css']:
    css = (SITE / 'assets/css' / name).read_text(encoding='utf-8')
    assert '/first-lp/categories/' not in css, name
    assert not re.search(r'#cch-first-lp[^{}]*\.c-illust[^{}]*\{', css), name
home = BeautifulSoup((SITE / 'index.html').read_bytes(), 'html.parser')
assert len(home.select('.home-first-guide__picture source')) == 2
for source in home.select('.home-first-guide__picture source'):
    assert source['media'] == '(max-width: 767.98px)'
    assert (SITE / source['srcset'].lstrip('/')).is_file()
assert not home.select('.home-guide-mobile')
report = dict(canonical_categories=expected, consumers=['beginner', 'quick_cart'],
              shared_illustration_css=True, shared_estimate_ctas=len(ctas), mobile_banner_sources=2)
out = ROOT / 'evidence/2026-10-06/lp-categories-estimate/static-inventory.json'
out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k!='canonical_categories'}, ensure_ascii=False))
