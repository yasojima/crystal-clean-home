"""Render the HOME banner and pending manga-LP slots from one source."""
import json
import re
from pathlib import Path
from bs4 import BeautifulSoup
from build_cart_catalogue import prices

ROOT = Path(__file__).resolve().parents[1]
TOPICS = ('ハウスクリーニングが人気な理由', 'エアコンクリーニングが人気な理由', '水まわりが人気な理由')


def fragments():
    catalogue = json.loads((ROOT / 'source/service-pages/catalogue.json').read_text(encoding='utf-8'))
    tiers = prices(BeautifulSoup(catalogue['products']['1']['html'], 'html.parser').select_one('.c-lineup-card__price'))['tiers']
    saving = next(t['price'] for t in tiers if t['min'] == 1) - next(t['price'] for t in tiers if t['min'] == 2)
    assert saving > 0
    upper = f'''<section class="home-pickup home-pickup--banner" id="home-pickup-banner" aria-labelledby="home-pickup-banner-title">
<div class="home-pickup__inner"><header class="home-pickup__heading"><span>PICK UP</span><h2 id="home-pickup-banner-title">まとめて頼むお掃除</h2></header>
<a class="home-pickup__banner" href="/house-cleaning/aircon/">
<div class="home-pickup__banner-copy"><span class="home-pickup__eyebrow">まとめてお得に</span><h3><span>エアコン２台、</span><span>まとめてお得に。</span></h3><p class="home-pickup__emphasis">１台あたり {saving:,}円 お得</p><span class="home-pickup__action">まとめて頼む料金を見る <span aria-hidden="true">→</span></span></div>
<div class="home-pickup__art" aria-hidden="true"><img src="/assets/images/cleaning-illustrations/aircon.png" alt="" loading="lazy" decoding="async"><img src="/assets/images/cleaning-illustrations/aircon.png" alt="" loading="lazy" decoding="async"></div>
<small class="home-pickup__note">壁掛けタイプ（お掃除機能なし）／同時に２台以上のご注文時・税込</small></a></div></section>'''
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
