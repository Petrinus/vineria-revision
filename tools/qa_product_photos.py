"""Read-only local browser verification of the requested shop photographs."""
from pathlib import Path
from playwright.sync_api import sync_playwright
import functools,http.server,json,threading
root=Path('site');out=Path('reports/product-photos');out.mkdir(parents=True,exist_ok=True)
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(http.server.SimpleHTTPRequestHandler,directory=str(root.resolve())))
threading.Thread(target=server.serve_forever,daemon=True).start();base='http://127.0.0.1:'+str(server.server_port)
checks=[];errors=[];originals=['v1','v2','v3','v4','v5','v6a','v6b']
try:
 with sync_playwright()as p:
  browser=p.chromium.launch();page=browser.new_page(viewport={'width':1440,'height':1000})
  page.on('pageerror',lambda e:errors.append(str(e)))
  for model in originals:
   path='entwuerfe/'+model+'/shop/index.html';page.goto(base+'/'+path,wait_until='networkidle')
   photos=page.locator('[data-real-product]').evaluate_all('(a)=>a.map(i=>({id:i.dataset.realProduct,loaded:i.complete&&i.naturalWidth>0}))')
   wines=[x for x in photos if x['id']not in ['mejillones','oricios','chorizo','cecina']]
   assert len(wines)>=6 and all(x['loaded']for x in photos),(model,photos)
   assert any(x['id']=='mejillones'for x in photos)and any(x['id']=='oricios'for x in photos),model
   assert page.locator('.product-card').count()==11,model
   page.screenshot(path=str(out/(model+'-shop.png')),full_page=True)
   page.set_viewport_size({'width':390,'height':900});page.wait_for_timeout(150)
   overflow=page.evaluate('document.documentElement.scrollWidth>innerWidth')
   page.screenshot(path=str(out/(model+'-mobile.png')),full_page=True)
   checks.append({'model':model,'photos':len(photos),'wine_photos':len(wines),'all_loaded':True,'mobile_overflow':overflow})
   assert not overflow,model
   page.set_viewport_size({'width':1440,'height':1000})
  page.goto(base+'/index.html')
  ids=page.locator('[data-proposal]').evaluate_all('(cards)=>cards.map(c=>c.dataset.proposal)')
  assert len(ids)==len(set(ids)),'Duplicate design option'
  assert set(ids)in [set(originals),set(originals+['v08'])],'An original option was removed or an unrequested model was added'
  browser.close()
finally:server.shutdown()
report={'shops':checks,'selector_ids':ids,'javascript_errors':errors,'passed':len(checks)==7 and not errors}
(out/'checks.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False,indent=2))
if not report['passed']:raise SystemExit(1)
