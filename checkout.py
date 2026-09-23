"""Publish captured checkout markup with a local-only data adapter."""
from pathlib import Path
from bs4 import BeautifulSoup,Comment
import re,json
from card_copy import apply_card_copy

def publish_checkout(root,header,data):
    from reference import local_url,replace_brand,BASE
    src=root/'source/osouji/checkout'
    def read(name):return BeautifulSoup((src/(name+'.html')).read_text(encoding='utf-8'),'html.parser')
    cart=read('cart');estimate=read('estimate');confirm=read('confirm')
    templates={}
    selectors={'parent':'.product-card','option':'.option-card','additional':'.additional-option-card','summary':'.cart__price-info','recommend':'.recommend-options','confirm-item':'.estimate-details__item'}
    for name,selector in selectors.items():
        el=(confirm if name=='confirm-item' else cart).select_one(selector)
        templates[name]=str(el)
    templates['confirm']=str(confirm.main)
    templates['empty']=(src/'empty.html').read_text(encoding='utf-8')
    recommendations=json.loads((src/'recommend-cards.json').read_text(encoding='utf-8'))
    for rawid,html in recommendations.items():templates['recommend-item-ref-'+rawid.replace('_','~')]=html
    container=cart.select_one('.cart-contents');container.clear();container['id']='cch-cart-lines'
    cart.select_one('.cart__price-info')['id']='cch-cart-summary'
    # Cards in the captured recommendations use the same product IDs as the catalogue.
    for el in cart.select('.js-product-card,.c-product-additional-card'):
        inp=el.select_one('input[name=product-id]')
        if inp:
            rid=inp.get('value','');parent=el.select_one('input[name=parent-id]')
            el['data-checkout-add']='ref-'+rid.replace('_','~')
    form=estimate.select_one('main form');form['id']='cch-estimate-form'
    for inp in form.select('input,select'):
        name=inp.get('name','')
        if name in ['last-name','first-name','last-name_kana','first-name_kana','email','tel_01','tel_02','tel_03','postal-code_01','postal-code_02','address_01','address_02','address_03','privacy-policy']:inp['required']=''
        if not inp.get('id'):inp['id']='cch-'+name
        labels={'email':'Eメールアドレス','tel_01':'電話番号（先頭）','tel_02':'電話番号（中央）','tel_03':'電話番号（末尾）','postal-code_01':'郵便番号（3桁）','postal-code_02':'郵便番号（4桁）','address_01':'都道府県','coupon-code':'クーポンコード'}
        if name in labels:inp['aria-label']=labels[name]
        if name=='email':inp['type']='email'
        if name.startswith('tel_'):inp['pattern']='[0-9]{1,4}';inp['maxlength']='4'
        if 'postal-code_' in name:inp['pattern']='[0-9]{'+('3' if name.endswith('01') else '4')+'}'
        if name.endswith('_kana'):inp['pattern']='[ァ-ヶー　 ]+'
    for name,soup,path in [('cart',cart,'/cart/'),('estimate',estimate,'/estimate/')]:
        main=soup.main
        if name=='estimate':
            review=soup.new_tag('div',id='cch-review');review['hidden']='';main.append(review)
        for el in main.select('script,input[type=hidden]'):el.decompose()
        for el in main.find_all(string=lambda x:isinstance(x,Comment)):el.extract()
        for el in main.select('form'):
            el['action']='#';el.attrs.pop('onsubmit',None);el['method']='get'
        for el in main.select('[onclick],[onsubmit]'):
            el.attrs.pop('onclick',None);el.attrs.pop('onsubmit',None)
        content=str(main)
        if name=='cart':
            for key,value in templates.items():
                if key!='confirm':content+='<template id="cch-template-'+key+'">'+value+'</template>'
        else:
            for key in ['confirm','confirm-item','summary']:content+='<template id="cch-template-'+key+'">'+templates[key]+'</template>'
        cleaned=BeautifulSoup(content,'html.parser')
        apply_card_copy(cleaned)
        for el in cleaned.select('form'):
            el['action']='#';el.attrs.pop('onsubmit',None)
        for el in cleaned.select('input[type=hidden]'):el.decompose()
        for el in cleaned.select('[src],[href]'):
            for attr in ['src','href']:
                if el.get(attr):el[attr]=local_url(el[attr],path)
        for el in cleaned.select('a[href]'):
            if '/cart/estimate' in el['href']:el['href']=BASE+'estimate/'
        styles=''.join('<link rel="stylesheet" href="'+local_url(l['href'],path)+'">' for l in soup.select('link[rel=stylesheet]') if l.get('href','').startswith('/assets/'))
        # Confirmation markup has dedicated style sheets in addition to form/common.css.
        if name=='estimate':
            existing={l['href'] for l in soup.select('link[rel=stylesheet]')}
            styles+=''.join('<link rel="stylesheet" href="'+local_url(l['href'],path)+'">' for l in confirm.select('link[rel=stylesheet]') if l.get('href','').startswith('/assets/') and l['href'] not in existing)
        styles+='<link rel="stylesheet" href="'+BASE+'reference/checkout.css">'
        if name=='cart':styles+='<link rel="stylesheet" href="'+BASE+'reference/cart-source.css?v=1">';styles+='<link rel="stylesheet" href="'+BASE+'reference/cart-exact.css?v=1">'
        shell=(root/'brand/reference/shell.html').read_text(encoding='utf-8')
        shell=shell.replace('{{TITLE}}',replace_brand(soup.title.text)).replace('{{HEADER}}',header).replace('{{STYLES}}',styles).replace('{{CONTENT}}',replace_brand(str(cleaned))).replace('{{CATALOG}}',data)
        shell=shell.replace('<script defer src="'+BASE+'reference/bridge.js', '<script defer src="'+BASE+'reference/cart-slider.js"></script><script defer src="'+BASE+'reference/bridge.js');shell=shell.replace('reference/bridge.js','reference/checkout.js').replace('<body>','<body data-checkout-page="'+name+'">')
        if name=='estimate':shell=shell.replace('<script defer src="'+BASE+'reference/checkout.js?v=rail1">','<script defer src="'+BASE+'reference/postal-data.js"></script><script defer src="'+BASE+'reference/checkout.js?v=rail1">')
        dest=root/'docs'/name/'index.html';dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(shell,encoding='utf-8')
    alias=root/'docs/cart/estimate/index.html';alias.parent.mkdir(parents=True,exist_ok=True);alias.write_text((root/'docs/estimate/index.html').read_text(encoding='utf-8'),encoding='utf-8')
