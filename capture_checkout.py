"""Capture public checkout presentation in an isolated, non-booking cart session."""
from pathlib import Path
from urllib.request import build_opener, HTTPCookieProcessor, Request
from urllib.parse import urlencode, urljoin, urlsplit
from http.cookiejar import CookieJar
from bs4 import BeautifulSoup
import json,re
ROOT=Path(__file__).resolve().parent
ORIGIN='https://www.osoujihonpo.com'
def capture():
    op=build_opener(HTTPCookieProcessor(CookieJar()))
    def get(path,data=None,headers=None):
        return op.open(Request(ORIGIN+path,data=data,headers={'User-Agent':'Mozilla/5.0','Referer':ORIGIN+'/house-cleaning/pack/',**(headers or {})}),timeout=40).read()
    empty=BeautifulSoup(get('/cart').decode('utf-8'),'html.parser').select_one('.empty-cart')
    info=json.loads(get('/api/v1/cart-info?temporary=0&detail=1&caller=on_page_load'))
    body={'temporary':0,'caller':'product_top','product':{'is_express':0,'id':666,'product_quantity':1},'options':[{'parent_id':666,'id':479,'product_quantity':1}]}
    added=json.loads(get('/api/v1/cart-add',json.dumps(body).encode(),{'Content-Type':'application/json','X-CSRF-Token':info['result']['csrf-token']}))
    assert added['result']['code']==0
    dest=ROOT/'source/osouji/checkout';dest.mkdir(exist_ok=True)
    (dest/'empty.html').write_text(str(empty),encoding='utf-8')
    pages={name:BeautifulSoup(get(path).decode('utf-8'),'html.parser') for name,path in [('cart','/cart'),('estimate','/cart/estimate')]}
    # This endpoint is only the input review, never the reservation submission.
    form=pages['estimate'].select_one('form')
    values={'_token':form.select_one('input[name=_token]')['value'],'last-name':'確認','first-name':'見本','last-name_kana':'カクニン','first-name_kana':'ミホン','email':'preview@example.com','tel_01':'090','tel_02':'0000','tel_03':'0000','postal-code_01':'100','postal-code_02':'0001','address_01':'13','address_02':'確認用','address_03':'確認用','address_04':'','privacy-policy':'on'}
    review=get(form['action'],urlencode(values).encode(),{'Content-Type':'application/x-www-form-urlencoded'})
    pages['confirm']=BeautifulSoup(review.decode('utf-8'),'html.parser')
    paths=set()
    for name,s in pages.items():
        for el in s.select('input[name=_token],meta[name=csrf-token],script:not([src])'):el.decompose()
        for el in s.select('[src],link[rel=stylesheet]'):
            path=urlsplit(urljoin(ORIGIN,el.get('src') or el.get('href'))).path
            if path.startswith('/assets/'):paths.add(path)
        # Keep only local presentation dependencies, excluding trackers.
        for el in s.select('script[src]'):
            if not el['src'].startswith('/assets/'):el.decompose()
        (dest/(name+'.html')).write_text(str(s),encoding='utf-8')
        print(name,s.title.get_text(),flush=True)
    done=set()
    while paths-done:
        for path in sorted(paths-done):
            done.add(path);f=ROOT/'source/osouji'/path.lstrip('/');f.parent.mkdir(parents=True,exist_ok=True)
            if not f.exists():
                try:f.write_bytes(get(path))
                except Exception as error:
                    print('asset unavailable',path,str(error),flush=True);continue
            if path.endswith('.css'):
                for u in re.findall(r'url\([\'\"]?([^\)\'\"]+)',f.read_text(encoding='utf-8')):
                    z=urlsplit(urljoin(ORIGIN+path,u))
                    if z.path.startswith('/assets/'):paths.add(z.path)
    print('assets',len(done))
if __name__=='__main__':capture()
