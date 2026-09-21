from pathlib import Path
from urllib.parse import urlsplit,urlunsplit,urljoin
from concurrent.futures import ThreadPoolExecutor,wait,FIRST_COMPLETED
from bs4 import BeautifulSoup
import requests,json,re,hashlib,time,threading
ROOT=Path(__file__).resolve().parent;RAW=ROOT/'source';RAW.mkdir(exist_ok=True)
ORIGIN='https://iekire.com/';local=threading.local();seen={};errors=[];futures={}
def canonical(u,base=ORIGIN):
 u=urljoin(base,u);p=urlsplit(u)
 if p.scheme not in ('http','https'):return None
 host=p.netloc.lower();scheme='https' if host in ['iekire.com','www.iekire.com'] else p.scheme
 if host=='www.iekire.com':host='iekire.com'
 return urlunsplit((scheme,host,p.path or '/',p.query,''))
def path_for(u,html=False):
 p=urlsplit(u);path=p.path.lstrip('/')
 if not path or path.endswith('/'):path+='index.html'
 elif html and not Path(path).suffix:path+='/index.html'
 if p.query:
  x=Path(path);path=str(x.with_name(x.stem+'--'+hashlib.sha256(p.query.encode()).hexdigest()[:10]+x.suffix)).replace('\\','/')
 if p.netloc!='iekire.com':path='vendor/'+p.netloc+'/'+path
 return path

def fetch(u,kind):
 if not hasattr(local,'s'):
  local.s=requests.Session();local.s.headers['User-Agent']='Mozilla/5.0 (compatible; SiteCopy/1.0)'
 err=None
 for attempt in range(2):
  try:
   r=local.s.get(u,timeout=35);r.raise_for_status();break
  except Exception as e:err=str(e)
 else:return {'url':u,'error':err},[]
 ct=r.headers.get('content-type','');ishtml='text/html' in ct;path=path_for(u,ishtml);data=r.content;dest=RAW/path;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
 row={'url':u,'path':path,'type':ct,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'html':ishtml,'resolved':r.url};links=[]
 def add(v,k,base=r.url):
  v=canonical(v,base)
  if v:links.append((v,k))
 if ishtml:
  soup=BeautifulSoup(data,'html.parser')
  for node in soup.find_all(True):
   for attr in ['src','poster','data-src','data-original','data-lazy-src']:
    if node.get(attr):add(node[attr],'asset')
   for attr in ['srcset','data-srcset']:
    for v in node.get(attr,'').split(','):
     if v.strip() and not v.strip().startswith('data:'):add(v.strip().split()[0],'asset')
   if node.name=='link' and node.get('href') and set(node.get('rel',[]))&{'stylesheet','icon','shortcut','apple-touch-icon','preload','manifest'}:add(node['href'],'asset')
   if node.name=='a' and node.get('href'):
    u2=canonical(node['href'],r.url)
    if u2 and urlsplit(u2).netloc=='iekire.com' and not re.search(r'/wp/(?:wp-admin|wp-login|xmlrpc)|/wp-json/',u2):add(u2,'page')
   for v in re.findall(r'url\(\s*[\"\']?([^\)\"\']+)',node.get('style','')):add(v,'asset')
  for style in soup.find_all('style'):
   for v in re.findall(r'url\(\s*[\"\']?([^\)\"\']+)',style.get_text()):add(v,'asset')
 elif 'css' in ct or urlsplit(u).path.endswith('.css'):
  text=data.decode('utf-8',errors='replace')
  for v in re.findall(r'url\(\s*[\"\']?([^\)\"\']+)',text):add(v,'asset')
  for v in re.findall(r'@import\s+[\"\']([^\"\']+)',text):add(v,'asset')
 elif 'javascript' in ct or urlsplit(u).path.endswith('.js'):
  text=data.decode('utf-8',errors='replace')
  for v in re.findall(r'[\"\']((?:https?://iekire\.com/|/wp/)[^\"\'<>\s]+\.(?:png|jpe?g|webp|gif|svg|css|woff2?)(?:\?[^\"\'\s]*)?)[\"\']',text):add(v,'asset')
 return row,links
seeds=json.loads((ROOT/'page-seeds.json').read_text(encoding='utf-8'))
with ThreadPoolExecutor(max_workers=8) as pool:
 def submit(u,kind):
  u=canonical(u)
  if not u or u in seen:return
  seen[u]=None;futures[pool.submit(fetch,u,kind)]=u
 for u in seeds:submit(u,'page')
 donecount=0
 while futures:
  finished,_=wait(futures,return_when=FIRST_COMPLETED)
  for f in finished:
   u=futures.pop(f)
   try:row,links=f.result()
   except Exception as e:row,links={'url':u,'error':str(e)},[]
   seen[u]=row
   if 'error' in row:errors.append(row)
   for link,kind in links:submit(link,kind)
   donecount+=1
   if donecount%100==0:print(json.dumps({'downloaded':donecount,'queued':len(futures),'errors':len(errors)}),flush=True)
(ROOT/'capture.json').write_text(json.dumps({'reference':ORIGIN,'files':list(seen.values()),'errors':errors},ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps({'total':len(seen),'pages':sum(x.get('html',False) for x in seen.values()),'errors':len(errors)}),flush=True)
