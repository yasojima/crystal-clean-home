"""Render the canonical site header and full footer into every public page."""
from pathlib import Path
import argparse
import hashlib
import json
import mimetypes
import re
from apply_cleaning_artwork import transform_references
from home_section_backgrounds import apply_home_section_backgrounds
from home_pickups import apply_home_pickups

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / 'source/site'
COMPONENTS = ROOT / 'source/shared-ui'
ASSETS = (
    '<link rel="stylesheet" href="/assets/css/aircon-header.css?v=2026100705">',
    '<link rel="stylesheet" href="/assets/css/site-footer.css?v=2026100701">',
    "<script src=\"/assets/js/aircon-header.js?v=2026100701\" defer></script>",
    '<link rel="stylesheet" href="/assets/css/site-cart.css?v=2026100604">',
    '<script src="/assets/js/cart-catalogue.js?v=2026100603" defer></script>',
    '<script src="/assets/js/cart-core.js?v=2026100528" defer></script>',
    '<script src="/assets/js/site-cart.js?v=2026100603" defer></script>',
)


def replace_div_contents(html, pattern, contents):
    start = re.search(pattern, html)
    if not start:
        return html
    depth = 1
    for tag in re.finditer(r'</?div\b[^>]*>', html[start.end():]):
        depth += -1 if tag.group().startswith('</') else 1
        if depth == 0:
            end = start.end() + tag.start()
            return html[:start.end()] + contents + html[end:]
    raise ValueError('Unclosed category grid')


def shared_category_cards(html, featured):
    cards = re.findall(r'<a\b[^>]*\bclass="[^"]*\bc-category-simple-card\b[^>]*>.*?</a>', featured, re.S)
    if len(cards) != 8:
        raise ValueError('The canonical category template must contain eight cards')
    html = replace_div_contents(html, r'<div class="lp-services(?: c-house-cleaning-links)?">', '\n'.join(cards))
    html = html.replace('<div class="lp-services">', '<div class="lp-services c-house-cleaning-links">')
    quick_cards = '\n'.join(cards).replace('/house-cleaning/', '/quick_cart/').replace('c-house-cleaning-links__link', 'step__card')
    return replace_div_contents(html, r'<div class="c-grid"[^>]*>(?=\s*<a class="c-category-simple-card step__card")', quick_cards)


