"""Build one corporate PR wireframe from the current copy and shared UI."""
import re
from html import escape
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
SITE = ROOT / 'source/site'


def build():
    data = json.loads((ROOT / 'source/office-cleaning/content.json').read_text(encoding='utf-8'))
    current = (SITE / 'business/cleaning/index.html').read_text(encoding='utf-8')
    head = current.split('<body')[0]
    head = re.sub(r'<title>.*?</title>', '<title>法人向け清掃 ワイヤーフレーム | Crystal Clean Home</title>', head)
    head = re.sub(r'<link[^>]*href="/assets/css/office-cleaning\.css[^>]*>', '', head)
    head = re.sub(r'<meta\b[^>]*name="robots"[^>]*>', '', head)
    head = head.replace('</head>', '<meta name="robots" content="noindex,nofollow">\n<link rel="stylesheet" href="/home-wireframe/business/wireframe.css">\n</head>')
    header = re.search(r'<header\b[^>]*class="c-header"[^>]*>.*?</header>', current, re.S).group()
    footer = re.search(r'<footer\b[^>]*class="c-footer\b[^>]*>.*?</footer>', current, re.S).group()

    def sentences(index):
        return [s + '。' for s in data['features'][index]['text'].split('。') if s]

    scenes = (
        ('日常では難しい箇所のお掃除', sentences(0)[1]),
        ('定期的な清掃', sentences(0)[2]),
        ('衛生面の清掃', data['features'][2]['text']),
        ('引き渡しに向けた清掃', sentences(3)[0]),
    )
    cards = ''.join(f'<article class="office-wf__scene"><span class="office-wf__number" aria-hidden="true">{i:02}</span><h3>{escape(title)}</h3><p>{escape(text)}</p></article>' for i, (title, text) in enumerate(scenes, 1))
    photo = lambda key, alt, lazy=True: f'<img src="/assets/images/office-cleaning/{key}.png" alt="{escape(alt)}" width="1536" height="1024" loading="{"lazy" if lazy else "eager"}" decoding="async">'
    features = ''.join(f'<article class="office-wf__feature"><figure>{photo(f["image"],f["title"])}</figure><div><h3>{escape(f["title"])}</h3><p>{escape(f["text"])}</p></div></article>' for f in data['features'])
    labels = ''.join(f'<li>{escape(label)}</li>' for _, label in data['gallery'])
    main = f'''<main class="office-wf">
<section class="office-wf__hero" aria-labelledby="office-wf-title"><div class="office-wf__container office-wf__hero-grid"><div><p class="office-wf__eyebrow">店舗・オフィス・共用部の清掃</p><h1 id="office-wf-title">{escape(data['title'])}</h1><p>{escape(data['intro'])}</p><div class="office-wf__hero-actions"><a class="office-wf__button" href="#office-wf-contact">法人向け清掃を相談する<span aria-hidden="true">→</span></a><a class="office-wf__text-link" href="#office-wf-scenes">相談できる清掃を見る<span aria-hidden="true">↓</span></a></div></div><figure>{photo('floor','店舗・オフィスの清掃に対応',False)}</figure></div></section>
<section class="office-wf__section office-wf__scene-section" id="office-wf-scenes" aria-labelledby="office-wf-scenes-title"><div class="office-wf__container"><h2 id="office-wf-scenes-title">こんな清掃をご相談いただけます</h2><div class="office-wf__scenes">{cards}</div></div></section>
<section class="office-wf__section" aria-labelledby="office-wf-features-title"><div class="office-wf__container"><h2 id="office-wf-features-title">{escape(data['heading'])}</h2><div class="office-wf__features">{features}</div></div></section>
<section class="office-wf__section office-wf__range-section" aria-labelledby="office-wf-range-title"><div class="office-wf__container"><h2 id="office-wf-range-title">幅広い清掃対応</h2><ul class="office-wf__range">{labels}</ul></div></section>
<section class="office-wf__section office-wf__contact" id="office-wf-contact" aria-labelledby="office-wf-contact-title"><div class="office-wf__container"><h2 id="office-wf-contact-title">法人向け清掃のご相談</h2><p>{escape(data['closing'])}</p><a class="office-wf__button" href="/contact/business/" data-demo-dialog>店舗・オフィスのお掃除を相談する<span aria-hidden="true">→</span></a></div></section>
</main>'''
    page = f'{head}<body class="c-office-cleaning office-wf-page">{header}{main}{footer}</body></html>'
    (HERE / 'index.html').write_text(page, encoding='utf-8', newline='\n')
    print('Built one corporate PR wireframe from the current copy, photos and shared UI.')


if __name__ == '__main__':
    build()
