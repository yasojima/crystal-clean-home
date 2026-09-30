import hashlib
import argparse
import json
import subprocess
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit
from xml.etree import ElementTree

root = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('--git', action='store_true', help='Also compare captured bytes with committed Git blobs')
args = parser.parse_args()
manifest = json.loads((root / 'source' / 'manifest.json').read_text(encoding='utf-8'))
site = root / 'source' / 'site'
unique = {record['path']: record for record in manifest['files'].values()}
git_blobs = {}
if args.git:
    tree = subprocess.check_output(['git', '-C', str(root), 'ls-tree', '-r', '-z', 'HEAD', '--', 'source/site'])
    for entry in tree.split(b'\0'):
        if entry:
            header, path = entry.split(b'\t', 1)
            git_blobs[path.decode('utf-8').removeprefix('source/site/')] = header.split()[2].decode('ascii')
def verify_file(item):
    relative, record = item
    path = site / relative
    if not path.is_file():
        return {'path': relative, 'error': 'missing'}
    data = path.read_bytes()
    if hashlib.sha256(data).hexdigest() != record['sha256']:
        return {'path': relative, 'error': 'hash mismatch'}
    if args.git and hashlib.sha1(b'blob ' + str(len(data)).encode('ascii') + b'\0' + data).hexdigest() != git_blobs.get(relative):
        return {'path': relative, 'error': 'committed Git blob mismatch or missing'}
    return None
with ThreadPoolExecutor(max_workers=8) as pool:
    errors = [error for error in pool.map(verify_file, unique.items()) if error]
sitemap = ElementTree.parse(site / 'sitemap.xml')
sitemap_urls = [node.text for node in sitemap.iter() if node.tag.endswith('}loc')]
def normalized(url):
    parts = urlsplit(url)
    return urlunsplit(('https', 'www.osoujihonpo.com', parts.path or '/', parts.query, ''))
sitemap_urls = sorted(set(normalized(url) for url in sitemap_urls))
captured = set(manifest['files'])
failed = set(manifest['failures'])
missing = sorted(set(sitemap_urls) - captured - failed)
unavailable_pages = {url: manifest['failures'][url] for url in sitemap_urls if url in failed}
unfinished = manifest['counts']['pending_pages'] + manifest['counts']['pending_assets']
report = {
    'source': manifest['origin'],
    'verified_at': datetime.now(timezone.utc).isoformat(),
    'verified_files': len(unique),
    'html_files': sum('text/html' in r['content_type'] for r in unique.values()),
    'total_bytes': sum(r['bytes'] for r in unique.values()),
    'matches_manifest': not errors,
    'unchanged_source_files': sum(r.get('source_sha256', r['sha256']) == r['sha256'] for r in unique.values()),
    'approved_scope_edited_files': sum(r.get('source_sha256', r['sha256']) != r['sha256'] for r in unique.values()),
    'integrity_errors': errors,
    'sitemap_urls': len(sitemap_urls),
    'sitemap_saved': sum(url in captured for url in sitemap_urls),
    'sitemap_unavailable': unavailable_pages,
    'sitemap_not_attempted': missing,
    'pending_urls': unfinished,
    'failure_categories': dict(Counter(manifest['failures'].values())),
    'over_100_MiB_files': [path for path, record in unique.items() if record['bytes'] > 100 * 1024 * 1024],
    'within_GitHub_Pages_1GB': sum(r['bytes'] for r in unique.values()) <= 1_000_000_000,
    'unavailable_source_urls': manifest['failures'],
    'response_conflicts': manifest['conflicts'],
    'committed_git_blobs_verified': args.git and not errors,
    'external_resources_remain_external': manifest['external_urls'],
}
if args.git:
    report['verified_git_source_tree'] = subprocess.check_output(['git', '-C', str(root), 'rev-parse', 'HEAD:source/site'], text=True).strip()
(root / 'source' / 'verification.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({k: v for k, v in report.items() if k not in {'unavailable_source_urls', 'response_conflicts', 'external_resources_remain_external'}}, ensure_ascii=False))
raise SystemExit(1 if errors or missing or unfinished or manifest['conflicts'] else 0)
