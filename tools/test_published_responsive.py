"""Check the changed shared assets and every HTML response against local bytes."""
import hashlib
import json
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / 'source/site'
ASSETS = ['assets/css/' + name for name in ('common.css', 'aircon-header.css',
          'aircon-layout.css', 'beginner-lp.css', 'site-footer.css')]
ASSETS += ['assets/js/aircon-header.js']
paths = [p.relative_to(SITE).as_posix() for p in SITE.rglob('*.html')] + ASSETS
revision = sys.argv[1]

def check(relative):
    route = '/' + relative.removesuffix('index.html')
    request = Request('https://yasojima.github.io' + route + '?verify=' + revision,
                      headers={'User-Agent': 'CrystalCleanHome-PublicationCheck/1.0'})
    with urlopen(request, timeout=45) as response:
        data = response.read()
        status = response.status
    expected = hashlib.sha256((SITE / relative).read_bytes()).hexdigest()
    actual = hashlib.sha256(data).hexdigest()
    return {'path': relative, 'status': status, 'sha256': actual,
            'expected_sha256': expected, 'passed': status == 200 and actual == expected}

with ThreadPoolExecutor(max_workers=3) as pool:
    records = list(pool.map(check, paths))
report = {'pages_revision': revision, 'checked_at': datetime.now(timezone.utc).isoformat(),
          'records': records, 'passed': all(r['passed'] for r in records)}
out = ROOT / 'evidence/2026-10-07/responsive-content/public-hashes.json'
out.write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps({'files': len(records), 'passed': report['passed'],
                  'failures': [r for r in records if not r['passed']]}))
raise SystemExit(0 if report['passed'] else 1)
