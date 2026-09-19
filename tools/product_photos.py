"""Real package photos for the client review. Never invent a bottle or relabel a photo.
Sources are explicit public product pages. Only image bytes are downloaded.
"""
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.parse import urlsplit,urljoin
from concurrent.futures import ThreadPoolExecutor
from PIL import Image,ImageOps,ImageChops
from bs4 import BeautifulSoup
import copy,hashlib,io,json,posixpath,re
ROOT=Path(__file__).resolve().parent.parent;SITE=ROOT/'site';A=SITE/'assets';OUT=A/'products';OUT.mkdir(parents=True,exist_ok=True)
SPEC=json.loads((ROOT/'models/product-photos.json').read_text())
CAND=ROOT/'reports/v7-media/candidates.json'
HISTORY={x['key']:x for x in json.loads(CAND.read_text())} if CAND.exists() else {}

def read(url):
 if urlsplit(url).scheme!='https':raise ValueError('Only HTTPS image sources are accepted')
 with urlopen(Request(url,headers={'User-Agent':'Mozilla/5.0','Accept':'image/avif,image/webp,image/png,image/jpeg,text/html;q=0.8'}),timeout=25)as r:
  data=r.read(18_000_001)
  if len(data)>18_000_000:raise ValueError('Image exceeds size limit')
  return data

def load_one(item):
 record=copy.deepcopy(item);id=item['id'];target=OUT/(id+'.webp');warnings=[]
 urls=[]
 if item.get('image'):urls.append(item['image'])
 old=HISTORY.get(item.get('candidate_key',''),{})
 for v in old.get('images',[]):
  u=v.get('url','');name=u.lower()
  if v.get('priority',0)>=100 or any(t in name for t in [id,item.get('candidate_key','__none__')]):
   if not any(t in name for t in ['logo','flag','icon','facebook.com','plugin','avatar','banner']):urls.append(u)
 if len(urls)==0:
  try:
   page=BeautifulSoup(read(item['source_page']),'html.parser')
   for m in page.select('meta[property="og:image"],meta[name="twitter:image"]'):
    if m.get('content'):urls.append(urljoin(item['source_page'],m['content']))
   for m in page.select('.product-cover img,.woocommerce-product-gallery img,.product-single__media img'):
    u=m.get('data-large_image')or m.get('src')
    if u:urls.append(urljoin(item['source_page'],u))
  except Exception as e:warnings.append(str(e)[:120])
 for url in dict.fromkeys(urls):
  try:
   raw=read(url);im=ImageOps.exif_transpose(Image.open(io.BytesIO(raw)));im.load()
   if max(im.size)<250:raise ValueError('Image too small for product display')
   original_size=im.size
   rgba=im.convert('RGBA');white=Image.new('RGBA',rgba.size,'white');white.alpha_composite(rgba);im=white.convert('RGB')
   # Remove plain exterior whitespace, never modify the label or proportions.
   diff=ImageChops.difference(im,Image.new('RGB',im.size,'white')).convert('L').point(lambda x:255 if x>29 else 0)
   box=diff.getbbox()
   if box:
    pad=max(8,round(max(im.size)*.012));l,t,r,b=box;im=im.crop((max(0,l-pad),max(0,t-pad),min(im.width,r+pad),min(im.height,b+pad)))
   # Landscape awards graphics are not bottle packshots. Keep searching; six are sufficient.
   if item['kind']=='wine' and im.width>im.height*1.1:raise ValueError('Landscape composition rather than bottle packshot')
   im.thumbnail((800,1100));im.save(target,quality=89,method=6)
   record.update(file='assets/products/'+id+'.webp',image_url=url,width=im.width,height=im.height,original_size=original_size,sha256=hashlib.sha256(raw).hexdigest(),downloaded=True)
   record['warnings']=warnings;return record
  except Exception as e:warnings.append(str(e)[:130])
 record.update(downloaded=False,warnings=warnings);return record

def rel(target,page):return posixpath.relpath(target,posixpath.dirname(page)or'.')
def put_photo(soup,holder,item,page):
 holder.clear();holder['class']=list(dict.fromkeys(holder.get('class',[])+['real-product-photo','photo-'+item['kind']]))
 im=soup.new_tag('img',src=rel(item['file'],page),alt=item['alt'],loading='eager',decoding='async');im['width']=str(item['width']);im['height']=str(item['height']);im['data-real-product']=item['id'];holder.append(im)

