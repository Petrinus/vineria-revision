"""Two explicitly requested proposals. Preserve eight old identities; share functionality."""
from pathlib import Path
from bs4 import BeautifulSoup
from PIL import Image
import copy,html,json,posixpath,re,shutil,hashlib
ROOT=Path(__file__).resolve().parents[1];SITE=ROOT/'site';A=SITE/'assets';LAB=A/'lab'
OLD=['v1','v2','v3','v4','v5','v6a','v6b','v08'];NEW={'v09':('09','Punk & Farbe'),'v10':('10','Die Bildvorlage')};ALL=OLD+list(NEW)
E=html.escape
def soup(text):return BeautifulSoup(text,'html.parser')
def rel(target,page):return posixpath.relpath(target,posixpath.dirname(page)or'.')
def image(name,page,alt='',cls='',extra=''):
 return f'<img src="{rel("assets/lab/"+name,page)}" alt="{E(alt)}" class="{cls}" {extra}>'
def append_markup(parent,text):
 for n in list(soup(text).contents):parent.append(n)
def include(s,page,name,kind='js'):
 if any(e.get('src','').split('?')[0].endswith('/'+name)for e in s.select('script[src]'))and kind=='js':return
 if any(e.get('href','').split('?')[0].endswith('/'+name)for e in s.select('link[href]'))and kind=='css':return
 el=s.new_tag('script',src=rel('assets/'+name,page),defer='')if kind=='js'else s.new_tag('link',rel='stylesheet',href=rel('assets/'+name,page));s.head.append(el)

EVENTS='''<section class="lab-events" id="events" data-common-events><p class="eyebrow">BESONDERE ANLÄSSE · CATERING · GROSSE RUNDE</p><h2>Ein Anlass.<br>Ein Tisch für Euch.</h2><p>Geburtstag, Firmenabend, eine große Runde oder spanische Spezialitäten für Eure Feier? Erzählt uns, was Ihr vorhabt. Wir melden uns per E-Mail oder Telefon, um alles Weitere zu besprechen.</p><p><a href="tel:+493042024943">Direkt anrufen: +49 30 42024943 ↗</a></p><details><summary>Event, Catering oder Gruppenreservierung anfragen ↓</summary><form data-events-form><label>Art der Anfrage<select name="type" required><option value="">Bitte auswählen</option><option>Catering</option><option>Große Gruppe / Gruppenreservierung</option><option>Private Feier im Restaurant</option><option>Firmenveranstaltung</option><option>Sonstiger Anlass</option></select></label><label>Kontaktname<input name="name" autocomplete="name" maxlength="100" required></label><label>Personenzahl<input name="people" type="number" min="1" max="999" required></label><label>Datum<input name="date" type="date" required></label><label>Uhrzeit · optional<input name="time" type="time"></label><label>Antwort bevorzugt<select name="reply"><option>Per E-Mail</option><option>Per Telefon</option><option>E-Mail oder Telefon</option></select></label><label>Kontakt-E-Mail<input name="email" type="email" autocomplete="email" maxlength="180" required></label><label>Telefon · optional<input name="phone" type="tel" autocomplete="tel" maxlength="50"></label><label class="full">Was habt Ihr vor?<textarea name="message" maxlength="4000" placeholder="Anlass, Ort, Wünsche, Allergien oder Fragen …"></textarea></label><p class="note full">Unverbindliche Anfrage. In dieser Vorschau wird Euer E-Mail-Programm geöffnet. Bitte dort prüfen und absenden; die Website versendet noch keine E-Mails automatisch.</p><button class="btn" type="submit">Anfrage als E-Mail öffnen ↗</button><p class="full" role="status" aria-live="polite"></p></form></details></section>'''

def menu(data):
 fallback=''.join('<h3>'+E(c['label'])+'</h3>'+''.join('<p>'+E(r['name'])+' · '+str(r['price']/100)+' €</p>'for r in c['items'])for c in data['sections'])
 return '<section class="lab-menu" id="speisekarte" data-complete-menu><div class="wrap"><div class="section-head"><div><p class="eyebrow">UNSERE GANZE KARTE</p><h2>Zum Teilen.<br>Zum Bleiben.</h2></div><p>Wochenkarte, unsere Klassiker und alle Weine. Die gesamte Auswahl an einem Ort.</p></div><button type="button" class="full-menu-control" data-full-menu aria-pressed="true">Nach Bereichen anzeigen</button><div data-live-menu>'+fallback+'</div></div></section>'
