"""Small targeted corrections after the shared-content build, before browser QA."""
from pathlib import Path
from bs4 import BeautifulSoup
from PIL import Image
import numpy as np,re
ROOT=Path(__file__).resolve().parents[1];SITE=ROOT/'site';A=SITE/'assets'
# Preserve the provided original file; remove only the nearly white background in the display copy.
p=A/'approved/logo.webp';im=Image.open(p).convert('RGBA');arr=np.array(im);nearwhite=np.min(arr[:,:,:3],axis=2).astype(float);arr[:,:,3]=np.uint8(np.clip((255-nearwhite)*255/22,0,255));Image.fromarray(arr).save(p,lossless=True)
for page in SITE.rglob('*.html'):
 s=BeautifulSoup(page.read_text(),'html.parser');m=re.search(r'/entwuerfe/(v[1-5]|v6[ab]|v08)/',str(page))
 if m and s.body:s.body['data-vde-style']=m[1]
 for script in s.find_all('script'):
  text=script.string or ''
  # Old historical prototypes may still attach tabs outside the replaced menu.
  if not script.get('src') and script.get('type')!='application/json' and not text.startswith('window.VDE='):
   text=text.replace("document.getElementById(t.getAttribute('aria-controls')).hidden=!active","(()=>{const panel=document.getElementById(t.getAttribute('aria-controls'));if(panel)panel.hidden=!active;})()")
   if text!=(script.string or ''):script.string=text
 page.write_text(str(s).replace('viewbox=','viewBox=').replace('preserveaspectratio=','preserveAspectRatio='))
p=A/'site.js';js=p.read_text();js=js.replace('../shop/${x.id}/index.html','../shop/produkt/index.html?id=${encodeURIComponent(x.id)}');p.write_text(js)
css='''
/* Keep historical headers within narrow viewports without replacing their styles. */
@media(max-width:720px){body[data-vde-style="v2"] .nav,body[data-vde-style="v3"] .nav,body[data-vde-style="v4"] .nav{flex-wrap:wrap;justify-content:space-between;padding-block:13px;gap:10px}body[data-vde-style="v2"] .navlinks,body[data-vde-style="v3"] .navlinks,body[data-vde-style="v4"] .navlinks{max-width:100%;flex-wrap:wrap;gap:10px}body[data-vde-style="v2"] .original-brand,body[data-vde-style="v3"] .original-brand,body[data-vde-style="v4"] .original-brand{width:190px!important;max-width:100%!important}}
.model08 .statement{width:calc(100% - 32px);margin-inline:16px}.model08 .intro:has(.dish-print){position:relative;padding-bottom:100px}.model08 .intro>.dish-print{position:absolute;right:15px;bottom:0;width:145px;max-height:145px}
/* The paper texture alone may extend beyond the composition, not the content. */
.model08 .collage-hero:before{inset:-30px 0 -25px}
'''
with (A/'content.css').open('a')as f:f.write(css)
# Record the responsible page and stack on a browser error; do not suppress test failures.
p=ROOT/'update/qa.py';text=p.read_text().replace("lambda e:errors.append(str(e))","lambda e:errors.append({'url':page.url,'message':str(e),'stack':e.stack})")
old="extent=page.evaluate('({width:innerWidth,content:document.documentElement.scrollWidth})');check"
new="extent=page.evaluate('({width:innerWidth,content:document.documentElement.scrollWidth,overflow:Array.from(document.querySelectorAll(\"body *\")).filter(e=>{let r=e.getBoundingClientRect();return r.width>0&&(r.right>innerWidth+1||r.left<-1)}).slice(0,12).map(e=>({tag:e.tagName,cls:e.className,text:e.textContent.slice(0,60)}))})');check"
text=text.replace(old,new);p.write_text(text)
