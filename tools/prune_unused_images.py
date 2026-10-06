"""Audit current page dependencies before deleting unused project images."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter
from html import unescape
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit

from lxml import html

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / 'source/site'
MANIFEST = ROOT / 'source/manifest.json'
REPORT = ROOT / 'evidence/2026-10-07/unused-assets-cleanup/plan.json'
IMAGES = {'.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg', '.avif', '.ico', '.bmp'}
TEXT = {'.html', '.css', '.js', '.mjs', '.json', '.webmanifest', '.svg'}
RESOURCE = IMAGES | TEXT | {'.woff', '.woff2', '.ttf', '.eot', '.otf', '.mp4', '.webm', '.pdf'}
QUOTED = re.compile(r'''["'`]([^"'`\s<>]+)["'`]''')
CSS_URL = re.compile(r'''url\(\s*["']?([^"')\s]+)''', re.I)
CSS_IMPORT = re.compile(r'''@import\s+["']([^"']+)["']''', re.I)
ASSET_PATH = re.compile(r'''(?:https?:)?(?://[^/\s"'<>]+)?/(?:assets|favicon)/[^\s"'<>`\\(){};,]+''')


def strings(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for child in value.values():
            yield from strings(child)
    elif isinstance(value, list):
        for child in value:
            yield from strings(child)


def references(path):
    text = path.read_text(encoding='utf-8', errors='replace')
    refs = CSS_URL.findall(text) + CSS_IMPORT.findall(text)
    refs += ASSET_PATH.findall(text.replace('\\/', '/').replace('\\"', '"'))
    refs += [v for v in QUOTED.findall(text) if Path(urlsplit(v).path).suffix.lower() in RESOURCE]
    if path.suffix == '.html':
        doc = html.fromstring(text)
        refs += doc.xpath('//@src | //@poster | //@data-src | //@data-original | //@href | //meta/@content')
        for value in doc.xpath('//@srcset | //@data-srcset'):
            refs += [part.strip().split()[0] for part in value.split(',') if part.strip()]
    if path.suffix in {'.json', '.webmanifest'}:
        refs += list(strings(json.loads(text)))
    return refs


def audit(hash_images=True):
    manifest = json.loads(MANIFEST.read_text(encoding='utf-8'))
    records = manifest['files']
    by_url = {urlsplit(url)._replace(query='', fragment='').geturl(): r['path'] for url, r in records.items()}
    files = {p.relative_to(SITE).as_posix(): p for p in SITE.rglob('*') if p.is_file()}
    pages = sorted(p for p in files if p.endswith('.html'))
    keep = set(pages)
    queue = pages.copy()
    image_refs = {}
    missing = set()
    local_hosts = {'www.osoujihonpo.com', 'osoujihonpo.com', 'yasojima.github.io', 'local.invalid'}
    while queue:
        rel = queue.pop()
        path = files[rel]
        if path.suffix.lower() not in TEXT:
            continue
        for value in references(path):
            value = unescape(unquote(value))
            if value.startswith(('data:', '#', 'javascript:', 'mailto:', 'tel:')) or '${' in value:
                continue
            parsed = urlsplit(urljoin('https://local.invalid/' + rel, value))
            if Path(parsed.path).suffix.lower() not in RESOURCE:
                continue
            absolute = parsed._replace(query='', fragment='').geturl()
            dep = by_url.get(absolute)
            if not dep and parsed.hostname in local_hosts:
                dep = parsed.path.lstrip('/')
            if not dep:
                continue
            if dep not in files:
                if parsed.hostname in local_hosts:
                    missing.add(dep)
                continue
            if files[dep].suffix.lower() in IMAGES:
                image_refs.setdefault(dep, set()).add(rel)
            if dep not in keep:
                keep.add(dep)
                queue.append(dep)
    # The header constructs these payment paths at runtime.
    for name in ('visa', 'master-card'):
        rel = f'assets/images/common-parts/payments/{name}.webp'
        if rel not in files:
            raise ValueError(f'Missing dynamic header image: {rel}')
        keep.add(rel)
        image_refs.setdefault(rel, set()).add('assets/js/aircon-header.js (dynamic)')
    site_unused = sorted(rel for rel, p in files.items() if p.suffix.lower() in IMAGES and rel not in keep)
    auxiliary = sorted(p.relative_to(ROOT).as_posix() for base in ('assets', 'evidence')
                       for p in (ROOT / base).rglob('*') if p.is_file() and p.suffix.lower() in IMAGES)
    selected = ['source/site/' + rel for rel in site_unused] + auxiliary
    candidates = [{'path': rel, 'bytes': (ROOT / rel).stat().st_size,
                   'sha256': hashlib.sha256((ROOT / rel).read_bytes()).hexdigest() if hash_images else None} for rel in selected]
    return manifest, {'pages_checked': len(pages), 'reachable_files': len(keep),
                      'used_site_images': len(image_refs), 'unused_site_images': len(site_unused),
                      'auxiliary_images': len(auxiliary), 'remove_count': len(candidates),
                      'remove_bytes': sum(c['bytes'] for c in candidates),
                      'unused_folders': dict(Counter(str(Path(r).parent).replace('\\', '/') for r in site_unused)),
                      'existing_missing_references': sorted(missing),
                      'used_images': {r: sorted(v) for r, v in sorted(image_refs.items())},
                      'candidates': candidates}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    manifest, report = audit(hash_images=not args.apply)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    if args.apply:
        prior = json.loads(REPORT.read_text(encoding='utf-8'))
        if [(c['path'], c['bytes']) for c in prior['candidates']] != [(c['path'], c['bytes']) for c in report['candidates']]:
            raise ValueError('Image files changed since the deletion plan was audited')
        report = prior
        for item in report['candidates']:
            target = (ROOT / item['path']).resolve(strict=True)
            if not target.is_relative_to(ROOT.resolve()) or target.suffix.lower() not in IMAGES:
                raise ValueError(f'Unsafe deletion target: {target}')
        for item in report['candidates']:
            (ROOT / item['path']).unlink()
        removed = {c['path'].removeprefix('source/site/') for c in report['candidates'] if c['path'].startswith('source/site/')}
        manifest['files'] = {u: r for u, r in manifest['files'].items() if r['path'] not in removed}
        unique = {r['path']: r for r in manifest['files'].values()}
        manifest['counts'].update(urls=len(manifest['files']), unique_paths=len(unique), bytes=sum(r['bytes'] for r in unique.values()))
        MANIFEST.write_bytes(json.dumps(manifest, ensure_ascii=False, indent=2).encode('utf-8'))
        _, after = audit(hash_images=False)
        if after['unused_site_images'] or after['used_images'] != report['used_images'] or after['existing_missing_references'] != report['existing_missing_references']:
            raise ValueError('Image dependency verification failed after deletion')
        report['applied'] = True
        report['used_images_preserved'] = True
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({k: report[k] for k in ('pages_checked', 'used_site_images', 'unused_site_images', 'auxiliary_images', 'remove_count', 'remove_bytes')}, ensure_ascii=False))


if __name__ == '__main__':
    main()
