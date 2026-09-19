"""Executable browser checks for the neutral review portal."""
from pathlib import Path
from playwright.sync_api import sync_playwright
import json,threading,http.server,functools,time
out=Path('reports/portal');out.mkdir(parents=True,exist_ok=True)
handler=functools.partial(http.server.SimpleHTTPRequestHandler,directory=str(Path('site').resolve()))
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),handler);threading.Thread(target=server.serve_forever,daemon=True).start();base=f'http://127.0.0.1:{server.server_port}'
results=[]
def ck(name,value):
 results.append({'check':name,'pass':bool(value)});print(('PASS 'if value else 'FAIL ')+name)
manifest=json.loads(Path('site/entwuerfe/ideen.json').read_text())
with sync_playwright() as p:
 b=p.chromium.launch();page=b.new_page(viewport={'width':1440,'height':1000});errors=[];posts=[]
 page.on('pageerror',lambda e:errors.append(str(e)));page.on('request',lambda r:posts.append(r.url) if r.method=='POST' else None)
 page.goto(base+'/entwuerfe/index.html');ck('Overview first, no winner',manifest['selected'] is None and not manifest['ranking'] and page.locator('#overview').is_visible() and not page.locator('#workspace').is_visible())
 ck('All published pairs represented',page.locator('[data-idea-card]').count()==len(manifest['ideas']))
 for idea in manifest['ideas']:
  row=page.locator('[data-idea-card="'+idea['id']+'"]');ck(idea['id']+' restaurant shop and management links',row.locator('.actions a').count()==4)
  row.locator('[data-open="pair"]').click();page.frame_locator('[data-frame="restaurant"]').locator('h1').wait_for();page.frame_locator('[data-frame="shop"]').locator('h1').wait_for()
  ck(idea['id']+' two homepages visible',page.locator('[data-pane="restaurant"]').is_visible() and page.locator('[data-pane="shop"]').is_visible())
  rs=page.frame_locator('[data-frame="restaurant"]').locator('body').evaluate('e=>getComputedStyle(e).backgroundColor');ss=page.frame_locator('[data-frame="shop"]').locator('body').evaluate('e=>getComputedStyle(e).backgroundColor');ck(idea['id']+' consistent paired background',rs==ss)
  page.locator('[data-view="all"]').click();page.frame_locator('[data-frame="management"]').locator('h1').wait_for();ck(idea['id']+' all three visible',page.locator('[data-pane]:visible').count()==3)
  page.locator('#workspace [data-overview]').click()
 page.locator('.nav [data-global-admin]').click();ck('Independent shared management',page.locator('[data-pane="management"]').is_visible() and not page.locator('[data-pane="restaurant"]').is_visible())
 admin=page.frame_locator('[data-frame="management"]');admin.locator('.side [data-tab="menu"]').click();ck('Menu management homepage usable',admin.locator('#menu-rows .row').count()>0)
 admin.locator('[data-section="menu"] [data-demo-save]').click();ck('Demo never claims publication','nichts veröffentlicht' in admin.locator('#status').inner_text())
 admin.locator('.side [data-tab="users"]').click();admin.locator('[data-account-demo]').first.click();ck('No password requested in public demo',admin.locator('input[type="password"]').count()==0)
 page.locator('#workspace [data-overview]').click()
 for width in [1440,390,320]:
  page.set_viewport_size({'width':width,'height':1000});page.wait_for_timeout(100);ck('No portal overflow '+str(width),page.evaluate('document.documentElement.scrollWidth<=innerWidth'))
  if width in [1440,390]:page.screenshot(path=str(out/f'portal-{width}.png'),full_page=True)
 ck('No POST requests',not posts);ck('No JavaScript exceptions',not errors)
 b.close()
server.shutdown()
report={'checks':len(results),'passed':sum(x['pass'] for x in results),'failed':[x for x in results if not x['pass']],'details':results,'errors':errors}
(out/'checks.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
raise SystemExit(0 if not report['failed'] else 1)
