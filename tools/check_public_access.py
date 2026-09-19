"""Read-only first-visit QA using the public website's normal navigation."""
from pathlib import Path
from playwright.sync_api import sync_playwright
import json,time
out=Path('reports');out.mkdir(exist_ok=True)
base='https://raw.githack.com/Petrinus/vineria-revision/main/site/'
report={'url':base+'index.html','time_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'account_required':False}
with sync_playwright() as pw:
 browser=pw.chromium.launch();context=browser.new_context(viewport={'width':1440,'height':1000});page=context.new_page()
 try:
  response=page.goto(base+'index.html',wait_until='networkidle',timeout=60000)
  report['http_status']=response.status;report['first_title']=page.title();report['first_text']=page.locator('body').inner_text()[:1300]
  page.screenshot(path=str(out/'public-first-visit.png'),full_page=True)
  button=page.get_by_role('button',name='Open the page',exact=True)
  report['provider_confirmation_required']=button.count()>0
  if button.count():
   button.click();page.wait_for_load_state('networkidle',timeout=60000)
  page.wait_for_selector('[data-slideshow]',timeout=30000)
  page.locator('img').evaluate_all('(xs)=>xs.forEach(x=>x.loading="eager")');page.wait_for_timeout(1500)
  report['restaurant_title']=page.title();report['restaurant_visible']=True
  report['restaurant_images']=page.locator('img').evaluate_all('(xs)=>xs.map(x=>({url:x.src,loaded:x.complete&&x.naturalWidth>0}))')
  page.screenshot(path=str(out/'public-restaurant.png'),full_page=True)
  response=page.goto(base+'shop/index.html',wait_until='networkidle',timeout=60000)
  report['shop_status']=response.status;report['shop_title']=page.title();report['products']=page.locator('.product-card').count()
  report['login_required_for_shop']=page.locator('input[type=password]').count()>0
  page.screenshot(path=str(out/'public-shop.png'),full_page=True)
  response=page.goto(base+'entwuerfe/index.html',wait_until='networkidle',timeout=60000)
  report['portal_status']=response.status;report['portal_title']=page.title();report['versions']=page.locator('.review-card').count()
 except Exception as e:report['error']=str(e)
 browser.close()
report['verified']=report.get('restaurant_visible') is True and report.get('products')==11 and report.get('versions')==2 and not report.get('error')
(out/'public-access.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False,indent=2))
if not report['verified']:raise SystemExit(1)
