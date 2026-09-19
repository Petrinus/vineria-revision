"""Functional checks for the responsive rebuild; screenshots are evidence, not proof of aesthetic perfection."""
from pathlib import Path
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from PIL import Image
from urllib.parse import urlsplit,unquote
import functools,http.server,threading,json,io,traceback
R=Path(__file__).resolve().parents[1];S=R/'site';OUT=R/'reports/responsive10';OUT.mkdir(exist_ok=True,parents=True)
class Quiet(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(S)));threading.Thread(target=server.serve_forever,daemon=True).start();BASE=f'http://127.0.0.1:{server.server_port}/';checks=[];errors=[]
def check(name,ok,detail=None):
 checks.append({'name':name,'pass':bool(ok),'detail':detail});print(('PASS 'if ok else'FAIL ')+name,detail or'',flush=True)
def extent(page):
 return page.evaluate('''()=>({viewport:innerWidth,width:document.documentElement.scrollWidth,overflow:[...document.querySelectorAll('body *')].filter(e=>{let r=e.getBoundingClientRect();return r.width&&r.right>innerWidth+1}).slice(0,8).map(e=>({tag:e.tagName,cls:e.className,text:e.textContent.slice(0,40)}))})''')
try:
 with sync_playwright()as p:
  browser=p.chromium.launch();ctx=browser.new_context(viewport={'width':1440,'height':1000},reduced_motion='reduce');page=ctx.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
  for kind,path in [('restaurant','index.html'),('shop','shop/index.html')]:
   page.goto(BASE+'entwuerfe/v10/'+path,wait_until='networkidle');page.locator('img').evaluate_all('(items)=>items.forEach(i=>i.loading="eager")');page.evaluate('document.fonts.ready');page.wait_for_timeout(400)
   bad=page.locator('img').evaluate_all('(a)=>a.filter(i=>!i.complete||!i.naturalWidth).map(i=>i.src)');check(kind+' all images load',not bad,bad)
   check(kind+' no old screenshot-board or hotspot navigation',page.locator('.replica-board,.ref-piece,.ref-hotspot,dialog').count()==0)
   check(kind+' clean separated PNG present',page.locator('img[src*="responsive10"][src$=".png"]').count()>=2)
   for width in [320,390,768,1024,1440,1920]:
    page.set_viewport_size({'width':width,'height':1000});page.wait_for_timeout(80);dim=extent(page);check(kind+' fits '+str(width),dim['width']<=width,dim if dim['width']>width else None)
    if width in [390,1440]:page.screenshot(path=str(OUT/f'{kind}-{width}.png'),full_page=True)
   page.set_viewport_size({'width':1440,'height':1000})
   if kind=='restaurant':
    check('all menu entries visible by default',page.locator('.live-menu-item:visible').count()==36,page.locator('.live-menu-item:visible').count());check('live headline is text',page.locator('h1').inner_text()=='Wein.\nTapas.\nLeben.')
    page.locator('[data-full-menu]').click();check('category mode works',page.locator('.live-menu-item:visible').count()<36)
    page.locator('[data-full-menu]').click();check('full menu returns',page.locator('.live-menu-item:visible').count()==36)
    page.locator('.v10-navigation a[href$="#weine"]').click();check('wine nav selects wine category',page.locator('#live-weisswein').is_visible())
    for anchor in ['vineria','besuch','speisekarte']:
     page.locator('.v10-navigation a[href$="#'+anchor+'"]').click();check('navigation to '+anchor,page.locator('#'+anchor).is_visible()and page.evaluate('location.hash')=='#'+anchor)
    page.locator('.lab-events summary').click();form=page.locator('[data-events-form]');check('catering opens inline',form.is_visible());check('catering group selection',form.locator('[name=type] option',has_text='Gruppenreservierung').count()==1)
    form.locator('[name=type]').select_option(label='Große Gruppe / Gruppenreservierung');form.locator('[name=name]').fill('Testperson');form.locator('[name=people]').fill('12');form.locator('[name=date]').fill('2027-05-10');form.locator('[name=email]').fill('test@example.com');form.locator('[name=message]').fill('Geburtstag mit zwölf Personen');check('event form validates',form.evaluate('(f)=>f.checkValidity()'))
    check('six curated Instagram photos retained',page.locator('[data-selected-instagram]').count()==6)
    page.set_viewport_size({'width':390,'height':844});page.locator('.v10-menu-toggle').click();check('mobile menu opens',page.locator('.v10-navigation').is_visible());page.locator('.v10-navigation a[href$="#vineria"]').click();check('mobile menu closes after choosing',not page.locator('.v10-navigation').is_visible());check('about visible after mobile navigation',page.locator('#vineria').is_visible())
    page.locator('.v10-menu-toggle').click();page.keyboard.press('Escape');check('mobile menu Escape closes',page.locator('.v10-menu-toggle').get_attribute('aria-expanded')=='false')
    page.set_viewport_size({'width':720,'height':1000});page.locator('html').evaluate('(e)=>e.style.fontSize="200%"');check('larger text reflows',extent(page)['width']<=720);page.locator('html').evaluate('(e)=>e.style.fontSize=""')
   else:
    check('shop catalogue retained',page.locator('.product-card').count()==11)
    page.locator('[data-add]').first.click();page.goto(BASE+'entwuerfe/v10/warenkorb/index.html',wait_until='networkidle');check('test cart adds product',page.locator('.cart-row').count()==1)
    page.goto(BASE+'entwuerfe/v10/checkout/index.html',wait_until='networkidle');check('test checkout works',page.locator('#checkout-form').count()==1)
    for width in [320,390,768,1440]:
     page.set_viewport_size({'width':width,'height':1000});check('checkout fits '+str(width),extent(page)['width']<=width)
    page.goto(BASE+'entwuerfe/v10/shop/produkt/index.html?id=mejillones',wait_until='networkidle');check('product detail works','Mejillones'in page.locator('h1').inner_text())
  # Shared editor retains changes and updated dishes are rendered by the rebuilt model.
  page.goto(BASE+'verwaltung/vorschau.html',wait_until='networkidle');before=page.evaluate('VdeReview.state()');page.evaluate('''()=>{let d=VdeReview.state();d.sections[0].items[0].name='RESPONSIVE TEST DISH';VdeReview.save(d);}''');page.goto(BASE+'entwuerfe/v10/index.html',wait_until='networkidle');check('shared management connected in browser',page.locator('.live-menu-item',has_text='RESPONSIVE TEST DISH').count()==1);page.evaluate('(d)=>VdeReview.save(d)',before)
  page.goto(BASE+'index.html',wait_until='networkidle');check('ten models preserved',page.locator('[data-proposal]').count()==10)
  # Generate genuine browser thumbnails for the existing comparator.
  for kind,sub in [('restaurant','index.html'),('shop','shop/index.html')]:
   page.set_viewport_size({'width':1440,'height':1000});page.goto(BASE+'entwuerfe/v10/'+sub,wait_until='networkidle');page.evaluate('document.fonts.ready');im=Image.open(io.BytesIO(page.screenshot())).convert('RGB');im.thumbnail((720,500));im.save(S/'assets/proposals'/f'v10-{kind}.webp',quality=90)
  check('no browser errors',not errors,errors);browser.close()
except Exception as e:
 errors.append(traceback.format_exc());check('test harness finished',False,str(e))
finally:server.shutdown()
# Check that the rebuilt pages only refer to existing local files.
broken=[]
for p in (S/'entwuerfe/v10').rglob('*.html'):
 doc=BeautifulSoup(p.read_text(),'html.parser')
 for el in doc.select('[src],a[href],link[href]'):
  raw=el.get('src')or el.get('href');u=urlsplit(raw)
  if u.scheme or u.netloc or not u.path:continue
  target=(p.parent/unquote(u.path)).resolve()
  if not target.exists():broken.append({'page':str(p.relative_to(S)),'target':raw})
check('all local navigation and resource paths exist',not broken,broken)
audit=json.loads((S/'assets/responsive10/asset-audit.json').read_text());check('only transparent clean PNGs imported',all(x['transparent_fraction']>0 and not x['work_guides_detected']for x in audit['layers']))
report={'passed':all(c['pass']for c in checks),'count':len(checks),'checks':checks,'errors':errors};(OUT/'checks.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps({'passed':report['passed'],'count':len(checks),'failures':[x for x in checks if not x['pass']]}))
if not report['passed']:raise SystemExit(1)
