"""Record what a first-time visitor sees, without credentials or access overrides."""
from pathlib import Path
from playwright.sync_api import sync_playwright
import json,time
out=Path('reports');out.mkdir(exist_ok=True)
url='https://raw.githack.com/Petrinus/vineria-revision/main/site/index.html'
report={'url':url,'time_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())}
with sync_playwright() as pw:
 browser=pw.chromium.launch();context=browser.new_context(viewport={'width':1440,'height':1000});page=context.new_page()
 try:
  response=page.goto(url,wait_until='networkidle',timeout=60000)
  report['http_status']=response.status;report['title']=page.title();report['visible_text']=page.locator('body').inner_text()[:2000]
  report['links']=page.locator('a').evaluate_all('(a)=>a.map(x=>({text:x.textContent,href:x.href})).slice(0,12)')
  report['buttons']=page.locator('button').all_text_contents();report['restaurant_visible']=page.locator('[data-slideshow]').count()>0
  page.screenshot(path=str(out/'public-first-visit.png'),full_page=True)
 except Exception as e:report['error']=str(e)
 browser.close()
(out/'public-access.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False,indent=2))
