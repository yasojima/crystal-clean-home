"""Import the site's reusable service components into their shared source."""
from pathlib import Path
import json
from bs4 import BeautifulSoup, Comment

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / 'source/site'
DATA = ROOT / 'source/service-pages'
CATEGORIES = ['aircon', 'pack', 'water', 'washer', 'kitchen', 'room', 'coating', 'others']


def clean(node):
    node = BeautifulSoup(str(node), 'html.parser')
    for comment in node.find_all(string=lambda n: isinstance(n, Comment)):
        comment.extract()
    return str(node).strip()


def main():
    if (DATA / 'catalogue.json').exists():
        raise SystemExit('Shared catalogue already exists; edit the current source instead.')
    templates = DATA / 'templates'
    templates.mkdir(parents=True, exist_ok=True)
    kitchen = BeautifulSoup((SITE / 'house-cleaning/kitchen/index.html').read_text(encoding='utf-8'), 'html.parser')
    selectors = {
        'hero': '.c-house-cleaning-mv', 'navigation': '.p-page-anchors',
        'floating': '.c-floating-buttons', 'cart-modal': '#add-cart-modal',
    }
    for name, sel in selectors.items():
        (templates / (name + '.html')).write_text(clean(kitchen.select_one(sel)), encoding='utf-8')
    for name, sel in [('concerns', '.c-issue-list'), ('reasons', '.p-reasons'),
                      ('voices', '.c-voice-card'), ('faq', '.c-faq-accordion'),
                      ('steps', '.c-step-list')]:
        (templates / (name + '.html')).write_text(clean(kitchen.select_one(sel).find_parent('section')), encoding='utf-8')
    category_list = kitchen.select('main > section')[-1]
    (templates / 'categories.html').write_text(clean(category_list), encoding='utf-8')
    catalogue = {'products': {}, 'offers': {}, 'pages': {}}
    for cat in CATEGORIES:
        soup = BeautifulSoup((SITE / 'house-cleaning' / cat / 'index.html').read_text(encoding='utf-8'), 'html.parser')
        page = {'category': cat, 'title': soup.select_one('main h1').get_text(' ', strip=True), 'groups': [], 'offers': []}
        groups = {}
        for index, block in enumerate(soup.select('main .c-lineup-product')):
            card = block.select_one('.c-lineup-card')
            pid = card.select_one('input[name="product-id"]')
            key = pid['value'] if pid else cat + '-estimate-' + str(index)
            heading = block.find_previous(lambda n: n.name == 'h2' and ('c-lineup-heading' in n.get('class', []) or 'category-heading' in n.get('class', [])))
            gid = heading.get('id') if heading else None
            gid = gid or ('lineup-' + str(len(groups) + 1))
            title = heading.get_text(' ', strip=True).replace(' lineup', '') if heading else page['title']
            if title not in groups:
                groups[title] = {'id': gid, 'title': title, 'products': []}
            groups[title]['products'].append(key)
            link = card.select_one('.c-lineup-card__heading a[href]')
            description = card.select_one('.c-lineup-card__description')
            catalogue['products'][key] = {
                'category': cat, 'name': card.select_one('.c-lineup-card__heading').get_text(' ', strip=True),
                'route': link.get('href') if link else None,
                'description': description.get_text(' ', strip=True) if description else '',
                'html': clean(block),
            }
        page['groups'] = list(groups.values())
        offer_blocks = []
        for node in soup.select('main .js-product-card[data-product-card="set-plan"]'):
            if node.find_parent(class_='c-lineup-product'):
                continue
            node = node.find_parent(class_='c-plan-card') or node
            if any(node is previous for previous in offer_blocks):
                continue
            offer_blocks.append(node)
        for i, node in enumerate(offer_blocks):
            key = cat + '-offer-' + str(i + 1)
            catalogue['offers'][key] = clean(node)
            page['offers'].append(key)
        anchors = []
        for a in soup.select('.p-page-anchors .c-page-anchors__anchor'):
            icon = a.select_one('.c-illust')
            anchors.append({'href': a.get('href'), 'text': a.get_text(' ', strip=True), 'icon': icon.get('class', []) if icon else []})
        page['anchors'] = anchors
        catalogue['pages'][cat] = page
    for path in sorted((SITE / 'house-cleaning').rglob('index.html')):
        route = path.parent.relative_to(SITE / 'house-cleaning').as_posix()
        if route in CATEGORIES:
            continue
        soup = BeautifulSoup(path.read_text(encoding='utf-8'), 'html.parser')
        cards = soup.select('main .c-product-card')
        if not cards:
            continue
        cat = route.split('/')[0]
        keys = []
        for i, card in enumerate(cards):
            pid = card.select_one('input[name="product-id"]')
            key = pid['value'] if pid else cat + '-estimate-0'
            keys.append(key)
            if key not in catalogue['products']:
                catalogue['products'][key] = {
                    'category': cat, 'name': card.select_one('.c-product-card__heading').get_text(' ', strip=True),
                    'route': '/house-cleaning/' + route + '/', 'description': '',
                    'detail_html': clean(card),
                    'option_html': [clean(n) for n in soup.select('.js-product-card[data-product-card="option"]')],
                }
        catalogue['pages'][route] = {
            'category': cat, 'title': soup.select_one('main h1').get_text(' ', strip=True),
            'groups': [{'id': 'service-lineup', 'title': 'サービス内容・料金', 'products': keys}],
            'offers': [], 'anchors': [],
        }
    (DATA / 'catalogue.json').write_text(json.dumps(catalogue, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print({'pages': len(catalogue['pages']), 'products': len(catalogue['products']), 'offers': len(catalogue['offers'])})


if __name__ == '__main__':
    main()
