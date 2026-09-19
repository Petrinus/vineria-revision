"""Inspect public, user-requested media; never log cookies or credentials."""
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup
from PIL import Image,ImageOps
import json,io,re
OUT=Path('reports/v7-media');OUT.mkdir(parents=True,exist_ok=True)
PAGES={
'bujanda':'https://familiamartinezbujanda.com/tienda/vinos/blancos-y-dulces/vina-bujanda-viura/',
'nieva':'https://martue.com/producto/blanco-nieva-sauvignon-blanc-2025/',
'vanidade':'https://vinaalmirante.com/en/vinos/vanidade-en/',
'egiarte':'https://tienda.lezaun.com/es/botellas-egiarte/29-egiarte-crianza-bio.html',
'lezaun':'https://tienda.lezaun.com/es/botellas-lezaun/25-lezaun-tempranillo.html',
'terrae':'https://www.bodegastempore.com/en/news/new-gold-medal-for-our-organic-wine-terrae-finca-vasallo-garnacha-100/',
'nuestro':'https://www.vinetibo.es/products/nuestro-8-meses',
'cecina-page':'https://www.montegomez.com/tienda-online/cecina-pablo/',
'oricios-page':'https://laespanolameats.com/es/conservas-de-pescado/caviar-de-oricios-.html',
'chorizo-page':'https://puxa.es/chorizo-extra-asturiano/35-chorizo-extra-paq-250-g.html'
}
for code in ['Ckbmq6yMEWS','CgpJbcXjyWV','DKU9PzaMm1w','DSDZcT3DI2I','BuzCKLOho7i']:
 PAGES['ig-'+code]='https://www.instagram.com/p/'+code+'/embed/captioned/'
DIRECT={
'mejillones':'https://www.fetasoller.com/userFiles/Image/Shop/Artikel/Oel_Essig_Eingelegtes/Eingelegtes/Cabo_de_Penas/00690_Mejillones_CaboDePenas.jpg',
'amazon':'https://m.media-amazon.com/images/I/51Xeos+OS1L._SX522_.jpg',
'oricios':'https://laespanolameats.com/6851-thickbox_default/caviar-de-oricios-.jpg',
'cecina':'https://www.montegomez.com/wp-content/uploads/2023/06/cecina-pablo.jpg'
}
def fetch(u):
 with urlopen(Request(u,headers={'User-Agent':'Mozilla/5.0 (compatible; Vineria design review)','Accept-Language':'de,en;q=0.8,es;q=0.7'}),timeout=18) as r:return r.read(10000000),r.status,r.geturl()
def inspect(kv):
 key,url=kv;r={'key':key,'url':url}
 try:
  raw,status,final=fetch(url);r.update(status=status,final=final)
  if key in DIRECT:
   im=ImageOps.exif_transpose(Image.open(io.BytesIO(raw))).convert('RGB');r['size']=im.size;im.thumbnail((900,1100));im.save(OUT/(key+'.jpg'),quality=90);return r
  s=BeautifulSoup(raw,'html.parser');r['title']=s.title.get_text(' ',strip=True) if s.title else '';r['text']=s.get_text(' ',strip=True)[:800] if key.startswith('ig-') else s.get_text(' ',strip=True)[-12000:]
  candidates=[]
  for m in s.select('meta[property="og:image"],meta[name="twitter:image"]'):
   if m.get('content'):candidates.append({'url':urljoin(final,m['content']),'alt':'og:image','priority':100})
  for im in s.select('img'):
   u=im.get('data-large_image') or im.get('data-src') or im.get('src') or ''
   if u.startswith('data:'):continue
   alt=im.get('alt','');p=30 if any(x in (u+' '+alt).lower() for x in [key,'product','bujanda','nieva','vanidade','egiarte','lezaun','vasallo','nuestro','chorizo']) else 0
   candidates.append({'url':urljoin(final,u),'alt':alt,'priority':p})
  for u in re.findall(r'"(?:display_url|image_url)"\s*:\s*"([^"<]+)"',raw.decode('utf-8','replace')):candidates.insert(0,{'url':u.replace('\\u0026','&').replace('\\/','/'),'alt':'public post image','priority':110})
  seen=set();r['images']=[]
  for c in sorted(candidates,key=lambda x:-x['priority']):
   if c['url'] not in seen and c['url'].startswith('https:'):r['images'].append(c);seen.add(c['url'])
  r['images']=r['images'][:15]
 except Exception as e:r['error']=str(e)[:250]
 return r
with ThreadPoolExecutor(max_workers=8) as ex:results=list(ex.map(inspect,{**PAGES,**DIRECT}.items()))
(OUT/'candidates.json').write_text(json.dumps(results,ensure_ascii=False,indent=2))
for r in results:print(r['key'],r.get('status',r.get('error')),r.get('title',''),r.get('size',''),[(x['alt'],x['url'])for x in r.get('images',[])[:3]])
