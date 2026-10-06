from pathlib import Path, PurePosixPath
from html.parser import HTMLParser
from urllib.parse import urljoin, urlsplit, unquote
from datetime import datetime, timezone
import hashlib
import json
import re
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
PAGES = Path(r'C:\Users\yasoj\AppData\Local\Temp\cch-pages-deploy-20261003')
EXPECTED = 'eeac4e27fa29c818b673c845f763807be2084630'
actual = subprocess.check_output(['git', '-C', str(PAGES), 'rev-parse', 'HEAD'], text=True).strip()
assert actual == EXPECTED
assert not subprocess.check_output(['git', '-C', str(PAGES), 'status', '--porcelain'])
BASE = 'https://yasojima.github.io/'
entries = {}
external = set()
missing = set()
omitted_rasters = set()
queue = ['beginner/index.html', 'house-cleaning/aircon/index.html']
seen = set()

def reference(value, parent):
    value = value.strip()
    if not value or value.startswith(('data:', '#', 'javascript:')) or '${' in value:
        return
    url = urljoin(urljoin(BASE, parent), value)
    parts = urlsplit(url)
    if parts.netloc != 'yasojima.github.io':
        external.add(url)
        return
    path = unquote(parts.path).lstrip('/')
    if '..' in PurePosixPath(path).parts:
        return
    if PurePosixPath(path).suffix.lower() in ('.png', '.jpg', '.jpeg', '.webp', '.gif') and (parent.endswith(('.js', '.json')) or parent == 'house-cleaning/aircon/index.html'):
        omitted_rasters.add(path)
        return
    if path not in seen:
        queue.append(path)

class Assets(HTMLParser):
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag in ('img', 'script', 'source', 'video'):
            for name in ('src', 'data-src', 'poster'):
                if attrs.get(name):
                    reference(attrs[name], self.parent)
            for name in ('srcset', 'data-srcset'):
                if attrs.get(name):
                    for part in attrs[name].split(','):
                        reference(part.strip().split()[0], self.parent)
        if tag == 'link' and attrs.get('href'):
            if any(x in attrs.get('rel', '').split() for x in ('stylesheet', 'icon', 'apple-touch-icon')):
                reference(attrs['href'], self.parent)
        if attrs.get('style'):
            for value in re.findall(r'url\(\s*[\"\']?([^\)\"\']+)', attrs['style']):
                reference(value, self.parent)

while queue:
    path = queue.pop(0)
    if path in seen:
        continue
    seen.add(path)
    full = PAGES / path
    if not full.is_file():
        missing.add(path)
        continue
    data = full.read_bytes()
    entries['02_published_source/site/' + path] = data
    suffix = full.suffix.lower()
    if suffix not in ('.html', '.css', '.js', '.json', '.svg'):
        continue
    content = data.decode('utf-8', errors='replace')
    if suffix == '.html':
        parser = Assets()
        parser.parent = path
        parser.feed(content)
    if suffix in ('.css', '.html', '.svg'):
        for value in re.findall(r'url\(\s*[\"\']?([^\)\"\']+)', content):
            reference(value, path)
    if suffix in ('.js', '.json'):
        for value in re.findall(r'[\"\'`](/(?:assets|favicon)/[^\"\'`\s<>]+)[\"\'`]', content):
            reference(value, path)
        for value in re.findall(r'(?:from\s+|import\s*\(\s*)[\"\']([^\"\']+)', content):
            if value.startswith(('.', '/', 'http')):
                reference(value, path)

for path in ('source/shared-ui/header.html', 'source/shared-ui/footer.html', 'source/shared-ui/cleaning-menu-heading.html', 'tools/build_shared_ui.py', 'tools/apply_viewport_hud.py'):
    data = subprocess.check_output(['git', '-C', str(ROOT), 'show', '0dfa240:' + path])
    entries['02_published_source/generator/' + path] = data