def about(page):
 return '<section class="lab-about wrap" id="vineria"><div class="lab-team-cutouts">'+image('owner-mono.webp',page,'Freigestellte Originalaufnahme aus der Vineria','owner', 'loading="lazy"')+image('portrait-mono.webp',page,'Freigestelltes Originalporträt aus der Vineria','portrait','loading="lazy"')+'<span>Menschen. Kein Konzept.</span></div><div><p class="eyebrow">DIE VINERIA · FRIEDRICHSHAIN</p><h2>Spanien im Herzen.<br>Berlin im Alltag.</h2><p>Kleine Teller, ausgesuchte Weine und die Menschen, mit denen man gerne noch ein bisschen bleibt. Ein Ort zum Teilen, Genießen und Wiederkommen.</p><p>Ein bisschen Spanien. Ein bisschen Uruguay. Und ganz viel Berlin.</p><a class="text-link" href="#events">Ein Abend mit Eurer Runde ↗</a></div></section>'
def contact(page,mapurl):
 return '<section class="lab-contact wrap" id="besuch"><div><p class="eyebrow">WIR SEHEN UNS IM KIEZ</p><h2>Komm vorbei.</h2><p>Bänschstraße 41<br>10247 Berlin</p><a class="btn outline" href="'+E(mapurl,quote=True)+'" target="_blank" rel="noopener">Route planen ↗</a><p><a href="tel:+493042024943">+49 30 42024943</a><br><a href="mailto:vineriadeleste@gmail.com">vineriadeleste@gmail.com</a></p></div><div><p class="eyebrow">ÖFFNUNGSZEITEN</p><div class="hours"><div><span>Dienstag–Donnerstag</span><span>ab 16 Uhr</span></div><div><span>Freitag–Samstag</span><span>ab 15 Uhr</span></div><div><span>Sonntag</span><span>12–18 Uhr</span></div><div><span>Montag</span><span>geschlossen</span></div></div><p>Küche Dienstag–Samstag bis ca. 22 Uhr.</p><a class="btn" href="https://vineriaytapas.de/#tebi-reservations" target="_blank" rel="noopener">Tisch reservieren ↗</a><p><a href="#events">Catering & große Gruppen →</a></p></div></section>'
def graphic_gallery(page,mono=False):
 labels=[('wine-shelf','Vino'),('asparagus','Espárragos'),('octopus','Pulpo'),('prawns','Gambas'),('paella','Paella'),('dessert','Algo dulce')]
 cards=''.join('<figure class="graphic-card">'+image(n+('-copy.webp'if mono else'-cut.webp'),page,t+' · Grafische Interpretation','', 'loading="lazy"')+'<figcaption><span>'+t+'</span><span>0'+str(i+1)+'</span></figcaption></figure>'for i,(n,t)in enumerate(labels))
 return '<section class="lab-graphics wrap" id="grafiken"><div class="lab-graphics-heading"><h2>Sechs kleine Geschichten.</h2><p class="gallery-art-note">Grafische Interpretationen der sechs ausgewählten Instagram-Fotos. Die Originalaufnahmen bleiben in der Galerie erhalten.</p></div><div class="graphic-cards">'+cards+'</div></section>'
def header(page,id):
 home=rel(f'entwuerfe/{id}/index.html',page);shop=rel(f'entwuerfe/{id}/shop/index.html',page)
 logo=image('wordmark.webp',page,'Vinería del Este')if id=='v10'else'<img src="'+rel('assets/approved/logo.webp',page)+'" alt="Vineria del Este · Vinos y Pintxos">'
 links=''.join('<a href="'+home+frag+'">'+label+'</a>'for frag,label in[('','Restaurant'),('#speisekarte','Speisekarte'),('#weine','Weine'),('#vineria','Über uns'),('#besuch','Kontakt')])
 return f'<header class="lab-header"><a class="lab-brand" href="{home}">{logo}</a><button type="button" class="lab-toggle" data-lab-toggle aria-controls="lab-nav" aria-expanded="false">Menü</button><nav class="lab-nav" id="lab-nav" aria-label="Hauptnavigation">{links}<a href="{shop}">Tienda</a><a href="https://vineriaytapas.de/#tebi-reservations" target="_blank" rel="noopener" class="nav-reserve">Reservieren ↗</a></nav></header>'