def transform(html, is_aircon=False):
    html = transform_references(html)
    html = re.sub(r'/assets/js/demo-contact\.js(?:\?v=\d+)?', '/assets/js/demo-contact.js?v=2026100601', html)
    has_estimate = '/assets/js/cart-estimate.js' in html
    html = re.sub(r'\s*<script\b[^>]*src="/assets/js/cart-estimate\.js(?:\?v=\d+)?"[^>]*>\s*</script>', '', html)
    newline = '\r\n' if '\r\n' in html else '\n'
    featured = (ROOT / 'source/service-pages/templates/categories.html').read_bytes().decode('utf-8').strip()
    html = shared_category_cards(html, featured)
    def shared_featured(match):
        section = match.group()
        if ('c-featured-cleaning' in section or 'home-cleaning-menu' in section or
                'ハウスクリーニングのメニュー一覧はこちら' in section):
            return featured
        return section
    html = re.sub(r'<section\b[^>]*>.*?</section>', shared_featured, html, flags=re.S)
    html = apply_home_section_backgrounds(apply_home_pickups(html))
    html = re.sub(r'<div class="home-first-guide home-business-guide">(.*?)</div>(?=</div>)', r'<a class="home-first-guide home-business-guide" href="/business/cleaning/">\1</a>', html, flags=re.S)
    if '<body class="c-home"' in html and '/assets/css/home-pickups.css' not in html:
        html = html.replace('</head>', '<link rel="stylesheet" href="/assets/css/home-pickups.css?v=2026100701">' + newline + '</head>', 1)
    heading = (COMPONENTS / 'cleaning-menu-heading.html').read_text(encoding='utf-8').strip()
    def shared_cleaning_heading(match):
        content = match[2]
        if (content.strip() in ('ハウスクリーニング一覧', '注目のハウスクリーニング') or
                'class="c-cleaning-menu-heading__brand"' in content):
            return match[1] + heading + match[3]
        return match[0]
    html = re.sub(r'(<h2\b[^>]*>)(.*?)(</h2>)', shared_cleaning_heading, html, flags=re.S)
    if 'class="l-section l-section--limited c-featured-cleaning ' in html and '/assets/css/aircon-layout.css' not in html:
        html = html.replace('</head>', '<link rel="stylesheet" href="/assets/css/aircon-layout.css?v=2026100706">' + newline + '</head>', 1)
    if re.search(r'<div\b[^>]*\bid="first-view"', html):
        html = re.sub(r'\s*<span class="c-site-page-top" id="first-view" aria-hidden="true"></span>', '', html)
    for name in ('header', 'footer'):
        fragment = (COMPONENTS / (name + '.html')).read_bytes().decode('utf-8').strip()
        pattern = r'<' + name + r'\b(?=[^>]*\bclass="[^"]*\bc-' + name + r'(?:\s|"))[^>]*>.*?</' + name + r'>'
        html, replaced = re.subn(pattern, lambda _: fragment, html, count=1, flags=re.S)
        if not replaced:
            marker = '<main' if name == 'header' else '</body>'
            html = html.replace(marker, fragment + newline + marker, 1)
    for rel in ('aircon-header.css', 'site-footer.css', 'aircon-header.js', 'site-cart.css',
                'cart-catalogue.js', 'cart-core.js', 'site-cart.js'):
        html = re.sub(r'\s*<(?:link|script)\b[^>]*(?:href|src)="/assets/(?:css|js)/' + re.escape(rel) + r'(?:\?v=\d+)?"[^>]*>(?:</script>)?', '', html)
    assets = (*ASSETS, '<script src="/assets/js/cart-estimate.js?v=2026100601" defer></script>') if has_estimate else ASSETS
    html = html.replace('</head>', newline.join(assets) + newline + '</head>', 1)
    html = re.sub(r'<script\b[^>]*src="/assets/js/(?:house-cleaning/(?:product-top|osoujiless)|simulation/parent-product|office/product-detail)\.js(?:\?[^\"]*)?"[^>]*>\s*</script>\s*', '', html)
    if '/assets/js/common.js' not in html:
        html = html.replace('</head>', '<script src="/assets/js/common.js?v=2026100602" defer></script>' + newline + '</head>', 1)
    else:
        html = re.sub(r'/assets/js/common\.js(?:\?v=\d+)?', '/assets/js/common.js?v=2026100602', html)
    html = re.sub(r'/assets/css/aircon-hero\.css(?:\?v=\d+)?', '/assets/css/aircon-hero.css?v=2026100701', html)
    html = re.sub(r'/assets/css/common\.css(?:\?[^"\s<>]*)?', '/assets/css/common.css?v=2026100707', html)
    html = re.sub(r'/assets/css/simulation/index\.css(?:\?v=\d+)?', '/assets/css/simulation/index.css?v=2026100704', html)
    html = re.sub(r'/assets/css/home-first-view\.css(?:\?v=\d+)?', '/assets/css/home-first-view.css?v=2026100705', html)
    html = re.sub(r'/assets/css/home-pickups\.css(?:\?v=\d+)?', '/assets/css/home-pickups.css?v=2026100802', html)
    html = re.sub(r'/assets/js/home-first-view\.js(?:\?v=\d+)?', '/assets/js/home-first-view.js?v=2026100601', html)
    if '<body class="c-home"' in html:
        for asset, kind in [('home-concerns.css', 'css'), ('home-concerns.js', 'js')]:
            html = re.sub(r'/assets/' + kind + '/' + re.escape(asset) + r'(?:\?v=\d+)?',
                          '/assets/' + kind + '/' + asset + ('?v=2026100706' if kind == 'css' else '?v=2026100608'), html)
    html = re.sub(r'/assets/css/beginner-lp\.css(?:\?v=\d+)?', '/assets/css/beginner-lp.css?v=2026100702', html)
    for stylesheet, version in (('first-lp-desktop.css', '2026100601'), ('first-lp-mobile.css', '2026100703')):
        html = re.sub(r'/assets/css/' + re.escape(stylesheet) + r'(?:\?v=\d+)?',
                      '/assets/css/' + stylesheet + '?v=' + version, html)
    if 'id="cch-first-lp"' in html and '/assets/js/lp-render-check.js' not in html:
        html = html.replace('</head>', '<script src="/assets/js/lp-render-check.js?v=2026100703"></script>' + newline + '</head>', 1)
    html = re.sub(r'/assets/js/lp-render-check\.js(?:\?v=\d+)?', '/assets/js/lp-render-check.js?v=2026100703', html)
    layout_version = '2026100707'
    html = re.sub(r'/assets/css/aircon-layout\.css\?v=\d+', f'/assets/css/aircon-layout.css?v={layout_version}', html)
    html = re.sub(r'/assets/css/service-format\.css(?:\?v=\d+)?', '/assets/css/service-format.css?v=2026100701', html)
    if 'class="c-first-view' in html and '/assets/js/service-first-view.js' not in html:
        html = html.replace('</head>', '<script src="/assets/js/service-first-view.js?v=2026100701" defer></script>' + newline + '</head>', 1)
    if not re.search(r'\bid="first-view"', html):
        marker = '<span class="c-site-page-top" id="first-view" aria-hidden="true"></span>'
        html = re.sub(r'(</header>)', lambda m: m.group() + newline + marker, html, count=1)
    html = re.sub(r'(<link\b[^\r\n]*href="/assets/css/home-pickups\.css[^\"]*"[^\r\n]*>)\r\n', r'\1\n', html)
    return html


