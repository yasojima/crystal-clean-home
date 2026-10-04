"""Render the canonical site header and full footer into every public page."""
from pathlib import Path
import argparse
import hashlib
import json
import mimetypes
import re

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / 'source/site'
COMPONENTS = ROOT / 'source/shared-ui'
ASSETS = (
    '<link rel="stylesheet" href="/assets/css/aircon-header.css?v=2026100312">',
    '<link rel="stylesheet" href="/assets/css/site-footer.css?v=2026100403">',
    '<script src="/assets/js/aircon-header.js?v=2026100401" defer></script>',
)


def transform(html, is_aircon=False):
    newline = '\r\n' if '\r\n' in html else '\n'
    if re.search(r'<div\b[^>]*\bid="first-view"', html):
        html = re.sub(r'\s*<span class="c-site-page-top" id="first-view" aria-hidden="true"></span>', '', html)
    for name in ('header', 'footer'):
        fragment = (COMPONENTS / (name + '.html')).read_bytes().decode('utf-8').strip()
        pattern = r'<' + name + r'\b(?=[^>]*\bclass="[^"]*\bc-' + name + r'(?:\s|"))[^>]*>.*?</' + name + r'>'
        html, replaced = re.subn(pattern, lambda _: fragment, html, count=1, flags=re.S)
        if not replaced:
            marker = '<main' if name == 'header' else '</body>'
            html = html.replace(marker, fragment + newline + marker, 1)
    for rel in ('aircon-header.css', 'site-footer.css', 'aircon-header.js'):
        html = re.sub(r'\s*<(?:link|script)\b[^>]*(?:href|src)="/assets/(?:css|js)/' + re.escape(rel) + r'(?:\?v=\d+)?"[^>]*>(?:</script>)?', '', html)
    html = html.replace('</head>', newline.join(ASSETS) + newline + '</head>', 1)
    if '/assets/js/common.js' not in html:
        html = html.replace('</head>', '<script src="/assets/js/common.js?v=2026100252" defer></script>' + newline + '</head>', 1)
    else:
        html = re.sub(r'/assets/js/common\.js(?:\?v=\d+)?', '/assets/js/common.js?v=2026100252', html)
    layout_version = '2026100503' if is_aircon else '2026100402'
    html = re.sub(r'/assets/css/aircon-layout\.css\?v=\d+', f'/assets/css/aircon-layout.css?v={layout_version}', html)
    if not re.search(r'\bid="first-view"', html):
        marker = '<span class="c-site-page-top" id="first-view" aria-hidden="true"></span>'
        html = re.sub(r'(</header>)', lambda m: m.group() + newline + marker, html, count=1)
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
    manifest_changes = sync_manifest([*pages, SITE/'assets/css/aircon-layout.css', SITE/'assets/css/site-footer.css', SITE/'assets/js/aircon-header.js'], args.check)
    print(json.dumps(dict(pages=len(pages), changed=changed, manifest_updates=len(manifest_changes), check=args.check), ensure_ascii=False))
    if args.check and (changed or manifest_changes):
        raise SystemExit(1)


if __name__ == '__main__':
    main()