def footer(page,id):
 home=rel(f'entwuerfe/{id}/index.html',page);service=rel(f'entwuerfe/{id}/service/index.html',page)
 links=''.join(f'<a href="{service}#{tag}">{label}</a>'for tag,label in[('impressum','Impressum'),('datenschutz','Datenschutz'),('agb','AGB'),('versand','Versand & Abholung'),('widerruf','Widerruf & Retouren')])
 return '<footer class="footer"><div class="wrap"><div class="footer-top"><div><div class="footer-word">Hasta pronto.</div><p class="note">Vineria del Este · Bänschstraße 41 · 10247 Berlin<br>+49 30 42024943 · vineriadeleste@gmail.com</p></div><nav class="footer-links">'+links+f'<a href="{home}#events">Catering & große Gruppen</a><a href="{rel("verwaltung/vorschau.html",page)}">Team · Verwaltung</a></nav></div><div class="footer-bottom"><span>Modell {NEW[id][0]} · Designvorschau · keine aktiven Zahlungen</span><a href="{rel("index.html",page)}">Alle Entwürfe vergleichen ↗</a></div></div></footer>'
def punk_home(page,data,mapurl):
 frames=''.join(image(n+'-cut.webp',page,'Grafische Interpretation · '+n,'punk-food','data-art-frame '+('hidden'if i else'')+' width="1200" height="1200"')for i,n in enumerate(['octopus','asparagus','prawns','paella','dessert','wine-shelf']))
 hero='<section class="punk-hero"><div class="punk-copy"><span class="punk-kicker">VINERIA DEL ESTE · BERLIN</span><h1><span>Wein.</span><span>Tapas.</span><span>Leben.</span></h1><p>Gute Produkte. Ehrliche Küche. Lange Abende.<br>Spanien im Herzen, Friedrichshain vor der Tür.</p><div class="hero-actions"><a class="btn" href="#speisekarte">Die ganze Karte ↓</a><a class="btn outline" href="shop/index.html">Unsere Tienda ↗</a></div></div><div class="punk-stage" data-art-slider>'+frames+image('owner-mono.webp',page,'Freigestellte Originalaufnahme aus der Vineria','owner-sticker','fetchpriority="high"')+'<span class="punk-address">BÄNSCHSTRASSE 41<br>FRIEDRICHSHAIN</span><div class="punk-slider-controls"><button data-art-prev aria-label="Vorherige Grafik">←</button><span data-art-count>01 / 6</span><button data-art-next aria-label="Nächste Grafik">→</button><button data-art-pause aria-pressed="false">Pause</button></div></div></section>'
 teaser='<section class="lab-tienda-teaser wrap">'+image('wine-shelf-cut.webp',page,'Grafische Weinauswahl','', 'loading="lazy"')+'<div><p class="eyebrow">TIENDA · PRODUCTOS ESPAÑOLES</p><h2>Nimm ein Stück<br>Vineria mit.</h2><p>Euch gefällt unsere Auswahl? Weine, Konserven und spanische Spezialitäten für zu Hause. Zum Aufmachen, Mitbringen und Teilen.</p><a class="btn" href="shop/index.html">Zum Shop →</a></div></section>'
 return hero+'<div class="punk-strip">KLEINE TELLER / GROSSE ABENDE / FRIEDRICHSHAIN</div><section data-live-news></section>'+menu(data)+about(page)+teaser+graphic_gallery(page)+contact(page,mapurl)+EVENTS+'<section id="instagram" data-live-instagram></section>'
