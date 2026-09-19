"""Preserve every proposal; pair each restaurant with a matching shop.
The review portal contains no active credentials, accounts or payment backend.
"""
from pathlib import Path
from bs4 import BeautifulSoup
import base64, copy, html, json, lzma, os, posixpath, re

R=Path(os.environ.get('VDE_OUTPUT','site'))
SRC=Path('src/proposals')
ORIG=json.loads(lzma.decompress(base64.b64decode((SRC/'originals.xz.txt').read_text())))
CONFIG=[
 dict(id='v1',num='01',title='Klassisch & ruhig',detail='Creme, Bordeaux und weiche Formen. Eine klare, zurückhaltende Gestaltung.',paper='#f6f1e7',ink='#522630',accent='#542631',soft='#e7dfcd',radius='28px'),
 dict(id='v2',num='02',title='Editorial & großzügig',detail='Große Überschriften, feine Linien und mehr Raum für Karte und Bilder.',paper='#f4eedf',ink='#35281f',accent='#752c35',soft='#e8dfcd',radius='0'),
 dict(id='v3',num='03',title='Kunst & Farbe',detail='Die farbige Grafikstudie mit spanischen Akzenten und einer expressiven Bildsprache.',paper='#f5f0e4',ink='#242c29',accent='#923b4e',soft='#e5e9dc',radius='0'),
 dict(id='v4',num='04',title='Kunst & deutsche Texte',detail='Die künstlerische Gestaltung mit Deutsch als Hauptsprache und wenigen spanischen Akzenten.',paper='#f5f0e4',ink='#242c29',accent='#923b4e',soft='#e5e9dc',radius='0'),
 dict(id='v5',num='05',title='Restaurant & Tienda',detail='Die warme, künstlerische Linie mit der Tienda als festem Teil des Restaurantauftritts.',paper='#f5f0e4',ink='#242c29',accent='#923b4e',soft='#e5e9dc',radius='0'),
 dict(id='v6a',num='06A',title='Fanzine & Fotokopie',detail='Schwarzweiß, Papierkanten und transparente Fotocollagen mit ruhigem Bilderwechsel.',paper='#f7f6f1',ink='#171717',accent='#171717',soft='#e8e7e1',radius='0'),
 dict(id='v6b',num='06B',title='Fotografie & warme Töne',detail='Die Alternative mit Originalfotos, Creme und Weinrot. Gleicher Aufbau für Restaurant und Tienda.',paper='#f5f0e4',ink='#352b27',accent='#89354b',soft='#e6e9dd',radius='0')
]
CAT=json.loads((R/'assets/catalog.json').read_text())

def rel(target,page):
 return posixpath.relpath(target,posixpath.dirname(page) or '.')

def parse(s):return BeautifulSoup(s,'html.parser')

def fix_svg(s):
 for old,new in [('viewbox','viewBox'),('basefrequency','baseFrequency'),('numoctaves','numOctaves'),('xchannelselector','xChannelSelector'),('ychannelselector','yChannelSelector'),('patternunits','patternUnits'),('patterntransform','patternTransform')]:
  s=s.replace(old+'=',new+'=')
 return s.replace('<feturbulence','<feTurbulence').replace('</feturbulence','</feTurbulence').replace('<fedisplacementmap','<feDisplacementMap').replace('</fedisplacementmap','</feDisplacementMap')

def no_stars(s):
 for e in list(s.select('.scene-star')):e.decompose()
 for e in list(s.find_all(['i','b','span'])):
  if e.get_text(strip=True) in ['✳','✳️','✴','✴️','★','☆']:e.decompose()
 return s

def review_nav(page,ident=None):
 cfg=next((x for x in CONFIG if x['id']==ident),None)
 label='Entwurf '+cfg['num'] if cfg else 'Projektübersicht'
 main=rel('index.html',page); admin=rel('verwaltung/index.html',page)
 rest=rel(f'entwuerfe/{ident}/index.html',page) if cfg else None
 shop=rel(f'entwuerfe/{ident}/shop/index.html',page) if cfg else None
 return f'''<div class="proposal-nav"><a href="{main}">← Alle Entwürfe</a><span>{label}</span><nav aria-label="Entwurfsansichten">{f'<a href="{rest}">Restaurant</a><a href="{shop}">Tienda</a>' if cfg else ''}<a href="{admin}">Verwaltung</a></nav></div>'''

