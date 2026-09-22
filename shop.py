"""Publish shared cart assets and remove homepage floating launchers."""
from pathlib import Path
import json,re,shutil
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parent
BASE='/crystal-clean-home/'
def publish_shop(root=ROOT):
    shutil.copytree(root/'brand/shop',root/'docs/brand/shop',dirs_exist_ok=True)
    target=root/'docs/index.html';html=target.read_text(encoding='utf-8')
    soup=BeautifulSoup(html,'html.parser')
    for el in soup.select('#fixed_side,.shop-home-cart,[data-shop-home]'):el.decompose()
    # Locate the old floating launcher by its title, not a broad CSS selector.
    for el in soup.find_all(string=re.compile('簡単見積もりシミュレーション')):
        parent=el.parent
        while parent and parent.name!='body':
            if parent.get('id') in ('simulation','simulation_banner','simulationBanner') or 'simulation' in ' '.join(parent.get('class',[])):
                parent.decompose();break
            parent=parent.parent
    target.write_text(str(soup),encoding='utf-8')
if __name__=='__main__':
    publish_shop()
    if (ROOT/'source/osouji/capture.json').exists():
        from reference import publish_reference
        publish_reference(ROOT)
