from pathlib import Path
from playwright.sync_api import sync_playwright
from PIL import Image
import http.server,functools,threading,json,copy,io
ROOT=Path(__file__).resolve().parents[1];SITE=ROOT/'site';OUT=ROOT/'reports/halftone';OUT.mkdir(parents=True,exist_ok=True)
class Quiet(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(SITE)));threading.Thread(target=server.serve_forever,daemon=True).start();base=f'http://127.0.0.1:{server.server_port}/';ids=['v1','v2','v3','v4','v5','v6a','v6b','v08'];checks=[];errors=[]
def check(name,v,detail=None):
 checks.append({'name':name,'pass':bool(v),'detail':detail});print(('PASS 'if v else'FAIL ')+name,detail or'',flush=True)
try:
 with sync_playwright()as p:
  b=p.chromium.launch();ctx=b.new_context(viewport={'width':1440,'height':1000},reduced_motion='reduce');page=ctx.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
  for id in ids:
   for kind,sub in [('restaurant','index.html'),('shop','shop/index.html')]:
    page.goto(base+f'entwuerfe/{id}/'+sub,wait_until='networkidle');page.locator('img').evaluate_all('(a)=>a.forEach(i=>i.loading="eager")');page.wait_for_timeout(150)
    bad=page.locator('img').evaluate_all('(a)=>a.filter(i=>!i.complete||!i.naturalWidth).map(i=>i.src)');check(id+'/'+kind+' images',not bad,bad)
    check(id+'/'+kind+' original logo',page.locator('.original-brand img').count()==1)
    if kind=='restaurant':check(id+' full menu',page.locator('.live-menu-item').count()==36);check(id+' shared blocks',page.locator('[data-live-news]').count()==1 and page.locator('[data-live-instagram]').count()==1)
    else:check(id+' catalogue',page.locator('.product-card').count()==11)
    for width in [1440,390,320]:
     page.set_viewport_size({'width':width,'height':1000});extent=page.evaluate('({width:innerWidth,content:document.documentElement.scrollWidth})');check(id+'/'+kind+' width '+str(width),extent['content']<=extent['width'],extent)
     if id in ['v08','v6a']and width in [1440,390]:page.screenshot(path=str(OUT/f'{id}-{kind}-{width}.png'),full_page=True)
    page.set_viewport_size({'width':1440,'height':1000});raw=page.screenshot(full_page=True)
    im=Image.open(io.BytesIO(raw)).convert('RGB');im=im.crop((0,0,im.width,min(im.height,1000)));im.thumbnail((720,500));(SITE/'assets/proposals').mkdir(exist_ok=True);im.save(SITE/'assets/proposals'/f'{id}-{kind}.webp',quality=88)
  page.goto(base+'verwaltung/vorschau.html',wait_until='networkidle');page.on('dialog',lambda d:d.accept())
  check('Delete cross and checkbox',page.locator('.control-delete').count()==13 and page.locator('[data-key=visible]').count()==13)
  page.locator('.control-delete').first.click();page.locator('#control-save').click();check('Delete dish persists',len(page.evaluate('VdeReview.state().sections[0].items'))==12)
  page.locator('#control-undo').click();check('Undo dish',len(page.evaluate('VdeReview.state().sections[0].items'))==13)
  page.locator('[data-control-tab=sections]').click();page.locator('#control-add').click();page.locator('[data-key=label]').last.fill('Desserts Test');page.locator('#control-save').click();catid=page.evaluate('VdeReview.state().sections.at(-1).id');check('Category creation',bool(catid))
  page.locator('[data-control-tab=menu]').click();page.locator('#control-category').select_option(catid);page.locator('#control-add').click();page.locator('[data-key=name]').fill('Test Dessert');page.locator('[data-key=price]').fill('8.50');page.locator('#control-save').click()
  for id in ids:
   other=ctx.new_page();other.goto(base+f'entwuerfe/{id}/index.html',wait_until='networkidle');check(id+' added category and dish',other.locator('[role=tab]').count()==5 and other.locator('.live-menu-item',has_text='Test Dessert').count()==1);other.close()
  page.locator('[data-control-tab=products]').click();page.locator('#control-add').click();page.locator('.control-product').last.locator('[data-key=name]').fill('Test Produkt');page.locator('.control-product').last.locator('[data-key=price]').fill('7.20');page.locator('#control-save').click();pid=page.evaluate('VdeReview.state().products.at(-1).id')
  other=ctx.new_page();other.goto(base+'entwuerfe/v08/shop/index.html',wait_until='networkidle');check('New product rendered',other.locator('.product-card').count()==12);other.locator(f'[data-add="{pid}"]').click();other.goto(base+'entwuerfe/v08/warenkorb/index.html',wait_until='networkidle');check('New product in cart',other.locator('main').inner_text().find('Test Produkt')>=0)
  other.goto(base+f'entwuerfe/v08/shop/produkt/index.html?id={pid}',wait_until='networkidle');check('New product detail',other.locator('h1').inner_text()=='Test Produkt');other.close()
  page.locator('[data-control-tab=news]').click();page.locator('#control-add').click();news=page.locator('.control-product').last;news.locator('[data-key=title]').fill('Paella QA');news.locator('[data-key=text]').fill('Sonntag 13 Uhr');news.locator('summary').click();news.locator('[data-image]').select_option('assets/approved/pulpo-halftone.webp');page.locator('#control-save').click()
  other=ctx.new_page();other.goto(base+'entwuerfe/v08/index.html',wait_until='networkidle');check('News with text and photo',other.locator('[data-live-news]').inner_text().find('Paella QA')>=0 and other.locator('[data-live-news] img').count()==2);other.close()
  page.locator('#news-show').uncheck();other=ctx.new_page();other.goto(base+'entwuerfe/v1/index.html',wait_until='networkidle');check('One-click news hide',other.locator('[data-live-news]').is_hidden());other.close()
  page.locator('[data-control-tab=instagram]').click();page.locator('#ig-show').uncheck();page.locator('#ig-count').select_option('8');other=ctx.new_page();other.goto(base+'entwuerfe/v4/index.html',wait_until='networkidle');check('Instagram configurable',other.locator('[data-live-instagram]').is_hidden());other.close()
  page.locator('#control-reset').click();page.locator('[data-control-tab=menu]').click();page.screenshot(path=str(OUT/'management-menu.png'),full_page=True);page.locator('[data-control-tab=news]').click();page.screenshot(path=str(OUT/'management-news.png'),full_page=True);page.set_viewport_size({'width':390,'height':1000});page.screenshot(path=str(OUT/'management-mobile.png'),full_page=True);check('Management mobile',page.evaluate('document.documentElement.scrollWidth<=innerWidth'));page.set_viewport_size({'width':1440,'height':1000});
  page.goto(base+'index.html',wait_until='networkidle');check('Only the original eight designs',page.locator('[data-proposal]').count()==8);page.screenshot(path=str(OUT/'catalogue.png'),full_page=True)
  check('No script errors',not errors,errors);b.close()
finally:server.shutdown()
report={'checks':checks,'passed':all(c['pass']for c in checks),'errors':errors};(OUT/'checks.json').write_text(json.dumps(report,indent=2,ensure_ascii=False));print('PASSED',report['passed'])
if not report['passed']:raise SystemExit(1)