def put(page,s,ident=None):
 s=no_stars(s)
 for e in s.select('.proposal-nav'):e.decompose()
 # Replace review-only header bars, never restaurant content.
 for selector in ['.review','.review-bar','.draft','.statusbar']:
  e=s.select_one(selector)
  if e:e.decompose()
 if s.body:s.body.insert(0,parse(review_nav(page,ident)))
 for m in s.select('meta[name=robots]'):m['content']='noindex,nofollow,noarchive'
 if s.html:s.html['lang']='de'
 if not s.select_one('link[data-proposal-chrome]'):
  e=s.new_tag('link',rel='stylesheet',href=rel('assets/proposal-chrome.css',page));e['data-proposal-chrome']='';s.head.append(e)
 p=R/page;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(fix_svg(str(s)))

# Snapshot the existing integrated themes before root becomes the catalogue.
ROOT_HTML=(R/'index.html').read_text()
if 'id="proposal-catalogue"' in ROOT_HTML:
 ROOT_HTML=(R/'fanzine/index.html').read_text()
ROOT_SOUP=parse(ROOT_HTML)
shop_pages={}
for folder in ['shop','warenkorb','checkout','service']:
 for p in (R/folder).rglob('*.html'):shop_pages[p.relative_to(R).as_posix()]=p.read_text()
editorial_pages={p.relative_to(R/'editorial').as_posix():p.read_text() for p in (R/'editorial').rglob('*.html')}


def rewrite_integrated(text,oldpage,newpage,base,editorial=False):
 s=parse(text);old_dir=posixpath.dirname(oldpage)
 def rewrite(value):
  if not value or value.startswith(('#','http:','https:','data:','mailto:','tel:','javascript:')):return value
  path,mark,frag=value.partition('#');path,qmark,query=path.partition('?')
  resolved=posixpath.normpath(posixpath.join(old_dir,path))
  if resolved.startswith('editorial/'):resolved=resolved[len('editorial/'):]
  if resolved.startswith('assets/'):target=resolved
  elif resolved.startswith('verwaltung/'):target=resolved
  elif resolved.startswith('entwuerfe/'):target='index.html'
  elif resolved in ['.','index.html']:target=base+'/index.html'
  elif resolved.startswith(('shop/','checkout/','warenkorb/','service/')):target=base+'/'+resolved
  else:return value
  return rel(target,newpage)+(qmark+query if qmark else '')+(mark+frag if mark else '')
 for e in s.find_all(True):
  for a in ['href','src','action']:
   if e.has_attr(a):e[a]=rewrite(e[a])
 for e in s.find_all('script'):
  raw=e.string or ''
  if raw.startswith('window.VDE='):
   d=json.loads(raw[len('window.VDE='):].rstrip(';'))
   d['root']=rel(base+'/index.html',newpage).removesuffix('index.html')
   d['home']=rel(base+'/index.html',newpage);d['shop']=rel(base+'/shop/index.html',newpage)
   e.string='window.VDE='+json.dumps(d,ensure_ascii=False)+';'
 return s

