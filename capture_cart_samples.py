"""Record public cart responses for published set compositions, without booking."""
from pathlib import Path
from urllib.request import build_opener,HTTPCookieProcessor,Request
from http.cookiejar import CookieJar
from concurrent.futures import ThreadPoolExecutor
import json
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parent
def capture():
    data=json.loads((ROOT/'docs/reference/catalog.json').read_text(encoding='utf-8'))
    sets=sorted({v['sourceId'] for p in data['products'] for v in p['variants'] if '_' in v.get('sourceId','')})
    def sample(key):
        op=build_opener(HTTPCookieProcessor(CookieJar()))
        def request(path,data=None,headers={}):return json.loads(op.open(Request('https://www.osoujihonpo.com'+path,data=data,headers={'User-Agent':'Mozilla/5.0',**headers}),timeout=30).read())
        info=request('/api/v1/cart-info?temporary=0&detail=1&caller=on_page_load')
        parent,*options=map(int,key.split('_'))
        body={'temporary':0,'caller':'product_top','product':{'is_express':0,'id':parent,'product_quantity':1},'options':[{'parent_id':parent,'id':n,'product_quantity':1} for n in options]}
        response=request('/api/v1/cart-add',json.dumps(body).encode(),{'Content-Type':'application/json','X-CSRF-Token':info['result']['csrf-token']})
        assert response['result']['code']==0,(key,response['result'].get('message'))
        c=response['cart'];items=[]
        for p in [c['product']]+c.get('options',[]):
            items.append({k:p[k] for k in ['id','parent_id','web_cart_name','amounts','unit'] if k in p})
        page=op.open(Request('https://www.osoujihonpo.com/cart',headers={'User-Agent':'Mozilla/5.0'}),timeout=30).read().decode('utf-8')
        soup=BeautifulSoup(page,'html.parser');cards={}
        for card in soup.select('.c-product-additional-card'):
            field=card.select_one('input[name=product-id]')
            if field:cards[field['value']]=str(card)
        return key,items,cards
    with ThreadPoolExecutor(max_workers=4) as pool:samples=list(pool.map(sample,sets))
    result={key:items for key,items,cards in samples};cards={key:value for _,_,group in samples for key,value in group.items()}
    (ROOT/'source/osouji/checkout/set-samples.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    for html in list(cards):
        s=BeautifulSoup(cards[html],'html.parser')
        for el in s.select('input[name=_token]'):el.decompose()
        cards[html]=str(s)
    (ROOT/'source/osouji/checkout/recommend-cards.json').write_text(json.dumps(cards,ensure_ascii=False,indent=2),encoding='utf-8')
    print('captured',len(result),'set compositions; no bookings submitted')
if __name__=='__main__':capture()
