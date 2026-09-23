"""Brand adaptation of captured reference markup; preserves the source main tree."""
from pathlib import Path
from urllib.parse import urljoin,urlsplit
from bs4 import BeautifulSoup
from card_copy import apply_card_copy
import tinycss2,re,json,shutil
ROOT=Path(__file__).resolve().parent;BASE='/crystal-clean-home/';REF=BASE+'reference/';ORIGIN='https://www.osoujihonpo.com'
def scope_css(css,scope):
    out=[]
    for rule in tinycss2.parse_stylesheet(css,skip_whitespace=True,skip_comments=True):
        if rule.type=='qualified-rule':
            raw=tinycss2.serialize(rule.prelude);sels=[];group=[];depth=0
            for token in rule.prelude:
                if token.type=='literal' and token.value==',':sels.append(tinycss2.serialize(group));group=[]
                else:group.append(token)
            sels.append(tinycss2.serialize(group));new=[]
            for s in sels:
                s=s.strip()
                s=re.sub(r'(?<![\w-])(?::root|html|body)(?![\w-])',scope,s)
                if scope not in s:s=scope+' '+s
                new.append(s)
            out.append(','.join(new)+'{'+tinycss2.serialize(rule.content)+'}')
        elif rule.type=='at-rule':
            pre='@'+rule.at_keyword+' '+tinycss2.serialize(rule.prelude)
            if rule.content is None:out.append(pre+';')
            elif rule.lower_at_keyword in ['media','supports','layer','container']:out.append(pre+'{'+scope_css(tinycss2.serialize(rule.content),scope)+'}')
            else:out.append(pre+'{'+tinycss2.serialize(rule.content)+'}')
    return '\n'.join(out)
def replace_brand(text):
    return text.replace('おそうじ本舗','クリスタルクリーンホーム').replace('お掃除本舗','クリスタルクリーンホーム')
def local_url(u,path):
    z=urlsplit(urljoin(ORIGIN+path,u))
    if z.netloc not in ['www.osoujihonpo.com','osoujihonpo.com']:return u
    if z.path.startswith('/assets/'):return REF+z.path.removeprefix('/')+('?' +z.query if z.query else '')
    if z.path.startswith('/house-cleaning/') and (ROOT/'source/osouji/pages'/z.path.strip('/')/'index.html').exists():return BASE+z.path.lstrip('/')+('?' +z.query if z.query else '')+('#'+z.fragment if z.fragment else '')
    if z.path.rstrip('/')=='/cart':return BASE+'cart/'
    if z.path.startswith('/cart/estimate'):return BASE+'estimate/'
    if not z.path or z.path=='/':return BASE
    return ORIGIN+z.path+('?' +z.query if z.query else '')+('#'+z.fragment if z.fragment else '')
def prices(el):
    p=el.select_one('.c-price__text')
    if not p:return None
    match=re.search(r'[0-9][0-9,]*',p.get_text())
    return int(match[0].replace(',','')) if match else None