for cfg in CONFIG:
 ident=cfg['id'];base='entwuerfe/'+ident;page=base+'/index.html'
 if ident in ('v6a','v6b'):
  text=ROOT_HTML if ident=='v6a' else editorial_pages['index.html']
  old='index.html' if ident=='v6a' else 'editorial/index.html'
  s=rewrite_integrated(text,old,page,base,ident=='v6b')
 else:
  s=parse(ORIG[ident+'.html'])
  s.title.string='Vineria del Este · Entwurf '+cfg['num']+' · Restaurant'
  # Remove optional upload tools from the public historical previews.
  for e in s.select('.review-panel,.project,.draftnote'):e.decompose()
  shoplink='shop/index.html'
  for e in s.find_all('a',href=True):
   h=e['href']
   if 'google.com/maps' in h:e['href']=CAT['map']
   if any(x in h for x in ['tienda_gestion','tienda-v5','tienda.html']):
    e['href']=rel('verwaltung/index.html',page) if '#admin' in h else shoplink
  for e in s.select('[data-reserve]'):
   a=s.new_tag('a',href='https://vineriaytapas.de/#tebi-reservations',target='_blank',rel='noopener');a['class']=e.get('class',[]);a.string='Reservieren ↗';e.replace_with(a)
  header_nav=s.select_one('.navlinks,.nav-links')
  if header_nav and not any('shop' in a.get('href','') for a in header_nav.find_all('a')):
   a=s.new_tag('a',href=shoplink);a['class']=['pill'] if ident=='v1' else ['button'] if ident=='v2' else ['cta'];a.string='Unser Shop ↗';header_nav.append(a)
  # An elegant shared invitation, consistent with the existing palette.
  if not s.select_one('[data-paired-shop]'):
   teaser=parse(f'''<section class="paired-shop" data-paired-shop><div><p>VINERIA DEL ESTE · TIENDA</p><h2>Ein Stück Vineria.<br>Für zu Hause.</h2><p>Euch gefällt unsere Auswahl? Entdeckt einige unserer Weine und spanischen Spezialitäten in unserer Tienda.</p></div><a href="{shoplink}">Unser Shop entdecken ↗</a></section>''')
   s.main.append(teaser)
  style=s.new_tag('style');style.string=f'''.paired-shop{{margin:45px auto;width:min(1180px,calc(100% - 44px));padding:38px 0;border-top:1px solid {cfg['accent']};display:flex;align-items:center;justify-content:space-between;gap:35px;color:{cfg['ink']}}}.paired-shop h2{{font:normal 45px/1.05 Georgia,serif;letter-spacing:-.035em;margin:12px 0}}.paired-shop p{{max-width:510px;font:14px/1.8 Arial,sans-serif}}.paired-shop p:first-child{{font-size:10px;letter-spacing:.12em}}.paired-shop>a{{padding:14px 20px;border:1px solid {cfg['accent']};color:{cfg['accent']};text-decoration:none;white-space:nowrap;border-radius:{cfg['radius']}}}@media(max-width:650px){{.paired-shop{{display:block}}.paired-shop>a{{display:inline-block;margin-top:12px}}.paired-shop h2{{font-size:36px}}}}''';s.head.append(style)
 put(page,s,ident)
 # Build a complete matching shop, product pages, cart and checkout for every proposal.
 for sub,text in shop_pages.items():
  target=base+'/'+sub
  if ident=='v6b':
   text=editorial_pages[sub];old='editorial/'+sub
  else:old=sub
  st=rewrite_integrated(text,old,target,base,ident=='v6b')
  st.title.string=st.title.get_text()+' · Entwurf '+cfg['num']
  if ident not in ('v6a','v6b'):
   st.body['class']=['paired-store','skin-'+ident]
   sk=st.new_tag('style');sk.string=f'''body.paired-store{{--paper:{cfg['paper']};--ink:{cfg['ink']};--accent:{cfg['accent']};--soft:{cfg['soft']};--line:#d0c7b8;--muted:#655e54;background:var(--paper)}}.paired-store .btn{{background:var(--accent);border-color:var(--accent);border-radius:{cfg['radius']}}}.paired-store .btn.outline{{background:transparent;color:var(--accent)}}.paired-store .hero h1 em,.paired-store .footer-word{{color:var(--accent)}}.paired-store .hero h1{{font-family:Georgia,serif;font-weight:400;font-size:clamp(54px,6.8vw,102px)}}.paired-store .scene:before,.paired-store .tape,.paired-store .product-art:before{{display:none}}.paired-store .product-art{{background:var(--soft)}}.paired-store .abstract-pack{{box-shadow:none;transform:none;border-color:var(--accent)}}.paired-store .scene-sticker{{background:var(--accent)}}.paired-store .statement{{background:var(--accent)}}.paired-store .store-art{{max-height:430px;width:100%;height:100%;display:block}}.paired-store .store-editorial-note{{font:normal 56px/1.1 Georgia,serif;letter-spacing:-.045em;color:var(--accent);padding:45px;border:1px solid var(--line);max-width:430px}}.paired-store .store-editorial-note small{{font:11px/1.8 Arial,sans-serif;letter-spacing:.12em;display:block;margin-top:30px}}.paired-store .scene{{min-height:340px}}@media(max-width:700px){{.paired-store .hero h1{{font-size:58px}}.paired-store .scene{{min-height:250px;height:280px}}.paired-store .store-editorial-note{{font-size:42px;padding:24px}}}}''';st.head.append(sk)
   scene=st.select_one('.shop-hero .scene')
   if scene:
    scene.clear()
    art=s.select_one('svg.artwork')
    if art:
     art=copy.copy(art);art['class']=['store-art'];scene.append(art)
    else:
     scene.append(parse('<div class="store-editorial-note">Gut ausgesucht.<br>Gern geteilt.<small>WEIN & SPANISCHE SPEZIALITÄTEN</small></div>'))
  put(target,st,ident)

# Keep older public links usable, but root is always the neutral catalogue.
# Existing /shop bookmarks lead into Fanzine and never back to a different proposal.
for sub,text in shop_pages.items():
 s=rewrite_integrated(text,sub,sub,'entwuerfe/v6a')
 put(sub,s,'v6a')
