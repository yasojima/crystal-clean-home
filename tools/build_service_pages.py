"""Build service pages from shared, existing site components and service data."""
from pathlib import Path
from copy import deepcopy
import argparse
import hashlib
import json
import re
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / 'source/site'
DATA = ROOT / 'source/service-pages'


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
        if 'c-faq-accordion__heading' in heading.get('class', []):
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
    if record.get('scope') and not any(label in card.get_text() for label in ('サービス範囲', 'コーティング範囲')):
        scope = tag('p', 'c-note c-service-scope', 'サービス範囲：' + '／'.join(record['scope']))
        description.insert_after(scope)
    for a in card.select('.c-lineup-card__image,.c-lineup-card__heading a'):
        if a.name == 'a' and record.get('route', '').split('?')[0] == f'/house-cleaning/{route}/':
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
    for button in block.select('.c-lineup-card__foot > .js-add-cart'):
        if 'c-product-additional-card__cart-button' not in button['class']:
            button['class'].append('c-product-additional-card__cart-button')
    normalize_text(block)
    for node in block.select('[id]'):
        node['id'] = f'{key}-{node["id"]}'
    for node in block.select('[aria-controls]'):
        node['aria-controls'] = f'{key}-{node["aria-controls"]}'
    wrapper = tag('div', 'c-lineup-products js-products')
    wrapper.append(block)
    return wrapper


OFFER_IMAGES = {'kitchen-fan':'kitchen-fan','kitchen':'kitchen-sink','bath':'bathroom','bath-fan':'bath-dryer','sink':'lavatory','pipe':'bath-pipe','ulblo':'bath-pipe','toilet':'toilet','wallpaper-dyeing-cloth':'wall'}
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
    return n


def navigation(page, primary, category, copy):
    n = template('navigation')
    n.select_one('h2').string = 'ご希望のサービスをお選びください' if '/' not in page['route'] else 'ご覧になりたい内容をお選びください'
    cards = n.select_one('.c-page-anchors')
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
        a.select_one('h3').string = item['text']
        icon = a.select_one('.c-illust')
        if icon:
            icon['class'] = item['icon'] or ['c-illust',f'c-illust--{icon_map[category]}','c-category-simple-card__icon']
        cards.append(a)
    container = tag('div', 'l-section l-section--limited u-py-48-72_40-56')
    inner = tag('div', 'l-section-inner l-section-inner--limited')
    inner.append(n); container.append(inner)
    return container


def concerns(page, primary, category_copy, copy):
    n = template('concerns'); n['id'] = 'service-introduction'
    detail = '/' in page['route']
    content = copy['products'][primary]
    issues = category_copy['concerns']
    n.select_one('.c-issue-list__heading').string = 'こんなお悩みはありませんか'
    for node, (first, second) in zip(n.select('.c-issue-card__text'), issues):
        node.clear()
        node.append(first)
        node.append(tag('br'))
        node.append(second)
    heading = [content['short'] + 'を丁寧にお手入れ','気になる箇所を清潔に'] if detail else category_copy['heading']
    lines(n.select_one('.p-content-box__heading'), [*heading[:-1], heading[-1].rstrip('！!') + '！'])
    subjects = [primary] if detail else category_copy['subjects']
    buttons = n.select_one('.c-tab__buttons'); panels = n.select_one('.c-tab__panels')
    button, panel = deepcopy(buttons.find('button')), deepcopy(panels.select_one('.c-tab__panel'))
    buttons.clear(); panels.clear()
    for index, key in enumerate(subjects):
        p = copy['products'][key]
        b, box = deepcopy(button), deepcopy(panel)
        bid, pid = f'service-tab-{index+1}', f'service-panel-{index+1}'
        b['id'], b['aria-controls'], b['aria-selected'], b['tabindex'] = bid, pid, str(index == 0).lower(), '0' if index == 0 else '-1'
        b.string = p['short']
        box['id'], box['aria-labelledby'] = pid, bid
        box['class'] = ['c-tab__panel'] + (['is-active'] if index == 0 else [])
        # Keep the existing tab and photograph frame; use one illustrative scene, without a fictitious comparison.
        photo = box.select_one('.c-compare-image')
        photo['class'] = ['c-service-photo','c-compare-image-tab__compare-image']
        photo.clear()
        img = tag('img', 'c-flex-image')
        image(img, p['scene'], p['focus'] + 'の清掃イメージ')
        photo.append(img)
        box.select_one('.c-compare-image-tab__text').string = p['description']
        for note in box.select('.c-note,.c-compare-image-tab__link-container'):
            note.decompose()
        buttons.append(b); panels.append(box)
    if len(subjects) == 1:
        buttons['class'].append('c-service-single-tab')
    return n