def publish_reference(root=ROOT):
    src=root/'source/osouji';out=root/'docs/reference';out.mkdir(exist_ok=True)
    assets=src/'assets';shutil.copytree(assets,out/'assets',dirs_exist_ok=True,ignore=lambda directory,names:[n for n in names if n.endswith('.css')])
    common=(assets/'js/common.js').read_text(encoding='utf-8')
    assert 'new a,new o,new S,new y,new E,new x,new Ee' in common
    common=common.replace('new a,new o,new S,new y,new E,new x,new Ee','new S,new y,new E,new x,new Ee')
    # Scroll locking changes the viewport width beneath our fixed header.
    # Local touch-action on the handle prevents touch scrolling without reflow.
    assert common.count('w(this.el,{reserveScrollBarGap:!0})') == 2
    common=common.replace('w(this.el,{reserveScrollBarGap:!0})','void 0').replace('b(this.el)','void 0')
    (out/'assets/js/common.js').write_text(common,encoding='utf-8')
    for original in assets.rglob('*.css'):
        f=out/'assets'/original.relative_to(assets);css=original.read_text(encoding='utf-8-sig')
        css=re.sub(r'url\(([^)]+)\)',lambda m:'url("'+local_url(m[1].strip(' \"\''),'/assets/'+f.relative_to(out/'assets').as_posix())+'")',css)
        css=scope_css(css,'.cch-reference')
        # Adapt only palette values; keep dimensions, composition and breakpoints.
        for a,b in {'#005bac':'#075b91','#0060ae':'#075b91','#004098':'#17354b','#e3f1fc':'#eef5f9','#f4f8fa':'#eef5f9'}.items():css=re.sub(re.escape(a),b,css,flags=re.I)
        css='\n'.join(line.rstrip() for line in css.splitlines())
        if not f.exists() or f.read_text(encoding='utf-8')!=css:
            temporary=f.with_suffix('.css.tmp');temporary.write_text(css,encoding='utf-8');temporary.replace(f)
    hostcss=''
    for f in [root/'docs/wp/wp-content/themes/original_theme/css/bulma.css',root/'docs/wp/wp-content/themes/original_theme/style--a15f99ca6e.css']:
        css=f.read_text(encoding='utf-8');css=re.sub(r'url\(([^)]+)\)',lambda m:'url("'+urljoin(BASE+'wp/wp-content/themes/original_theme/'+('css/' if f.name=='bulma.css' else ''),m[1].strip(' \"\''))+'")',css);hostcss+=scope_css(css,'.cch-host')
    (out/'host.css').write_text(hostcss,encoding='utf-8')
    site=json.loads((root/'brand/site.json').read_text(encoding='utf-8'));header=(root/'brand/header/template.html').read_text(encoding='utf-8')
    for k,v in dict(site,logo_tag='div').items():
        if isinstance(v,str):header=header.replace('{{'+k+'}}',v)
    h=BeautifulSoup(header,'html.parser')
    for im in h.select('img[data-src]'):im['src']=im['data-src']
    header=str(h); products={};page_outputs=[];counts={}
    for f in sorted((src/'pages').rglob('index.html')):
        path='/'+f.parent.relative_to(src/'pages').as_posix()+'/'
        soup=BeautifulSoup(f.read_bytes(),'html.parser');main=soup.select_one('main')
        if main:apply_card_copy(main)
        if not main:continue
        for card in main.select('.js-product-card'):
            field=card.select_one('input[name=product-id]');heading=card.select_one('h3,h4,h2,h5')
            if not field or not heading:continue
            rawid=field.get('value','');group=card.find_parent(class_='js-products');parent=group.select_one('[data-product-card=parent] input[name=product-id]') if group else None
            parent_id=parent.get('value') if parent and card.get('data-product-card')=='option' else None
            if parent_id and group:
                parent_card=group.select_one('[data-product-card=parent]');room_select=parent_card.select_one('.js-room-types') if parent_card else None
                options_group=card.find_parent(attrs={'data-switch-target':'options'})
                if room_select and options_group:
                    branch=card
                    while branch.parent is not options_group:branch=branch.parent
                    idx=options_group.find_all(recursive=False).index(branch)
                    room_options=room_select.select('option')
                    if idx<len(room_options):parent_id=room_options[idx].get('value',parent_id)
            room=card.select_one('.js-room-types');choices=room.select('option') if room else [None]
            pricewrap=card.select_one('[data-switch-target=prices]');pricechoices=pricewrap.find_all(recursive=False) if pricewrap else []
            cname=heading.get_text(' ',strip=True);img=card.select_one('img[src]') or (group.select_one('[data-product-card=parent] img[src]') if group else None);variants=[]
            for i,choice in enumerate(choices):
                rid=choice.get('value',rawid) if choice else rawid;sid='ref-'+(parent_id+'~' if parent_id else '')+rid
                pe=pricechoices[i] if i<len(pricechoices) else card
                price=prices(pe);unitnode=pe.select_one('.c-price__unit');unit='式'
                if unitnode:
                    match=re.search(r'[／/]\s*(.+)',unitnode.text)
                    if match:unit=match[1].strip()
                v=dict(id=sid,name=choice.get_text(' ',strip=True) if choice else '標準',price=price,unit=unit,max=999,sourceId=rid)
                regular=pe.select_one('[data-discount]')
                if regular:
                    m=re.search(r'[0-9][0-9,]*',regular.get('data-discount',''))
                    if m:v['regularPrice']=int(m[0].replace(',',''))
                counters=card.select('[data-switch-target=counters] input') or card.select('.js-counter input')
                counter=counters[min(i,len(counters)-1)] if counters else None
                quantities=card.select('.js-product-quantity select option')
                if counter:v['max']=int(counter.get('max',30))
                elif quantities:v['max']=max(int(o.get('value',1)) for o in quantities)
                tier=pe.select('.c-multi-campaign-price__item')
                if len(tier)>1:v['multiPrice']=prices(tier[1])
                if '〜' in pe.get_text() or '～' in pe.get_text():v['fromPrice']=True
                if parent_id:v['requires']='ref-'+parent_id
                variants.append(v)
            pid='ref-card-'+(parent_id+'~' if parent_id else '')+rawid
            card['data-cch-variants']=json.dumps([v['id'] for v in variants]);card['data-cch-card']=pid
            if pid not in products or len(products[pid]['variants'])<len(variants):
                products[pid]=dict(id=pid,category='reference',name=replace_brand(cname),description='',images=[local_url(img['src'],path)] if img else [BASE+'wp/wp-content/themes/original_theme/img/logo.svg'],variants=variants,detail=BASE+path.lstrip('/'))
        counts[path]=dict(sections=len(main.select(':scope > *')),cards=len(main.select('.js-product-card')))
        # Keep public markup; exclude executable tracking and remote form transport.
        for script in main.select('script'):script.decompose()
        for tag in main.select('[src],[href],[poster],[srcset]'):
            for attr in ['src','href','poster']:
                if tag.get(attr) and not tag[attr].startswith(('#','data:','mailto:','tel:','javascript:')):tag[attr]=local_url(tag[attr],path)
            if tag.get('srcset'):tag['srcset']=', '.join(' '.join([local_url(part.strip().split()[0],path)]+part.strip().split()[1:]) for part in tag['srcset'].split(',') if part.strip())
        for tag in main.select('[style]'):tag['style']=re.sub(r'url\([\'\"]?([^\)\'\"]+)[\'\"]?\)',lambda m:'url('+local_url(m[1],path)+')',tag['style'])
        crumb=soup.select_one('.c-breadcrumbs');crumb=str(crumb) if crumb else ''
        crumb=re.sub(r'href="([^"]+)"',lambda m:'href="'+local_url(m[1],path)+'"',crumb)
        styles=''.join('<link rel="stylesheet" href="'+local_url(l['href'],path)+'">' for l in soup.select('link[rel=stylesheet]') if l.get('href','').startswith('/assets/'))
        original_header=soup.select_one('header');hidden='<div hidden>'+str(original_header)+'</div>' if original_header else ''
        html=(root/'brand/reference/shell.html').read_text(encoding='utf-8').replace('{{TITLE}}',replace_brand(soup.title.text if soup.title else '清掃メニュー')).replace('{{HEADER}}',header).replace('{{STYLES}}',styles).replace('{{CONTENT}}',replace_brand(crumb+str(main))).replace('{{HIDDEN_HEADER}}',hidden)
        page_outputs.append((path,html))
    catalog=json.loads((root/'brand/shop/catalog.json').read_text(encoding='utf-8'));catalog['products']+=list(products.values())
    variant_map={v['id']:v for p in catalog['products'] for v in p['variants']}
    samples=json.loads((src/'checkout/set-samples.json').read_text(encoding='utf-8'))
    product_map={v['id']:p for p in catalog['products'] for v in p['variants']}
    for set_id,parts in samples.items():
        components=[]
        for part in parts:
            sid='ref-'+(str(part['parent_id'])+'~' if 'parent_id' in part else '')+str(part['id'])
            amount=part['amounts'][0];regular=amount['price']+amount['price_tax'];price=regular-amount['price_discount']-amount['price_discount_tax']
            if sid not in variant_map:
                v=dict(id=sid,name='標準',price=price,regularPrice=regular,unit=part['unit'],max=30,sourceId=str(part['id']))
                if 'parent_id' in part:v['requires']='ref-'+str(part['parent_id'])
                parent=product_map.get('ref-'+str(part.get('parent_id',part['id']))) or product_map['ref-'+set_id]
                p=dict(id='ref-cart-'+sid,category='reference',name=replace_brand(part['web_cart_name']),description='',images=parent['images'],variants=[v],detail=parent['detail']);catalog['products'].append(p);variant_map[sid]=v;product_map[sid]=p
            variant_map[sid]['regularPrice']=regular;variant_map[sid]['price']=price
            components.append(sid)
        variant_map['ref-'+set_id]['components']=components
    recommendation_cards=json.loads((src/'checkout/recommend-cards.json').read_text(encoding='utf-8'))
    for rawid,html in recommendation_cards.items():
        sid='ref-'+rawid.replace('_','~');card=BeautifulSoup(html,'html.parser');apply_card_copy(card);p=product_map.get(sid)
        if p:
            img=card.select_one('img[src]');desc=card.select_one('.c-product-additional-card__description')
            if img:p['images']=[local_url(img['src'],'/cart/')]
            if desc:p['description']=replace_brand(desc.get_text(' ',strip=True))
    for v in variant_map.values():
        ids=v.get('sourceId','').split('_')
        if len(ids)>1:
            components=['ref-'+ids[0]]+['ref-'+ids[0]+'~'+n for n in ids[1:]]
            if all(n in variant_map for n in components) and sum(variant_map[n]['price'] or 0 for n in components)==v['price']:v['components']=components
    (out/'catalog.json').write_text(json.dumps(catalog,ensure_ascii=False,indent=2),encoding='utf-8')
    (out/'catalog.js').write_text('window.CCHReferenceCatalog='+json.dumps(catalog,ensure_ascii=False)+';',encoding='utf-8')
    data=json.dumps(catalog,ensure_ascii=False).replace('</','<\\/')
    for path,html in page_outputs:
        html=html.replace('{{CATALOG}}',data);dest=root/'docs'/path.strip('/')/'index.html';dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(html,encoding='utf-8')
        if path=='/house-cleaning/pack/':(root/'docs/services/index.html').write_text(html,encoding='utf-8')
    from checkout import publish_checkout
    publish_checkout(root,header,data)
    shutil.copytree(root/'brand/reference',out,dirs_exist_ok=True)
    (root/'reference-report.json').write_text(json.dumps({'pages':counts,'products':len(products),'variants':sum(len(p['variants']) for p in products.values())},ensure_ascii=False,indent=2),encoding='utf-8')
    from shared_ui import publish_shared_ui
    publish_shared_ui(root)
    print('Published reference pages',len(page_outputs),'products',len(products))
if __name__=='__main__':publish_reference()
