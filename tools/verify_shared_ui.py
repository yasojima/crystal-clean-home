"""Verify shared fragments, all menu destinations, and unchanged page content."""
from pathlib import Path
import json
import re
import subprocess
import argparse
from bs4 import BeautifulSoup
from build_shared_ui import SITE, COMPONENTS, transform

baseline='38e9ab2'
parser=argparse.ArgumentParser()
parser.add_argument('--preserve-main', action='store_true')
parser.add_argument('--output', default='evidence/2026-10-03/local/shared-ui-static.json')
args=parser.parse_args()
checked=[]
targets={}
for page in sorted(SITE.rglob('*.html')):
    relative=page.relative_to(SITE).as_posix()
    html=page.read_bytes().decode('utf-8')
    assert transform(html)==html, relative
    parsed=BeautifulSoup(html,'html.parser')
    for name in ['header','footer']:
        actual=re.search(r'<'+name+r'\b(?=[^>]*\bclass="[^"]*\bc-'+name+r'(?:\s|"))[^>]*>.*?</'+name+r'>',html,re.S).group()
        assert actual==(COMPONENTS/(name+'.html')).read_bytes().decode('utf-8').strip(),(relative,name)
    assert len(parsed.select('#menu'))==1,relative
    assert len(parsed.select('footer.c-footer'))==1,relative
    assert len(parsed.select('.aircon-footer-menu__row'))==5,relative
    assert len(parsed.select('.aircon-footer-menu .c-footer-accordion__content a'))==42,relative
    assert not parsed.select('.aircon-footer-menu__detail-heading'),relative
    if args.preserve_main:
        original=subprocess.check_output(['git','show',baseline+':source/site/'+relative])
        before=BeautifulSoup(original,'html.parser')
        assert str(parsed.main)==str(before.main),(relative,'main changed')
    for anchor in parsed.header.select('.c-house-cleaning-menu a[href*="#"]'):
        route,fragment=anchor['href'].split('#',1)
        if route not in targets:
            targets[route]=BeautifulSoup((SITE/(route.strip('/')+'/index.html')).read_bytes(),'html.parser')
        target=targets[route]
        assert target.find(id=fragment),(relative,anchor['href'])
    checked.append(relative)
report=dict(pages=len(checked),main_unchanged=args.preserve_main,shared_fragments=True,checked=checked)
out=Path(args.output)
out.parent.mkdir(parents=True,exist_ok=True)
out.write_bytes((json.dumps(report,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
print(json.dumps({k:v for k,v in report.items() if k!='checked'},ensure_ascii=False))