def sync_manifest(paths, check=False):
    manifest_path = ROOT / 'source/manifest.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    changed = []
    for path in paths:
        relative = path.relative_to(SITE).as_posix()
        data = path.read_bytes()
        digest = hashlib.sha256(data).hexdigest()
        records = [r for r in manifest['files'].values() if r['path'] == relative]
        if not records:
            url = manifest['origin'].rstrip('/') + '/' + relative
            record = dict(path=relative, effective_url=url, status=200,
                          content_type=mimetypes.guess_type(relative)[0] or 'application/octet-stream',
                          origin_type='local-shared-ui')
            manifest['files'][url] = record
            records = [record]
        for record in records:
            if record.get('sha256') != digest or record.get('bytes') != len(data):
                if record.get('sha256') and not record.get('origin_type', '').startswith('local-'):
                    record.setdefault('source_sha256', record['sha256'])
                    record.setdefault('source_bytes', record['bytes'])
                    record['scope_edited'] = True
                record.update(sha256=digest, bytes=len(data))
                changed.append(relative)
    if changed and not check:
        unique = {r['path']:r for r in manifest['files'].values()}
        manifest['counts'].update(urls=len(manifest['files']), unique_paths=len(unique),
                                  bytes=sum(r['bytes'] for r in unique.values()))
        manifest_path.write_bytes(json.dumps(manifest, ensure_ascii=False, indent=2).encode('utf-8'))
    return changed


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    changed = []
    pages = sorted(SITE.rglob('*.html'))
    for page in pages:
        original = page.read_bytes().decode('utf-8')
        output = transform(original, is_aircon=(page == SITE / 'house-cleaning/aircon/index.html'))
        if output != original:
            changed.append(page.relative_to(SITE).as_posix())
            if not args.check:
                page.write_bytes(output.encode('utf-8'))
    from build_cart_catalogue import build as build_cart
    build_cart(args.check)
    manifest_changes = sync_manifest([*pages, SITE/'assets/css/common.css', SITE/'assets/css/simulation/index.css', SITE/'assets/css/aircon-header.css', SITE/'assets/css/aircon-hero.css', SITE/'assets/css/service-format.css', SITE/'assets/js/service-first-view.js', SITE/'assets/css/aircon-layout.css', SITE/'assets/css/site-footer.css', SITE/'assets/js/aircon-header.js', SITE/'assets/css/home-first-view.css', SITE/'assets/css/home-concerns.css', SITE/'assets/js/home-concerns.js', SITE/'assets/css/beginner-lp.css', SITE/'assets/js/home-first-view.js', SITE/'assets/js/common.js', SITE/'assets/css/site-cart.css', SITE/'assets/js/cart-catalogue.js', SITE/'assets/js/cart-core.js', SITE/'assets/js/site-cart.js', SITE/'assets/images/common-parts/icon/share.svg', SITE/'assets/images/home/first-guide-banner.png', SITE/'assets/images/home/business-guide-banner.png', SITE/'assets/images/home/first-guide-banner-mobile.png', SITE/'assets/images/home/business-guide-banner-mobile.png'], args.check)
    manifest_changes += sync_manifest([SITE/'assets/js/cart-estimate.js', SITE/'assets/js/demo-contact.js', SITE/'assets/js/lp-render-check.js'], args.check)
    manifest_changes += sync_manifest([SITE/'assets/css/first-lp-desktop.css', SITE/'assets/css/first-lp-mobile.css'], args.check)
    manifest_changes += sync_manifest([SITE/'assets/css/home-pickups.css'], args.check)
    manifest_changes += sync_manifest([SITE/'assets/images/home/aircon-bundle-banner.png'], args.check)
    manifest_changes += sync_manifest([SITE/'assets/css/office-cleaning.css', *sorted((SITE/'assets/images/office-cleaning').glob('*.png'))], args.check)
    manifest_changes += sync_manifest(sorted((SITE/'assets/images/cleaning-illustrations').glob('*.png')), args.check)
    print(json.dumps(dict(pages=len(pages), changed=changed, manifest_updates=len(manifest_changes), check=args.check), ensure_ascii=False))
    if args.check and (changed or manifest_changes):
        raise SystemExit(1)


if __name__ == '__main__':
    main()