def reasons(shared):
    n = template('reasons')
    scenes = ('reason-mop-bucket', 'reason-carpet-extractor', 'reason-floor-polisher')
    for i,(item,words) in enumerate(zip(n.select('.c-reasons__item'),shared['reasons'])):
        item.select_one('h3').string = words[0]
        item.select_one('p').string = words[1]
        image(item.select_one('img'), scenes[i], '')
    return n


def voices(page, copy):
    n = template('voices')
    n.select_one('h2').string = 'ご利用者様の声'
    profiles = json.loads((DATA / 'voice-copy.json').read_text(encoding='utf-8'))
    concern, scope, work, finish, extra, care = profiles[page['route']]
    titles = (f'{concern}を相談できました', f'{scope}が分かって安心',
              f'{work}まで見てもらえた', f'{finish}を一緒に確認！',
              f'{extra}相談できて助かりました', f'{care}を教わりました')
    title_overrides = json.loads((DATA / 'voice-title-overrides.json').read_text(encoding='utf-8'))
    titles = tuple(title_overrides.get(page['route'], {}).get(str(index), title)
                   for index, title in enumerate(titles))
    variants = (
        (f'{concern}が気になって依頼しました。最初に状態を一緒に見て、お願いする範囲を決められたので、初めてでも迷いませんでした。',
         f'気になっていた{concern}について相談しました。作業前に現状を確認してもらい、どこまで頼めるかがはっきりしました。',
         f'{concern}について相談したくて申し込みました。実際の状態を見ながら話せたので、必要な作業をイメージできました。'),
        (f'作業前に{scope}を説明してもらいました。料金と当日の流れを聞いてからお願いでき、安心してお任せできました。',
         f'初めての依頼でしたが、{scope}を一つずつ確認できました。希望を伝えたうえで作業範囲と料金を決められてよかったです。',
         f'{scope}が分からず質問しました。スタッフさんが気さくに答えてくれたので、作業の内容に納得してから頼めました。'),
        (f'自分では難しい{work}。使う道具と手順を聞き、周囲を保護して進める様子を見て、丁寧さが伝わりました。',
         f'{work}は自分でできず気になっていました。途中で作業箇所を教えてもらえたので、何をしているか分かりやすかったです。',
         f'普段は手を付けにくい{work}をお願いしました。状態に合わせて道具を替えていることも聞けて、安心できました。'),
        (f'作業後に{finish}を一緒に確かめました。気になっていた場所を自分で確認できて、お願いしてよかったです！',
         f'{finish}を仕上げの説明と一緒に確認できました。毎日使う場所なので、変化が分かってうれしかったです！',
         f'最後に{finish}を見ながら説明を受けました。どこを作業したのか分かり、仕上がりにも納得です。'),
        (f'当日、{extra}相談しました。追加できる範囲と料金を先に聞けたので、その場で落ち着いて決められました。',
         f'作業を見ていて{extra}お願いできるか尋ねました。対応できる内容と費用を説明してくれて、段取りがスムーズでした。',
         f'予定外でしたが{extra}相談してみました。作業内容や支払いの流れを先に確認できたので、急なお願いでも安心でした。'),
        (f'作業後に{care}を教わりました。対象箇所を見ながら聞けたので、家での手入れにも役立てられそうです。',
         f'{care}について質問すると、無理なく続けられる方法を教えてくれました。仕上がりだけでなく、その後のことも分かって助かります。',
         f'終わってから{care}を聞きました。日頃どこに気を付ければよいか具体的に分かり、頼んだ後も安心です。')
    )
    variant = sum(ord(char) for char in page['route']) % 3
    cards = n.select('.c-voice-card')
    assert len(cards) == 6
    for index, card in enumerate(cards):
        card.select_one('h3').string = titles[index]
        card.select_one('p').string = variants[index][variant]
    return n


