"""Executable review QA. Screenshots and honest results, no personal data."""
from pathlib import Path
from urllib.parse import urljoin,urlparse,unquote
from urllib.request import Request,urlopen
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from functools import partial
from threading import Thread
from playwright.sync_api import sync_playwright
import json,time,sys
R=Path('site').resolve();OUT=Path('reports');OUT.mkdir(exist_ok=True)
results=[]
def check(name,ok,detail=''):
 results.append({'check':name,'pass':bool(ok),'detail':str(detail)});print(('PASS ' if ok else 'FAIL ')+name+' '+str(detail)[:180],flush=True)
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',8765),partial(Quiet,directory=str(R)))
Thread(target=server.serve_forever,daemon=True).start();base='http://127.0.0.1:8765/'
with sync_playwright() as pw:
 browser=pw.chromium.launch()
 context=browser.new_context(viewport={'width':1440,'height':1000})
 page=context.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 pages=sorted(R.rglob('*.html'))
 for p in pages:
  relative=p.relative_to(R).as_posix();response=page.goto(base+relative,wait_until='networkidle');page.locator('img').evaluate_all('(xs)=>xs.forEach(x=>x.loading="eager")');page.wait_for_timeout(150)
  check('HTTP '+relative,response.status==200)
  check('Title/lang '+relative,bool(page.title()) and page.locator('html').get_attribute('lang')=='de')
  check('No broken images '+relative,page.locator('img').evaluate_all('(xs)=>xs.every(x=>x.complete&&x.naturalWidth>0)'))
  bad=page.locator('a[href],link[href],script[src]').evaluate_all('''(els)=>els.map(e=>e.href||e.src).filter(x=>x&&x.startsWith(location.origin))''')
  missing=[]
  for u in bad:
   parts=urlparse(u);dest=R/unquote(parts.path).lstrip('/')
   if not dest.is_file() and not (dest.is_dir() and (dest/'index.html').exists()):missing.append(u)
  check('Local links '+relative,not missing,missing[:3])
  if relative in ['index.html','shop/index.html','editorial/index.html','editorial/shop/index.html','entwuerfe/index.html','verwaltung/index.html']:
   for width in [1440,390,320]:
    page.set_viewport_size({'width':width,'height':950});page.wait_for_timeout(120)
    size=page.evaluate('({scroll:document.documentElement.scrollWidth,width:innerWidth})')
    check(f'No horizontal overflow {relative} {width}',size['scroll']<=width+1,size)
    if width in [1440,390]:page.screenshot(path=str(OUT/(relative.replace('/','-').replace('.html','')+f'-{width}.png')),full_page=True)
   page.set_viewport_size({'width':1440,'height':1000})
 page.goto(base+'index.html');check('36 menu entries',page.locator('.dish').count()==36)
 page.locator('[data-tab="klassiker"]').click();check('16 classics visible',page.locator('#klassiker .dish:visible').count()==16)
 page.locator('[data-tab="klassiker"]').press('ArrowRight');check('Keyboard wine tab',page.locator('[data-tab="weisswein"]').get_attribute('aria-selected')=='true')
 count=page.locator('[data-slide-number]').inner_text();page.locator('[data-next]').click();check('Slideshow next',page.locator('[data-slide-number]').inner_text()!=count)
 page.locator('[data-pause]').click();check('Slideshow pause',page.locator('[data-pause]').get_attribute('aria-pressed')=='true')
 page.goto(base+'shop/index.html');check('11 products',page.locator('.product-card').count()==11)
 page.locator('[data-filter="rotwein"]').click();check('4 red wines filter',page.locator('.product-card:visible').count()==4)
 page.locator('[data-filter="all"]').click();page.locator('[data-search]').fill('Bujanda');check('Search specific wine',page.locator('.product-card:visible').count()==1)
 page.locator('[data-search]').fill('');card=page.locator('[data-product="bujanda-blanco"]');card.locator('[data-variant]').select_option('case');card.locator('[data-add]').click()
 page.goto(base+'warenkorb/index.html');check('Six bottle case format','6 ×' in page.locator('#warenkorb').inner_text());check('Case plus wine shipping','83,40' in page.locator('#warenkorb').inner_text())
 page.goto(base+'checkout/index.html');page.locator('[name="test"]').check();page.locator('[name="age"]').check();page.locator('#checkout-form button[type="submit"]').click();check('Checkout review stage',page.locator('#finish-test').count()==1)
 page.locator('#finish-test').click();check('Explicit nonpayment confirmation','nichts bezahlt' in page.locator('#checkout').inner_text())
 page.goto(base+'shop/index.html');page.locator('[data-product="chorizo"] [data-add]').click();page.goto(base+'warenkorb/index.html');check('Cold product disables normal shipping',page.locator('[name="delivery"][value="shipping"]').is_disabled())
 page.locator('#clear-cart').click();check('Empty cart has no checkout link',page.locator('#warenkorb').get_by_text('Zum Test-Checkout').count()==0)
 # Public static admin must neither send nor accept credentials.
 page.goto(base+'verwaltung/index.html');sent=[];page.on('request',lambda r:sent.append(r) if r.method=='POST' else None)
 page.locator('[name="username"]').fill('Test');page.locator('[name="password"]').fill('fictional-passphrase');page.locator('#admin-login button').click();check('Static login no POST',len(sent)==0);check('Static login honest disabled state','keinen Verwaltungsserver' in page.locator('#login-message').inner_text())
 check('No JS exceptions',not errors,errors)
 reduced=browser.new_context(reduced_motion='reduce');p=reduced.new_page();p.goto(base+'index.html');check('Reduced-motion default pauses slideshow',p.locator('[data-pause]').get_attribute('aria-pressed')=='true');reduced.close()
 nojs=browser.new_context(java_script_enabled=False);p=nojs.new_page();p.goto(base+'index.html');check('No-JS all menu items readable',p.locator('.dish:visible').count()==36);p.goto(base+'shop/index.html');check('No-JS product links exist',p.locator('.product-card h2 a').count()==11);nojs.close()
 browser.close()
server.shutdown()
OUT.joinpath('qa.json').write_text(json.dumps({'checks':len(results),'passed':sum(x['pass'] for x in results),'failed':[x for x in results if not x['pass']],'details':results},indent=2,ensure_ascii=False))
if not all(x['pass'] for x in results):sys.exit(1)
