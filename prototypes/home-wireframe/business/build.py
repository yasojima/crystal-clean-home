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


def build():
    data = json.loads((ROOT / 'source/office-cleaning/content.json').read_text(encoding='utf-8'))
    current = (SITE / 'business/cleaning/index.html').read_text(encoding='utf-8')
    head = current.split('<body')[0]
    head = re.sub(r'<title>.*?</title>', '<title>法人向け清掃 ワイヤーフレーム | Crystal Clean Home</title>', head)
    head = re.sub(r'<link[^>]*href="/assets/css/office-cleaning\.css[^>]*>', '', head)
    head = re.sub(r'<meta\b[^>]*name="robots"[^>]*>', '', head)
    head = head.replace('</head>', '<meta name="robots" content="noindex,nofollow">\n<link rel="stylesheet" href="/home-wireframe/business/wireframe.css?v=2026100808">\n</head>')
    header = re.search(r'<header\b[^>]*class="c-header"[^>]*>.*?</header>', current, re.S).group()
    footer = re.search(r'<footer\b[^>]*class="c-footer\b[^>]*>.*?</footer>', current, re.S).group()

    def sentences(index):
        return [s + '。' for s in data['features'][index]['text'].split('。') if s]

    def photo(key, alt, lazy=True):
        return f'<img src="/assets/images/office-cleaning/{key}.png" alt="{escape(alt)}" width="1536" height="1024" loading="{"lazy" if lazy else "eager"}" decoding="async">'

    scenes = (
        ('日常では難しい箇所のお掃除', sentences(0)[1]),
        ('定期的な清掃', sentences(0)[2]),
        ('衛生面の清掃', data['features'][2]['text']),
        ('引き渡しに向けた清掃', sentences(3)[0]),
    )
    scene_items = ''.join(f'<article class="office-wf__scene"><span class="office-wf__scene-number" aria-hidden="true">{i:02}</span><h3>{escape(title)}</h3><p>{escape(text)}</p></article>' for i, (title, text) in enumerate(scenes, 1))
    gallery_labels = dict(data['gallery'])
    features = []
    for i, (feature, layout) in enumerate(zip(data['features'], FEATURE_LAYOUTS), 1):
        detail = ''
        if layout == 'sanitizing':
            detail = f'<figure class="office-wf__detail-photo">{photo("shower",gallery_labels["shower"])}<figcaption>{escape(gallery_labels["shower"])}</figcaption></figure>'
        features.append(f'''<article class="office-wf__feature office-wf__feature--{layout}" id="office-wf-{layout}">
<figure class="office-wf__main-photo">{photo(feature['image'],feature['title'])}</figure>
<div class="office-wf__feature-copy"><span class="office-wf__number" aria-hidden="true">{i:02}</span><div><h3>{escape(feature['title'])}</h3><p>{escape(feature['text'])}</p></div></div>
{detail}</article>''')
    spreads = f'<div class="office-wf__spread office-wf__spread--first">{features[0]}{features[1]}</div><div class="office-wf__spread office-wf__spread--second">{features[2]}{features[3]}</div>'
    gallery = ''.join(f'<figure class="office-wf__gallery-photo office-wf__gallery-photo--{key}">{photo(key,gallery_labels[key])}<figcaption>{escape(gallery_labels[key])}</figcaption></figure>' for key in GALLERY_KEYS)
    main = f'''<main class="office-wf">
<section class="office-wf__hero" aria-labelledby="office-wf-title">
<div class="office-wf__cover">
<div class="office-wf__cover-title"><p class="office-wf__eyebrow">クリスタルクリーンホーム</p><h1 id="office-wf-title">{escape(data['title'])}</h1><p class="office-wf__cover-word">店舗・オフィスを、<span>清潔に。</span></p><p class="office-wf__cover-category">店舗・オフィス・共用部の清掃</p><a class="office-wf__inquiry-link" href="#office-wf-contact">法人向け清掃のご相談<span aria-hidden="true">↗</span></a></div>
<figure class="office-wf__cover-photo">{photo('floor','大きな窓と広いフロアのある店舗・オフィスの空間',False)}<figcaption aria-hidden="true">法人向け清掃サービス</figcaption></figure>
</div>
<div class="office-wf__container office-wf__intro"><p class="office-wf__statement">{escape(data['heading'])}</p><div><p class="office-wf__intro-copy">{escape(data['intro'])}</p><a class="office-wf__text-link" href="#office-wf-scenes">相談できる清掃を見る<span aria-hidden="true">↓</span></a></div></div>
</section>
<section class="office-wf__section office-wf__scene-section" id="office-wf-scenes" aria-labelledby="office-wf-scenes-title"><div class="office-wf__container"><header class="office-wf__section-head"><p class="office-wf__eyebrow" aria-hidden="true">01 / 清掃のご相談</p><h2 id="office-wf-scenes-title">こんな清掃をご相談いただけます</h2></header><div class="office-wf__scenes">{scene_items}</div></div></section>
<section class="office-wf__section office-wf__services" aria-labelledby="office-wf-features-title"><div class="office-wf__container"><header class="office-wf__section-head office-wf__section-head--display"><div><p class="office-wf__eyebrow" aria-hidden="true">02 / サービス紹介</p><h2 id="office-wf-features-title">法人向け清掃のご案内</h2></div><p class="office-wf__display-word" aria-hidden="true">清潔な空間へ</p></header><div class="office-wf__features">{spreads}</div></div></section>
<section class="office-wf__section office-wf__range-section" aria-labelledby="office-wf-range-title"><div class="office-wf__container"><header class="office-wf__section-head"><p class="office-wf__eyebrow" aria-hidden="true">03 / 対応箇所</p><h2 id="office-wf-range-title">幅広い清掃対応</h2></header><div class="office-wf__gallery">{gallery}</div></div></section>
<section class="office-wf__section office-wf__contact" id="office-wf-contact" aria-labelledby="office-wf-contact-title"><div class="office-wf__container office-wf__contact-grid"><div><p class="office-wf__eyebrow" aria-hidden="true">04 / お問い合わせ</p><h2 id="office-wf-contact-title">法人向け清掃のご相談</h2></div><div><p>{escape(data['closing'])}</p><a class="office-wf__inquiry-link" href="/contact/business/" data-demo-dialog>お問い合わせはこちら<span aria-hidden="true">↗</span></a></div></div></section>
</main>'''
    page = f'{head}<body class="c-office-cleaning office-wf-page">{header}{main}{footer}</body></html>'
    (HERE / 'index.html').write_text(page, encoding='utf-8', newline='\n')
    print('Built the corporate brochure proposal with two editorial spreads.')


if __name__ == '__main__':
    build()
