"""Build service pages from shared, existing site components and service data."""
from pathlib import Path
from copy import deepcopy
import argparse
import hashlib
import json
import re
from bs4 import BeautifulSoup
from build_shared_ui import transform as shared_ui

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / 'source/site'
DATA = ROOT / 'source/service-pages'
AIRCON_COMPARISONS = json.loads((DATA / 'aircon-comparisons.json').read_text(encoding='utf-8'))
SERVICE_COMPARISONS = json.loads((DATA / 'service-comparisons.json').read_text(encoding='utf-8'))
ADDITIONAL_OPTIONS = json.loads((DATA / 'additional-options.json').read_text(encoding='utf-8'))['products']
ADDITIONAL_PLANS = json.loads((DATA / 'additional-plans.json').read_text(encoding='utf-8'))['products']
STATIC_REASONS = ('index.html', 'about/index.html', 'quick_cart/option/index.html',
                  'lab/online_store/detergent/product-303/index.html')
NAVY_STYLESHEET = '<link rel="stylesheet" href="/assets/css/reasons-navy.css?v=2026100211">'


def parse(value):
    return BeautifulSoup(value, 'html.parser')


def tag(name, classes=None, text=None, **attrs):
    n = BeautifulSoup('', 'html.parser').new_tag(name, attrs=attrs)
    if classes:
        n['class'] = classes.split()
    if text is not None:
        n.string = text
    return n


def template(name):
    return parse((DATA / 'templates' / f'{name}.html').read_text(encoding='utf-8')).find()


def lines(node, values):
    node.clear()
    for i, value in enumerate(values):
        if i:
            node.append(tag('br'))
        node.append(value)


def image(node, scene, alt, eager=False):
    node['src'] = f'/assets/images/service-scenes/{scene}.webp'
    node['alt'] = alt
    node['width'], node['height'] = '1536', '1024'
    node['loading'] = 'eager' if eager else 'lazy'
    node['decoding'] = 'async'
    node.attrs.pop('srcset', None)


def normalize_text(root):
    replacements = {
        '防カビチタンコーティング': '防カビコーティング',
        'エコ洗浄': '低刺激洗剤による洗浄',
        '特殊汚れ/強い汚れ/追加範囲_0.5㎡ごとに': '強い汚れ・追加範囲（0.5㎡ごと）',
        '一坪(3,3㎡)以上の場合、1㎡ごとに': '1坪（3.3㎡）を超える場合（追加1㎡）',
        'フローリング補修（リペア）※': 'フローリング補修（リペア）',
    }
    for text in list(root.find_all(string=True)):
        value = str(text)
        for old, new in replacements.items():
            value = value.replace(old, new)
        if value != str(text):
            text.replace_with(value)
    for heading in root.select('h1,h2,h3,h4,h5'):
        if {'c-faq-accordion__heading', 'c-issue-list__heading'} & set(heading.get('class', [])):
            continue
        for text in list(heading.find_all(string=True)):
            if text.strip():
                text.replace_with(str(text).replace('？', '').rstrip('。'))


def remove_details(root):
    for node in list(root.select('a,button')):
        if '詳しく見る' in node.get_text():
            node.decompose()
    for dialog in root.select('dialog'):
        dialog.decompose()
    for foot in root.select('.c-lineup-card__foot,.c-product-additional-card__foot,.c-set-plan-card__foot'):
        base = next(c for c in foot['class'] if c.endswith('__foot'))
        modifier = base + '--no-detail'
        if modifier not in foot['class']:
            foot['class'].append(modifier)


