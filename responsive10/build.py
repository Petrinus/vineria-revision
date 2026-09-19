"""Replace only model 10 and its matching shop. Do not publish raster mockups as UI."""
from pathlib import Path
from bs4 import BeautifulSoup
from PIL import Image,ImageDraw,ImageFilter
import html,json,copy,hashlib,runpy,shutil
R=Path(__file__).resolve().parents[1];S=R/'site';A=S/'assets';P=A/'responsive10';E=html.escape

def parse(s):return BeautifulSoup(s,'html.parser')
def rel(target,page):
 import posixpath
 return posixpath.relpath(target,posixpath.dirname(page)or'.')
def image(name,page,alt='',cls='',extra=''):
 path='assets/responsive10/'+name
 im=Image.open(S/path);w,h=im.size
 return f'<img class="{cls}" src="{rel(path,page)}" alt="{E(alt)}" width="{w}" height="{h}" decoding="async" {extra}>'
def bar(page):
 return '<div class="proposal-nav"><a href="'+rel('index.html',page)+'">← Alle Entwürfe</a><span>Entwurf 10 · Papier & Grafik</span><nav aria-label="Entwurfsansichten"><a href="'+rel('entwuerfe/v10/index.html',page)+'">Restaurant</a><a href="'+rel('entwuerfe/v10/shop/index.html',page)+'">Tienda</a><a href="'+rel('verwaltung/vorschau.html',page)+'">Verwaltung</a></nav></div>'
def header(page):
 home=rel('entwuerfe/v10/index.html',page);shop=rel('entwuerfe/v10/shop/index.html',page)
 links=''.join(f'<a href="{home}#{anchor}">{label}</a>'for anchor,label in [('restaurant','Restaurant'),('speisekarte','Speisekarte'),('weine','Weine')])
 links+=f'<a href="{shop}">Shop</a><a href="{home}#vineria">Über uns</a><a href="{home}#besuch">Kontakt</a>'
 return '<header class="v10-header"><a class="v10-brand" href="'+home+'">'+image('wordmark.png',page,'Vinería del Este · Wein, Tapas, Gente')+'</a><button type="button" class="v10-menu-toggle" aria-controls="v10-navigation" aria-expanded="false">Menü <span aria-hidden="true">☰</span></button><nav class="v10-navigation" id="v10-navigation" aria-label="Hauptnavigation">'+links+'<a class="v10-reserve" href="https://vineriaytapas.de/#tebi-reservations" target="_blank" rel="noopener">Reservieren <span aria-hidden="true">→</span></a></nav></header>'
def footer(page):
 home=rel('entwuerfe/v10/index.html',page);service=rel('entwuerfe/v10/service/index.html',page)
 links=''.join(f'<a href="{service}#{tag}">{name}</a>'for tag,name in [('impressum','Impressum'),('datenschutz','Datenschutz'),('agb','AGB'),('versand','Versand & Abholung'),('widerruf','Widerruf')])
 return '<footer class="v10-footer"><div class="v10-foot-main"><div class="v10-foot-greeting">Hasta<br>pronto.<span aria-hidden="true">✳</span></div><div><h2>Adresse</h2><p>Bänschstraße 41<br>10247 Berlin</p></div><div><h2>Öffnungszeiten</h2><p>Di–Do ab 16 Uhr<br>Fr–Sa ab 15 Uhr<br>So 12–18 Uhr · Mo geschlossen</p></div><div><h2>Kontakt</h2><p><a href="tel:+493042024943">+49 30 42024943</a><br><a href="mailto:vineriadeleste@gmail.com">vineriadeleste@gmail.com</a></p><a href="'+home+'#events">Catering & Gruppen ↗</a></div><a class="v10-social" href="https://www.instagram.com/vineria.del.este/" target="_blank" rel="noopener" aria-label="Vineria auf Instagram"><svg viewBox="0 0 32 32" width="38" height="38" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><rect x="4" y="4" width="24" height="24" rx="7"/><circle cx="16" cy="16" r="6"/><circle cx="23" cy="9" r="1" fill="currentColor"/></svg></a></div><div class="v10-foot-bottom"><nav aria-label="Service">'+links+'</nav><a href="'+rel('verwaltung/vorschau.html',page)+'">Team · Verwaltung</a><span>VINERIA DEL ESTE · BERLIN</span></div><p class="v10-demo-note">Designvorschau · kein aktiver Verkauf. Die Verwaltung speichert Teständerungen nur in diesem Browser.</p></footer>'
