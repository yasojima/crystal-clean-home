"""Build the single corporate brochure proposal from canonical copy and photos."""
import re
from html import escape
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
SITE = ROOT / 'source/site'
FEATURE_LAYOUTS = ('aircon', 'carpet', 'sanitizing', 'handover')
GALLERY_KEYS = ('glass', 'kitchen', 'hood', 'lighting', 'toilet', 'hallway', 'basin', 'balcony')
STATEMENT_LEAD = '店舗やオフィス'
STATEMENT_MAIN_PARTS = ('環境づくりを', 'サポート')
SCENE_TITLE_LINES = ('日常では落とせない汚れから', '定期清掃・衛生管理・引き渡しまで')
CONTACT_COPY = '清掃箇所やご希望の時期について、お気軽にご相談ください。'
INTRO_PARAGRAPHS = (
    'クリスタルクリーンホームでは店舗やオフィスの利用状況に合わせ、日々のお掃除から定期的な清掃まで丁寧にご案内しています。',
    'ご家庭のお掃除で大切にしている丁寧な作業と細やかな気配りを、法人のお客様の空間づくりにも生かします。設備や素材の状態と汚れの程度を確認し、それぞれの場所に合ったお掃除をご提案します。',
    '床や設備がきれいに整った職場は、毎日の仕事を気持ちよく始められる場所になります。心地よく使える環境を保つことで、従業員の皆様が前向きに働く意欲を支えます。',
    '毎日通う場所だからこそ、「今日もここで働きたい」と思える空間を大切に。働く皆様にも訪れるお客様にも、明るく気持ちのよい印象を届けるお手伝いをします。',
    '日々のお手入れと定期的な清掃を組み合わせ、汚れをためず、快適に使える状態を保ちます。利用状況やご希望に合わせて、長く心地よく過ごせる店舗・オフィスづくりをお手伝いします。',
)


def paragraphs(text):
    text = text.replace('清潔な状態を保ちます。', '快適に使える状態を保ちます。').replace('清潔', '快適')
    sentences = re.findall(r'[^。]+。|[^。]+$', text)
    return ''.join(f'<p>{escape(sentence)}</p>' for sentence in sentences)