def faq(category_copy, shared, questions=None):
    n = template('faq'); n['id'] = 'service-faq'
    n.select_one('h2').string = 'よくある質問'
    for item, words in zip(n.select('.c-faq-accordion__item'), shared['faq'] + (questions or category_copy['faq'])):
        question = words[0].rstrip('。！？?')
        item.select_one('button').string = question + ('？' if question.endswith('か') else '')
        item.select_one('.c-faq-accordion__text').string = words[1]
    return n


def steps(shared):
    n = template('steps'); n['id'] = 'service-flow'
    n.select_one('h2').string = 'ご利用の流れ'
    for item, words in zip(n.select('.c-step-list__item'),shared['steps']):
        item.select_one('.c-step-list-item__heading-main').string = words[0]
        item.select_one('.c-step-list-item__text p').string = words[1]
    for note in n.select('.c-step-list-item__note'): note.decompose()
    return n


def lineup_heading(title, anchor, scene):
    n = template('lineup-heading')
    n['id'] = anchor
    label = n.select_one('.c-lineup-heading__contain')
    subtitle = deepcopy(label.select_one('.c-lineup-heading__sub-text'))
    label.clear()
    label.append(title)
    label.append(subtitle)
    image(n.select_one('img'), scene, '')
    return n


def render(route, page, catalogue, copy):
    path = SITE / 'house-cleaning' / route / 'index.html'
    original = path.read_text(encoding='utf-8')
    page = {**page,'route':route}
    cat = copy['categories'][page['category']]
    primary = page['groups'][0]['products'][0]
    p = copy['products'][primary]
    main = tag('main', 'c-service-page', **{'data-service-layout':'shared-v1'})
    main.append(tag('h1','c-page-heading',page['title']))
    hero = template('hero')
    hero_words = cat['hero'] if '/' not in route else [p['short'] + 'を丁寧に','素材と状態に合わせたお手入れ']
    lines(hero.select_one('p'),hero_words)
    for src in hero.select('source'): src.decompose()
    image(hero.select_one('img'),p['scene'],p['focus']+'の清掃イメージ',True)
    main.append(hero); main.append(template('floating'))
    main.append(navigation(page,primary,page['category'],copy))
    main.append(concerns(page,primary,cat,copy))
    main.append(reasons(copy['shared']))
    apply = tag('div', id='apply'); main.append(apply)
    for group in page['groups']:
        apply.append(lineup_heading(group['title'], group['id'], copy['products'][group['products'][0]]['scene']))
        for key in group['products']:
            apply.append(product(key,route,catalogue,copy))
    if page['offers']:
        offers_id = 'anchor00' if route == 'pack' else 'service-sets'
        if page['category'] == 'aircon':
            section = template('aircon-offers')
            panels = section.select('.c-tab__panel .recommend-plan-cards')
            assert len(panels) == 2 and len(page['offers']) == 3
            for index, key in enumerate(page['offers']):
                panels[0 if index < 2 else 1].append(offer(key,catalogue))
            apply.append(section)
        else:
            apply.append(lineup_heading('組み合わせてご利用いただけるプラン', offers_id, p['scene']))
            section = tag('section','l-section l-section--limited')
            inner = tag('div','l-section-inner l-section-inner--limited')
            grid = tag('div','c-service-offers c-grid',style='--grid-col-pc:repeat(2,1fr);--grid-gap-pc:32px;--grid-col-sp:repeat(1,1fr);--grid-gap-sp:24px;')
            for key in page['offers']:
                grid.append(offer(key,catalogue))
            inner.append(grid); section.append(inner); apply.append(section)
    questions = None
    if '/' in route:
        detail_faq = json.loads((DATA / 'detail-faq.json').read_text(encoding='utf-8'))
        if page['category'] != 'coating' or primary == '806':
            questions = detail_faq.get(primary, detail_faq.get(p['scene']))
    main.append(voices(page,copy)); main.append(faq(cat,copy['shared'],questions)); main.append(steps(copy['shared']))
    main.append(template('categories')); main.append(template('cart-modal'))
    normalize_text(main)
    output, count = re.subn(r'<main\b[^>]*>.*?</main>',lambda _:str(main),original,count=1,flags=re.S)
    assert count == 1, route
    if '/assets/css/service-pages.css' not in output:
        output = output.replace('</head>','<link rel="stylesheet" href="/assets/css/service-pages.css?v=2026100202"/>\n</head>')
    output = re.sub(r'/assets/css/service-pages\.css\?v=\d+',
                    '/assets/css/service-pages.css?v=2026100202', output)
    output = re.sub(r'<link\b[^>]*href="/assets/css/house-cleaning/[^\"]+"[^>]*>\s*','',output)
    output = re.sub(r'<script\b[^>]*src="/assets/js/house-cleaning/[^\"]+"[^>]*>\s*</script>\s*','',output)
    output = output.replace('</body>','<script src="/assets/js/house-cleaning/product-top.js"></script>\n</body>')
    return output