def heading():return '<h1 class="v10-title"><span>Wein.</span><span>Tapas.</span><span>Leben.</span></h1>'
def hero(page):
 return '<section class="v10-hero" id="restaurant"><figure class="v10-photo">'+image('good-wine.png',page,'Guter Wein, bessere Gespräche','v10-handnote')+image('toast-photo.png',page,'Gemeinsam am Tisch in der Bildvorlage','v10-toast','fetchpriority="high"')+'<figcaption><span>BÄNSCHSTRASSE 41</span><span>BERLIN</span></figcaption></figure><div class="v10-hero-copy">'+heading()+'<div class="v10-mark" aria-hidden="true"><i></i><span>✳</span></div><p>Ein Ort für gute Produkte,<br>ehrliche Küche und inspirierende Begegnungen. Spanien im Herzen,<br>Berlin im Alltag.</p><div class="v10-actions"><a class="v10-button" href="#speisekarte">Speisekarte ansehen</a><a class="v10-button outline" href="https://vineriaytapas.de/#tebi-reservations" target="_blank" rel="noopener">Tisch reservieren</a></div></div><aside class="v10-wine"><a class="v10-wine-paper" href="shop/index.html" aria-label="Unsere Tienda entdecken">'+image('wine-paper.png',page,'Buen vino, buena compañía · Tienda, Produkte aus Spanien','', 'fetchpriority="high"')+'</a>'+image('salud.png',page,'¡Salud!','v10-salud')+'<a class="v10-small-link" href="#events">Catering & große Gruppen ↗</a></aside></section>'
def shortcuts(page):
 content=[('Unser Restaurant','Kleine Gerichte, große Weine und ein Stück Spanien in Berlin. Ein lebendiger Ort zum Teilen, Genießen und Wiederkommen.','Mehr erfahren','#vineria','olives.png'),('Speisekarte','Saisonale Tapas, Klassiker und besondere Weine. Unsere vollständige Auswahl an einem Ort.','Zur Karte','#speisekarte','herbs.png'),('Shop','Spanische Produkte für zu Hause. Wein, Konserven, Spezialitäten und mehr.','Zum Shop','shop/index.html','conservas.png')]
 return '<section class="v10-shortcuts" aria-label="Die Vineria entdecken">'+''.join('<article><div><h2>'+title+'</h2><p>'+text+'</p><a href="'+href+'">'+label+' <span aria-hidden="true">→</span></a></div>'+image(img,page,'','', 'loading="lazy"')+'</article>'for title,text,label,href,img in content)+'</section>'
def seed_script(data,page):
 cfg={'root':rel('index.html',page).removesuffix('index.html'),'shop':rel('entwuerfe/v10/shop/index.html',page),'content':data}
 return '<script id="vde-content-seed" type="application/json">'+json.dumps(cfg,ensure_ascii=False).replace('<','\\u003c')+'</script>'
def head(title,page):
 return '<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow,noarchive"><title>'+E(title)+'</title>'+''.join('<link rel="stylesheet" href="'+rel('assets/'+c,page)+'">'for c in ['site.css','content.css','proposal-chrome.css','responsive10.css'])
