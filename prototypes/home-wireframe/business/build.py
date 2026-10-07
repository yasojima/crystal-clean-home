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
STATEMENT_LINES = ('店舗やオフィスの清潔な', '環境づくりをサポート')
INTRO_COPY = 'クリスタルクリーンホームでは店舗やオフィスの利用状況に合わせ、日々のお掃除から定期的な清掃まで丁寧にご案内しています。ご家庭のお掃除で大切にしている丁寧な作業と細やかな気配りを、法人のお客様の空間づくりにも生かします。設備や素材の状態と汚れの程度を確認し、それぞれの場所に合ったお掃除をご提案します。多くの方が利用する店舗やオフィスで皆様が快適に過ごせるよう、清潔な環境づくりをお手伝いします。'


def build():
    data = json.loads((ROOT / 'source/office-cleaning/content.json').read_text(encoding='utf-8'))
    current = (SITE / 'business/cleaning/index.html').read_text(encoding='utf-8')
    head = current.split('<body')[0]
    head = re.sub(r'<title>.*?</title>', '<title>法人向け清掃 ワイヤーフレーム | Crystal Clean Home</title>', head)
    head = re.sub(r'<link[^>]*href="/assets/css/office-cleaning\.css[^>]*>', '', head)
    head = re.sub(r'<meta\b[^>]*name="robots"[^>]*>', '', head)
    head = head.replace('</head>', '<meta name="robots" content="noindex,nofollow">\n<link rel="stylesheet" href="/home-wireframe/business/wireframe.css?v=2026100819">\n</head>')
    header = re.search(r'<header\b[^>]*class="c-header"[^>]*>.*?</header>', current, re.S).group()
    footer = re.search(r'<footer\b[^>]*class="c-footer\b[^>]*>.*?</footer>', current, re.S).group()

    def photo(key, alt, lazy=True):
        return f'<img src="/assets/images/office-cleaning/{key}.png" alt="{escape(alt)}" width="1536" height="1024" loading="{"lazy" if lazy else "eager"}" decoding="async">'

    def inquiry_link():
        return '<a class="office-wf__inquiry-link c-category-simple-card" href="/contact/business/" data-demo-dialog><span class="office-wf__inquiry-surface c-category-simple-card__bottom"><span class="office-wf__inquiry-text c-category-simple-card__text">ご相談窓口</span></span></a>'

    scenes = (
        ('日常では難しい箇所のお掃除', '日々のお掃除では落としにくい汚れや、手の届きにくい箇所をご相談いただけます。エアコン内部、床の黒ずみ、カーペットのシミなど、設備や素材の状態を確認し、場所に合った清掃をご案内します。'),
        ('定期的な清掃', '店舗やオフィスの利用状況、汚れのたまりやすい場所に合わせて、定期的な清掃をご相談いただけます。日頃のお掃除と専門的な清掃を組み合わせ、皆様が気持ちよく使える環境づくりをお手伝いします。'),
        ('衛生面の清掃', '多くの方が利用する店舗やオフィスでは、よく触れる場所や水まわりの汚れも気になります。トイレや洗面所、厨房など、場所と素材の状態を確認し、お掃除や除菌・抗菌のお手入れをご案内します。'),
        ('引き渡しに向けた清掃', '改装後やテナントの入れ替えに伴う清掃をご相談いただけます。床、窓、備え付けの設備などの状態を確認し、引き渡しに必要な清掃の範囲と進め方をご案内します。時期や作業時間もご相談ください。'),
    )
    scene_items = ''.join(f'<div class="c-reasons__item"><article class="office-wf__scene c-reason-card c-reasons__card"><span class="office-wf__scene-number c-reasons__point" aria-hidden="true">{i:02}</span><h3 class="c-reason-card__heading">{escape(title)}</h3><p class="c-reason-card__description">{escape(text)}</p></article><div class="c-reasons__navy" aria-hidden="true"></div></div>' for i, (title, text) in enumerate(scenes, 1))
    gallery_labels = dict(data['gallery'])
    features = []
    for i, (feature, layout) in enumerate(zip(data['features'], FEATURE_LAYOUTS), 1):
        detail = ''
        if layout == 'sanitizing':
            detail = f'<figure class="office-wf__detail-photo">{photo("basin",gallery_labels["basin"])}</figure>'
        section_head = '<header class="office-wf__section-head office-wf__section-head--display"><h2 id="office-wf-features-title">法人向け清掃のご案内</h2><p class="office-wf__display-word" aria-hidden="true">清潔な空間へ</p></header>' if layout == 'aircon' else ''
        features.append(f'''<article class="office-wf__feature office-wf__feature--{layout}" id="office-wf-{layout}">
{section_head}
<figure class="office-wf__main-photo">{photo(feature['image'],feature['title'])}</figure>
<div class="office-wf__feature-copy"><span class="office-wf__number" aria-hidden="true">{i:02}</span><div><h3>{escape(feature['title'])}</h3><p>{escape(feature['text'])}</p></div></div>
{detail}</article>''')
    spreads = f'<div class="office-wf__spread office-wf__spread--first">{features[0]}{features[1]}</div><div class="office-wf__spread office-wf__spread--second">{features[2]}{features[3]}</div>'
    gallery = ''.join(f'<figure class="office-wf__gallery-photo office-wf__gallery-photo--{key}">{photo(key,gallery_labels[key])}<figcaption>{escape(gallery_labels[key])}</figcaption></figure>' for key in GALLERY_KEYS)
    main = f'''<main class="office-wf">
<section class="office-wf__hero" aria-labelledby="office-wf-title">
<div class="office-wf__cover-frame"><div class="office-wf__cover">
<div class="office-wf__cover-title"><h1 id="office-wf-title">{escape(data['title'])}</h1><p class="office-wf__cover-word">店舗・オフィスを、<span>清潔に。</span></p>{inquiry_link()}</div>
<figure class="office-wf__cover-photo">{photo('floor','大きな窓と広いフロアのある店舗・オフィスの空間',False)}</figure>
</div></div>
<div class="office-wf__container office-wf__intro"><p class="office-wf__statement">{''.join(f'<span>{escape(line)}</span>' for line in STATEMENT_LINES)}</p><div><p class="office-wf__intro-copy">{escape(INTRO_COPY)}</p></div></div>
</section>
<section class="office-wf__section office-wf__scene-section c-home" id="office-wf-scenes" aria-labelledby="office-wf-scenes-title"><div class="office-wf__container"><header class="office-wf__section-head"><h2 id="office-wf-scenes-title">こんな清掃をご相談いただけます</h2></header><div class="office-wf__scenes c-grid c-reasons c-reasons--navy">{scene_items}</div></div></section>
<section class="office-wf__section office-wf__services" aria-labelledby="office-wf-features-title"><div class="office-wf__container"><div class="office-wf__features">{spreads}</div></div></section>
<section class="office-wf__section office-wf__range-section" aria-labelledby="office-wf-range-title"><div class="office-wf__container"><header class="office-wf__section-head"><h2 id="office-wf-range-title">幅広い清掃対応</h2></header><div class="office-wf__gallery">{gallery}</div></div></section>
<section class="office-wf__section office-wf__contact" id="office-wf-contact" aria-labelledby="office-wf-contact-title"><div class="office-wf__container office-wf__contact-grid"><div><h2 id="office-wf-contact-title">法人向け清掃のご相談</h2></div><div><p>{escape(data['closing'])}</p>{inquiry_link()}</div></div></section>
</main>'''
    page = f'{head}<body class="c-office-cleaning office-wf-page">{header}{main}{footer}</body></html>'
    (HERE / 'index.html').write_text(page, encoding='utf-8', newline='\n')
    print('Built the corporate brochure proposal with two editorial spreads.')


if __name__ == '__main__':
    build()