def sync_manifest(routes, check):
    path = ROOT / 'source/manifest.json'
    manifest = json.loads(path.read_text(encoding='utf-8'))
    files = [SITE / 'house-cleaning' / route / 'index.html' for route in routes]
    files += list((SITE / 'assets/images/service-scenes').glob('*.webp'))
    files += [SITE / 'assets/css/service-pages.css', SITE / 'assets/css/common.css']
    changed = []
    for file in files:
        rel = file.relative_to(SITE).as_posix()
        data = file.read_bytes()
        digest = hashlib.sha256(data).hexdigest()
        records = [r for r in manifest['files'].values() if r['path'] == rel]
        if not records:
            url = manifest['origin'].rstrip('/') + '/' + rel
            record = {'path':rel, 'effective_url':url, 'status':200,
                      'content_type':'image/webp' if file.suffix == '.webp' else 'text/css',
                      'origin_type':'local-service-page'}
            manifest['files'][url] = record
            records = [record]
        for record in records:
            if record.get('sha256') != digest:
                if record.get('sha256'):
                    record.setdefault('source_sha256', record['sha256'])
                record.update(bytes=len(data), sha256=digest)
                changed.append(rel)
    if changed and not check:
        unique = {r['path']:r for r in manifest['files'].values()}
        manifest['counts'].update(urls=len(manifest['files']), unique_paths=len(unique),
                                  bytes=sum(r['bytes'] for r in unique.values()))
        path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
    return changed


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--check',action='store_true')
    args = parser.parse_args()
    catalogue = json.loads((DATA / 'catalogue.json').read_text(encoding='utf-8'))
    copy = json.loads((DATA / 'copy.json').read_text(encoding='utf-8'))
    if not args.check: enrich(catalogue)
    changed = []
    for route,page in catalogue['pages'].items():
        path = SITE / 'house-cleaning' / route / 'index.html'
        output = render(route,page,catalogue,copy)
        if output.encode('utf-8') != path.read_bytes():
            changed.append(route)
            if not args.check: path.write_bytes(output.encode('utf-8'))
    manifest_changes = sync_manifest(catalogue['pages'], args.check)
    print(json.dumps({'pages':len(catalogue['pages']),'changed':changed,'manifest_updates':len(manifest_changes),'check':args.check},ensure_ascii=False))
    if args.check and (changed or manifest_changes): raise SystemExit(1)


if __name__ == '__main__':
    main()