def build():
    data = json.loads((ROOT / 'source/office-cleaning/content.json').read_text(encoding='utf-8'))
    current = (SITE / 'business/cleaning/index.html').read_text(encoding='utf-8')
    head = current.split('<body')[0]
    head = re.sub(r'<title>.*?</title>', '<title>法人向け清掃 ワイヤーフレーム | Crystal Clean Home</title>', head)
    head = re.sub(r'<link[^>]*href="/assets/css/office-cleaning\.css[^>]*>', '', head)
    head = re.sub(r'<meta\b[^>]*name="robots"[^>]*>', '', head)
    head = head.replace('</head>', '<meta name="robots" content="noindex,nofollow">\n<link rel="stylesheet" href="/home-wireframe/business/wireframe.css?v=2026100832">\n</head>')
    header = re.search(r'<header\b[^>]*class="c-header"[^>]*>.*?</header>', current, re.S).group()
    footer = re.search(r'<footer\b[^>]*class="c-footer\b[^>]*>.*?</footer>', current, re.S).group()

    def photo(key, alt, lazy=True):
        return f'<img src="/assets/images/office-cleaning/{key}.png" alt="{escape(alt)}" width="1536" height="1024" loading="{"lazy" if lazy else "eager"}" decoding="async">'

    def inquiry_link():
        return '<a class="office-wf__inquiry-link c-category-simple-card" href="/contact/business/" data-demo-dialog><span class="office-wf__inquiry-surface c-category-simple-card__bottom"><span class="office-wf__inquiry-text c-category-simple-card__text">ご相談窓口</span></span></a>'

    scenes = (
        ('日常の汚れから定期清掃まで', '日々のお掃除で落としにくい汚れや、エアコン内部など手の届きにくい箇所に対応します。店舗やオフィスの利用状況、設備や素材の状態に合わせて、清掃の範囲と定期的なお手入れをご案内します。'),
        ('衛生面の清掃', '多くの方が利用する店舗やオフィスでは、よく触れる場所や水まわりの汚れも気になります。トイレや洗面所、厨房など、場所と素材の状態を確認し、お掃除や除菌・抗菌のお手入れをご案内します。'),
        ('引き渡しに向けた清掃', '改装後やテナントの入れ替えに伴う清掃をご相談いただけます。床、窓、備え付けの設備などの状態を確認し、引き渡しに必要な清掃の範囲と進め方をご案内します。時期や作業時間もご相談ください。'),
    )
    scene_items = ''.join(f'<div class="c-reasons__item"><article class="office-wf__scene c-reason-card c-reasons__card"><img class="c-reasons__point" src="/assets/images/reasons/reference-point-{i:02}.webp" alt="POINT {i:02}" width="205" height="70" loading="lazy" decoding="async"><h3 class="c-reason-card__heading">{escape(title)}</h3><p class="c-reason-card__description">{escape(text)}</p></article><div class="c-reasons__navy" aria-hidden="true"></div></div>' for i, (title, text) in enumerate(scenes, 1))
    gallery_labels = dict(data['gallery'])
    features = []
    for i, (feature, layout) in enumerate(zip(data['features'], FEATURE_LAYOUTS), 1):
        detail = ''
        if layout == 'sanitizing':
            detail = f'<figure class="office-wf__detail-photo">{photo("basin",gallery_labels["basin"])}</figure>'
        section_head = '<header class="office-wf__section-head office-wf__section-head--display"><h2 id="office-wf-features-title" class="office-wf__display-word">快適な空間へ</h2></header>' if layout == 'aircon' else ''
        features.append(f'''<article class="office-wf__feature office-wf__feature--{layout}" id="office-wf-{layout}">
{section_head}
<figure class="office-wf__main-photo">{photo(feature['image'],feature['title'])}</figure>
<div class="office-wf__feature-copy"><span class="office-wf__number" aria-hidden="true">{i:02}</span><div><h3>{escape(feature['title'])}</h3>{paragraphs(feature['text'])}</div></div>
{detail}</article>''')
    spreads = f'<div class="office-wf__spread office-wf__spread--first">{features[0]}{features[1]}</div><div class="office-wf__spread office-wf__spread--second">{features[2]}{features[3]}</div>'
    gallery = ''.join(f'<figure class="office-wf__gallery-photo office-wf__gallery-photo--{key}">{photo(key,gallery_labels[key])}<figcaption>{escape(gallery_labels[key])}</figcaption></figure>' for key in GALLERY_KEYS)
    main = f'''<main class="office-wf">
<section class="office-wf__hero" aria-labelledby="office-wf-title">
<div class="office-wf__cover-frame"><div class="office-wf__cover">
<div class="office-wf__cover-title"><h1 id="office-wf-title">{escape(data['title'])}</h1><p class="office-wf__cover-word">店舗・オフィスを、<span>快適に。</span></p>{inquiry_link()}</div>
<figure class="office-wf__cover-photo">{photo('floor','大きな窓と広いフロアのある店舗・オフィスの空間',False)}</figure>
</div></div>
<div class="office-wf__container office-wf__intro"><h2 class="office-wf__statement"><span class="office-wf__statement-lead">{escape(STATEMENT_LEAD)}</span><span class="office-wf__statement-main">{''.join(f'<span>{escape(part)}</span>' for part in STATEMENT_MAIN_PARTS)}</span></h2><div class="office-wf__intro-copy">{''.join(f'<p>{escape(text)}</p>' for text in INTRO_PARAGRAPHS)}</div></div>
</section>
<section class="office-wf__section office-wf__scene-section c-home" id="office-wf-scenes" aria-labelledby="office-wf-scenes-title"><div class="l-section-inner"><div class="p-reasons"><header class="office-wf__container office-wf__section-head"><h2 id="office-wf-scenes-title">{''.join(f'<span>{escape(line)}</span>' for line in SCENE_TITLE_LINES)}</h2></header><div class="office-wf__scenes c-grid c-reasons p-reasons__contents c-reasons--navy" style="--grid-col-pc: repeat(3, 1fr); --grid-gap-pc: 0; --grid-col-sp: repeat(1, 1fr); --grid-gap-sp: 24px;">{scene_items}</div></div></div></section>
<section class="office-wf__section office-wf__services" aria-labelledby="office-wf-features-title"><div class="office-wf__container"><div class="office-wf__features">{spreads}</div></div></section>
<section class="office-wf__section office-wf__range-section" aria-labelledby="office-wf-range-title"><div class="office-wf__container"><header class="office-wf__section-head"><h2 id="office-wf-range-title">幅広い清掃対応</h2></header><div class="office-wf__gallery">{gallery}</div></div></section>
<section class="office-wf__section office-wf__contact" id="office-wf-contact" aria-labelledby="office-wf-contact-title"><div class="office-wf__container office-wf__contact-grid"><h2 id="office-wf-contact-title">法人向け清掃のご相談</h2><p>{escape(CONTACT_COPY)}</p>{inquiry_link()}</div></section>
</main>'''
    page = f'{head}<body class="c-office-cleaning office-wf-page">{header}{main}{footer}</body></html>'
    (HERE / 'index.html').write_text(page, encoding='utf-8', newline='\n')
    print('Built the corporate brochure proposal with two editorial spreads.')


if __name__ == '__main__':
    build()
