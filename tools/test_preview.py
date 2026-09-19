from pathlib import Path
from playwright.sync_api import sync_playwright
from urllib.request import Request,urlopen
import json,subprocess,time
out=Path('checks');out.mkdir(exist_ok=True)
server=subprocess.Popen(['python3','-m','http.server','8106','--directory','site'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
results=[]
try:
 time.sleep(1)
 with sync_playwright() as p:
  b=p.chromium.launch(headless=True)
  for w in [1440,390,320]:
   page=b.new_page(viewport={'width':w,'height':960});errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
   for path,label in [('index.html','restaurant'),('shop/index.html','shop'),('editorial/index.html','editorial'),('entwuerfe/index.html','portal')]:
    page.goto('http://127.0.0.1:8106/'+path);page.wait_for_timeout(500)
    # Trigger lazy image loading without changing the final screenshot position.
    page.evaluate('document.querySelectorAll("img").forEach(i=>i.loading="eager")');page.wait_for_timeout(400)
    result={'path':path,'width':w,'overflow':page.evaluate('document.documentElement.scrollWidth>innerWidth+1'),'broken_images':page.locator('img').evaluate_all('(a)=>a.filter(i=>!i.complete||i.naturalWidth===0).map(i=>i.src)'),'errors':errors.copy()};results.append(result)
    page.screenshot(path=str(out/f'{label}-{w}.png'),full_page=False)
   page.close()
  page=b.new_page(viewport={'width':1280,'height':900});page.goto('http://127.0.0.1:8106/shop/index.html');page.locator('[data-add="bujanda-blanco"]').click();page.goto('http://127.0.0.1:8106/warenkorb/index.html');results.append({'cart_persists':page.locator('.cart-row').count()==1,'total':page.locator('.sum-row.total').inner_text()});page.goto('http://127.0.0.1:8106/checkout/index.html');page.locator('[name=test]').check();page.locator('[name=age]').check();page.locator('button[type=submit]').click();page.locator('#finish-test').click();results.append({'checkout_completes':'Test abgeschlossen' in page.locator('body').inner_text()})
  page.goto('http://127.0.0.1:8106/index.html');page.locator('[data-tab=rotwein]').click();results.append({'wine_tab':page.locator('#rotwein').is_visible(),'week_hidden':not page.locator('#wochenkarte').is_visible()});page.locator('[data-pause]').click();results.append({'pause':page.locator('[data-pause]').get_attribute('aria-pressed')=='true'})
  page.emulate_media(reduced_motion='reduce');page.reload();results.append({'reduced_motion':page.locator('[data-pause]').get_attribute('aria-pressed')=='true'})
  page.goto('http://127.0.0.1:8106/verwaltung/index.html');calls=[];page.on('request',lambda r:calls.append(r.url) if r.method=='POST' else None);page.locator('[name=username]').fill('demo');page.locator('[name=password]').fill('not-a-real-password');page.locator('button[type=submit]').click();results.append({'public_admin_transmits_nothing':len(calls)==0,'public_admin_explains_server': 'keinen Verwaltungsserver' in page.locator('#login-message').inner_text()})
  b.close()
finally:server.terminate()
# Public links are fetched anonymously as normal HTTP clients.
for path in ['index.html','shop/index.html','entwuerfe/index.html']:
 u='https://raw.githack.com/Petrinus/vineria-revision/main/site/'+path
 try:
  with urlopen(Request(u,headers={'User-Agent':'VineriaReviewCheck/1.0'}),timeout=35) as r:
   body=r.read().decode('utf-8','replace');results.append({'public_url':u,'status':r.status,'content_type':r.headers.get('Content-Type'),'title_present':'Vineria del Este' in body or 'Vinería del Este' in body,'bytes':len(body)})
 except Exception as e:results.append({'public_url':u,'error':str(e)})
(out/'results.json').write_text(json.dumps(results,ensure_ascii=False,indent=2));print(json.dumps(results,ensure_ascii=False,indent=2))
