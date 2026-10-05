"""Compile cart prices and every selectable variant from the published markup."""
import argparse
import json
import re
from pathlib import Path

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / 'source/site'
OUTPUT = SITE / 'assets/js/cart-catalogue.js'


def text(node):
    return node.get_text(' ', strip=True) if node else ''


def prices(node):
    values = node.select('.c-price__text, .c-plan-price__text')
    values = [v for v in values if not v.find_parent('dialog')]
    if not values:
        assert 'ご相談ください' in text(node), text(node)[:200]
        return {'tiers': [], 'quote': True, 'approximate': False, 'unit': '式'}
    tiers = []
    for value in values:
        label = value.find_parent(attrs={'data-text': True})
        label = label.get('data-text', '') if label else ''
        threshold = re.search(r'(\d+)(?:台|セット)以上', label)
        minimum = int(threshold[1]) if threshold else 1
        digits = re.sub(r'[,\s]', '', text(value))
        match = re.fullmatch(r'(\d+)(?:[〜～~])?', digits)
        assert match, digits
        amount = int(match[1])
        assert amount > 0, digits
        tiers.append({'min': minimum, 'price': amount})
    assert len({t['min'] for t in tiers}) == len(tiers), tiers
    unit_node = values[0].parent.select_one('.c-price__unit, .c-plan-price__unit')
    unit_text = next(unit_node.stripped_strings, '') if unit_node else ''
    unit = re.split(r'[／/]', unit_text)[-1].strip() or '式'
    return {'tiers': sorted(tiers, key=lambda t: t['min']), 'quote': False,
            'approximate': any(re.search('[〜～~]', text(v)) for v in values), 'unit': unit}


def card_name(card):
    return text(card.select_one('.c-lineup-card__heading, .c-product-additional-card__heading, '
                                 '.c-simulation-product-card__heading, .c-product-card__heading, '
                                 '.c-option-card__heading, .product-card__heading, '
                                 '.c-plan-card-list-item__heading')) or text(card.select_one('h2,h3,h4,h5'))


def variants(card):
    selector = card.select_one('.js-room-types')
    pid = card.select_one('input[name="product-id"]')
    if not pid:
        wrapper = card.find_parent(id=re.compile(r'^product'))
        assert wrapper, text(card)[:100]
        return [(wrapper['id'].removeprefix('product'), '', card)]
    if not selector:
        return [(pid['value'], '', card)]
    container = card.select_one('[data-switch-target="prices"], .js-price')
    panels = container.find_all(recursive=False)
    options = selector.select('option')
    assert len(panels) == len(options)
    return [(o['value'], text(o), p) for o, p in zip(options, panels)]


def compile_catalogue():
    items, pages, occurrences = {}, {}, []
    extra_plans = json.loads((ROOT / 'source/service-pages/additional-plans.json').read_text(encoding='utf-8'))
    plan_parents = {p['id']: p['product'] for plans in extra_plans['products'].values() for p in plans}
    conflicts = []
    for path in sorted(SITE.rglob('*.html')):
        route = '/' + path.relative_to(SITE).as_posix().removesuffix('index.html')
        soup = BeautifulSoup(path.read_text(encoding='utf-8'), 'html.parser')
        cards = soup.select('.js-product-card')
        bindings = []
        for index, card in enumerate(cards):
            kind = card.get('data-product-card', 'parent')
            if kind == 'plan':
                continue
            entries = variants(card)
            parent_id = None
            if kind == 'option':
                wrapper = card.find_parent(class_='js-products')
                assert wrapper, (route, index, 'option parent')
                parent = wrapper.select_one('[data-product-card="parent"]')
                parent_variants = variants(parent)
                option_list = card.find_parent(class_='c-lineup-option-list')
                option_index = 0
                if option_list:
                    siblings = option_list.parent.find_all(class_='c-lineup-option-list', recursive=False)
                    option_index = next(i for i, sibling in enumerate(siblings) if sibling is option_list)
                parent_id = parent_variants[option_index][0]
            keys = []
            for pid, variant_name, price_node in entries:
                key = f'option:{parent_id}:{pid}' if kind == 'option' else f'{"plan" if kind == "set-plan" else "product"}:{pid}'
                name = card_name(card)
                if variant_name:
                    name += '：' + variant_name
                if kind == 'set-plan':
                    plan = card.find_parent(class_='c-plan-card')
                    heading = plan.select_one('h2,h3')
                    name = text(heading) + '：' + name
                assert name, (route, index, pid)
                record = dict(name=name, kind=kind, **prices(price_node), url=route)
                if (kind == 'parent' and pid in ('1', '2')) or (kind == 'set-plan' and pid.split('_')[0] in ('1', '2')):
                    record['quantityGroup'] = 'wall-aircon'
                if kind == 'option':
                    record['parentKey'] = 'product:' + parent_id
                if kind == 'set-plan':
                    record['includes'] = ['product:' + plan_parents.get(pid, pid.split('_')[0])]
                if key in items:
                    previous = items[key]
                    for field in ('tiers', 'quote', 'approximate'):
                        if previous[field] != record[field]:
                            conflicts.append((key, field, previous[field], record[field], previous['url'], route))
                else:
                    items[key] = record
                keys.append(key)
                occurrences.append(dict(route=route, index=index, key=key, **record))
            bindings.append(dict(index=index, keys=keys))
        if bindings:
            pages[route] = bindings
    assert not conflicts, json.dumps(conflicts, ensure_ascii=False, indent=2)
    for key, record in items.items():
        if record.get('parentKey'):
            assert record['parentKey'] in items, (key, record['parentKey'])
    return dict(taxRate=10, items=items, pages=pages), occurrences


def build(check=False):
    data, occurrences = compile_catalogue()
    output = 'window.CCH_CART_CATALOGUE = ' + json.dumps(data, ensure_ascii=False, separators=(',', ':')) + ';\n'
    changed = not OUTPUT.exists() or OUTPUT.read_text(encoding='utf-8') != output
    if changed and not check:
        OUTPUT.write_text(output, encoding='utf-8', newline='\n')
    print(json.dumps(dict(pages=len(data['pages']), items=len(data['items']),
                         selections=len(occurrences), quote=sum(v['quote'] for v in data['items'].values()),
                         changed=changed), ensure_ascii=False))
    if check and changed:
        raise SystemExit('Cart catalogue is out of date')
    return data, occurrences


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    build(parser.parse_args().check)