# Retain the original editorial URL as a matching pair.
for sub,text in editorial_pages.items():
 s=rewrite_integrated(text,'editorial/'+sub,'editorial/'+sub,'entwuerfe/v6b',True)
 put('editorial/'+sub,s,'v6b')
# A durable dedicated address for the black-and-white restaurant.
p=R/'fanzine/index.html';p.parent.mkdir(exist_ok=True)
s=rewrite_integrated(ROOT_HTML,'index.html','fanzine/index.html','entwuerfe/v6a');put('fanzine/index.html',s,'v6a')

# A quiet shared navigation strip, separate from each design's identity.
(R/'assets/proposal-chrome.css').write_text('''
.proposal-nav{box-sizing:border-box;display:flex;align-items:center;justify-content:space-between;gap:16px;padding:10px 24px;background:#202020;color:#f8f7f4;font:11px/1.5 Arial,Helvetica,sans-serif;position:relative;z-index:30;letter-spacing:0}.proposal-nav a{color:inherit!important;text-decoration:none!important;font:inherit!important;border:0!important}.proposal-nav a:hover{text-decoration:underline!important}.proposal-nav nav{display:flex;gap:20px}.proposal-nav span{opacity:.7}.proposal-nav a:focus-visible{outline:2px solid #fff;outline-offset:3px}.scene-star{display:none!important}@media(max-width:600px){.proposal-nav{padding:9px 12px;font-size:10px;gap:8px;flex-wrap:wrap}.proposal-nav span{order:3}.proposal-nav nav{gap:14px}}
''')
# Static catalogue assets copied verbatim from reviewed source.
for name in ['catalogue.css','catalogue.js','management-preview.js']:
 (R/'assets'/name).write_text((SRC/name).read_text())


def portal(page):
 root=lambda p:rel(p,page)
 cards=[]
 for x in CONFIG:
  rest=root('entwuerfe/'+x['id']+'/index.html');shop=root('entwuerfe/'+x['id']+'/shop/index.html')
  cards.append(f'''<article class="idea" data-proposal="{x['id']}"><div class="pair-images"><a href="{rest}" aria-label="Entwurf {x['num']}: Restaurant öffnen"><img src="{root('assets/proposals/'+x['id']+'-restaurant.webp')}" alt="Restaurant – {x['title']}" width="720" height="500" loading="lazy"><span>Restaurant ↗</span></a><a href="{shop}" aria-label="Entwurf {x['num']}: Tienda öffnen"><img src="{root('assets/proposals/'+x['id']+'-shop.webp')}" alt="Tienda – {x['title']}" width="720" height="500" loading="lazy"><span>Tienda ↗</span></a></div><div class="idea-copy"><span class="number">ENTWURF {x['num']}</span><h2>{x['title']}</h2><p>{x['detail']}</p><div class="idea-links"><a class="button" href="{rest}">Restaurant</a><a class="button outline" href="{shop}">Tienda</a><button class="text-button" data-open-pair="{x['id']}">Beide ansehen ↓</button></div></div></article>''')
 data=[dict(id=x['id'],title='Entwurf '+x['num']+' · '+x['title'],restaurant=root('entwuerfe/'+x['id']+'/index.html'),shop=root('entwuerfe/'+x['id']+'/shop/index.html')) for x in CONFIG]
 admin=root('verwaltung/index.html');demo=root('verwaltung/vorschau.html')
 template=(SRC/'catalogue.html').read_text()
 for key,value in [('CARDS',''.join(cards)),('ADMIN',admin),('DEMO',demo),('CSS',root('assets/catalogue.css')),('JS',root('assets/catalogue.js')),('DATA',json.dumps(data,ensure_ascii=False))]:template=template.replace('{{'+key+'}}',value)
 p=R/page;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(template)
portal('index.html');portal('entwuerfe/index.html')
# Unified management has its own entry and remains outside all shop customer flows.
admin=(SRC/'management.html').read_text().replace('{{CSS}}','../assets/catalogue.css').replace('{{JS}}','../assets/management-preview.js')
(R/'verwaltung/index.html').write_text(admin)
(R/'verwaltung/vorschau.html').write_text(admin.replace('data-management-home','data-management-preview'))
(R/'assets/proposals.json').write_text(json.dumps(CONFIG,ensure_ascii=False,indent=2))
(R/'robots.txt').write_text('User-agent: *\nDisallow: /\n')
print('Proposal catalogue: 7 equal alternatives, 7 matching shops, 1 separate shared management. No decorative stars.')