def replica_home(page,data,mapurl):
 manifest=json.loads((LAB/'extraction.json').read_text());pieces=[]
 for name,box in manifest['crops'].items():
  x,y,r,b=box;style=f'left:{x/1217*100:.7f}%;top:{y/1280*100:.7f}%;width:{(r-x)/1217*100:.7f}%;height:{(b-y)/1280*100:.7f}%'
  pieces.append(image(name+'.webp',page,'','ref-piece',f'style="{style}" data-source-piece="{name}"'))
 def hot(label,box,href=None,panel=None):
  x,y,r,b=box;style=f'left:{x/1217*100:.7f}%;top:{y/1280*100:.7f}%;width:{(r-x)/1217*100:.7f}%;height:{(b-y)/1280*100:.7f}%'
  href=href or '#'+str(panel);attrs=f' data-open-panel="{panel}" aria-haspopup="dialog"'if panel else''
  if href.startswith('https:'):attrs+=' target="_blank" rel="noopener"'
  return f'<a class="ref-hotspot" style="{style}" href="{E(href,quote=True)}"{attrs}><span class="sr-only">{E(label)}</span></a>'
 hotspots=hot('Vineria del Este · Startseite',[10,0,250,140],'index.html')
 for label,box,panel in [('Unser Restaurant',[268,36,372,93],'vineria'),('Speisekarte',[383,36,506,93],'speisekarte'),('Weine',[516,36,589,93],'weine'),('Über uns',[699,36,785,93],'vineria'),('Kontakt',[801,36,895,93],'besuch'),('Speisekarte ansehen',[624,674,854,725],'speisekarte'),('Unser Restaurant · mehr erfahren',[46,875,257,1060],'vineria'),('Zur Karte',[460,875,591,1062],'speisekarte'),('Route planen',[76,760,260,819],'besuch')]:hotspots+=hot(label,box,panel=panel)
 for label,box,href in [('Shop',[606,36,674,93],'shop/index.html'),('Zur Tienda',[918,484,1147,640],'shop/index.html'),('Zum Shop',[778,875,990,1062],'shop/index.html'),('Tisch reservieren',[1007,37,1205,95],'https://vineriaytapas.de/#tebi-reservations'),('Tisch reservieren',[624,732,854,786],'https://vineriaytapas.de/#tebi-reservations'),('Instagram',[991,1120,1050,1190],'https://www.instagram.com/vineria.del.este/')]:hotspots+=hot(label,box,href)
 for label,x,r,tag in [('Impressum',298,367,'impressum'),('Datenschutz',371,447,'datenschutz'),('AGB',451,490,'agb'),('Versand',493,550,'versand'),('Widerruf',553,619,'widerruf')]:hotspots+=hot(label,[x,1220,r,1254],'service/index.html#'+tag)
 info='<div class="reference-contact"><div><strong>ADRESSE</strong><p>Bänschstraße 41<br>10247 Berlin</p><a href="'+E(mapurl,quote=True)+'" target="_blank" rel="noopener">Route planen ↗</a></div><div><strong>ÖFFNUNGSZEITEN</strong><p>Di–Do ab 16 · Fr–Sa ab 15<br>So 12–18 Uhr<br>Mo geschlossen</p></div><div><strong>KONTAKT</strong><a href="tel:+493042024943">+49 30 42024943</a><a href="mailto:vineriadeleste@gmail.com">vineriadeleste@gmail.com</a><a href="#events" data-open-panel="events">Catering & große Gruppen ↗</a></div></div>'
 board='<section class="replica-board" aria-label="Vineria del Este · Wein, Tapas, Leben"><h1 class="sr-only">Vineria del Este · Wein. Tapas. Leben.</h1>'+''.join(pieces)+hotspots+info+'</section>'
 nav=''.join(f'<a href="#{target}" data-open-panel="{target}">{label}</a>'for target,label in[('vineria','Restaurant'),('speisekarte','Speisekarte'),('weine','Weine'),('besuch','Kontakt'),('events','Catering')])+'<a href="shop/index.html">Shop</a>'
 mobile='<section class="replica-mobile"><header><a href="index.html">'+image('wordmark.webp',page,'Vineria del Este','r-logo')+'</a><a class="text-link" href="https://vineriaytapas.de/#tebi-reservations" target="_blank" rel="noopener">Reservieren ↗</a></header><nav aria-label="Hauptnavigation">'+nav+'</nav>'+image('headline.webp',page,'Wein. Tapas. Leben.','r-headline')+'<p class="r-copy">Ein Ort für gute Produkte, ehrliche Küche und inspirierende Begegnungen. Spanien im Herzen, Berlin im Alltag.</p><div class="r-actions"><a class="btn" href="#speisekarte" data-open-panel="speisekarte">Speisekarte ansehen</a><a class="btn outline" href="#events" data-open-panel="events">Catering & Feiern</a></div>'+image('left-collage.webp',page,'Fotocollage aus der Bildvorlage','r-collage')+'<div class="r-tienda">'+image('bottle.webp',page,'Weinillustration aus der Bildvorlage')+'<a href="shop/index.html">'+image('tienda-note.webp',page,'Tienda · Zum Shop')+'</a></div><div class="r-features">'
 for title,txt,pic,target in [('Unser Restaurant','Kleine Gerichte, große Weine und ein Stück Spanien in Berlin.','olives','vineria'),('Speisekarte','Saisonale Tapas, Klassiker und besondere Weine.','herbs','speisekarte'),('Shop','Spanische Produkte für zu Hause. Wein, Konserven, Spezialitäten und mehr.','tin','shop')]:
  link='shop/index.html'if target=='shop'else'#'+target;extra=''if target=='shop'else' data-open-panel="'+target+'"'
  mobile+=f'<article><div><h2>{title}</h2><p>{txt}</p><a href="{link}"{extra}>Mehr erfahren →</a></div>'+image(pic+'.webp',page,'')+'</article>'
 mobile+='</div></section>'
 extra='<nav class="replica-extra-links" aria-label="Weitere Inhalte">'+''.join(f'<a href="#{t}" data-open-panel="{t}">{l}</a>'for t,l in[('news','Aktuelles'),('events','Catering & große Gruppen'),('instagram','Instagram'),('grafiken','Grafische Tellerstudien')])+f'<a href="{rel("verwaltung/vorschau.html",page)}">Team · Verwaltung</a></nav>'
 panels=[('speisekarte','Speisekarte & Weine',menu(data)),('vineria','Die Vineria',about(page)),('besuch','Kontakt & Besuch',contact(page,mapurl)),('events','Catering & große Gruppen',EVENTS),('news','Aktuelles','<section data-live-news></section>'),('instagram','Die Vineria in Bildern','<section id="instagram" data-live-instagram></section>'),('grafiken','Grafische Tellerstudien',graphic_gallery(page,True))]
 dialog='<dialog class="replica-dialog" id="replica-dialog" aria-labelledby="replica-dialog-title"><div class="replica-dialog-head"><h2 id="replica-dialog-title">Die Vineria</h2><button type="button" data-close-panel aria-label="Schließen">×</button></div>'+''.join(f'<section class="modal-panel" data-panel="{id}" data-label="{label}" hidden>{markup}</section>'for id,label,markup in panels)+'</dialog>'
 return board+mobile+extra+dialog

