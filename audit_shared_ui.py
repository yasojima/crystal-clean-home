"""Inventory shared typography, section connectors and imported card copy."""
from pathlib import Path
import json
import re
import subprocess
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent

def files(folder):
    return [ROOT / p for p in subprocess.check_output(['rg', '--files', folder, '-g', '*.html'], cwd=ROOT, text=True).splitlines()]

def audit():
    pages = [p for p in files('docs') if p.name == 'index.html']
    missing, connectors = [], {}
    for p in pages:
        text = p.read_text(encoding='utf-8')
        if 'brand/header/style.css' not in text:
            missing.append(str(p.relative_to(ROOT)))
        if '-bubbles' in text:
            soup = BeautifulSoup(re.sub(r'<script\b[^>]*>.*?</script>', '', text, flags=re.S), 'lxml')
            count = len(soup.select('.l-section[class*="-bubbles"]'))
            if count:
                connectors[str(p.relative_to(ROOT))] = count
    print(json.dumps(dict(pages=len(pages), missing=missing, connectorPages=len(connectors), connectors=sum(connectors.values())), ensure_ascii=False), flush=True)
    rows = {}
    for p in files('source/osouji/pages'):
        soup = BeautifulSoup(p.read_text(encoding='utf-8'), 'lxml')
        for e in soup.select('[class*="card"]'):
            classes = ' '.join(e.get('class', []))
            if not any(k in classes for k in ['__description', '__text', '__heading']):
                continue
            if e.find_parent(['header', 'footer']) or e.select('[class*="__description"],[class*="__text"],[class*="__heading"]'):
                continue
            text = e.get_text(' ', strip=True)
            if text:
                rows.setdefault(text, dict(classes=classes, pages=[]))['pages'].append(str(p.relative_to(ROOT)))
    (ROOT / 'card-copy-inventory.json').write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding='utf-8')
    print('Unique card texts:', len(rows), flush=True)

if __name__ == '__main__':
    audit()
