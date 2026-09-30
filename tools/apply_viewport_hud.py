"""Attach the shared viewport HUD and refresh the local response manifest."""
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / 'source/site'
SCRIPT = 'assets/js/viewport-hud.js'
TAG = b'<script src="/assets/js/viewport-hud.js" defer></script>'
manifest_path = ROOT / 'source/manifest.json'
manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
documents = list(SITE.rglob('*.html'))
missing_head = [str(path.relative_to(SITE)) for path in documents
                if not re.search(rb'</head\s*>', path.read_bytes(), re.I)]
if missing_head:
    raise RuntimeError(f'HTML documents without a head: {missing_head}')

changed = {}
for path in documents:
    data = path.read_bytes()
    if TAG not in data:
        data = re.sub(rb'</head\s*>', lambda match: TAG + b'\n' + match[0], data, count=1, flags=re.I)
        path.write_bytes(data)
    changed[path.relative_to(SITE).as_posix()] = data

for record in manifest['files'].values():
    if record['path'] in changed:
        record.setdefault('source_sha256', record['sha256'])
        data = changed[record['path']]
        record.update(bytes=len(data), sha256=hashlib.sha256(data).hexdigest())

data = (SITE / SCRIPT).read_bytes()
url = manifest['origin'].rstrip('/') + '/' + SCRIPT
manifest['files'][url] = {
    'path': SCRIPT, 'effective_url': url, 'status': 200,
    'content_type': 'text/javascript; charset=UTF-8', 'bytes': len(data),
    'sha256': hashlib.sha256(data).hexdigest(), 'origin_type': 'local-debug-ui'
}
manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({'html_documents_with_hud': len(documents), 'shared_script': SCRIPT}))
