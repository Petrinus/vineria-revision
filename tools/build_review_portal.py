"""Independent review portal. Does not modify restaurant/shop designs or activate authentication."""
from pathlib import Path
from html import escape
import json,shutil,os
R=Path(os.environ.get('VDE_OUTPUT','site'));R.mkdir(exist_ok=True)
ROOT=Path(__file__).resolve().parent.parent
T=ROOT/'review'
if not T.exists():
 print('Review-only templates absent; skip public comparison portal.');raise SystemExit(0)
ideas=[
 {'id':'fanzine','label':'06A','name':'Fanzine · Papier & Schwarz','summary':'Fotokopie und unregelmäßige Bildkanten. Restaurant und Tienda bilden ein zusammengehörendes Designpaar.','restaurant':'../index.html','shop':'../shop/index.html','previewRestaurant':'../assets/portal-fanzine-restaurant.jpg','previewShop':'../assets/portal-fanzine-shop.jpg'},
 {'id':'editorial','label':'06B','name':'Editorial · Creme & Wein','summary':'Warme Farben, ruhige Typografie und mehr fotografische Fläche. Dieselbe Formensprache in Restaurant und Tienda.','restaurant':'../editorial/index.html','shop':'../editorial/shop/index.html','previewRestaurant':'../assets/portal-editorial-restaurant.jpg','previewShop':'../assets/portal-editorial-shop.jpg'}
]
for p in sorted((R/'propuestas').glob('*/idea.json')) if (R/'propuestas').exists() else []:
 d=json.loads(p.read_text());slug=p.parent.name
 if not all((p.parent/x).is_file() for x in ['index.html','shop/index.html']):continue
 d.update(restaurant=f'../propuestas/{slug}/index.html',shop=f'../propuestas/{slug}/shop/index.html')
 ideas.append(d)
# Existing executed browser captures are only thumbnails; links always open the actual paired pages.
for theme,prefix in [('fanzine',''),('editorial','editorial-')]:
 for area,stem in [('restaurant',prefix+'index-1440.png'),('shop',prefix+'shop-index-1440.png')]:
  target=R/'assets'/f'portal-{theme}-{area}.jpg';source=ROOT/'reports'/stem
  if source.exists():
   from PIL import Image
   im=Image.open(source).convert('RGB');im=im.crop((0,0,im.width,min(im.height,round(im.width/.72))));im.thumbnail((720,1000));im.save(target,quality=82)
  elif not target.exists():
   from PIL import Image
   im=Image.new('RGB',(720,480),'#edeae2');im.save(target,quality=80)
cards=[]
for d in ideas:
 E=escape; rid=E(d['id']);r=E(d['restaurant']);s=E(d['shop'])
 cards.append(f'''<article class="idea" data-idea-card="{rid}"><div class="idea-head"><span class="idea-id">IDEE {E(d['label'])}</span><span class="idea-id">Restaurant + Tienda</span></div><h2>{E(d['name'])}</h2><div class="paired"><a class="mini" href="{r}" data-idea="{rid}" data-open="restaurant"><img src="{E(d['previewRestaurant'])}" alt="Restaurant · {E(d['name'])}" loading="lazy"><span>Restaurant <b>↗</b></span></a><a class="mini" href="{s}" data-idea="{rid}" data-open="shop"><img src="{E(d['previewShop'])}" alt="Tienda · {E(d['name'])}" loading="lazy"><span>Tienda <b>↗</b></span></a></div><p>{E(d['summary'])}</p><div class="actions"><a class="btn" href="{r}" data-idea="{rid}" data-open="pair">Beide zusammen ansehen</a><a class="btn light" href="{r}" target="_blank" rel="noopener">Restaurant ↗</a><a class="btn light" href="{s}" target="_blank" rel="noopener">Tienda ↗</a><a class="btn light" href="../verwaltung/vorschau.html" data-idea="{rid}" data-open="management">Verwaltung</a></div></article>''')
portal=(T/'portal.html').read_text().replace('__IDEA_CARDS__',''.join(cards)).replace('__IDEAS_JSON__',json.dumps(ideas,ensure_ascii=False).replace('<','\\u003c'))
(R/'entwuerfe').mkdir(exist_ok=True);(R/'entwuerfe/index.html').write_text(portal)
D=json.loads((ROOT/'src/catalog.json').read_text());D={'menu':D['menu'],'products':[{k:p[k] for k in ['name','price','category','pack']} for p in D['products']]}
admin=(T/'management.html').read_text().replace('__CATALOG_JSON__',json.dumps(D,ensure_ascii=False).replace('<','\\u003c'))
(R/'verwaltung').mkdir(exist_ok=True);(R/'verwaltung/vorschau.html').write_text(admin)
(R/'entwuerfe/ideen.json').write_text(json.dumps({'selected':None,'ranking':False,'management':'../verwaltung/vorschau.html','ideas':ideas},ensure_ascii=False,indent=2))
print('PORTAL:',len(ideas),'paired ideas; no selected winner; one shared management demo.')
