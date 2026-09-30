"""Prepare the approved scope reduction and retain shared dependencies."""
import hashlib
import json
import re
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.parse import urljoin, urlsplit, unquote
from lxml import html
from site_scope import ROOT, ORIGIN, excluded_url, prune_html

SITE = ROOT / 'source/site'
STAGE = Path.home() / 'AppData/Local/Temp/cch-scope-stage'
manifest = json.loads((ROOT / 'source/manifest.json').read_text(encoding='utf-8'))
records = manifest['files']
unique = {r['path']: r for r in records.values()}
urls_by_path = {r['path']: u for u, r in records.items()}
local_by_url_path = {unquote(urlsplit(u).path): r['path'] for u, r in records.items()}
asset_extensions = {'.css', '.js', '.mjs', '.json', '.webmanifest', '.png', '.jpg', '.jpeg', '.webp', '.gif', '.svg', '.ico', '.avif', '.bmp', '.woff', '.woff2', '.ttf', '.eot', '.otf', '.mp4', '.webm', '.mp3', '.pdf', '.zip'}
css_urls = re.compile(r'url\(\s*[\"\']?([^\"\')\s]+)', re.I)
css_imports = re.compile(r'''@import\s+["']([^"']+)["']''', re.I)
js_assets = re.compile(r'''["'`]((?:/assets/|/favicon/|\.\.?/)[^"'`\s<>]+)["'`]''')


def resource_urls(data, kind, url):
    suffix = Path(urlsplit(url).path).suffix.lower()
    if 'text/html' in kind:
        try:
            doc = html.fromstring(data)
        except (ValueError, html.etree.ParserError):
            return []
        refs = doc.xpath('//@src | //@poster | //@data-src | //@data-original')
        for value in doc.xpath('//@srcset | //@data-srcset'):
            refs += [part.strip().split()[0] for part in value.split(',') if part.strip()]
        refs += [node.get('href') for node in doc.xpath('//link[@href]') if any(word in node.get('rel', '').lower() for word in ['stylesheet', 'icon', 'manifest', 'preload'])]
        refs += [value for value in doc.xpath('//a/@href') if Path(urlsplit(value).path).suffix.lower() in asset_extensions]
        for text in doc.xpath('//@style | //style/text()'):
            refs += css_urls.findall(text)
        for text in doc.xpath('//script[not(@src)]/text()'):
            refs += [ref for ref in js_assets.findall(text) if Path(urlsplit(ref).path).suffix.lower() in asset_extensions]
        return refs
    if suffix == '.css' or 'text/css' in kind:
        text = data.decode('utf-8', 'replace')
        return css_urls.findall(text) + css_imports.findall(text)
    if suffix in {'.js', '.mjs'} or 'javascript' in kind:
        return [ref for ref in js_assets.findall(data.decode('utf-8', 'replace')) if Path(urlsplit(ref).path).suffix.lower() in asset_extensions]
    if suffix in {'.json', '.webmanifest'}:
        try:
            value = json.loads(data)
            return [icon['src'] for icon in value.get('icons', [])]
        except (ValueError, AttributeError, KeyError):
            pass
    return []


pages = sorted(p for p, r in unique.items() if p.endswith('.html') and not excluded_url(urls_by_path[p]))
edited = {}
cuts = {}
def prepare_page(path):
    before = (SITE / path).read_bytes()
    after, count = prune_html(before)
    return path, after if after != before else None, count

with ThreadPoolExecutor(max_workers=8) as pool:
    for path, data, count in pool.map(prepare_page, pages):
        if data is not None:
            edited[path] = data
            cuts[path] = count

keep = set(pages)
queue = pages.copy()
missing = set()
while queue:
    path = queue.pop()
    r = unique[path]
    data = edited.get(path)
    if data is None:
        data = (SITE / path).read_bytes()
    for ref in resource_urls(data, r['content_type'], urls_by_path[path]):
        parsed = urlsplit(urljoin(urls_by_path[path], ref))
        if parsed.scheme not in {'http', 'https'} or parsed.hostname not in {'www.osoujihonpo.com', 'osoujihonpo.com'}:
            continue
        dependency = local_by_url_path.get(unquote(parsed.path))
        if dependency:
            if dependency not in keep:
                keep.add(dependency)
                if Path(dependency).suffix.lower() in {'.css', '.js', '.mjs', '.json', '.webmanifest'} or 'text/html' in unique[dependency]['content_type']:
                    queue.append(dependency)
        else:
            missing.add(urljoin(urls_by_path[path], ref))

for name in ['robots.txt', 'sitemap.xml']:
    if name in unique:
        keep.add(name)
xml = (SITE / 'sitemap.xml').read_text(encoding='utf-8')
filtered_xml = re.sub(r'\s*<url>.*?</url>', lambda match: '' if excluded_url(re.search(r'<loc>(.*?)</loc>', match.group(), re.S).group(1)) else match.group(), xml, flags=re.S)
if filtered_xml != xml:
    edited['sitemap.xml'] = filtered_xml.encode('utf-8')

remove = sorted(set(unique) - keep)
removed_set = set(remove)
def move_entries(folder=SITE):
    children = sorted(folder.iterdir())
    for child in children:
        relative = child.relative_to(SITE).as_posix()
        if child.is_dir():
            if not any(p.startswith(relative + '/') for p in keep):
                yield relative
            else:
                yield from move_entries(child)
        elif relative in removed_set:
            yield relative

excluded = manifest.setdefault('excluded_urls', {})
for url, r in list(records.items()):
    if r['path'] not in keep:
        excluded[url] = 'approved page exclusion' if excluded_url(url) else 'used only by excluded pages'
        del records[url]
    elif r['path'] in edited:
        data = edited[r['path']]
        r.setdefault('source_sha256', r['sha256'])
        r.setdefault('source_bytes', r['bytes'])
        r['sha256'] = hashlib.sha256(data).hexdigest()
        r['bytes'] = len(data)
        r['scope_edited'] = True

new_unique = {r['path']: r for r in records.values()}
manifest['counts'].update(urls=len(records), unique_paths=len(new_unique), bytes=sum(r['bytes'] for r in new_unique.values()))
manifest['scope_file'] = 'source/scope.json'
report = {
    'removed_files': len(remove),
    'removed_bytes': sum(unique[p]['source_bytes'] if unique[p].get('source_bytes') else unique[p]['bytes'] for p in remove),
    'remaining_files': len(new_unique),
    'remaining_html_files': sum(p.endswith('.html') for p in keep),
    'remaining_bytes': manifest['counts']['bytes'],
    'edited_html_files': len(cuts),
    'excluded_files': remove,
    'move_entries': list(move_entries()),
    'edited_files': sorted(edited),
    'missing_source_dependencies': sorted(missing),
}
STAGE.mkdir(parents=True, exist_ok=True)
for path, data in edited.items():
    dest = STAGE / 'edited' / path
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(data)
(STAGE / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
(STAGE / 'scope-report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({k: v for k, v in report.items() if k not in {'excluded_files', 'move_entries', 'edited_files', 'missing_source_dependencies'}}, ensure_ascii=False))
print('missing_dependencies', len(missing))
print('stage', STAGE)
