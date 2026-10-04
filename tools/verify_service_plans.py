"""Verify plan coverage, real option references and preserved existing purchases."""
import json
import subprocess
from pathlib import Path
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'source/service-pages'
catalogue = json.loads((DATA / 'catalogue.json').read_text(encoding='utf-8'))
plans = json.loads((DATA / 'additional-plans.json').read_text(encoding='utf-8'))['products']
checks = []
unique = set()
existing = 0

def purchases(card):
    return {
        'ids': [n['value'] for n in card.select('input[name="product-id"]')],
        'prices': [n.get_text(strip=True) for n in card.select('.c-plan-price__text')],
        'quantities': [[n['value'] for n in select.select('option')]
                       for select in card.select('.js-product-quantity select')],
    }

for route, page in catalogue['pages'].items():
    soup = BeautifulSoup((ROOT / 'source/site/house-cleaning' / route / 'index.html').read_text(encoding='utf-8'), 'html.parser')
    baseline = BeautifulSoup(subprocess.check_output(['git', 'show', 'a16ce14:source/site/house-cleaning/' + route + '/index.html']).decode('utf-8'), 'html.parser')
    section = soup.select_one('#apply > section:has([data-service-offer])')
    assert section, route
    assert section.select_one('.c-bracket-heading__text').get_text(strip=True) == '人気の組み合わせプラン'
    for old in baseline.select('[data-service-offer]'):
        current = section.select_one('[data-service-offer="' + old['data-service-offer'] + '"]')
        assert current and purchases(current) == purchases(old), (route, 'existing purchase changed')
        existing += 1
    keys = [key for group in page['groups'] for key in group['products']]
    if page['category'] == 'aircon':
        checks.append({'route': route, 'usesExistingAirconPlans': True})
        continue
    wrappers = soup.select('#apply > .c-lineup-products')
    for key, product in zip(keys, wrappers):
        available = {card.select_one('input[name="product-id"]')['value']
                     for card in product.select('.c-product-additional-card')}
        cards = section.select('[data-plan-product="' + key + '"]')
        assert len(cards) == len(plans[key]) == 2, (route, key)
        for card, record in zip(cards, plans[key]):
            assert card['data-demo-plan'] == record['id']
            unique.add(record['id'])
            assert card.select_one('.c-plan-card-detail__image')
            assert len(card.select('.c-plan-card-list-item')) == 1
            assert card.select_one('.c-plan-card-list-item__heading').get_text(strip=True) == record['label']
            assert card.select_one('.js-add-cart').has_attr('data-demo-dialog')
            assert purchases(card)['prices'] == [f"{record['price']:,}", f"{record['multi_price']:,}"]
            assert record['price'] > record['multi_price'] > 0
            assert all(option['id'] in available and option['quantity'] > 0 for option in record['options']), (route, key, 'option missing')
            assert [n.get_text(strip=True) for n in card.select('.c-plan-card-detail__option')] == [o['name'] + (f" ×{o['quantity']}" if o['quantity'] > 1 else '') for o in record['options']]
            assert (ROOT / 'source/site' / card.select_one('img')['src'].lstrip('/')).is_file()
        checks.append({'route': route, 'product': key, 'newPlans': 2})
assert len(unique) == sum(map(len, plans.values())) == 86
report = {'passed': True, 'pages': len(catalogue['pages']), 'newProducts': len(plans), 'newPlans': len(unique), 'existingPurchasesPreserved': existing, 'checks': checks}
out = ROOT / 'evidence/2026-10-04/service-plans'
out.mkdir(parents=True, exist_ok=True)
(out / 'verification.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({key: value for key, value in report.items() if key != 'checks'}))
