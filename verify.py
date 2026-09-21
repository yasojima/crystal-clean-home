from pathlib import Path
from lxml import html
from urllib.parse import urlsplit, unquote
import json, re, hashlib
ROOT=Path(__file__).resolve().parent
manifest=json.loads((ROOT/'capture.json').read_text(encoding='utf-8'))
missing={};counts=[];source_hash_failures=[]
for f in manifest['files']:
    if 'path' not in f:continue
    p=ROOT/'source'/f['path']
    if hashlib.sha256(p.read_bytes()).hexdigest()!=f['sha256']:source_hash_failures.append(f['path'])
    if not f.get('html'):continue
    published=ROOT/'docs'/f['path']
    s=html.fromstring(p.read_text(encoding='utf-8'))
    d=html.fromstring(published.read_text(encoding='utf-8'))
    for tag in ['section','main','header','footer','h1','h2','h3','img','form']:
        a=len(s.xpath('//'+tag));b=len(d.xpath('//'+tag))
        if a!=b:counts.append({'page':f['path'],'tag':tag,'source':a,'output':b})
    for node in d.iter():
        for attr in ['src','href','poster','data-src','data-lazy-src']:
            val=node.get(attr,'') or ''
            if val.startswith('/crystal-clean-home/'):
                path=unquote(urlsplit(val).path[len('/crystal-clean-home/'):])
                target=ROOT/'docs'/path
                if target.is_dir():target=target/'index.html'
                if not target.exists():missing.setdefault(val,[]).append(f['path'])
report={'htmlPages':sum(f.get('html',False) for f in manifest['files']), 'capturedFiles':sum('path' in f for f in manifest['files']), 'missingLocalReferences':missing,'structureDifferences':counts,'sourceHashFailures':source_hash_failures,'source404':manifest['errors']}
(ROOT/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:v if k not in ['source404','missingLocalReferences','structureDifferences','sourceHashFailures'] else len(v) for k,v in report.items()}))