def apply(download=True):
 records=list(ThreadPoolExecutor(max_workers=5).map(load_one,SPEC['products'])) if download else json.loads((A/'product-photo-sources.json').read_text())['products']
 photos={r['id']:r for r in records if r.get('downloaded')}
 # Never publish a nominally completed update if the requested assets were not obtained.
 assert 'mejillones' in photos and 'oricios' in photos,'The two requested tins could not both be obtained'
 assert sum(r['kind']=='wine' for r in photos.values())>=6,'Fewer than six real wine packshots downloaded'
 report={'products':records,'usage':SPEC['usage'],'wine_photos':sum(r['kind']=='wine'for r in photos.values()),'pages_changed':[]}
 for file in [ROOT/'src/catalog.json',A/'catalog.json']:
  catalog=json.loads(file.read_text())
  for p in catalog['products']:
   if p['id'] in photos:
    m=photos[p['id']];p.update(m.get('catalogue_correction',{}));p['image']=m['file'];p['imageAlt']=m['alt'];p['imageSource']=m['source_page'];p['imageRights']='review_only_pending_clearance'
  file.write_text(json.dumps(catalog,ensure_ascii=False,indent=2))
 updated=json.loads((A/'catalog.json').read_text());by_id={p['id']:p for p in updated['products']}
 for path in SITE.rglob('*.html'):
  page=path.relative_to(SITE).as_posix()
  if not ('shop' in path.parts or 'warenkorb' in path.parts or 'checkout' in path.parts):continue
  soup=BeautifulSoup(path.read_text(),'html.parser');changed=False
  for card in soup.select('.product-card[data-product]'):
   id=card['data-product'];item=photos.get(id)
   if not item:continue
   holder=card.select_one('.product-art')
   if holder:put_photo(soup,holder,item,page);changed=True
   if item.get('catalogue_correction'):
    p=by_id[id];e=card.select_one('.eyebrow')
    if e:e.string=p['brand']+' · '+p['pack']
    desc=card.find('p',recursive=False)
    if desc:desc.string=p['description']
    select=card.select_one('select[data-variant] option[value=single]')
    if select:select.string=p['pack']+' · '+format(p['price']/100,'.2f').replace('.',',')+' €'
    unit=card.select_one('[data-unit]')
    if unit:unit.string=format(p['price']*1000/p['amount']/100,'.2f').replace('.',',')+' €/kg · zzgl. Versand'
  id=path.parent.name
  if id in photos:
   item=photos[id]
   for holder in soup.select('.product-art'):
    if holder.find_parent(class_='product-card') is None:put_photo(soup,holder,item,page);changed=True
   for cap in soup.select('.art-caption'):cap.decompose()
   if item.get('catalogue_correction'):
    for e in soup.find_all(string=True):
     if e.parent.name in ('script','style'):continue
     txt=str(e).replace('Agromar','Cabo de Peñas').replace('110 g','111 g')
     if 'Eine kleine Auswahl von der asturischen Küste.'in txt:txt=txt.replace('Eine kleine Auswahl von der asturischen Küste.','Aus Galicien, für den gemeinsamen Tisch.')
     if txt!=str(e):e.replace_with(txt)
   main=soup.find('main')
   if main and item['kind']=='wine' and not main.select_one('[data-vintage-note]'):
    p=soup.new_tag('p');p['class']=['product-photo-note','wrap'];p['data-vintage-note']='';p.string='Produktabbildung zur Designvorschau. Etikett und Jahrgang können von der vorhandenen Restaurantkarte abweichen.';main.append(p)
  for script in soup.find_all('script'):
   text=(script.string or'').strip()
   if text.startswith('window.VDE='):
    data=json.loads(text[len('window.VDE='):].rstrip(';'));data['products']=updated['products'];script.string='window.VDE='+json.dumps(data,ensure_ascii=False).replace('<','\\u003c')+';'
  if changed:
   if not soup.select_one('link[data-product-photos]'):
    link=soup.new_tag('link',rel='stylesheet',href=rel('assets/product-photos.css',page));link['data-product-photos']='';soup.head.append(link)
   path.write_text(str(soup));report['pages_changed'].append(page)
 (A/'product-photos.css').write_text('''.product-art.real-product-photo{display:flex;align-items:center;justify-content:center;background:#fff!important;padding:22px;position:relative;overflow:hidden}.product-art.real-product-photo:before,.product-art.real-product-photo:after{display:none!important}.product-art.real-product-photo img{display:block;max-width:100%;width:100%;height:100%;object-fit:contain;mix-blend-mode:normal;filter:none;clip-path:none;transform:none;margin:0}.product-art.real-product-photo.photo-wine img{max-height:330px;width:auto;max-width:80%;height:100%}.product-card .product-art.real-product-photo{height:345px;min-height:280px}.product-detail .product-art.real-product-photo{min-height:450px}.product-detail .product-art.real-product-photo img{max-height:560px}.product-photo-note{font:11px/1.7 Arial,sans-serif;opacity:.75;margin-block:24px}.product-art.real-product-photo.photo-pack img,.product-art.real-product-photo.photo-tin img{max-height:280px}.model08 .product-art.real-product-photo{padding:25px;background:#fff!important}@media(max-width:700px){.product-card .product-art.real-product-photo{height:305px;min-height:240px}.product-art.real-product-photo.photo-wine img{max-height:265px}.product-detail .product-art.real-product-photo{min-height:320px}}''')
 (A/'product-photo-sources.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
 out=ROOT/'reports/product-photos';out.mkdir(parents=True,exist_ok=True);(out/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
 print(json.dumps({'downloaded':list(photos),'wine_photos':report['wine_photos'],'shop_pages_changed':len(report['pages_changed'])},indent=2))
 return photos
if __name__=='__main__':apply()
