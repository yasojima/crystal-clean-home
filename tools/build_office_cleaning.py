"""Generate the corporate cleaning page from its single content source."""
from pathlib import Path
import json
import re
from html import escape
from build_shared_ui import transform, sync_manifest
from apply_site_identity import transform as apply_identity

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / 'source/site'
DATA = ROOT / 'source/office-cleaning/content.json'

def render():
    data = json.loads(DATA.read_text(encoding='utf-8'))
    head = (SITE / 'index.html').read_text(encoding='utf-8').split('<body')[0]
    head = re.sub(r'\s*<(?:link|script)[^>]*(?:href|src)="/assets/(?:css|js)/home-[^"]+"[^>]*>(?:</script>)?', '', head)
    head = re.sub(r'(<meta\b[^>]*\b(?:name|property)="(?:description|og:description)"[^>]*\bcontent=")[^"]*', r'\g<1>店舗・オフィスのエアコン、床、除菌・抗菌、引き渡し清掃をご案内します。', head)
    head = re.sub(r'https://yasojima.github.io/(?=["<])', 'https://yasojima.github.io/business/cleaning/', head)
    head = re.sub(r'\s*<link[^>]*href="/assets/css/office-cleaning\.css[^>]*>', '', head)
    head = head.replace('</head>', '<link rel="stylesheet" href="/assets/css/office-cleaning.css?v=2026100701">\n</head>')
    photo = lambda key, label: f'<img src="/assets/images/office-cleaning/{key}.png" alt="{escape(label)}" width="1536" height="1024" loading="lazy" decoding="async">'
    intro = ''.join(f'<p>{escape(t)}</p>' for t in data['intro'])
    features = ''.join(f'<article class="office-cleaning__feature"><div class="office-cleaning__text"><h3>{escape(f["title"])}</h3><p>{"<br>".join(escape(t) for t in f["lines"])}</p></div><figure>{photo(f["image"], f["title"])}</figure></article>' for f in data['features'])
    gallery = ''.join(f'<li><figure>{photo(key, label)}<figcaption>{escape(label)}</figcaption></figure></li>' for key, label in data['gallery'])
    html = f'''{head}<body class="c-office-cleaning"><main class="office-cleaning">
<h1>{escape(data['title'])}</h1><div class="office-cleaning__intro">{intro}</div>
<section aria-labelledby="office-cleaning-heading"><h2 id="office-cleaning-heading">{escape(data['heading'])}</h2>{features}
<div class="office-cleaning__range"><h3>幅広い清掃対応</h3><ul>{gallery}</ul></div>
<div class="office-cleaning__closing"><p>{'<br>'.join(escape(t) for t in data['closing'])}</p></div></section>
<div class="office-cleaning__contact"><a class="c-double-icon-button" href="/contact/business/"><span class="c-double-icon-button__inner">店舗・オフィスのお掃除を相談する<span aria-hidden="true">›</span></span></a></div>
</main></body></html>'''
    return apply_identity(transform(html), True)

if __name__ == '__main__':
    target = SITE / 'business/cleaning/index.html'
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render(), encoding='utf-8', newline='')
    sitemap = SITE / 'sitemap.xml'
    xml = sitemap.read_bytes().decode('utf-8')
    url = 'https://yasojima.github.io/business/cleaning/'
    if url not in xml:
        xml = xml.replace('</urlset>', f'  <url><loc>{url}</loc></url>\n</urlset>')
        sitemap.write_bytes(xml.encode('utf-8'))
    paths = [target, sitemap, SITE / 'assets/css/office-cleaning.css', *sorted((SITE / 'assets/images/office-cleaning').glob('*.png'))]
    sync_manifest(paths)
    print('Built corporate cleaning page: four features and twelve photo subjects; no opening photo banner.')
