"""Generate the corporate page from its canonical content and layout."""
from pathlib import Path
from string import Template
import json
import re
from html import escape
from build_shared_ui import transform, sync_manifest
from apply_site_identity import transform as apply_identity
from service_banner import render_service_banner

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / 'source/site'
CONTENT = ROOT / 'source/office-cleaning'


def photo(key, label):
    return f'<img src="/assets/images/office-cleaning/{key}.png" alt="{escape(label)}" width="1536" height="1024" loading="lazy" decoding="async">'

def render():
    data = json.loads((CONTENT / 'content.json').read_text(encoding='utf-8'))
    values = {key: escape(value) for key, value in data.items() if isinstance(value, str)}
    banner = data['banner']
    values['service_banner'] = render_service_banner(
        data['title'], banner['lines'], banner['artwork'], banner['alt'],
        mobile_src=banner['mobile_artwork'],
        image_width=banner['width'], image_height=banner['height'])
    values['intro'] = ''.join(f'<p>{escape(paragraph)}</p>' for paragraph in data['intro'])
    values['services'] = ''.join(
        '<article class="office-wf__service"><div class="office-wf__service-panel">'
        f'<div class="office-wf__service-copy"><h3>{escape(service["title"])}</h3>'
        + ''.join(f'<p>{escape(paragraph)}</p>' for paragraph in service['paragraphs'])
        + f'</div><figure class="office-wf__service-photo">{photo(service["image"], service["title"])}</figure></div></article>'
        for service in data['services']
    )
    values['gallery'] = ''.join(
        f'<figure class="office-wf__gallery-photo office-wf__gallery-photo--{key}">'
        f'{photo(key, label)}<figcaption>{escape(label)}</figcaption></figure>'
        for key, label in data['gallery']
    )
    main = Template((CONTENT / 'page.html').read_text(encoding='utf-8')).substitute(values)
    head = (SITE / 'index.html').read_text(encoding='utf-8').split('<body')[0]
    head = re.sub(r'\s*<(?:link|script)[^>]*(?:href|src)="/assets/(?:css|js)/home-[^"]+"[^>]*>(?:</script>)?', '', head)
    head = re.sub(r'(<meta\b[^>]*\b(?:name|property)="(?:description|og:description)"[^>]*\bcontent=")[^"]*', r'\g<1>店舗・オフィスの快適な環境づくりを、日々のお掃除から定期清掃・衛生管理・引き渡しまでサポートします。', head)
    head = re.sub(r'https://yasojima.github.io/(?=["<])', 'https://yasojima.github.io/business/cleaning/', head)
    head = re.sub(r'\s*<link[^>]*href="/assets/css/office-cleaning\.css[^>]*>', '', head)
    head = re.sub(r'(<meta\b[^>]*property="og:url"[^>]*content=")[^"]*', r'\g<1>https://yasojima.github.io/business/cleaning/', head)
    if '/assets/css/aircon-hero.css' not in head:
        head = head.replace('</head>', '<link rel="stylesheet" href="/assets/css/aircon-hero.css?v=2026100902">\n</head>')
    head = head.replace('</head>', '<link rel="stylesheet" href="/assets/css/office-cleaning.css?v=2026100902">\n</head>')
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
    print('Built corporate page: introduction, four alternating service panels, twelve photos and closing copy.')