def enrich(catalogue):
    changed = False
    for route in catalogue['pages']:
        soup = parse((SITE / 'house-cleaning' / route / 'index.html').read_text(encoding='utf-8'))
        if soup.select_one('main[data-service-layout]'):
            continue
        for card in soup.select('main .c-product-card'):
            pid = card.select_one('input[name="product-id"]')
            if not pid or pid['value'] not in catalogue['products']:
                continue
            p = catalogue['products'][pid['value']]
            scopes = [n.get_text(' ', strip=True) for n in card.select('.c-product-card-list__description')]
            if scopes:
                p['scope'] = scopes
                changed = True
    if changed:
        (DATA / 'catalogue.json').write_text(json.dumps(catalogue, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def extra_product(key, catalogue):
    record = catalogue['products'][key]
    detail = parse(record['detail_html'])
    block = parse(catalogue['products']['1071']['html']).find()
    block['id'] = f'product{key}'
    block.select_one('input[name="product-id"]')['value'] = key
    block.select_one('.c-lineup-card__heading a').string = record['name']
    block.select_one('.c-lineup-card__price-item').clear()
    block.select_one('.c-lineup-card__price-item').append(deepcopy(detail.select_one('.c-price')))
    timing = detail.select_one('.c-product-card-list__time')
    if timing:
        block.select_one('.c-lineup-card__time-description').string = timing.get_text(' ', strip=True)
    for n in block.select('.c-lineup-options'):
        n.decompose()
    return block


def entrance_options(block, key, catalogue):
    records = catalogue['products']['1073']['option_html']
    option = next(parse(v).find() for v in records if f'value="{"1151" if key == "1074" else "1150"}"' in v)
    source = parse(catalogue['products']['696']['html'])
    container = deepcopy(source.select_one('.c-lineup-options'))
    list_node = container.select_one('.c-lineup-options__cards')
    if list_node is None:
        list_node = container.select_one('.c-grid')
    original = source.select_one('.c-product-additional-card')
    card = deepcopy(original)
    card.select_one('.c-product-additional-card__heading').clear()
    card.select_one('.c-product-additional-card__heading').append(option.select_one('.c-option-card__heading').get_text(' ', strip=True))
    card.select_one('input[name="product-id"]')['value'] = option.select_one('input[name="product-id"]')['value']
    current_price = card.select_one('.c-price')
    current_price.replace_with(deepcopy(option.select_one('.c-price')))
    illustration = card.select_one('img')
    if illustration:
        illustration['src'] = '/assets/images/common-parts/illust/entrance.svg'
        illustration['alt'] = ''
    list_node.clear()
    list_node.append(card)
    block.append(container)


def add_missing_options(block, key, catalogue):
    if block.select_one('.c-product-additional-card'):
        assert key not in ADDITIONAL_OPTIONS, f'Existing options must remain unchanged: {key}'
        return
    options = ADDITIONAL_OPTIONS[key]
    assert len(options) >= 2
    source = parse(catalogue['products']['696']['html'])
    container = deepcopy(source.select_one('.c-lineup-options'))
    container.select_one('.c-lineup-options__accordion-trigger')['aria-controls'] = 'additional-options'
    container.select_one('.c-lineup-options__accordion-contents')['id'] = 'additional-options'
    grid = container.select_one('.c-lineup-option-list__contents')
    original = deepcopy(grid.select_one('.c-product-additional-card'))
    grid.clear()
    for option in options:
        card = deepcopy(original)
        card['data-demo-option'] = option['id']
        card.select_one('.c-product-additional-card__heading').string = option['name']
        card.select_one('.c-price__text').string = f"{option['price']:,}"
        card.select_one('.c-price__unit').string = ' (税込)／' + option['unit']
        description = card.select_one('.c-additional-option-card__description')
        description['class'] = ['c-product-additional-card__description']
        description.string = option['description']
        img = card.select_one('img')
        img['src'] = SERVICE_COMPARISONS[option['scene']][option['state']]
        img['alt'] = option['name'] + 'の作業イメージ'
        img['width'], img['height'] = '72', '72'
        img['style'] = 'width:72px;height:72px;object-fit:cover;'
        img['decoding'] = 'async'
        card.select_one('input[name="product-id"]')['value'] = option['id']
        card.select_one('.js-add-cart')['data-demo-dialog'] = ''
        grid.append(card)
    variants = block.select('.js-room-types option')
    option_list = container.select_one('.c-lineup-option-list')
    for _ in variants[1:]:
        other = deepcopy(option_list)
        other['class'] = ['c-lineup-option-list']
        option_list.parent.append(other)
    for old in block.select('.c-lineup-options'):
        old.decompose()
    block.append(container)


def product(key, route, catalogue, copy):
    record, content = catalogue['products'][key], copy['products'][key]
    block = parse(record['html']).find() if 'html' in record else extra_product(key, catalogue)
    block['id'] = f'product{key}'
    card = block.select_one('.c-lineup-card')
    heading = card.select_one('.c-lineup-card__heading')
    heading.name = 'h3'
    description = card.select_one('.c-lineup-card__description')
    if not description:
        description = tag('p', 'c-lineup-card__description')
        (card.select_one('.c-lineup-card__room-select') or heading).insert_after(description)
    description.string = content['description']
    for img in card.select('.c-lineup-card__image img'):
        image(img, content['scene'], content['focus'] + 'の清掃イメージ')
        if route == 'aircon' and key in AIRCON_COMPARISONS:
            img['src'] = AIRCON_COMPARISONS[key]['after']
    if record.get('scope') and not any(label in card.get_text() for label in ('サービス範囲', 'コーティング範囲')):
        scope = tag('p', 'c-note c-service-scope', 'サービス範囲：' + '／'.join(record['scope']))
        description.insert_after(scope)
    for a in card.select('.c-lineup-card__image,.c-lineup-card__heading a'):
        if a.name == 'a':
            a.name = 'span'
            a.attrs.pop('href', None)
    if key in ['1071', '1073', '1074']:
        entrance_options(block, key, catalogue)
    option_copy = json.loads((DATA / 'option-copy.json').read_text(encoding='utf-8'))
    for node in block.select('.c-additional-option-card__description,.c-product-additional-card__description'):
        original = node.get_text(' ', strip=True)
        if original in option_copy:
            node['class'] = ['c-product-additional-card__description']
            node.string = option_copy[original]
        else:
            raise ValueError(f'Option copy missing for {key}: {original}')
    remove_details(block)
    add_missing_options(block, key, catalogue)
    for button in block.select('.c-lineup-card__foot > .js-add-cart'):
        control_class = ('c-product-additional-card__detail-button'
                         if button.name == 'a' and not button.parent.select_one('.js-product-quantity')
                         else 'c-product-additional-card__cart-button')
        if control_class not in button['class']:
            button['class'].append(control_class)
    normalize_text(block)
    for node in block.select('[id]'):
        node['id'] = f'{key}-{node["id"]}'
    for node in block.select('[aria-controls]'):
        node['aria-controls'] = f'{key}-{node["aria-controls"]}'
    wrapper = tag('div', 'c-lineup-products js-products')
    wrapper.append(block)
    return wrapper


OFFER_IMAGES = {'kitchen-fan':'kitchen-fan','kitchen':'kitchen-sink','bath':'bathroom','bath-fan':'bath-dryer','sink':'lavatory','pipe':'bath-pipe','ulblo':'bath-adapter','toilet':'toilet','wallpaper-dyeing-cloth':'wallpaper-dyeing'}
OFFER_COPY = {
    '666_479': 'レンジフードの部品とキッチンをまとめて清掃します。換気扇の油汚れからシンクの水アカまで、それぞれに合う方法で丁寧に洗浄します。',
    'bath-dryer': '浴室と浴室乾燥機をまとめて清掃します。浴槽や床の水アカだけでなく、乾燥機の内部にたまったホコリも確認して取り除きます。',
    'lavatory': '浴室と洗面台の汚れをまとめてお掃除します。皮脂汚れや水アカを素材に合った方法で落とし、毎日使う水まわりを清潔に整えます。',
    'bath-pipe': '浴室の表面と追い焚き配管をまとめて清掃します。浴槽や床の汚れを落とした後、普段は手が届かない配管内部も洗浄します。',
    'adapter': '浴室を丁寧に清掃し、対応する循環アダプターを取り付けます。給湯設備との適合を確認してから交換し、最後に動作を点検します。',
    'wall': 'トイレの清掃と壁紙の染色を組み合わせたサービスです。便器や床を清掃し、壁紙の状態を確認したうえで室内の色合いを整えます。',
}
AIRCON_OFFER_COPY = {
    'aircon-offer-1': '通常のお掃除に完全分解洗浄を加え、取り外せる部品と内部の汚れを丁寧に洗い流します。機種と設置状況を確認して作業範囲をご案内します。',
    'aircon-offer-2': '完全分解洗浄に防虫キャップと防カビコーティングを組み合わせたプランです。洗浄後の状態を確認し、それぞれの施工内容をご案内します。',
    'aircon-offer-3': '天井埋め込みタイプの清掃に防カビコーティングを組み合わせます。機種や設置状況を確認し、対応できる作業を事前にご案内します。',
}


def offer(key, catalogue):
    n = parse(catalogue['offers'][key]).find()
    n['data-service-offer'] = key
    old_sources = [i['src'] for i in n.select('img')]
    for img in n.select('img'):
        basename = Path(img['src']).stem
        if basename in OFFER_IMAGES:
            image(img, OFFER_IMAGES[basename], '')
    desc = n.select_one('.c-set-plan-card__description')
    if desc:
        joined = ' '.join(old_sources)
        which = ('666_479' if 'kitchen-fan' in joined else 'bath-dryer' if 'bath-fan' in joined else
                 'lavatory' if '/sink.' in joined else 'adapter' if 'ulblo' in joined else 'wall' if 'wallpaper' in joined else 'bath-pipe')
        desc.string = OFFER_COPY[which]
    for desc in n.select('.c-plan-card__description'):
        desc.string = AIRCON_OFFER_COPY[key]
    for label in n.select('.c-set-plan-card__label'):
        if '悪臭' in label.get_text():
            label.string = 'トイレと壁紙をまとめてお手入れ'
    remove_details(n)
    normalize_text(n)
    if n.select_one('.c-set-plan-card__heading'):
        source = n
        n = tag('div', 'c-plan-card js-product-card', **{'data-product-card': 'plan', 'data-service-offer': key})
        title = source.select_one('.c-set-plan-card__heading').extract()
        title.name = 'h3'; title['class'] = ['c-plan-card__heading']
        for br in title.select('br'):
            br.attrs.clear()
        if key == 'pack-offer-5':
            title.clear()
            for index, line in enumerate(('浴室クリーニング・', '浴室用アダプター', '取り付けセット')):
                if index:
                    title.append(tag('br'))
                title.append(line)
        n.append(title)
        body = tag('div', 'c-plan-card__body')
        detail = deepcopy(parse(catalogue['offers']['aircon-offer-1']).select_one('.c-plan-card-detail'))
        picture = detail.select_one('img')
        base_scene = OFFER_IMAGES[Path(old_sources[0]).stem]
        picture['src'] = SERVICE_COMPARISONS[base_scene]['after']
        picture['alt'] = title.get_text(' ', strip=True) + 'の基本サービス'
        picture['style'] = 'width:80px;height:auto;aspect-ratio:1;object-fit:cover;'
        option_labels = {'kitchen': 'キッチンクリーニング', 'bath-fan': '浴室乾燥機クリーニング',
                         'sink': '洗面台クリーニング', 'pipe': '追い焚き配管クリーニング',
                         'ulblo': '浴室用アダプター取り付け', 'wallpaper-dyeing-cloth': '壁紙染色'}
        detail.select_one('.c-plan-card-detail__option').string = option_labels[Path(old_sources[1]).stem]
        body.append(detail)
        description = source.select_one('.c-set-plan-card__description').extract()
        description['class'] = ['c-plan-card__description']
        body.append(description); n.append(body)
        items = tag('ul', 'c-plan-card__list c-plan-card-list')
        item = tag('li', 'c-plan-card__item c-plan-card-list-item js-product-card', **{'data-product-card': 'set-plan'})
        label = source.select_one('.c-set-plan-card__label')
        if label:
            for br in label.select('br'):
                br.replace_with('\n')
            for line in label.get_text().splitlines():
                if line.strip():
                    item.append(tag('p', 'c-plan-card-list-item__discount', line.strip()))
        head = tag('div', 'c-plan-card-list-item__head')
        price = source.select_one('.c-set-plan-card__price').extract()
        price['class'] = ['c-plan-card-list-item__price']
        for node in price.select('.c-price,.c-price__text,.c-price__unit'):
            node['class'] = [c.replace('c-price', 'c-plan-price', 1) for c in node['class']]
        head.append(price); item.append(head)
        controls = tag('div', 'c-plan-card-list-item__body')
        quantity = source.select_one('.js-product-quantity').extract()
        quantity['class'] = ['c-card-select', 'c-plan-card-list-item__quantity', 'js-product-quantity']
        button = source.select_one('.js-add-cart').extract()
        button['class'] = ['c-button', 'c-button--fill-red', 'c-plan-card-list-item__cart-button', 'js-add-cart']
        controls.append(quantity); controls.append(button); item.append(controls)
        for hidden in source.select('input[name="product-id"]'):
            item.append(hidden.extract())
        items.append(item); n.append(items)
    return n


def additional_plan(record, catalogue, copy):
    card = parse(catalogue['offers']['aircon-offer-1']).find()
    card['data-service-offer'] = record['id']
    card['data-demo-plan'] = record['id']
    card['data-plan-product'] = record['product']
    card.select_one('.c-plan-card__heading').string = record['name']
    if record['id'].endswith('-2'):
        card.select_one('.c-plan-card__label').decompose()
    picture = card.select_one('.c-plan-card-detail__image')
    picture['src'] = SERVICE_COMPARISONS[copy['products'][record['product']]['scene']]['after']
    picture['alt'] = copy['products'][record['product']]['short'] + 'の作業イメージ'
    picture['style'] = 'width:80px;height:auto;aspect-ratio:1;object-fit:cover;'
    picture['decoding'] = 'async'
    options = card.select_one('.c-plan-card-detail__options')
    options.clear()
    for option in record['options']:
        suffix = f" ×{option['quantity']}" if option['quantity'] > 1 else ''
        options.append(tag('p', 'c-plan-card-detail__option', option['name'] + suffix))
    card.select_one('.c-plan-card__description').string = record['description']
    items = card.select_one('.c-plan-card-list')
    item = deepcopy(items.select_one('.c-plan-card-list-item'))
    items.clear()
    discounts = item.select('.c-plan-card-list-item__discount')
    discounts[0].string = '2セット以上ご注文でお得！'
    discounts[1].decompose()
    item.select_one('.c-plan-card-list-item__heading').string = record['label']
    for row, price, label in zip(item.select('.c-plan-multi-discount-price__item'),
                                 [record['price'], record['multi_price']],
                                 ['1セットご注文時', '2セット以上ご注文時']):
        row['data-text'] = label
        row.select_one('.c-plan-price__text').string = f'{price:,}'
    item.select_one('input[name="product-id"]')['value'] = record['id']
    item.select_one('.js-add-cart')['data-demo-dialog'] = ''
    items.append(item)
    return card


def additional_plans_section(page, route, catalogue, copy):
    section = template('aircon-offers')
    section['id'] = 'anchor00' if route == 'pack' else 'service-sets'
    section.select_one('.recommend-plan__text').decompose()
    heading = section.select_one('.recommend-plan__heading')
    heading.clear()
    heading.append(tag('span', 'c-bracket-heading__text', '人気の組み合わせプラン'))
    buttons = section.select_one('.c-tab__buttons')
    panels = section.select_one('.c-tab__panels')
    button, panel = deepcopy(buttons.find('button')), deepcopy(panels.select_one('.c-tab__panel'))
    buttons.clear(); panels.clear()
    keys = list(dict.fromkeys(key for group in page['groups'] for key in group['products']))
    if len(keys) > 2:
        representatives = [group['products'][0] for group in page['groups']]
        keys = list(dict.fromkeys(representatives + keys))[:2]
    subjects = [(ADDITIONAL_PLANS[key][0]['tab_lines'], [additional_plan(r, catalogue, copy) for r in ADDITIONAL_PLANS[key]]) for key in keys]
    if page['offers'] and len(subjects) < 2:
        subjects.append((['お得なセット'], [offer(key, catalogue) for key in page['offers']]))
    for index, (labels, cards) in enumerate(subjects):
        b, box = deepcopy(button), deepcopy(panel)
        bid, pid = f'service-plan-button-{index+1}', f'service-plan-panel-{index+1}'
        b['id'], b['aria-controls'], b['aria-selected'], b['tabindex'] = bid, pid, str(index == 0).lower(), '0' if index == 0 else '-1'
        b.clear()
        span = tag('span')
        lines(span, labels)
        for br in span.select('br'):
            br['class'] = ['u-sp-only']
        b.append(span)
        box['id'], box['aria-labelledby'] = pid, bid
        box['class'] = ['c-tab__panel'] + (['is-active'] if index == 0 else [])
        box['tabindex'] = '0' if index == 0 else '-1'
        grid = box.select_one('.recommend-plan-cards')
        grid.clear()
        for card in cards:
            grid.append(card)
        buttons.append(b); panels.append(box)
    return section


def navigation(page, primary, category, copy):
    n = template('navigation')
    n.select_one('h2').string = 'ご希望のサービスをお選びください' if '/' not in page['route'] else 'ご覧になりたい内容をお選びください'
    cards = n.select_one('.c-page-anchors')
    if page.get('selector_columns_pc'):
        cards['style'] = cards.get('style', '').replace('repeat(auto-fit, minmax(228px,228px))', f"repeat({page['selector_columns_pc']}, minmax(0,228px))")
    if page['route'] == 'aircon':
        cards['style'] = cards.get('style', '').replace('repeat(3,1fr)', 'repeat(2,minmax(0,1fr))')
    sample = deepcopy(cards.select_one('a'))
    cards.clear()
    items = page['anchors'][:]
    if not items:
        if '/' in page['route']:
            items = [{'href':'#service-introduction','text':'お掃除のポイント','icon':[]}, {'href':'#service-lineup','text':'サービス内容・料金','icon':[]}, {'href':'#service-faq','text':'よくある質問','icon':[]}]
        else:
            items = [{'href':'#'+g['id'],'text':g['title'],'icon':[]} for g in page['groups']]
    icon_map = {'aircon':'aircon','pack':'pack','water':'bath','washer':'washing-machine','kitchen':'kitchen','room':'room','coating':'coating','others':'other'}
    for item in items:
        a = deepcopy(sample)
        a['href'] = item['href']
        label = item['text']
        if page['route'] == 'aircon':
            label = {'#lineup01': '壁掛けタイプ', '#lineup02': '天井埋め込みタイプ'}.get(item['href'], label)
        a.select_one('h3').string = label
        icon = a.select_one('.c-illust')
        if icon:
            icon['class'] = item['icon'] or ['c-illust',f'c-illust--{icon_map[category]}','c-category-simple-card__icon']
        cards.append(a)
    cards['style'] = cards.get('style', '').replace('repeat(3,1fr)', 'repeat(2,minmax(0,1fr))')
    container = tag('div', 'l-section l-section--limited c-service-selector')
    inner = tag('div', 'l-section-inner l-section-inner--limited')
    inner.append(n); container.append(inner)
    return container


def concerns(page, primary, category_copy, copy):
    n = template('concerns'); n['id'] = 'service-introduction'
    content = copy['products'][primary]
    issues = category_copy['concerns']
    n.select_one('.c-issue-list__heading').string = 'こんなお悩みはありませんか？'
    for node, (first, second) in zip(n.select('.c-issue-card__text'), issues):
        node.clear()
        node.append(first)
        node.append(tag('br'))
        node.append(second)
    heading = category_copy['heading']
    lines(n.select_one('.p-content-box__heading'), [*heading[:-1], heading[-1].rstrip('！!') + '！'])
    subjects = category_copy['subjects']
    buttons = n.select_one('.c-tab__buttons'); panels = n.select_one('.c-tab__panels')
    button, panel = deepcopy(buttons.find('button')), deepcopy(panels.select_one('.c-tab__panel'))
    buttons.clear(); panels.clear()
    for index, key in enumerate(subjects):
        p = copy['products'][key]
        b, box = deepcopy(button), deepcopy(panel)
        bid, pid = f'service-tab-{index+1}', f'service-panel-{index+1}'
        b['id'], b['aria-controls'], b['aria-selected'], b['tabindex'] = bid, pid, str(index == 0).lower(), '0' if index == 0 else '-1'
        b.string = p['short']
        if page['route'] == 'aircon' and key in ('2', '3'):
            lines(b, ['お掃除機能付き', 'エアコン'] if key == '2' else ['天井埋め込み', 'エアコン'])
            b.find('br')['class'] = ['u-sp-only']
        mobile_tab_lines = {
            'レンジフード・換気扇': ['レンジフード・', '換気扇'],
            'キッチンコーティング': ['キッチン', 'コーティング'],
            'ベランダ・外回り高圧洗浄': ['ベランダ・', '外回り高圧洗浄'],
        }
        if p['short'] in mobile_tab_lines:
            lines(b, mobile_tab_lines[p['short']])
            b.find('br')['class'] = ['u-sp-only']
        box['id'], box['aria-labelledby'] = pid, bid
        box['class'] = ['c-tab__panel'] + (['is-active'] if index == 0 else [])
        photo = box.select_one('.c-compare-image')
        photo.clear()
        comparison = AIRCON_COMPARISONS[key] if page['category'] == 'aircon' else SERVICE_COMPARISONS[p['scene']]
        photo['class'] = ['c-compare-image', 'c-compare-image-tab__compare-image', 'c-aircon-compare']
        for state, label in [('before', 'Before'), ('after', 'After')]:
            photo.append(tag('img', 'c-flex-image c-compare-image__item',
                             src=comparison[state],
                             alt=p['short'] + ' ' + label + '（清掃イメージ）',
                             width='1536', height='1024', loading='lazy', decoding='async'))
        box.select_one('.c-compare-image-tab__text').string = p['description']
        for note in box.select('.c-note,.c-compare-image-tab__link-container'):
            note.decompose()
        photo.insert_after(
            tag('p', 'c-note c-aircon-comparison-note', '汚れの状況により、完全に除去できない場合がございます。'),
            tag('p', 'c-note c-aircon-comparison-note', '本比較画像は作業の一例です。'),
        )
        buttons.append(b); panels.append(box)
    if len(subjects) == 1:
        buttons['class'].append('c-service-single-tab')
    return n


def reasons(shared, route):
    n = template('reasons')
    n.select_one('h2').string = 'お客様から選ばれる理由'
    for index, (item, words) in enumerate(zip(n.select('.c-reasons__item'), shared['reasons']), 1):
        item.select_one('h3').string = words[0]
        item.select_one('p').string = words[1]
        label = tag('img', 'c-reasons__point', src=f'/assets/images/reasons/reference-point-{index:02d}.webp',
                    alt=f'POINT {index:02d}', width='205', height='70', loading='lazy', decoding='async')
        item.select_one('.c-reasons__card').insert(0, label)
    return n


def ensure_navy_stylesheet(output):
    pattern = r'<link rel="stylesheet" href="/assets/css/reasons-(?:glass|navy)\.css\?v=\d+"\s*/?>'
    if re.search(pattern, output):
        return re.sub(pattern, NAVY_STYLESHEET, output)
    linebreak = '\r\n' if '\r\n' in output else '\n'
    return output.replace('</head>', NAVY_STYLESHEET + linebreak + '</head>', 1)


def render_static_reasons(original):
    output = original
    grid_class = 'class="c-grid c-reasons p-reasons__contents"'
    navy_class = 'class="c-grid c-reasons p-reasons__contents c-reasons--navy"'
    if grid_class in output:
        output = output.replace(grid_class, navy_class, 1)
    else:
        output = output.replace('c-reasons--glass', 'c-reasons--navy', 1)
    photo_pattern = re.compile(r'<img\b[^>]*\bc-reasons__bg\b[^>]*>')
    glass_pattern = re.compile(r'<div\b[^>]*class="c-reasons__glass"[^>]*>.*?</div>', re.S)
    photo_count = len(photo_pattern.findall(output))
    navy = str(template('reasons').select_one('.c-reasons__navy'))
    if photo_count == 3:
        output = photo_pattern.sub(lambda _: navy, output, count=3)
    elif photo_count != 0:
        raise ValueError('Unexpected reason image count')
    elif len(glass_pattern.findall(output)) == 3:
        output = glass_pattern.sub(lambda _: navy, output, count=3)
    if output.count('class="c-reasons__navy"') != 3:
        raise ValueError('Missing three reason navy panels')
    return ensure_navy_stylesheet(output)


def decorate_heading(heading, english, japanese, artwork=None):
    heading['class'] = heading.get('class', []) + ['c-section-heading']
    heading.clear()
    title = tag('span', 'c-section-heading__english')
    if artwork:
        kind, file, height = artwork
        title['class'] += ['c-section-heading__english--art', f'c-section-heading__english--{kind}']
        title.append(tag('img', src=f'/assets/images/voices/{file}', alt=english,
                         width='1200', height=str(height), loading='lazy', decoding='async'))
    else:
        title.string = english
    heading.append(title)
    heading.append(tag('span', 'c-section-heading__subtitle', japanese))


def voices(page, copy):
    n = template('voices')
    n['class'] = n.get('class', []) + ['c-voice-section--bubble-preview']
    decorate_heading(n.select_one('h2'), "USER'S VOICE", 'ご利用いただいたお客様の声',
                     ('voice', 'reference-users-voice.webp', 85))
    grid = n.select_one('.p-content-box__content > .c-grid')
    grid['class'] = grid.get('class', []) + ['c-voice-bubbles']
    records = json.loads((DATA / 'voices.json').read_text(encoding='utf-8'))['pages'][page['route']]
    cards = n.select('.c-voice-card')
    assert len(records) == len(cards) == 6, page['route']
    for card, record in zip(cards, records):
        card['style'] = f"--voice-avatar: url('/assets/images/voices/{record['avatar']}.svg');"
        card.select_one('h3').string = record['title']
        card.select_one('p').string = record['body']
        profile = tag('div', 'c-voice-card__profile')
        identity = tag('div', 'c-voice-card__identity')
        identity.append(tag('span', 'c-voice-card__nickname', record['nickname']))
        identity.append(tag('span', 'c-voice-card__demographic', record['demographic']))
        stars = tag('span', 'c-voice-card__stars', role='img',
                    **{'aria-label': f"5つ星中{record['rating']}つ星"})
        for position in range(5):
            star_class = 'c-voice-card__star' + (' c-voice-card__star--empty' if position >= record['rating'] else '')
            stars.append(tag('span', star_class, **{'aria-hidden': 'true'}))
        profile.append(identity); profile.append(stars); card.insert(0, profile)
    return n


def faq(category_copy, shared, questions=None, decorated=False):
    n = template('faq'); n['id'] = 'service-faq'
    n.select_one('h2').string = 'よくある質問'
    if decorated:
        decorate_heading(n.select_one('h2'), 'Q&A', 'よくある質問')
    for item, words in zip(n.select('.c-faq-accordion__item'), shared['faq'] + (questions or category_copy['faq'])):
        question = words[0].rstrip('。！？?')
        item.select_one('button').string = question + ('？' if question.endswith('か') else '')
        item.select_one('.c-faq-accordion__text').string = words[1]
    return n


AIRCON_STEPS = [
    ('お見積りのご相談', '清掃内容と料金の目安をご案内します。'),
    ('作業内容と日時の調整', '訪問日時と事前の準備をご案内します。'),
    ('ご訪問と作業前の確認', '内容・料金のご了承後に作業を始めます。'),
    ('清掃と仕上がりの確認', '清掃後の仕上がりを一緒に確認します。'),
    ('お支払い', '現金・電子マネー・カードでお支払い。'),
]


def steps(shared, decorated=False, original_aircon=False):
    n = template('steps'); n['id'] = 'service-flow'
    if original_aircon:
        n['class'].append('c-service-flow--aircon')
    n.select_one('h2').string = 'ご利用の流れ'
    if decorated:
        decorate_heading(n.select_one('h2'), 'HOW TO USE', 'ご利用の流れ',
                         ('flow', 'reference-how-to-use.webp', 150))
    step_copy = AIRCON_STEPS if original_aircon else shared['steps']
    for item, words in zip(n.select('.c-step-list__item'), step_copy):
        item.select_one('.c-step-list-item__heading-main').string = words[0]
        item.select_one('.c-step-list-item__text p').string = words[1]
    for note in n.select('.c-step-list-item__note'): note.decompose()
    if decorated:
        n.select_one('.u-width-pc-1024')['class'] = ['c-howto-container']
        n.select_one('.c-step-list')['class'].append('c-howto')
        for index, item in enumerate(n.select('.c-step-list__item'), 1):
            heading = item.select_one('.c-step-list-item__heading-main').get_text()
            description = item.select_one('.c-step-list-item__text p').get_text()
            icon = item.select_one('.c-icon').extract()
            icon['class'] = [c for c in icon['class'] if c != 'c-step-list-item__icon'] + ['c-howto__icon']
            item.clear()
            item['class'] = ['c-step-list__item', 'c-howto__item']
            visual = tag('div', 'c-howto__visual', **{'aria-hidden': 'true'})
            visual.append(icon)
            item.append(visual)
            step = tag('p', 'c-howto__step')
            label = tag('span', 'c-howto__step-label', 'STEP ')
            label.append(tag('span', 'c-howto__number', f'{index:02}'))
            step.append(label)
            item.append(step)
            item.append(tag('h3', 'c-howto__heading', heading))
            description_node = tag('p', 'c-howto__description', description)
            if original_aircon:
                description_node.clear()
                for line in description.splitlines():
                    if description_node.contents:
                        description_node.append(tag('br'))
                    description_node.append(line)
            item.append(description_node)
    return n


def lineup_heading(title, anchor, scene, rounded=False):
    n = template('lineup-heading')
    n['id'] = anchor
    label = n.select_one('.c-lineup-heading__contain')
    subtitle = deepcopy(label.select_one('.c-lineup-heading__sub-text'))
    label.clear()
    label.append(title)
    if rounded:
        n['class'].append('c-lineup-heading--round')
        subtitle.clear()
        subtitle.append(tag('span', 'c-lineup-heading__label', 'lineup'))
        n.append(subtitle)
        n.select_one('img').decompose()
    else:
        label.append(subtitle)
        image(n.select_one('img'), scene, '')
    return n


def add_section_curve(section, direction, previous_color):
    section['class'] = section.get('class', []) + ['c-curved-section', f'c-curved-section--{direction}']
    section.insert(0, tag('span', f'c-section-curve c-section-curve--{direction}',
                          style=f'--curve-color: {previous_color};', **{'aria-hidden': 'true'}))


def decorate_sections(main):
    for selector, direction, color in (
        ('#service-introduction', 'down', '#fff'),
        ('.p-reasons', 'up', '#e3f1fc'),
        ('.c-voice-section--bubble-preview', 'up', '#e3f1fc'),
        ('#service-faq', 'down', '#fff'),
        ('#service-flow', 'up', '#e3f1fc'),
    ):
        section = main.select_one(selector)
        if selector == '.p-reasons':
            section = section.find_parent('section')
        add_section_curve(section, direction, color)
    main.select_one('.c-voice-section--bubble-preview')['style'] = '--bg-color: #fff;'
    add_section_curve(main.select_one('#service-flow').find_next_sibling('section'), 'down', '#fff')


def render(route, page, catalogue, copy):
    path = SITE / 'house-cleaning' / route / 'index.html'
    original = path.read_text(encoding='utf-8')
    page = {**page,'route':route}
    cat = copy['categories'][page['category']]
    primary = page['groups'][0]['products'][0]
    p = copy['products'][primary]
    main = tag('main', 'c-service-page', **{'data-service-layout':'shared-v2'})
    hero = template('hero')
    banner = copy['banners'][route]
    lines(hero.select_one('p'), banner['lines'])
    for src in hero.select('source'): src.decompose()
    image(hero.select_one('img'), banner['scene'], banner['alt'], True)
    if 'position' in banner:
        hero.select_one('img')['style'] = '--banner-image-position: ' + banner['position'] + ';'
    hero['class'].append('c-house-cleaning-mv--check')
    hero.insert(0, tag('h1', 'c-house-cleaning-mv__sr-heading', page['title']))
    check = tag('span', 'c-house-cleaning-mv__check')
    check.append(tag('span', 'c-house-cleaning-mv__check-label', 'Check！'))
    hero.append(check)
    nav = navigation(page,primary,page['category'],copy)
    first_classes = 'c-first-view' + (' c-first-view--expanded' if route != 'aircon' else '')
    first_view = tag('div', first_classes, id='first-view', **{'data-floating-visibility-trigger': ''})
    first_view.append(hero); first_view.append(nav); main.append(first_view)
    floating = template('floating')
    floating['class'] = [name for name in floating['class'] if name != 'is-visible']
    main.append(floating)
    main.append(concerns(page,primary,cat,copy))
    main.append(reasons(copy['shared'], route))
    apply = tag('div', id='apply'); main.append(apply)
    for group in page['groups']:
        apply.append(lineup_heading(group['title'], group['id'], copy['products'][group['products'][0]]['scene'], rounded=True))
        for key in group['products']:
            apply.append(product(key,route,catalogue,copy))
    if page['category'] == 'aircon':
        section = template('aircon-offers')
        section.select_one('.recommend-plan__text').decompose()
        heading = section.select_one('.recommend-plan__heading')
        heading.clear()
        heading.append(tag('span', 'c-bracket-heading__text', '人気の組み合わせプラン'))
        panels = section.select('.c-tab__panel .recommend-plan-cards')
        assert len(panels) == 2
        if page['offers']:
            assert len(page['offers']) == 3
            for index, key in enumerate(page['offers']):
                panels[0 if index < 2 else 1].append(offer(key,catalogue))
        else:
            relevant = ['aircon-offer-3'] if primary == '3' else ['aircon-offer-1', 'aircon-offer-2']
            chosen = 1 if primary == '3' else 0
            for key in relevant:
                panels[chosen].append(offer(key, catalogue))
            section.select('.c-tab__button')[1 - chosen].decompose()
            panels[1 - chosen].find_parent(class_='c-tab__panel').decompose()
            button = section.select_one('.c-tab__button')
            button['aria-selected'], button['tabindex'] = 'true', '0'
            box = section.select_one('.c-tab__panel')
            box['class'], box['tabindex'] = ['c-tab__panel', 'is-active'], '0'
        apply.append(section)
    else:
        apply.append(additional_plans_section(page, route, catalogue, copy))
    main.append(voices(page,copy))
    main.append(faq(cat,copy['shared'],decorated=True))
    main.append(steps(copy['shared'],decorated=True,original_aircon=(route == 'aircon')))
    categories = template('categories')
    categories['style'] = '--bg-color: #e3f1fc;'
    featured_heading = categories.find('h2')
    featured_heading['class'] = ['c-heading-level-2', 'p-reasons__heading', 'c-featured-cleaning__heading']
    featured_heading.string = '注目のハウスクリーニング'
    featured_cards = categories.select_one('.c-house-cleaning-links')
    featured_cards['class'] = [name for name in featured_cards['class'] if name != 'u-mt-24']
    main.append(categories); main.append(template('cart-modal'))
    decorate_sections(main)
    normalize_text(main)
    output, count = re.subn(r'<main\b[^>]*>.*?</main>',lambda _:str(main),original,count=1,flags=re.S)
    assert count == 1, route
    output = re.sub(r'\s*<ol\b[^>]*class="c-breadcrumbs"[^>]*>.*?</ol>\s*(?=<main\b)',
                    '\n', output, count=1, flags=re.S)
    css_version = '2026100210'
    if '/assets/css/service-pages.css' not in output:
        output = output.replace('</head>',f'<link rel="stylesheet" href="/assets/css/service-pages.css?v={css_version}"/>\n</head>')
    output = re.sub(r'/assets/css/service-pages\.css\?v=\d+',
                    f'/assets/css/service-pages.css?v={css_version}', output)
    output = ensure_navy_stylesheet(output)
    for name, version in [('aircon-voice-bubbles', '2026100236'), ('aircon-hero', '2026100402'),
                          ('aircon-layout', '2026100505' if route == 'aircon' else '2026100402'), ('service-format', '2026100403')]:
        pattern = r'<link\b[^>]*href="/assets/css/' + name + r'\.css(?:\?v=\d+)?"[^>]*>\s*'
        output = re.sub(pattern, '', output)
        output = output.replace('</head>', f'<link rel="stylesheet" href="/assets/css/{name}.css?v={version}">\n</head>', 1)
    if '/assets/js/aircon-comparison.js' not in output:
        output = output.replace('</head>', '<script src="/assets/js/aircon-comparison.js?v=2026100250" defer></script>\n</head>', 1)
    output = re.sub(r'<link\b[^>]*href="/assets/css/house-cleaning/[^\"]+"[^>]*>\s*','',output)
    output = re.sub(r'<script\b[^>]*src="/assets/js/house-cleaning/[^\"]+"[^>]*>\s*</script>\s*','',output)
    output = output.replace('</body>','<script src="/assets/js/house-cleaning/product-top.js"></script>\n</body>')
    return shared_ui(output, is_aircon=(route == 'aircon'))


def sync_manifest(routes, check):
    path = ROOT / 'source/manifest.json'
    manifest = json.loads(path.read_text(encoding='utf-8'))
    files = [SITE / 'house-cleaning' / route / 'index.html' for route in routes]
    files += [SITE / rel for rel in STATIC_REASONS]
    files += list((SITE / 'assets/images/service-scenes').glob('*.webp'))
    files += list((SITE / 'assets/images/service-scenes').glob('aircon-*-*.png'))
    files += [SITE / 'assets/css/service-pages.css', SITE / 'assets/css/reasons-navy.css',
              SITE / 'assets/css/aircon-voice-bubbles.css',
              SITE / 'assets/css/aircon-header.css',
              SITE / 'assets/css/aircon-hero.css',
              SITE / 'assets/css/aircon-layout.css', SITE / 'assets/css/service-format.css',
              SITE / 'assets/images/common-parts/decoration/section-arrows-black.svg',
              SITE / 'assets/images/common-parts/decoration/section-curve-down.svg',
              SITE / 'assets/images/common-parts/decoration/section-curve-up.svg',
              SITE / 'assets/images/voices/reference-rating.webp',
              SITE / 'assets/images/voices/reference-users-voice.webp',
              SITE / 'assets/images/voices/reference-how-to-use.webp',
              *(SITE / f'assets/images/reasons/reference-point-{index:02d}.webp' for index in range(1, 4)),
              SITE / 'assets/js/aircon-header.js', SITE / 'assets/js/aircon-comparison.js', SITE / 'assets/js/common.js',
              *(SITE / f'assets/images/voices/{name}.svg' for name in (
                  'woman-long', 'man-short', 'woman-bob', 'woman-senior', 'man-young', 'man-senior')),
              SITE / 'assets/css/common.css']
    changed = []
    obsolete = {'assets/images/reasons/navy-glass-vertical.png', 'assets/css/reasons-glass.css',
                'assets/images/voices/anonymous-person.svg'}
    obsolete_keys = [key for key, record in manifest['files'].items() if record['path'] in obsolete]
    for key in obsolete_keys:
        del manifest['files'][key]
        changed.append(key)
    for file in files:
        rel = file.relative_to(SITE).as_posix()
        data = file.read_bytes()
        digest = hashlib.sha256(data).hexdigest()
        records = [r for r in manifest['files'].values() if r['path'] == rel]
        if not records:
            url = manifest['origin'].rstrip('/') + '/' + rel
            record = {'path':rel, 'effective_url':url, 'status':200,
                      'content_type':{'.webp':'image/webp','.png':'image/png','.svg':'image/svg+xml',
                                      '.js':'application/javascript'}.get(file.suffix,'text/css'),
                      'origin_type':'local-service-page'}
            manifest['files'][url] = record
            records = [record]
        for record in records:
            if record.get('sha256') != digest:
                if record.get('sha256') and not record.get('origin_type', '').startswith('local-'):
                    record.setdefault('source_sha256', record['sha256'])
                record.update(bytes=len(data), sha256=digest)
                changed.append(rel)
    if changed and not check:
        unique = {r['path']:r for r in manifest['files'].values()}
        manifest['counts'].update(urls=len(manifest['files']), unique_paths=len(unique),
                                  bytes=sum(r['bytes'] for r in unique.values()))
        path.write_bytes(json.dumps(manifest, ensure_ascii=False, indent=2).encode('utf-8'))
    return changed


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--check',action='store_true')
    parser.add_argument('--route')
    args = parser.parse_args()
    catalogue = json.loads((DATA / 'catalogue.json').read_text(encoding='utf-8'))
    copy = json.loads((DATA / 'copy.json').read_text(encoding='utf-8'))
    routes = {args.route: catalogue['pages'][args.route]} if args.route else catalogue['pages']
    if not args.check and not args.route: enrich(catalogue)
    changed = []
    for route,page in routes.items():
        path = SITE / 'house-cleaning' / route / 'index.html'
        output = render(route,page,catalogue,copy)
        if output.encode('utf-8') != path.read_bytes():
            changed.append(route)
            if not args.check: path.write_bytes(output.encode('utf-8'))
    for rel in STATIC_REASONS:
        path = SITE / rel
        original = path.read_bytes().decode('utf-8')
        output = render_static_reasons(original)
        if output != original:
            changed.append('/' + rel)
            if not args.check: path.write_bytes(output.encode('utf-8'))
    manifest_changes = sync_manifest(routes, args.check)
    print(json.dumps({'pages':len(routes),'changed':changed,'manifest_updates':len(manifest_changes),'check':args.check},ensure_ascii=False))
    if args.check and (changed or manifest_changes): raise SystemExit(1)


if __name__ == '__main__':
    main()
