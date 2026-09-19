"""Browser, route, image and common-function checks; never alters public content."""
from pathlib import Path
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from PIL import Image
import functools,http.server,threading,json,io,numpy as np,traceback,posixpath
from urllib.parse import urlsplit,unquote
ROOT=Path(__file__).resolve().parents[1];SITE=ROOT/'site';OUT=ROOT/'reports/design-lab';OUT.mkdir(parents=True,exist_ok=True)
IDS=['v1','v2','v3','v4','v5','v6a','v6b','v08','v09','v10'];checks=[];errors=[]
class Quiet(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(SITE)));threading.Thread(target=server.serve_forever,daemon=True).start();BASE=f'http://127.0.0.1:{server.server_port}/'
def check(name,value,detail=None):
 checks.append({'name':name,'pass':bool(value),'detail':detail});print(('PASS 'if value else'FAIL ')+name,detail or'',flush=True)
def thumbnail(source,target):
 im=Image.open(io.BytesIO(source)).convert('RGB');im=im.crop((0,0,im.width,min(im.height,1050)));im.thumbnail((720,500));im.save(target,quality=90)
try:
 with sync_playwright()as p:
  browser=p.chromium.launch();ctx=browser.new_context(viewport={'width':1440,'height':1000},reduced_motion='reduce')
  ctx.on('page',lambda pg:pg.on('pageerror',lambda er:errors.append({'page':pg.url,'error':str(er)})))
  page=ctx.new_page()
  for id in IDS:
   page.set_viewport_size({'width':1440,'height':1000});page.goto(BASE+f'entwuerfe/{id}/index.html',wait_until='networkidle')
   if id=='v10':page.locator('.ref-hotspot[data-open-panel="speisekarte"]').first.click()
   check(id+' complete menu in DOM',page.locator('.live-menu-item').count()==36)
   check(id+' all 36 entries visible',page.locator('.live-menu-item:visible').count()==36)
   check(id+' full-menu control',page.locator('[data-full-menu]').count()==1)
   if id=='v10':page.locator('[data-close-panel]').click();page.locator('.replica-extra-links [data-open-panel="events"]').click()
   check(id+' one common catering form',page.locator('[data-events-form]').count()==1)
   check(id+' nine event fields',page.locator('[data-events-form] [name]').count()==9)
   check(id+' large-group option',page.locator('[name=type] option',has_text='Große Gruppe').count()==1)
   if id=='v10':page.locator('[data-close-panel]').click()
   page.locator('img').evaluate_all('(xs)=>xs.forEach(x=>x.loading="eager")');page.wait_for_timeout(450)
   broken=page.locator('img').evaluate_all('(xs)=>xs.filter(x=>!x.complete||!x.naturalWidth).map(x=>x.getAttribute("src"))');check(id+' images loaded',not broken,broken)
   for width in [1440,390,320]:
    page.set_viewport_size({'width':width,'height':1000});page.wait_for_timeout(90);dimensions=page.evaluate('({viewport:innerWidth,width:document.documentElement.scrollWidth})');check(id+' responsive '+str(width),dimensions['width']<=dimensions['viewport'],dimensions)
    if id in ['v09','v10']:
     page.screenshot(path=str(OUT/f'{id}-restaurant-{width}.png'),full_page=True)
   page.set_viewport_size({'width':1440,'height':1000})
   if id in ['v09','v10']:
    thumbnail(page.screenshot(full_page=True),SITE/'assets/proposals'/f'{id}-restaurant.webp')
    if id=='v09':
     check('09 uses exact photographic cutout',page.locator('.owner-sticker[src*="owner-mono.webp"]').count()==1);page.locator('[data-art-next]').click();check('09 graphic slideshow',page.locator('[data-art-count]').inner_text().startswith('02'))
    if id=='v10':
     check('10 uses extracted pieces',page.locator('[data-source-piece]').count()==19)
     raw=page.locator('.replica-board').screenshot(path=str(OUT/'v10-reference-reconstruction.png'))
     rendered=Image.open(io.BytesIO(raw)).convert('RGB').resize((1217,1280));ref=Image.open(SITE/'assets/lab/reference-original.png').convert('RGB').resize((1217,1280))
     a=np.asarray(rendered,dtype=float);b=np.asarray(ref,dtype=float);mae=float(np.mean(np.abs(a[:1086]-b[:1086])));check('10 source composition pixel comparison above corrected footer',mae<4,{'mean_absolute_error_0_255':round(mae,4)})
     for name in ['speisekarte','weine','vineria','besuch','events','news','instagram','grafiken']:
      page.locator('[data-open-panel="'+name+'"]:visible').first.click();check('10 opens '+name,page.locator('#replica-dialog').evaluate('(x)=>x.open'));page.locator('[data-close-panel]').click()
  for id in ['v09','v10']:
   for kind,route in [('shop','shop/index.html'),('product','shop/produkt/index.html?id=bujanda-blanco'),('cart','warenkorb/index.html'),('checkout','checkout/index.html'),('service','service/index.html')]:
    page.goto(BASE+f'entwuerfe/{id}/'+route,wait_until='networkidle')
    check(id+'/'+kind+' paired theme',page.locator('body.'+('lab09'if id=='v09'else'lab10')).count()==1)
    if kind=='shop':
     check(id+' eleven products',page.locator('.product-card').count()==11)
     page.locator('img').evaluate_all('(xs)=>xs.forEach(x=>x.loading="eager")');page.wait_for_timeout(250)
     check(id+' store images',page.locator('img').evaluate_all('(xs)=>xs.every(x=>x.complete&&x.naturalWidth>0)'))
     for w in [1440,390,320]:
      page.set_viewport_size({'width':w,'height':1000});page.screenshot(path=str(OUT/f'{id}-shop-{w}.png'),full_page=True);check(id+' shop width '+str(w),page.evaluate('document.documentElement.scrollWidth<=innerWidth'))
     page.set_viewport_size({'width':1440,'height':1000});thumbnail(page.screenshot(full_page=True),SITE/'assets/proposals'/f'{id}-shop.webp');page.locator('[data-add="bujanda-blanco"]').click()
    if kind=='product':check(id+' actual wine detail','Bujanda' in page.locator('main').inner_text())
    if kind=='cart':check(id+' test cart works','Bujanda' in page.locator('main').inner_text())
    if kind=='checkout':check(id+' no-payment test checkout',page.locator('#checkout-form').count()==1 and 'Test' in page.locator('main').inner_text())
   # All local dependencies and routes of the complete new paired route sets.
   missing=[]
   for f in (SITE/'entwuerfe'/id).rglob('*.html'):
    s=BeautifulSoup(f.read_text(),'html.parser')
    for el in s.select('[href],[src]'):
     val=el.get('href')or el.get('src');u=urlsplit(val)
     if u.scheme or u.netloc or not u.path:continue
     target=(f.parent/unquote(u.path)).resolve()
     if not target.exists():missing.append({'page':str(f.relative_to(SITE)),'target':val})
   check(id+' every local route and dependency exists',not missing,missing)
  page.goto(BASE+'verwaltung/vorschau.html',wait_until='networkidle');page.on('dialog',lambda d:d.accept());check('Shared management retains remove and visibility controls',page.locator('.control-delete').count()==13)
  page.locator('[data-control-tab=sections]').click();page.locator('#control-add').click();page.locator('[data-key=label]').last.fill('QA Specials');page.locator('#control-save').click();category=page.evaluate('VdeReview.state().sections.at(-1).id');page.locator('[data-control-tab=menu]').click();page.locator('#control-category').select_option(category);page.locator('#control-add').click();page.locator('[data-key=name]').fill('QA Gericht');page.locator('[data-key=price]').fill('9.90');page.locator('#control-save').click()
  for id in ['v09','v10']:
   other=ctx.new_page();other.goto(BASE+f'entwuerfe/{id}/index.html',wait_until='networkidle');check(id+' shared category and dish update',other.locator('.live-menu-item',has_text='QA Gericht').count()==1);other.close()
  page.locator('#control-reset').click();page.goto(BASE+'index.html',wait_until='networkidle');actual=page.locator('[data-proposal]').evaluate_all('(xs)=>xs.map(x=>x.dataset.proposal)');check('All ten models present without duplicates',actual==IDS,actual)
  for id in ['v09','v10']:
   page.locator('[data-open-pair="'+id+'"]').click();page.frame_locator('#frame-left').locator('body').wait_for();page.frame_locator('#frame-right').locator('.product-card').first.wait_for();check(id+' paired comparator opens',id in page.locator('#frame-left').get_attribute('src') and id in page.locator('#frame-right').get_attribute('src'));page.locator('#close-viewer').click()
  page.screenshot(path=str(OUT/'ten-model-selector.png'),full_page=True)
  check('No browser errors',not errors,errors);browser.close()
except Exception as exc:
 errors.append({'exception':str(exc),'trace':traceback.format_exc()});check('Run completed without exception',False,str(exc))
finally:
 server.shutdown();report={'passed':all(c['pass']for c in checks)and not errors,'count':len(checks),'checks':checks,'errors':errors};(OUT/'checks.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps({'passed':report['passed'],'checks':len(checks),'failed':[x for x in checks if not x['pass']]},ensure_ascii=False,indent=2))
if not report['passed']:raise SystemExit(1)
