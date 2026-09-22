"""Publish shared cart assets and the homepage cart entry."""
from pathlib import Path
import json,re,shutil
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parent
BASE='/crystal-clean-home/'
def publish_shop(root=ROOT):
    shutil.copytree(root/'brand/shop',root/'docs/brand/shop',dirs_exist_ok=True)
    target=root/'docs/index.html';html=target.read_text(encoding='utf-8')
    soup=BeautifulSoup(html,'html.parser')
    # The new cart replaces only the homepage's old floating calculator.
    for el in soup.select('.shop-home-cart,[data-shop-home]'):el.decompose()
    # Locate the old floating launcher by its title, not a broad CSS selector.
    for el in soup.find_all(string=re.compile('簡単見積もりシミュレーション')):
        parent=el.parent
        while parent and parent.name!='body':
            if parent.get('id') in ('simulation','simulation_banner','simulationBanner') or 'simulation' in ' '.join(parent.get('class',[])):
                parent.decompose();break
            parent=parent.parent
    link=soup.new_tag('a',href=BASE+'cart/',attrs={'class':'shop-home-cart'});link.string='カートを確認・見積もり予約 →';soup.body.append(link)
    if not soup.select_one('[data-shop-home]'):
        style=soup.new_tag('style',attrs={'data-shop-home':'true'});style.string='.shop-home-cart{position:fixed;right:24px;bottom:24px;z-index:900;background:#075b91;color:white;padding:20px 24px;border-radius:4px;font-family:"Yu Gothic",YuGothic,sans-serif;font-weight:bold;box-shadow:0 4px 16px #17354b26}@media(max-width:600px){.shop-home-cart{right:12px;bottom:12px;padding:12px 16px;font-size:13px;right:12px;left:12px;bottom:76px}}';soup.head.append(style)
    target.write_text(str(soup),encoding='utf-8')
if __name__=='__main__':
    publish_shop()
    if (ROOT/'source/osouji/capture.json').exists():
        from reference import publish_reference
        publish_reference(ROOT)
