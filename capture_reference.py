"""Capture linked cleaning pages and their public presentation assets."""
from pathlib import Path
from urllib.parse import urljoin,urlsplit
from urllib.request import Request,urlopen
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup
import json,re
ROOT=Path(__file__).resolve().parent;OUT=ROOT/'source/osouji';ORIGIN='https://www.osoujihonpo.com'
def get(url):
 with urlopen(Request(url,headers={'User-Agent':'Mozilla/5.0','Referer':ORIGIN+'/'}),timeout=40) as r:return r.read()
def capture():
 seed=BeautifulSoup((OUT/'pack.html').read_bytes(),'html.parser')
 paths=sorted({urlsplit(urljoin(ORIGIN,a['href'])).path for a in seed.select('a[href]') if a['href'].startswith('/house-cleaning/')})
 pages={};errors=[]
 def page(path):
  f=OUT/'pages'/path.strip('/')/'index.html';f.parent.mkdir(parents=True,exist_ok=True)
  try:
   b=get(ORIGIN+path);f.write_bytes(b);return path,b
  except Exception as e:return path,str(e)
 with ThreadPoolExecutor(max_workers=8) as pool:
  for path,b in pool.map(page,paths):
   if isinstance(b,bytes):pages[path]=b
   else:errors.append([path,b])
 assets=set()
 for path,b in pages.items():
  s=BeautifulSoup(b,'html.parser');main=s.select_one('main') or s
  for tag in list(main.select('[src],[srcset],[poster]'))+s.select('link[rel=stylesheet],script[src]'):
   for attr in ['src','href','poster']:
    if tag.get(attr):
     u=urljoin(ORIGIN+path,tag[attr]);z=urlsplit(u)
     if z.netloc==urlsplit(ORIGIN).netloc and z.path.startswith('/assets/'):assets.add(z.path)
   for part in tag.get('srcset','').split(','):
    if part.strip():
     z=urlsplit(urljoin(ORIGIN+path,part.strip().split()[0]));
     if z.path.startswith('/assets/'):assets.add(z.path)
  for u in re.findall(r'url\([\'\"]?([^\)\'\"]+)',str(main)):
   z=urlsplit(urljoin(ORIGIN+path,u))
   if z.path.startswith('/assets/'):assets.add(z.path)
 done=set()
 def asset(path):
  f=OUT/'assets'/path.removeprefix('/assets/');f.parent.mkdir(parents=True,exist_ok=True)
  try:
   b=f.read_bytes() if f.exists() else get(ORIGIN+path);f.write_bytes(b);return path,b
  except Exception as e:return path,str(e)
 while assets-done:
  batch=sorted(assets-done);done.update(batch)
  with ThreadPoolExecutor(max_workers=10) as pool:
   for path,b in pool.map(asset,batch):
    if isinstance(b,str):errors.append([path,b]);continue
    if path.endswith(('.css','.js')):
     text=b.decode('utf-8',errors='replace')
     urls=re.findall(r'url\([\'\"]?([^\)\'\"]+)',text) if path.endswith('.css') else re.findall(r'[\'\"](/assets/[^\'\"]+)[\'\"]',text)
     for u in urls:
      z=urlsplit(urljoin(ORIGIN+path,u))
      if z.path.startswith('/assets/'):assets.add(z.path)
 print('captured',len(pages),'pages',len(done),'assets; failures',len(errors),flush=True)
 (OUT/'capture.json').write_text(json.dumps({'pages':list(pages),'assets':sorted(done),'errors':errors},ensure_ascii=False,indent=2),encoding='utf-8')
 print(errors,flush=True)
if __name__=='__main__':capture()
