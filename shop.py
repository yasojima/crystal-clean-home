"""Publish the branded catalog and estimate prototype. Canonical assets: brand/shop."""
from pathlib import Path
import json,re,shutil
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parent
BASE='/crystal-clean-home/'
def publish_shop(root=ROOT):
    brand=root/'brand/shop'; data=json.loads((brand/'catalog.json').read_text(encoding='utf-8'))
    site=json.loads((root/'brand/site.json').read_text(encoding='utf-8'))
    header=(root/'brand/header/template.html').read_text(encoding='utf-8')
    for k,v in dict(site,logo_tag='div').items():
        if isinstance(v,str):header=header.replace('{{'+k+'}}',v)
    h=BeautifulSoup(header,'html.parser')
    for img in h.select('img[data-src]'):img['src']=img['data-src'];img.attrs.pop('data-src',None)
    for a in h.select('a[href]'):
        if a['href']==BASE+'service/house/':a['href']=BASE+'services/'
    header=str(h)
    directory=(root/'brand/service-directory/template.html').read_text(encoding='utf-8')
    shell=(brand/'shell.html').read_text(encoding='utf-8')
    for page,title in [('services','サービスを選ぶ'),('cart','お見積もり内容'),('estimate','見積もりのご予約')]:
        html=shell.replace('{{TITLE}}',title).replace('{{HEADER}}',header).replace('{{PAGE}}',page).replace('{{DIRECTORY}}',directory).replace('{{CATALOG}}',json.dumps(data,ensure_ascii=False).replace('</','<\\/'))
        target=root/'docs'/page/'index.html';target.parent.mkdir(parents=True,exist_ok=True);target.write_text(html,encoding='utf-8')
    shutil.copytree(brand,root/'docs/brand/shop',dirs_exist_ok=True)
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
if __name__=='__main__':publish_shop()
