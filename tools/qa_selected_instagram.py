"""Read-only browser QA against locally built pages. Uses no Instagram connection."""
from pathlib import Path
from playwright.sync_api import sync_playwright
from PIL import Image
import functools,http.server,threading,json,hashlib
ROOT=Path(__file__).resolve().parents[1];SITE=ROOT/'site';OUT=ROOT/'reports/instagram-selection';OUT.mkdir(parents=True,exist_ok=True)
expected=json.loads((ROOT/'media/instagram-curated.json').read_text())
IDS=['v1','v2','v3','v4','v5','v6a','v6b','v08']
class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self,*a):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(SITE)))
threading.Thread(target=server.serve_forever,daemon=True).start();base=f'http://127.0.0.1:{server.server_port}/'
checks=[];errors=[]
def check(name,value,detail=None):
    checks.append({'name':name,'pass':bool(value),'detail':detail});print(('PASS 'if value else'FAIL ')+name,flush=True)
try:
    with sync_playwright()as p:
        browser=p.chromium.launch();context=browser.new_context(viewport={'width':1440,'height':1000},reduced_motion='reduce');page=context.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
        for ident in IDS:
            page.goto(base+f'entwuerfe/{ident}/index.html',wait_until='networkidle')
            gallery=page.locator('[data-live-instagram]');gallery.scroll_into_view_if_needed()
            gallery.locator('img').evaluate_all('(imgs)=>imgs.forEach(i=>i.loading="eager")');page.wait_for_timeout(200)
            hrefs=gallery.locator('[data-selected-instagram]').evaluate_all('(a)=>a.map(x=>x.getAttribute("href"))')
            check(ident+' exact six posts',hrefs==[x['permalink']for x in expected['items']],hrefs)
            loaded=gallery.locator('img').evaluate_all('(a)=>a.every(i=>i.complete&&i.naturalWidth>=240)')
            check(ident+' six original images load',loaded)
            check(ident+' full menu preserved',page.locator('.live-menu-item').count()==36)
            check(ident+' original logo preserved',page.locator('.original-brand img').count()==1)
            for width in [1440,390,320]:
                page.set_viewport_size({'width':width,'height':1000});gallery.scroll_into_view_if_needed();page.wait_for_timeout(70)
                check(ident+' no overflow '+str(width),page.evaluate('document.documentElement.scrollWidth<=innerWidth'))
                if ident=='v08'and width in [1440,390]:gallery.screenshot(path=str(OUT/f'gallery-{width}.png'))
            page.set_viewport_size({'width':1440,'height':1000})
        page.goto(base+'verwaltung/vorschau.html',wait_until='networkidle')
        page.locator('[data-control-tab=instagram]').click()
        check('Default displays six',page.locator('#ig-count').input_value()=='6')
        check('Four, six and eight available',page.locator('#ig-count option').evaluate_all('(a)=>a.map(x=>x.value)')==['4','6','8'])
        for value,count in [('4',4),('8',6),('6',6)]:
            page.locator('#ig-count').select_option(value)
            other=context.new_page();other.goto(base+'entwuerfe/v08/index.html',wait_until='networkidle')
            rows=other.locator('[data-selected-instagram]').evaluate_all('(a)=>a.map(x=>x.getAttribute("href"))')
            check('Setting '+value+' shows '+str(count)+' without duplicates',len(rows)==count and len(set(rows))==count)
            other.close()
        page.locator('[data-control-tab=news]').click();page.locator('summary').first.click()
        check('Six photographs available in the news image picker',page.locator('select[data-image] option[value^="assets/instagram-selected/"]').count()==6)
        page.goto(base+'verwaltung/instagram-auswahl.html',wait_until='networkidle')
        check('Independent selection sheet shows all six',page.locator('.selected-photos article').count()==6)
        check('Selection sheet images load',page.locator('img').evaluate_all('(a)=>a.every(i=>i.complete&&i.naturalWidth>0)'))
        page.screenshot(path=str(OUT/'selected-photos-page.png'),full_page=True)
        page.goto(base+'index.html',wait_until='networkidle')
        check('Exactly eight original design options',page.locator('[data-proposal]').evaluate_all('(a)=>a.map(x=>x.dataset.proposal)')==IDS)
        # An older local preview must refresh only the gallery, not discard edited menu text.
        old=page.evaluate('null')
        page.goto(base+'verwaltung/vorschau.html',wait_until='networkidle')
        page.evaluate("""()=>{const state=VdeReview.state();state.sections[0].items[0].name='Preserved local edit';delete state.instagram.selection_id;state.instagram.items=[{image:'assets/bar.webp',alt:'Old gallery'}];state.instagram.count=4;localStorage.setItem(VdeReview.KEY,JSON.stringify(state));}""")
        page.goto(base+'entwuerfe/v3/index.html',wait_until='networkidle')
        check('Old gallery is replaced by the exact selected six',page.locator('[data-selected-instagram]').count()==6)
        check('Local menu edits survive gallery update',page.locator('.live-menu-item',has_text='Preserved local edit').count()==1)
        check('No browser errors',not errors,errors);browser.close()
finally:server.shutdown()
report={'selection_id':expected['selection_id'],'checks':checks,'passed':all(c['pass']for c in checks),'errors':errors}
(OUT/'checks.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
if not report['passed']:raise SystemExit(1)
