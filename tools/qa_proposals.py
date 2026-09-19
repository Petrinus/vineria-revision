from pathlib import Path
from playwright.sync_api import sync_playwright
from PIL import Image
from bs4 import BeautifulSoup
import json,os,shutil,threading,http.server,socketserver,functools,posixpath
R=Path(os.environ.get('VDE_OUTPUT','site')).resolve();(R/'assets/proposals').mkdir(exist_ok=True)
report=[]
def check(name,ok,detail=''):
 report.append(dict(name=name,pass_=bool(ok),detail=str(detail)));print('PASS' if ok else 'FAIL',name,detail)
class Quiet(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=socketserver.TCPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(R)))
threading.Thread(target=server.serve_forever,daemon=True).start();URL=f'http://127.0.0.1:{server.server_address[1]}/'
with sync_playwright() as p:
 kwargs=dict(headless=True,args=['--no-sandbox'])
 if shutil.which('chromium'):kwargs['executable_path']=shutil.which('chromium')
 b=p.chromium.launch(**kwargs);context=b.new_context(viewport={'width':1440,'height':1000},reduced_motion='reduce');page=context.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 cfg=json.loads((R/'assets/proposals.json').read_text())
 for x in cfg:
  for kind,tail in [('restaurant','index.html'),('shop','shop/index.html')]:
   url=f"entwuerfe/{x['id']}/{tail}";resp=page.goto(URL+url,wait_until='load');page.wait_for_timeout(120)
   check(url+' loads',resp.status==200)
   check(url+' no green stars',page.locator('.scene-star').count()==0 and '✳' not in page.locator('body').inner_text())
   if kind=='shop':check(url+' 11 products',page.locator('.product-card').count()==11)
   else:check(url+' matching shop link',page.locator('.proposal-nav a').filter(has_text='Tienda').get_attribute('href')=='shop/index.html')
   broken=page.locator('img').evaluate_all('(imgs)=>imgs.filter(i=>i.getAttribute("src")&&!i.complete||i.getAttribute("src")&&i.complete&&i.naturalWidth===0).map(i=>i.getAttribute("src"))')
   check(url+' images',not broken,broken)
   pic=R/'assets/proposals'/f"{x['id']}-{kind}.png";page.screenshot(path=str(pic))
   im=Image.open(pic);im.resize((720,500),Image.Resampling.LANCZOS).save(pic.with_suffix('.webp'),quality=80);pic.unlink()
   for width in [390,320]:
    page.set_viewport_size({'width':width,'height':850});page.wait_for_timeout(60)
    dims=page.evaluate('({s:document.documentElement.scrollWidth,w:innerWidth})');check(url+f' width {width}',dims['s']<=width+1,dims)
   page.set_viewport_size({'width':1440,'height':1000})
 page.goto(URL);check('7 equal proposal cards',page.locator('.idea').count()==7);check('No preferred design',page.locator('.current,.recommended,.ribbon').count()==0);check('No iframe until selection',page.locator('iframe[src]').count()==0);check('Shared management present',page.locator('a[href="verwaltung/index.html"]').count()>=2)
 page.screenshot(path=str(R.parent/'portal-desktop.png'),full_page=True)
 page.locator('[data-open-pair="v2"]').click();page.wait_for_timeout(200)
 check('Pair viewer opens',page.locator('#vergleich').is_visible());check('Restaurant and shop paired','v2/index.html' in page.locator('#frame-left').get_attribute('src') and 'v2/shop/index.html' in page.locator('#frame-right').get_attribute('src'))
 page.locator('#proposal-right').select_option('v6a');check('Independent comparison','v6a/shop' in page.locator('#frame-right').get_attribute('src'))
 page.locator('[data-mode=mobile]').click();check('Mobile comparison',page.locator('#vergleich').evaluate('(e)=>e.classList.contains("mobile")'))
 page.locator('#close-viewer').click();check('Closing clears frames',page.locator('iframe[src]').count()==0)
 page.set_viewport_size({'width':390,'height':844});page.goto(URL);page.screenshot(path=str(R.parent/'portal-mobile.png'),full_page=True);check('Portal mobile no overflow',page.evaluate('document.documentElement.scrollWidth<=innerWidth'))
 page.goto(URL+'entwuerfe/v1/shop/index.html');page.locator('[data-add=mejillones]').click();page.goto(URL+'entwuerfe/v1/warenkorb/index.html');check('Variant 01 cart works','Mejillones' in page.locator('#warenkorb').inner_text());check('Checkout belongs to same pair','../checkout/index.html'==page.locator('#warenkorb a').filter(has_text='Checkout').get_attribute('href'))
 page.goto(URL+'verwaltung/index.html');check('Separate management page',page.locator('#admin-entry').is_visible());check('No real password entry',page.locator('input[type=password]').is_disabled())
 page.goto(URL+'verwaltung/vorschau.html');page.wait_for_selector('.edit-row');check('Management menu 13 weekly rows',page.locator('.edit-row').count()==13)
 first=page.locator('input[data-field=name]').first;first.fill('Lokale Testzeile');page.locator('#save-demo').click();page.reload();page.wait_for_selector('.edit-row');check('Demo saved locally',page.locator('input[data-field=name]').first.input_value()=='Lokale Testzeile')
 page.locator('[data-admin-tab=products]').click();check('11 management products',page.locator('.edit-row').count()==11);page.locator('[data-admin-tab=team]').click();check('Two preview team entries',page.locator('.team-row').count()==2);check('No password in preview',page.locator('input[type=password]:enabled').count()==0)
 check('No JavaScript exceptions',not errors,errors)
 b.close()
# Internal resource targets across every public HTML file.
missing=[]
for f in R.rglob('*.html'):
 soup=BeautifulSoup(f.read_text(),'html.parser')
 for el in soup.find_all(True):
  for a in ['href','src']:
   val=el.get(a,'')
   if not val or val.startswith(('#','http:','https:','mailto:','tel:','data:','javascript:')):continue
   v=val.partition('#')[0].partition('?')[0]
   if v and not (f.parent/v).resolve().exists():missing.append((str(f.relative_to(R)),v))
check('All local links and assets exist',not missing,missing[:25])
(R.parent/'proposal-qa.json').write_text(json.dumps(report,indent=2,ensure_ascii=False))
server.shutdown()
if any(not x['pass_'] for x in report):raise SystemExit(1)
print('ALL',len(report),'CHECKS PASSED')
