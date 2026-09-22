"""Check that editorial changes preserve structure, identifiers and conditions."""
from pathlib import Path
import json
import re
import subprocess
from bs4 import BeautifulSoup
from card_copy import apply_card_copy, eligible

ROOT = Path(__file__).resolve().parent
changes, untouched, pages = {}, {}, 0
for filename in subprocess.check_output(['rg', '--files', 'source/osouji/pages', '-g', '*.html'], cwd=ROOT, text=True).splitlines():
    soup = BeautifulSoup((ROOT / filename).read_bytes(), 'lxml')
    main = soup.select_one('main')
    before = [(e.name, dict(e.attrs)) for e in main.find_all()]
    numbers = re.findall(r'\d+(?:[,.]\d+)*', main.get_text())
    voices = [str(e) for e in main.select('[class*="voice-card"],[class*="voice-service-card"],[class*="doctor-recommendation"]')]
    delta = apply_card_copy(main)
    assert not apply_card_copy(main), 'Copy replacements must be idempotent: ' + filename
    assert before == [(e.name, dict(e.attrs)) for e in main.find_all()], filename
    assert numbers == re.findall(r'\d+(?:[,.]\d+)*', main.get_text()), filename
    assert voices == [str(e) for e in main.select('[class*="voice-card"],[class*="voice-service-card"],[class*="doctor-recommendation"]')], filename
    if delta:
        pages += 1
    for old, new in delta:
        changes[old.strip()] = new.strip()
    for e in main.select('[class*="card"]'):
        if eligible(e) and not any(x in e.get_text() for x in changes.values()):
            text=e.get_text(' ',strip=True)
            if text: untouched[text]=' '.join(e.get('class',[]))
(ROOT / 'card-copy-review.json').write_text(json.dumps(dict(changes=changes, unchanged=untouched), ensure_ascii=False, indent=2), encoding='utf-8')
print(f'PASS: {pages} source pages; {len(changes)} unique edited text nodes; structure, attributes, numbers and testimonials unchanged')
