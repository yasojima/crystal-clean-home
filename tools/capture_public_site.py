from __future__ import annotations

import concurrent.futures
import hashlib
import json
import re
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import deque
from datetime import datetime, timezone
from pathlib import Path

from lxml import etree, html
import requests

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / 'source' / 'site'
MANIFEST = ROOT / 'source' / 'manifest.json'
ORIGIN = 'https://www.osoujihonpo.com'
ASSET_EXT = {'.css', '.js', '.mjs', '.json', '.webmanifest', '.png', '.jpg', '.jpeg', '.webp', '.gif', '.svg', '.ico', '.avif', '.woff', '.woff2', '.ttf', '.eot', '.otf', '.mp4', '.webm', '.mp3', '.pdf', '.zip'}
IMAGE_EXT = {'.png', '.jpg', '.jpeg', '.webp', '.gif', '.svg', '.ico', '.avif'}
URL_PATTERN = re.compile(r'url\(\s*[\"\']?([^\"\')\s]+)', re.I)
JS_ASSET_PATTERN = re.compile(r'''["'`]((?:/assets/|/favicon/|\.\.?/)[^"'`\s<>]+)["'`]''')
IMPORT_PATTERN = re.compile(r'''@import\s+["']([^"']+)["']''', re.I)
SITE.mkdir(parents=True, exist_ok=True)
lock = threading.Lock()
halt = threading.Event()
worker_state = threading.local()
state = json.loads(MANIFEST.read_text(encoding='utf-8')) if MANIFEST.exists() else {'origin': ORIGIN, 'files': {}, 'external_urls': [], 'failures': {}, 'conflicts': []}
records = state['files']
external = set(state['external_urls'])
failed = state['failures']
for skipped_url in [u for u, message in failed.items() if message == 'Stopped after access limit']:
    del failed[skipped_url]
claimed = {v['path']: (u, v['sha256']) for u, v in records.items()}
seen = set(records)
pending_pages: set[str] = set()
pending_assets: set[str] = set()


def normalize(value: str, base: str) -> str | None:
    value = value.strip()
    if not value or value.startswith(('data:', 'javascript:', 'mailto:', 'tel:', '#', 'blob:')):
        return None
    u = urllib.parse.urlsplit(urllib.parse.urljoin(base, value))
    if u.scheme not in {'http', 'https'}:
        return None
    if u.hostname not in {'www.osoujihonpo.com', 'osoujihonpo.com'}:
        external.add(urllib.parse.urlunsplit((u.scheme, u.netloc, u.path, u.query, '')))
        return None
    return urllib.parse.urlunsplit(('https', 'www.osoujihonpo.com', u.path or '/', u.query, ''))


def local_path(url: str, content_type: str = '') -> str:
    path = urllib.parse.unquote(urllib.parse.urlsplit(url).path).lstrip('/')
    parts = Path(path).parts
    if '..' in parts or any(':' in p for p in parts):
        raise ValueError(f'Unsafe path: {path}')
    if not path or path.endswith('/'):
        path += 'index.html'
    elif not Path(path).suffix and 'text/html' in content_type:
        path += '/index.html'
    return path


def fetch(url: str) -> tuple[str, bytes | None, str]:
    if halt.is_set():
        return url, None, ''
    started = datetime.now(timezone.utc).isoformat()
    error = ''
    for attempt in range(3):
        try:
            if not hasattr(worker_state, 'session'):
                worker_state.session = requests.Session()
                worker_state.session.headers.update({'User-Agent': 'Mozilla/5.0 (compatible; AuthorizedSiteSnapshot/1.0)', 'Accept-Encoding': 'identity'})
            worker_state.session.cookies.clear()
            with worker_state.session.get(url, timeout=45) as response:
                if response.status_code >= 400:
                    raise urllib.error.HTTPError(url, response.status_code, response.reason, response.headers, None)
                effective = response.url
                if urllib.parse.urlsplit(effective).hostname not in {'www.osoujihonpo.com', 'osoujihonpo.com'}:
                    return url, None, f'External redirect: {effective}'
                data = response.content
                kind = response.headers.get('Content-Type', '')
                status = response.status_code
            path = local_path(url, kind)
            digest = hashlib.sha256(data).hexdigest()
            with lock:
                prior = claimed.get(path)
                if prior and prior[1] != digest:
                    state['conflicts'].append({'url': url, 'path': path, 'first_url': prior[0], 'sha256': digest})
                    variant = ROOT / 'source' / 'query-variants' / hashlib.sha256(url.encode()).hexdigest()[:16] / Path(path).name
                    variant.parent.mkdir(parents=True, exist_ok=True)
                    variant.write_bytes(data)
                    return url, None, f'Different responses share path: {path}'
                target = SITE / path
                if not target.resolve().is_relative_to(SITE.resolve()):
                    raise ValueError(f'Path outside snapshot: {path}')
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(data)
                claimed[path] = (url, digest)
                records[url] = {'path': path, 'effective_url': effective, 'status': status, 'content_type': kind, 'bytes': len(data), 'sha256': digest, 'retrieved_at': started}
                failed.pop(url, None)
            return url, data, kind
        except urllib.error.HTTPError as exc:
            error = f'HTTP {exc.code}'
            if exc.code == 429:
                halt.set()
                break
            if exc.code not in {500, 502, 503, 504}:
                break
        except Exception as exc:
            error = f'{type(exc).__name__}: {exc}'
        if attempt < 2:
            time.sleep(1 + attempt)
    return url, None, error


def enqueue_asset(value: str, base: str) -> None:
    u = normalize(value, base)
    if u and u not in seen and u not in failed and not urllib.parse.urlsplit(u).path.startswith('/api/'):
        pending_assets.add(u)