def add_card(file,id):
 s=soup(file.read_text());page=file.relative_to(SITE).as_posix();num,title=NEW[id]
 old=s.select_one(f'[data-proposal="{id}"]')
 if old:old.decompose()
 base=s.select_one('[data-proposal="v08"]');assert base is not None
 card=copy.deepcopy(base);card['data-proposal']=id
 for a in card.select('a[href]'):a['href']=rel(f'entwuerfe/{id}/shop/index.html'if'/shop/'in a['href']else f'entwuerfe/{id}/index.html',page)
 for im in card.select('img'):
  area='shop'if'shop'in im['src']else'restaurant';im['src']=rel(f'assets/proposals/{id}-{area}.webp',page);im['alt']=title+' · '+area
 card.select_one('.number').string='MODELL '+num;card.h2.string=title
 card.select_one('.idea-copy p').string='Expressive Farben, grobe Druckraster, Fotoreißkanten und echte Porträtausschnitte. Restaurant und Tienda als gemeinsames Punk-Fanzine.'if id=='v09'else'Die beigefügte Bildvorlage aus ihren Originalteilen rekonstruiert: Oliven, Kräuter, Konservendose, Typografie und gemalter Seitenabschluss. Mit bedienbaren Menüs.'
 for b in card.select('[data-open-pair]'):b['data-open-pair']=id
 s.select_one('#ideen').append(card);j=s.select_one('#proposal-data');values=[x for x in json.loads(j.string)if x['id']!=id];values.append({'id':id,'title':'Modell '+num+' · '+title,'restaurant':rel(f'entwuerfe/{id}/index.html',page),'shop':rel(f'entwuerfe/{id}/shop/index.html',page)});j.string=json.dumps(values,ensure_ascii=False)
 note=s.select_one('.intro-note p')
 if note:note.string='Die acht bisherigen Ideen bleiben erhalten. Modell 09 und 10 ergänzen die Auswahl. Vergleicht jeweils Restaurant und die passende Tienda.'
 file.write_text(str(s))

