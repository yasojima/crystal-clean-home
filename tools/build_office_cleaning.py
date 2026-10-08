"""Generate the corporate page from its canonical content and layout."""
from pathlib import Path
from string import Template
import json
import re
from html import escape
from build_shared_ui import transform, sync_manifest
from apply_site_identity import transform as apply_identity

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / 'source/site'
CONTENT = ROOT / 'source/office-cleaning'


def photo(key, label):
    return f'<img src="/assets/images/office-cleaning/{key}.png" alt="{escape(label)}" width="1536" height="1024" loading="lazy" decoding="async">'

def render():
    data = json.loads((CONTENT / 'content.json').read_text(encoding='utf-8'))
    values = {key: escape(value) for key, value in data.items() if isinstance(value, str)}
    for key in ('mosaic_heading', 'mosaic_care', 'mosaic_welcome', 'mosaic_label'):
        values[key] = ''.join(f'<span>{escape(value)}</span>' for value in data[key])
    values['hero'] = escape(data['hero'][0]) + f'<span>{escape(data["hero"][1])}</span>'
    values['points'] = ''.join(
        f'<div class="c-reasons__item"><article class="c-reason-card c-reasons__card">'
        f'<img class="c-reasons__point" src="/assets/images/reasons/reference-point-{i:02}.webp" alt="POINT {i:02}" width="205" height="70" loading="lazy" decoding="async">'
        f'<h3 class="c-reason-card__heading">{escape(point["title"])}</h3>'
        f'<p class="c-reason-card__description">{escape(point["text"])}</p></article>'
        '<div class="c-reasons__navy" aria-hidden="true"></div></div>'
        for i, point in enumerate(data['points'], 1)
    )
    values['gallery'] = ''.join(
        f'<figure class="office-wf__gallery-photo office-wf__gallery-photo--{key}">'
        f'{photo(key, label)}<figcaption>{escape(label)}</figcaption></figure>'
        for key, label in data['gallery']
    )
    values['inquiry'] = (
        '<a class="office-wf__inquiry-link c-category-simple-card" href="#" data-demo-dialog>'
        '<span class="office-wf__inquiry-surface c-category-simple-card__bottom">'
        f'<span class="office-wf__inquiry-text c-category-simple-card__text">{escape(data["contact_label"])}</span></span></a>'
    )
    main = Template((CONTENT / 'page.html').read_text(encoding='utf-8')).substitute(values)
    head = (SITE / 'index.html').read_text(encoding='utf-8').split('<body')[0]
    head = re.sub(r'\s*<(?:link|script)[^>]*(?:href|src)="/assets/(?:css|js)/home-[^"]+"[^>]*>(?:</script>)?', '', head)
    head = re.sub(r'(<meta\b[^>]*\b(?:name|property)="(?:description|og:description)"[^>]*\bcontent=")[^"]*', r'\g<1>店舗・オフィスの快適な環境づくりを、日々のお掃除から定期清掃・衛生管理・引き渡しまでサポートします。', head)
    head = re.sub(r'https://yasojima.github.io/(?=["<])', 'https://yasojima.github.io/business/cleaning/', head)
    head = re.sub(r'\s*<link[^>]*href="/assets/css/office-cleaning\.css[^>]*>', '', head)
    head = re.sub(r'(<meta\b[^>]*property="og:url"[^>]*content=")[^"]*', r'\g<1>https://yasojima.github.io/business/cleaning/', head)
    head = head.replace('</head>', '<link rel="stylesheet" href="/assets/css/office-cleaning.css?v=2026100820">\n</head>')
    return apply_identity(transform(f'{head}<body class="c-office-cleaning office-wf-page">{main}</body></html>'), True)

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
    print('Built corporate page: static hero, vertical composition, blended kitchen, three points, eight photos and consultation.')
