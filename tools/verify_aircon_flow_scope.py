"""Verify that the flow preview changes only the aircon section and its stylesheet."""
import argparse
import json
import re
import subprocess
from pathlib import Path
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('--base', required=True)
parser.add_argument('--output', type=Path, default=ROOT / 'evidence/2026-10-04/aircon-flow/scope.json')
args = parser.parse_args()

def git(*parts):
    return subprocess.check_output(['git', '-C', str(ROOT), *parts])

aircon = 'source/site/house-cleaning/aircon/index.html'
css = 'source/site/assets/css/aircon-flow.css'
changed = git('diff', '--name-only', args.base, '--', 'source/site').decode().splitlines()
assert set(changed) <= {aircon, css}, changed
tracked = set(git('ls-tree', '-r', '--name-only', args.base, 'source/site').decode().splitlines())
present = {p.relative_to(ROOT).as_posix() for p in (ROOT / 'source/site').rglob('*') if p.is_file()}
assert present - tracked == {css}, sorted(present - tracked)
assert not tracked - present, sorted(tracked - present)
before_copy = json.loads(git('show', f'{args.base}:source/service-pages/copy.json'))
current_copy = json.loads((ROOT / 'source/service-pages/copy.json').read_text(encoding='utf-8'))
assert current_copy['categories']['aircon'].pop('flow')
assert current_copy == before_copy, 'other service copy changed'

before = BeautifulSoup(git('show', f'{args.base}:{aircon}'), 'html.parser')
after = BeautifulSoup((ROOT / aircon).read_text(encoding='utf-8'), 'html.parser')
before.select_one('#service-flow').replace_with('FLOW')
after.select_one('#service-flow').replace_with('FLOW')
new_links = after.select('link[href^="/assets/css/aircon-flow.css"]')
assert len(new_links) == 1
new_links[0].decompose()
normalize = lambda soup: re.sub(r'>\s+<', '><', str(soup)).strip()
assert normalize(before) == normalize(after), 'aircon outside the flow changed'
report = {'base': args.base, 'passed': True, 'changed_public_paths': sorted(set(changed) | {css}),
          'other_seven_categories_unchanged': True, 'aircon_outside_flow_unchanged': True,
          'shared_copy_unchanged': True, 'existing_global_assets_unchanged': True}
args.output.parent.mkdir(parents=True, exist_ok=True)
args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8', newline='\n')
print(json.dumps(report, ensure_ascii=False))