notes = {
    'GPTへの相談文.txt': '00_GPTへの相談文.txt',
    '状況と確認結果.md': '01_状況と確認結果.md',
    '未公開候補について.txt': '04_unpublished_candidate/README.txt',
    'unpublished-candidate.diff': '04_unpublished_candidate/candidate.diff',
    '実機写真について.txt': '06_実機写真について.txt',
}
for source, target in notes.items():
    entries[target] = (OUT / source).read_bytes()

evidence = {
    'evidence/2026-10-07/lp-render-isolation/public-integrity.json': '03_evidence/published-integrity.json',
    'evidence/2026-10-07/lp-render-isolation/public-normal.json': '03_evidence/windows-normal-page.json',
    'evidence/2026-10-07/lp-render-isolation/lp-paint-audit.json': '03_evidence/lp-paint-audit.json',
    'evidence/2026-10-07/lp-render-isolation/public-modes.json': '03_evidence/windows-diagnostic-modes.json',
    'evidence/2026-10-06/ios-filter-artifact/research.json': '03_evidence/research-and-failed-device-result.json',
    'evidence/2026-10-07/lp-paint-boundary/public-normal-header-hidden.png': '03_evidence/WINDOWS_COMPARISON_not_iPhone_symptom.png',
    'evidence/2026-10-07/lp-paint-boundary/before-geometry.json': '03_evidence/unpublished-candidate-before-geometry.json',
    'evidence/2026-10-07/lp-paint-boundary/after-geometry.json': '03_evidence/unpublished-candidate-after-geometry.json',
    'evidence/2026-10-07/lp-paint-boundary/geometry-diff.json': '03_evidence/unpublished-candidate-geometry-diff.json',
}
for source, target in evidence.items():
    entries[target] = (ROOT / source).read_bytes()

manifest = {
    'created_utc': datetime.now(timezone.utc).isoformat(),
    'published_commit': EXPECTED,
    'source_commit': '0dfa240',
    'runtime_basis': 'Clean published checkout at exact Pages commit; no unpublished candidate applied.',
    'actual_device': {'model': 'iPhone XS Max', 'os': 'iOS 18.7.10', 'browsers': ['Chrome', 'Safari'], 'status': 'UNRESOLVED'},
    'actual_symptom_photo_included': False,
    'photo_reason': 'The user attachment original file is unavailable locally. Attach existing symptom photo separately.',
    'excluded': ['Device information photo and private identifiers', 'Git repository/authentication files', 'Unrelated website pages', 'External font downloads'],
    'external_references': sorted(external),
    'unavailable_static_references': sorted(missing),
    'omitted_raster_references': sorted(omitted_rasters),
    'omitted_raster_reason': 'Counterexample page photos and catalogue-wide runtime image references are omitted. Their source URLs and original code remain present. LP HTML and CSS referenced images plus vector assets are included.',
    'files': [{'path': key, 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()} for key, data in sorted(entries.items())],
}
manifest_data = json.dumps(manifest, ensure_ascii=False, indent=2).encode('utf-8')
entries['05_manifest.json'] = manifest_data
(OUT / 'bundle-manifest.json').write_bytes(manifest_data)
dest = OUT / 'CrystalCleanHome_LP_黒い表示_GPT相談_20261007.zip'
with zipfile.ZipFile(dest, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as z:
    for name, data in sorted(entries.items()):
        z.writestr(name, data)
with zipfile.ZipFile(dest) as z:
    assert z.testzip() is None
    for item in manifest['files']:
        assert hashlib.sha256(z.read(item['path'])).hexdigest() == item['sha256']
assert not subprocess.check_output(['git', '-C', str(PAGES), 'status', '--porcelain'])
print(json.dumps({'zip': str(dest), 'bytes': dest.stat().st_size, 'files': len(entries), 'unavailable_static_references': sorted(missing), 'actual_photo_included': False}, ensure_ascii=False))
