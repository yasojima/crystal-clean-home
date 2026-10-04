"""Verify new option coverage and preservation of every existing option list."""
import hashlib
import json
from pathlib import Path
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'source/service-pages'
EVIDENCE = ROOT / 'evidence/2026-10-04/service-options'
catalogue = json.loads((DATA / 'catalogue.json').read_text(encoding='utf-8'))
added = json.loads((DATA / 'additional-options.json').read_text(encoding='utf-8'))['products']
baseline = json.loads((EVIDENCE / 'existing-options-baseline.json').read_text(encoding='utf-8'))
checks = []
for route, page in catalogue['pages'].items():
    soup = BeautifulSoup((ROOT / 'source/site/house-cleaning' / route / 'index.html').read_text(encoding='utf-8'), 'html.parser')
    keys = [key for group in page['groups'] for key in group['products']]
    wrappers = soup.select('#apply > .c-lineup-products')
    assert len(keys) == len(wrappers), route
    for key, wrapper in zip(keys, wrappers):
        options = next((node for node in wrapper.select('.c-lineup-options')
                        if node.select_one('.c-product-additional-card')), None)
        assert options and options.select_one('.c-product-additional-card'), (route, key)
        previous = baseline.get(route + ':' + key)
        if previous:
            assert hashlib.sha256(str(options).encode()).hexdigest() == previous['hash'], (route, key, 'existing list changed')
            checks.append({'route': route, 'product': key, 'existingPreserved': True, 'cards': previous['cards']})
            continue
        assert key in added, (route, key)
        lists = options.select('.c-lineup-option-list')
        variant_count = len(wrapper.select('.js-room-types option')) or 1
        assert len(lists) == variant_count, (route, key, 'variant options missing')
        trigger = options.select_one('.c-lineup-options__accordion-trigger')
        assert trigger and trigger['aria-controls'] == options.select_one('.c-lineup-options__accordion-contents')['id']
        for option_list in lists:
            cards = option_list.select('.c-product-additional-card')
            assert len(cards) == len(added[key]) >= 2
            for record, card in zip(added[key], cards):
                assert card.select_one('.c-product-additional-card__heading').get_text(strip=True) == record['name']
                assert card.select_one('.c-price__text').get_text(strip=True) == f"{record['price']:,}"
                assert card.select_one('input[name="product-id"]')['value'] == record['id']
                assert card.select_one('.js-product-quantity select')
                assert card.select_one('.js-add-cart').has_attr('data-demo-dialog')
                assert (ROOT / 'source/site' / card.select_one('img')['src'].lstrip('/')).is_file()
        checks.append({'route': route, 'product': key, 'newCards': len(added[key]), 'variants': variant_count})
report = {'passed': True, 'pages': len(catalogue['pages']), 'newProducts': len(added), 'newOptions': sum(map(len, added.values())), 'existingListsPreserved': len(baseline), 'checks': checks}
(EVIDENCE / 'verification.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({k: v for k, v in report.items() if k != 'checks'}))
