"""Render the HOME banner and pending manga-LP slots from one source."""
import json
import re
from hashlib import sha256
from pathlib import Path
from bs4 import BeautifulSoup
from build_cart_catalogue import prices

ROOT = Path(__file__).resolve().parents[1]
TOPICS = ('ハウスクリーニングが人気な理由', 'エアコンクリーニングが人気な理由', '水まわりが人気な理由')


def fragments():
    catalogue = json.loads((ROOT / 'source/service-pages/catalogue.json').read_text(encoding='utf-8'))
    tiers = prices(BeautifulSoup(catalogue['products']['1']['html'], 'html.parser').select_one('.c-lineup-card__price'))['tiers']
    single = next(t['price'] for t in tiers if t['min'] == 1)
    multiple = next(t['price'] for t in tiers if t['min'] == 2)
    saving = single - multiple
    assert saving > 0
    banner = json.loads((ROOT / 'source/home-pickup-banner/banner.json').read_text(encoding='utf-8'))
    snapshot = dict(single=single, multiple=multiple, saving=saving,
                    total=multiple*2, totalSaving=saving*2)
    if snapshot != banner['generationPriceSnapshot']:
        raise ValueError('Regenerate the HOME banner to match the current aircon prices')
    if sha256((ROOT / 'source/site' / banner['asset']).read_bytes()).hexdigest() != banner['sha256']:
        raise ValueError('HOME banner artwork differs from its canonical metadata')
    cta = banner['cta']
    bounds = ';'.join(f'--home-pickup-cta-{key}:{cta[key]/banner[axis]*100:.6f}%'
                      for key, axis in (('x', 'width'), ('y', 'height'), ('width', 'width'), ('height', 'height')))
    alt = (f'エアコンクリーニング。２台まとめて{saving*2:,}円お得。１台あたり{saving:,}円お得。'
           '壁掛けタイプ（お掃除機能なし）／同時に２台以上のご注文時／税込。')
    upper = f'''<section class="home-pickup home-pickup--banner" id="home-pickup-banner" aria-labelledby="home-pickup-banner-title">
<div class="home-pickup__inner"><header class="home-pickup__heading"><span>PICK UP</span><h2 id="home-pickup-banner-title">まとめて頼むお掃除</h2></header>
<div class="home-pickup__banner" style="{bounds}"><img class="home-pickup__banner-image" src="/{banner['asset']}" width="{banner['width']}" height="{banner['height']}" alt="{alt}" loading="lazy" decoding="async"><a class="home-pickup__banner-cta" href="/house-cleaning/aircon/" aria-label="エアコンクリーニングの料金・サービスを見る"></a></div></div></section>'''
    cards = ''.join(f'''<article class="home-pickup__slot"><div class="home-first-view__placeholder home-pickup__placeholder"><span class="home-first-view__label">NO IMAGE</span><p class="home-first-view__note">ここにバナーが入ります</p></div><div class="home-pickup__copy"><h3>{title}</h3><p>漫画LP制作予定</p></div></article>''' for title in TOPICS)
    later = f'''<section class="home-pickup home-pickup--features" id="home-pickup" aria-labelledby="home-pickup-title"><div class="home-pickup__inner"><header class="home-pickup__heading"><span>PICK UP</span><h2 id="home-pickup-title">ピックアップ</h2></header><div class="home-pickup__slots">{cards}</div></div></section>'''
    return upper, later


def apply_home_pickups(html):
    if '<body class="c-home"' not in html:
        return html
    html = re.sub(r'<section\b(?=[^>]*\bid="home-pickup(?:-banner)?")[^>]*>.*?</section>\s*', '', html, flags=re.S)
    upper, later = fragments()
    for marker, fragment in ((r'<section\b[^>]*\bid="home-cleaning-list"[^>]*>', upper), (r'<section\b[^>]*\bc-featured-cleaning\b[^>]*>', later)):
        match = re.search(marker, html)
        if not match:
            raise ValueError('Missing HOME pickup insertion point')
        html = html[:match.start()] + fragment + '\n' + html[match.start():]
    return html
