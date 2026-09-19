"""Read-only verification of the actual public proposal portal."""
from pathlib import Path
from playwright.sync_api import sync_playwright
import json,time
BASE='https://raw.githack.com/Petrinus/vineria-revision/main/site/'
OUT=Path('reports/proposals');OUT.mkdir(parents=True,exist_ok=True)
report={'url':BASE+'index.html','checked_at':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'pairs':[],'provider_confirmation_required':False}
with sync_playwright() as pw:
    browser=pw.chromium.launch()
    ctx=browser.new_context(viewport={'width':1440,'height':1000},reduced_motion='reduce')
    page=ctx.new_page()
    def visit(path,selector):
        response=page.goto(BASE+path,wait_until='networkidle',timeout=60000)
        consent=page.get_by_role('button',name='Open the page',exact=True)
        if consent.count():
            report['provider_confirmation_required']=True
            consent.click()
            page.wait_for_load_state('networkidle',timeout=60000)
        report['last_page']={'url':page.url,'title':page.title(),'text':page.locator('body').inner_text()[:1200]}
        page.wait_for_selector(selector,timeout=20000)
        return response.status
    try:
        visit('index.html','#proposal-catalogue')
        report['title']=page.title()
        report['equal_cards']=page.locator('.idea').count()
        report['password_fields']=page.locator('input[type=password]').count()
        report['shared_management_link']=page.locator('a[href="verwaltung/index.html"]').count()
        report['preferred_designs']=page.locator('.current,.recommended,.ribbon').count()
        page.locator('img').evaluate_all('(xs)=>xs.forEach(x=>x.loading="eager")')
        page.wait_for_timeout(1200)
        page.screenshot(path=str(OUT/'public-selector.png'),full_page=True)
        for ident in ['v1','v2','v3','v4','v5','v6a','v6b']:
            record={'id':ident}
            record['restaurant_status']=visit(f'entwuerfe/{ident}/index.html','.proposal-nav')
            record['restaurant_title']=page.title()
            record['decorative_star_count']=page.locator('.scene-star').count()
            record['restaurant_to_shop']=page.locator('.proposal-nav a').filter(has_text='Tienda').get_attribute('href')
            record['shop_status']=visit(f'entwuerfe/{ident}/shop/index.html','.product-card')
            record['product_count']=page.locator('.product-card').count()
            record['shop_title']=page.title()
            report['pairs'].append(record)
        report['management_status']=visit('verwaltung/index.html','#admin-entry')
        report['management_password_disabled']=page.locator('input[type=password]').is_disabled()
        visit('verwaltung/vorschau.html','.edit-row')
        report['management_preview_rows']=page.locator('.edit-row').count()
    except Exception as e:
        report['error']=str(e)
        report['failed_page']={'url':page.url,'title':page.title(),'text':page.locator('body').inner_text()[:2000]}
        page.screenshot(path=str(OUT/'public-error.png'),full_page=True)
    browser.close()
report['verified']=report.get('equal_cards')==7 and len(report['pairs'])==7 and all(r.get('product_count')==11 and r.get('decorative_star_count')==0 for r in report['pairs']) and report.get('management_password_disabled') is True and not report.get('error')
(OUT/'public-catalogue-check.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps(report,ensure_ascii=False,indent=2))
if not report['verified']:raise SystemExit(1)