def enqueue_page(value: str, base: str) -> None:
    u = normalize(value, base)
    if not u or u in seen or u in failed:
        return
    p = urllib.parse.urlsplit(u)
    if p.query or p.path.startswith('/api/'):
        return
    if Path(p.path).suffix.lower() in ASSET_EXT:
        pending_assets.add(u)
    else:
        pending_pages.add(u)


def parse(url: str, data: bytes, kind: str) -> None:
    suffix = Path(urllib.parse.urlsplit(url).path).suffix.lower()
    if 'text/html' in kind or suffix in {'.html', '.htm'}:
        try:
            doc = html.fromstring(data)
        except (etree.ParserError, ValueError):
            return
        for value in doc.xpath('//@src | //@poster | //@data-src | //@data-original'):
            enqueue_asset(value, url)
        for value in doc.xpath('//@srcset | //@data-srcset'):
            for item in value.split(','):
                bits = item.strip().split()
                if bits:
                    enqueue_asset(bits[0], url)
        for node in doc.xpath('//link[@href]'):
            rel = node.get('rel', '').lower()
            if any(r in rel for r in ['stylesheet', 'icon', 'manifest', 'preload']):
                enqueue_asset(node.get('href'), url)
        for value in doc.xpath('//a/@href | //area/@href'):
            enqueue_page(value, url)
        for value in doc.xpath('//@style | //style/text()'):
            for asset in URL_PATTERN.findall(value):
                enqueue_asset(asset, url)
        for value in doc.xpath('//script[not(@src)]/text()'):
            for asset in JS_ASSET_PATTERN.findall(value):
                if Path(urllib.parse.urlsplit(asset).path).suffix.lower() in ASSET_EXT:
                    enqueue_asset(asset, url)
    elif suffix in {'.css', '.js', '.mjs', '.json', '.webmanifest'} or any(k in kind for k in ['javascript', 'text/css', 'application/json']):
        text = data.decode('utf-8', 'replace')
        if suffix == '.css' or 'text/css' in kind:
            for asset in URL_PATTERN.findall(text) + IMPORT_PATTERN.findall(text):
                enqueue_asset(asset, url)
        elif suffix in {'.js', '.mjs'} or 'javascript' in kind:
            for asset in JS_ASSET_PATTERN.findall(text):
                if Path(urllib.parse.urlsplit(asset).path).suffix.lower() in ASSET_EXT:
                    enqueue_asset(asset, url)
        elif suffix in {'.json', '.webmanifest'}:
            try:
                manifest = json.loads(text)
                for icon in manifest.get('icons', []):
                    enqueue_asset(icon.get('src', ''), url)
            except (ValueError, AttributeError):
                pass


def save() -> None:
    state['external_urls'] = sorted(external)
    state['captured_at'] = datetime.now(timezone.utc).isoformat()
    state['counts'] = {'urls': len(records), 'unique_paths': len(claimed), 'bytes': sum(v[1]['bytes'] for v in {r['path']: (u, r) for u, r in records.items()}.values()), 'failures': len(failed), 'conflicts': len(state['conflicts']), 'pending_pages': len(pending_pages), 'pending_assets': len(pending_assets)}
    MANIFEST.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(state['counts']), flush=True)


def batch(urls: list[str]) -> None:
    seen.update(urls)
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        for url, data, kind in pool.map(fetch, urls):
            if data is None:
                failed[url] = kind or 'Stopped after access limit'
                print(f'FAILED {url}: {failed[url]}', flush=True)
            else:
                parse(url, data, kind)
    save()


def assets() -> None:
    while pending_assets and not halt.is_set():
        todo = sorted(pending_assets - seen - set(failed))[:40]
        if not todo:
            pending_assets.clear()
            break
        pending_assets.difference_update(todo)
        batch(todo)


def main() -> None:
    for url, record in list(records.items()):
        path = SITE / record['path']
        textual = 'text/html' in record['content_type'] or any(t in record['content_type'] for t in ['javascript', 'text/css', 'application/json']) or path.suffix.lower() in {'.html', '.htm', '.css', '.js', '.mjs', '.json', '.webmanifest'}
        if textual and path.is_file():
            parse(url, path.read_bytes(), record['content_type'])
    initial = [ORIGIN + '/', ORIGIN + '/robots.txt', ORIGIN + '/sitemap.xml', ORIGIN + '/cart']
    batch([u for u in initial if u not in records])
    if halt.is_set():
        raise SystemExit('Capture stopped on HTTP 429; no bypass attempted.')
    assets()
    xml = etree.fromstring((SITE / 'sitemap.xml').read_bytes())
    sitemap = xml.xpath('//*[local-name()="loc"]/text()')
    state['sitemap_url_count'] = len(sitemap)
    for url in sitemap:
        enqueue_page(url, ORIGIN)
    def priority(url: str) -> tuple[int, int, str]:
        path = urllib.parse.urlsplit(url).path
        prefix = path.split('/')[1]
        return ({'shop': 4, 'area': 3, 'info': 3, 'guide': 2}.get(prefix, 0), path.count('/'), url)
    cycles = 0
    while pending_pages and not halt.is_set():
        todo = sorted(pending_pages - seen - set(failed), key=priority)[:40]
        if not todo:
            pending_pages.clear()
            break
        pending_pages.difference_update(todo)
        batch(todo)
        cycles += 1
        if cycles <= 2 or cycles % 10 == 0:
            assets()
    assets()
    save()
    if halt.is_set():
        raise SystemExit('Capture stopped on HTTP 429; no bypass attempted.')
    print('CAPTURE_FINISHED', flush=True)


if __name__ == '__main__':
    main()
