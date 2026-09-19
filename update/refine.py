"""Refine public preview pages. No server, account, security or payment changes."""
from pathlib import Path
from bs4 import BeautifulSoup
from PIL import Image
import numpy as np,re
ROOT=Path(__file__).resolve().parents[1];SITE=ROOT/'site';A=SITE/'assets'
p=A/'approved/logo.webp'
im=Image.open(p).convert('RGBA');arr=np.array(im)
nearwhite=np.min(arr[:,:,:3],axis=2).astype(float)
arr[:,:,3]=np.uint8(np.clip((255-nearwhite)*255/22,0,255))
Image.fromarray(arr).save(p,lossless=True)
for page in SITE.rglob('*.html'):
    soup=BeautifulSoup(page.read_text(),'html.parser')
    match=re.search(r'/entwuerfe/(v[1-5]|v6[ab]|v08)/',str(page))
    if match and soup.body:
        soup.body['data-vde-style']=match[1]
    # The old local-preview UI expects HTML removed by the replacement editor.
    # Remove its duplicate script tag, including any cache query string.
    if soup.select_one('#vde-control'):
        for script in list(soup.find_all('script',src=True)):
            filename=script['src'].split('?',1)[0].rsplit('/',1)[-1]
            if filename=='management-preview.js':
                script.decompose()
    page.write_text(str(soup).replace('viewbox=','viewBox=').replace('preserveaspectratio=','preserveAspectRatio='))
p=A/'site.js'
js=p.read_text().replace('../shop/${x.id}/index.html','../shop/produkt/index.html?id=${encodeURIComponent(x.id)}')
p.write_text(js)
css='''
@media(max-width:720px){body[data-vde-style="v2"] .nav,body[data-vde-style="v3"] .nav,body[data-vde-style="v4"] .nav{flex-wrap:wrap;justify-content:space-between;padding-block:13px;gap:10px}body[data-vde-style="v2"] .navlinks,body[data-vde-style="v3"] .navlinks,body[data-vde-style="v4"] .navlinks{max-width:100%;flex-wrap:wrap;gap:10px}body[data-vde-style="v2"] .original-brand,body[data-vde-style="v3"] .original-brand,body[data-vde-style="v4"] .original-brand{width:190px!important;max-width:100%!important}}
.model08 .statement{width:calc(100% - 32px);margin-inline:16px}.model08 .intro:has(.dish-print){position:relative;padding-bottom:100px}.model08 .intro>.dish-print{position:absolute;right:15px;bottom:0;width:145px;max-height:145px}
.model08 .collage-hero:before{inset:-30px 0 -25px}
'''
with (A/'content.css').open('a')as f:
    f.write(css)