def main():
 for name in ['lab.css','ui.js']:shutil.copyfile(ROOT/'design-lab'/name,A/('lab-ui.js'if name=='ui.js'else name))
 source=SITE/'entwuerfe/v08';base=soup((source/'index.html').read_text());data=json.loads(base.select_one('#vde-content-seed').string)['content'];cat=json.loads((A/'catalog.json').read_text());mapurl=cat.get('map')or base.select_one('a[href*="google.com/maps"]')['href']
 before={id:hashlib.sha256((SITE/'entwuerfe'/id/'index.html').read_bytes()).hexdigest()for id in OLD}
 # Copy the stable paired route set before touching shared extras in any previous model.
 for id in NEW:shutil.copytree(source,SITE/'entwuerfe'/id,dirs_exist_ok=True)
 newpages=[]
 for id,(num,title)in NEW.items():
  folder=SITE/'entwuerfe'/id
  for f in folder.rglob('*.html'):
   page=f.relative_to(SITE).as_posix();sub=f.relative_to(folder).as_posix();s=soup(f.read_text().replace('/v08/','/'+id+'/').replace('Modell 08','Modell '+num))
   s.body['class']=['lab09'if id=='v09'else'lab10'];s.body['data-vde-style']=id
   for el in s.select('link[href*="model08.css"],link[href$="lab.css"],script[src$="lab-ui.js"],style'):el.decompose()
   for el in s.select('.proposal-nav span'):el.string='Modell '+num
   oldheader=s.select_one('header.header')
   if oldheader:oldheader.replace_with(soup(header(page,id)))
   oldfooter=s.select_one('footer.footer')
   if oldfooter:oldfooter.replace_with(soup(footer(page,id)))
   if sub=='index.html':
    s.main.clear();append_markup(s.main,punk_home(page,data,mapurl)if id=='v09'else replica_home(page,data,mapurl))
    if id=='v10':
     for el in s.select('header.lab-header,footer.footer'):el.decompose()
   elif sub=='shop/index.html':
    hero=s.select_one('.collage-hero,.shop-hero')
    art='paella-cut.webp'if id=='v09'else'bottle.webp'
    markup='<section class="lab-shop-lead wrap"><div><p class="eyebrow">VINERIA DEL ESTE · TIENDA</p><h1>Für den Tisch.<br>Für zu Hause.</h1><p>Weine, Konserven und spanische Spezialitäten. Ein kleines Stück Vineria zum Mitnehmen.</p><div class="actions"><a class="btn" href="#sortiment">Auswahl entdecken ↓</a><a class="btn outline" href="../index.html">Zum Restaurant ↗</a></div></div><div class="lab-shop-art">'+image(art,page,'Illustration · Vineria del Este')+'</div></section>'
    if hero:hero.replace_with(soup(markup))
   s.title.string='Vineria del Este · '+('Restaurant'if sub=='index.html'else'Tienda & Service')+' · Modell '+num+' · '+title
   include(s,page,'lab.css','css');include(s,page,'model08.js');include(s,page,'lab-ui.js')
   for text in s.find_all(string=True):
    if text.parent.name not in ['script','style']and'Collage & Papier'in str(text):text.replace_with(str(text).replace('Collage & Papier',title))
   f.write_text(str(s));newpages.append(page)
 # Give all earlier restaurant styles the same event form and explicit full-menu view.
 for id in OLD:
  f=SITE/'entwuerfe'/id/'index.html';page=f.relative_to(SITE).as_posix();s=soup(f.read_text())
  for old in list(s.select('#events,[data-common-events]')):old.decompose()
  ig=s.select_one('[data-live-instagram]');fragment=soup(EVENTS)
  if ig:ig.insert_before(fragment)
  else:s.main.append(fragment)
  host=s.select_one('[data-live-menu]')
  if host and not host.find_parent(attrs={'data-complete-menu':True}):
   host.parent['data-complete-menu']='';button=s.new_tag('button',type='button');button['class']=['full-menu-control'];button['data-full-menu']='';button.string='Gesamte Karte anzeigen';host.insert_before(button)
  include(s,page,'lab.css','css');include(s,page,'model08.js');include(s,page,'lab-ui.js');f.write_text(str(s))
 for f in (SITE/'entwuerfe').rglob('*.html'):
  page=f.relative_to(SITE).as_posix();match=re.match(r'entwuerfe/(v[1-5]|v6[ab]|v08|v09|v10)/',page)
  if not match:continue
  id=match[1];s=soup(f.read_text());ft=s.select_one('footer nav,footer')
  if ft and not any('#events'in a.get('href','')for a in ft.find_all('a')):
   a=s.new_tag('a',href=rel(f'entwuerfe/{id}/index.html',page)+'#events');a.string='Catering & große Gruppen';ft.append(a)
  f.write_text(str(s).replace('viewbox=','viewBox=').replace('preserveaspectratio=','preserveAspectRatio='))
 for file in [SITE/'index.html',SITE/'entwuerfe/index.html']:
  for id in NEW:add_card(file,id)
 for manifest in [A/'proposals.json']:
  if manifest.exists():
   values=json.loads(manifest.read_text());values=[x for x in values if x['id']not in NEW]
   for id,(n,t)in NEW.items():values.append({'id':id,'num':n,'title':t,'paper':'#eee8d9','ink':'#24221f','accent':'#dfdf4a'if id=='v09'else'#29251e','radius':'0'})
   manifest.write_text(json.dumps(values,ensure_ascii=False,indent=2))
 # Update editor wording and expose all twelve new graphics without changing stored content.
 for path in [A/'control.js',ROOT/'update/control.js']:
  if path.exists():
   text=path.read_text().replace('alle acht Entwürfe','alle zehn Entwürfe')
   extra=''.join('<option value="assets/lab/'+name+suffix+'">'+label+' · '+style+'</option>'for name,label in [('wine-shelf','Weinregal'),('asparagus','Spargel'),('octopus','Gegrillter Pulpo'),('prawns','Gambas'),('paella','Paella'),('dessert','Dessert')]for suffix,style in [('-color.webp','Punk / Farbe'),('-copy.webp','Fotokopie')])
   if 'assets/lab/asparagus-color.webp'not in text:text=text.replace('<option value="">Bild auswählen …</option>','<option value="">Bild auswählen …</option>'+extra)
   path.write_text(text)
 p=SITE/'verwaltung/vorschau.html';txt=p.read_text().replace('ACHT GESTALTUNGSSTILE','ZEHN GESTALTUNGSSTILE').replace('alle acht Entwürfe','alle zehn Entwürfe').replace('Acht Stile','Zehn Stile');p.write_text(txt)
 (SITE/'gestion').mkdir(exist_ok=True);(SITE/'gestion/index.html').write_text('<!doctype html><html lang="de"><meta charset="utf-8"><meta name="robots" content="noindex,nofollow"><meta http-equiv="refresh" content="0;url=../verwaltung/vorschau.html"><title>Vineria · Verwaltung</title><p><a href="../verwaltung/vorschau.html">Vorschau der täglichen Verwaltung öffnen</a></p></html>')
 report={'models':ALL,'new_models':list(NEW),'preserved_designs':OLD,'old_restaurant_hashes_before':before,'menu_entries':sum(len(c['items'])for c in data['sections']),'products':len(data['products']),'new_pages':newpages,'common_catering_in_all_models':True,'real_joomla_installation':False,'management_mode':'Local review; future standalone Joomla-backed interface','source_reconstruction':'Literal extracted pieces with functional navigation; reference placeholder contacts corrected'}
 out=ROOT/'reports/design-lab';out.mkdir(parents=True,exist_ok=True);(out/'build.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
