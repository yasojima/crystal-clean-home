from pathlib import Path
from lxml import html
from collections import Counter
from urllib.parse import urlsplit
import json

ROOT = Path(__file__).resolve().parent
paths = sorted({f['path'] for f in json.loads((ROOT/'capture.json').read_text(encoding='utf-8'))['files'] if f.get('html') and not f['path'].startswith('vendor/')})
issues = []
actions = Counter()
forms = 0
for index, path in enumerate(paths):
    if index % 50 == 0:
        print('Checking', index, path, flush=True)
    doc = html.fromstring((ROOT/'docs'/path).read_text(encoding='utf-8'))
    for node in doc.xpath('//a[@href] | //area[@href]'):
        value = node.get('href', '')
        if urlsplit(value).scheme or value.startswith('//'):
            issues.append((path, value))
    for node in doc.xpath('//*[@data-demo-action]'):
        actions[node.get('data-demo-action')] += 1
    for node in doc.xpath('//form'):
        forms += 1
        if node.get('method') != 'dialog' or node.get('action') != '#':
            issues.append((path, 'form active'))
    if not doc.xpath('//script[@data-demo-guard]'):
        issues.append((path, 'missing guard'))
    if not doc.xpath('//meta[@http-equiv="Content-Security-Policy"]'):
        issues.append((path, 'missing form policy'))
report = {'pages':len(paths), 'activeExternalLinksOrErrors':issues, 'demoControls':dict(actions), 'disconnectedForms':forms}
(ROOT/'demo-verification.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(report, ensure_ascii=False), flush=True)
assert not issues