def build():
 P.mkdir(exist_ok=True)
 src=Image.open(A/'lab/reference-original.png').convert('RGBA');mask=Image.new('L',src.size,0)
 pts=[(0,337),(56,323),(142,333),(215,350),(276,351),(274,185),(337,171),(501,135),(553,148),(551,292),(568,533),(584,708),(596,802),(565,826),(494,843),(409,831),(346,850),(243,854),(165,852),(81,856),(0,835)]
 ImageDraw.Draw(mask).polygon(pts,fill=255);src.putalpha(mask.filter(ImageFilter.GaussianBlur(.4)));src.crop(src.getchannel('A').getbbox()).save(P/'toast-photo.png',optimize=True)
 data=json.loads((A/'review-content.json').read_text());old=parse((S/'entwuerfe/v10/index.html').read_text());old_seed=old.select_one('#vde-content-seed')
 if old_seed:data=json.loads(old_seed.string)['content']
 mapurl=json.loads((A/'catalog.json').read_text())['map']
 helpers=runpy.run_path(str(R/'design-lab/build.py'))
 old_hashes={str(p.relative_to(S)):hashlib.sha256(p.read_bytes()).hexdigest()for p in (S/'entwuerfe').rglob('*.html')if '/v10/'not in str(p)}
 page='entwuerfe/v10/index.html'
 markup=hero(page)+shortcuts(page)+'<section class="v10-news" data-live-news></section>'
 markup+=helpers['menu'](data)+helpers['about'](page)
 markup+='<section class="v10-shop-invite"><div>'+image('bottle-ink.png',page,'Botella, copa y lettering originales sin fondo','', 'loading="lazy"')+'</div><div><p class="eyebrow">TIENDA · PRODUCTOS ESPAÑOLES</p><h2>Un poquito de aquí.<br>Für zu Hause.</h2><p>Euch gefällt unsere Auswahl? Einige unserer Weine und spanischen Spezialitäten gibt es auch in unserer Tienda. Zum Mitbringen, Aufmachen und Teilen.</p><a class="v10-button" href="shop/index.html">Unsere Tienda entdecken →</a></div></section>'
 markup+=helpers['contact'](page,mapurl)+helpers['EVENTS']+'<section id="instagram" data-live-instagram></section>'
 js=''.join('<script defer src="'+rel('assets/'+f,page)+'"></script>'for f in ['content-engine.js','responsive10-ui.js'])
 full='<!DOCTYPE html><html lang="de"><head>'+head('Vineria del Este · Modell 10 · Papier, Wein & Tapas',page)+seed_script(data,page)+js+'</head><body class="v10-layout"><a class="skip" href="#main">Zum Inhalt</a>'+bar(page)+header(page)+'<main id="main">'+markup+'</main>'+footer(page)+'</body></html>'
 (S/page).write_text(full)
 changed=[page]
 for p in (S/'entwuerfe/v10').rglob('*.html'):
  if p==S/page:continue
  page2=p.relative_to(S).as_posix();s=parse(p.read_text());s.body['class']=['v10-layout','v10-shop']
  for e in list(s.select('link[rel=stylesheet],style')):e.decompose()
  for c in ['site.css','content.css','proposal-chrome.css','responsive10.css']:s.head.append(s.new_tag('link',rel='stylesheet',href=rel('assets/'+c,page2)))
  for el in list(s.select('.proposal-nav,header,footer')):el.decompose()
  for el in reversed(list(parse(bar(page2)+header(page2)).contents)):s.body.insert(0,el)
  for el in list(parse(footer(page2)).contents):s.body.append(el)
  for script in list(s.find_all('script',src=True)):
   name=script['src'].split('?')[0].rsplit('/',1)[-1]
   if name not in ['content-engine.js','site.js']:script.decompose()
  s.head.append(s.new_tag('script',src=rel('assets/responsive10-ui.js',page2),defer=''))
  if page2.endswith('/shop/index.html'):
   h=s.select_one('.lab-shop-lead,.shop-hero,.v10-store-hero')
   assert h is not None,'Missing shop hero container'
   h.clear();h['class']=['v10-store-hero']
   fragment='<div><p class="eyebrow">VINERIA DEL ESTE · TIENDA</p><h1>Ein Stück Spanien.<br>Für Deinen Tisch.</h1><p>Weine, Konserven und gute Dinge zum Teilen. Die Auswahl aus unserer Vineria für zu Hause.</p><a href="#sortiment" class="v10-button">Auswahl entdecken ↓</a></div>'+image('bottle-ink.png',page2,'Botella y copa · dibujo original sin papel','', 'fetchpriority="high"')
   for el in list(parse(fragment).contents):h.append(el)
  p.write_text(str(s));changed.append(page2)
 for name in ['responsive10.css','responsive10-ui.js']:shutil.copyfile(R/'responsive10'/name,A/name)
 index=parse((S/'index.html').read_text());card=index.select_one('[data-proposal="v10"]')
 if card:
  for label in card.select('h2,h3'):
   if '10'not in label.get_text():label.string='Papier & Grafik'
  paragraphs=card.find_all('p')
  if paragraphs:paragraphs[-1].string='Freigestellte Originalgrafiken, echte Texte und responsive Seiten. Restaurant und Tienda im gleichen Papier-Look.'
 (S/'index.html').write_text(str(index))
 assert all(hashlib.sha256((S/name).read_bytes()).hexdigest()==sha for name,sha in old_hashes.items()),'Other models changed'
 report={'model':'v10','html_pages_updated':len(changed),'other_models_unchanged':True,'new_models':0,'implementation':'semantic responsive HTML + separate transparent PNG artwork, not a tiled image','modals_removed':True,'live_menu_items':sum(len(c['items'])for c in data['sections']),'products':len(data['products']),'fonts':'Live headlines and controls use locally served fonts or system fallbacks. Not a certified original font identification.'}
 out=R/'reports/responsive10';out.mkdir(parents=True,exist_ok=True);(out/'build.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report))
if __name__=='__main__':build()
