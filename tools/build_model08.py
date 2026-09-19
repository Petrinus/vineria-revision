"""Independent model 08. Local files only.
Rebuilds the existing v08 directory and its single card without duplicating models.
"""
from pathlib import Path
from bs4 import BeautifulSoup
import copy,json,posixpath,shutil
ROOT=Path(__file__).resolve().parent.parent
SITE=ROOT/'site';A=SITE/'assets';SOURCE=SITE/'entwuerfe/v6a';DEST=SITE/'entwuerfe/v08';MODEL=ROOT/'models/08'
def parse(text):return BeautifulSoup(text,'html.parser')
def rel(target,page):return posixpath.relpath(target,posixpath.dirname(page)or'.')
HERO='''<section class="collage-hero wrap"><figure class="photo-stack" data-collage-slides><div class="photo-layer is-visible"><img src="../../assets/terrasse.webp" alt="Ein Moment auf der Terrasse der Vineria" fetchpriority="high" width="640" height="800"></div><div class="photo-layer"><img src="../../assets/bar.webp" alt="Originalaufnahme an der Bar der Vineria" width="640" height="800"></div><div class="photo-layer"><img src="../../assets/photo-4b6ccc01af.webp" alt="Ein Gericht aus der Vineria" width="640" height="800"></div><figcaption>Bänschstraße 41. Ein guter Platz.</figcaption><div class="photo-controls"><button type="button" data-collage-prev aria-label="Vorheriges Bild">←</button><span data-collage-count>01 / 03</span><button type="button" data-collage-next aria-label="Nächstes Bild">→</button><button type="button" data-collage-pause aria-pressed="false">Pause</button></div></figure><div class="hero-copy"><p class="eyebrow">SPANISCH–URUGUAYISCHE KÜCHE<br>BERLIN · FRIEDRICHSHAIN</p><h1><span>Wein.</span><span>Tapas.</span><span>Leben.</span></h1><p>Ein Glas Wein. Kleine Teller zum Teilen.<br>Und die Menschen, mit denen man gern noch ein bisschen bleibt.</p><div class="hero-actions"><a class="btn" href="https://vineriaytapas.de/#tebi-reservations" target="_blank" rel="noopener">Tisch reservieren ↗</a><a class="btn outline" href="shop/index.html">Unser Shop ↗</a></div><span class="handnote">Ein Abend, der bleiben darf.</span></div><aside class="shop-slip"><img class="bottle-feature" src="../../assets/products/vanidade.webp" alt="Vanidade Albariño aus unserer Weinauswahl" width="260" height="400"><div class="slip-paper"><span class="handnote">auch für zu Hause</span><p class="eyebrow">VINERIA DEL ESTE · TIENDA</p><h2>Gut ausgesucht.<br>Gern geteilt.</h2><p>Euch gefällt unsere Auswahl? Nehmt ein Stück Vineria mit nach Hause.</p><a href="shop/index.html">Zur Tienda →</a></div></aside></section>'''
SHOP='''<section class="collage-hero shop-hero wrap"><div class="bottle-stack" aria-label="Weine aus unserem Sortiment"><img src="../../../assets/products/bujanda-blanco.webp" alt="Viña Bujanda Viura"><img src="../../../assets/products/vanidade.webp" alt="Vanidade Albariño"><img src="../../../assets/products/blanco-nieva.webp" alt="Blanco Nieva Sauvignon Blanc"></div><div class="hero-copy"><p class="eyebrow">VINERIA DEL ESTE · TIENDA<br>PRODUCTOS ESPAÑOLES</p><h1>Für den Tisch.<br>Für zu Hause.</h1><p>Die Weine, über die wir gern reden. Die kleinen Dosen, die man gemeinsam öffnet. Unsere Auswahl für Euren nächsten Abend.</p><div class="hero-actions"><a class="btn" href="#sortiment">Auswahl entdecken ↓</a><a class="btn outline" href="../index.html">Zum Restaurant ↗</a></div><span class="handnote">Ein kleines Stück Spanien.</span></div><aside class="shop-slip"><div class="slip-paper"><p class="eyebrow">UNSERE AUSWAHL</p><h2>Mitbringen.<br>Aufmachen.<br>Zusammen.</h2><p>Weine, Konserven und spanische Spezialitäten. Flasche oder Karton: Ihr habt die Wahl.</p><div class="receipt-tag">ABHOLEN IN DER VINERIA<br>VERSAND IN DEUTSCHLAND</div><p>Sortiment und Preise sind Beispiele. Noch kein Verkauf.</p></div></aside></section>'''
EVENTS='''<section class="events-sheet wrap" id="events"><p class="eyebrow">BESONDERE ANLÄSSE · CATERING</p><h2>Ein guter Anlass.<br>Ein Tisch für Euch.</h2><p>Ein Geburtstag, ein Abend mit dem Team oder spanische Spezialitäten für Eure Feier? Erzählt uns, was Ihr vorhabt. Wir melden uns per E-Mail oder Telefon, um die Einzelheiten zu besprechen.</p><p><a class="text-link" href="tel:+493042024943">Direkt anrufen: +49 30 42024943 ↗</a></p><details><summary class="btn outline">Event oder Catering anfragen ↓</summary><form class="events-form" data-events-form><label>Art der Anfrage<select name="type" required><option value="">Bitte auswählen</option><option>Catering</option><option>Private Feier im Restaurant</option><option>Firmenveranstaltung</option><option>Größere Gruppe</option><option>Sonstiger Anlass</option></select></label><label>Kontaktname<input name="name" autocomplete="name" required maxlength="100"></label><label>Anzahl der Personen<input name="people" type="number" min="1" max="999" required></label><label>Gewünschtes Datum<input name="date" type="date" required></label><label>Ungefähre Uhrzeit · optional<input name="time" type="time"></label><label>Antwort bevorzugt<select name="reply"><option>Per E-Mail</option><option>Per Telefon</option><option>E-Mail oder Telefon</option></select></label><label>E-Mail<input name="email" type="email" autocomplete="email" required maxlength="180"></label><label>Telefon · optional<input name="phone" type="tel" autocomplete="tel" maxlength="50"></label><label class="full">Was habt Ihr vor?<textarea name="message" maxlength="4000" placeholder="Anlass, Ort, besondere Wünsche oder Fragen …"></textarea></label><p class="full note">Die Anfrage ist unverbindlich. In der Vorschau wird Euer E-Mail-Programm geöffnet; versendet wird erst dort. Es werden keine Formulardaten auf dieser Website gespeichert.</p><button class="btn" type="submit">Anfrage als E-Mail öffnen ↗</button><p class="full" role="status" aria-live="polite"></p></form></details></section>'''
def add_optional_content(s,page):
 source=ROOT/'shared/content.json'
 if not source.is_file():return
 for old in s.select('[data-vde-news],[data-vde-instagram],#vde-shared-data'):old.decompose()
 extras=json.loads(source.read_text());catalog=json.loads((A/'catalog.json').read_text())
 n=parse('<section class="vde-shared vde-news" data-vde-news hidden><p class="vde-eyebrow">Aktuelles aus der Vineria</p><div class="vde-news-grid"></div></section>').section;s.main.insert(0,n)
 g=parse('<section class="vde-shared vde-instagram" data-vde-instagram><div class="vde-instagram-head"><div><p class="vde-eyebrow">MOMENTE AUS DER VINERIA</p><h2>Ein bisschen Kiez.</h2></div><a href="https://www.instagram.com/vineria.del.este/" target="_blank" rel="noopener noreferrer">@vineria.del.este ↗</a></div><div class="vde-instagram-grid"></div><p class="vde-source-note">Galerievorschau; automatische Instagram-Verbindung noch nicht aktiv.</p></section>').section;s.main.append(g)
 data={'schema':1,'mode':'review','root':rel('index.html',page).removesuffix('index.html'),'shop':'shop/index.html','extras':extras,'menu':catalog['menu']}
 el=s.new_tag('script',type='application/json',id='vde-shared-data');el.string=json.dumps(data,ensure_ascii=False).replace('<','\\u003c');s.body.append(el)
 for name,kind in [('features.css','css'),('features.js','js')]:
  if not(A/name).exists():continue
  el=s.new_tag('link',rel='stylesheet',href=rel('assets/'+name,page))if kind=='css'else s.new_tag('script',src=rel('assets/'+name,page),defer='');s.head.append(el)
def add_card(file):
 s=parse(file.read_text());page=file.relative_to(SITE).as_posix();cards=[c for c in s.select('[data-proposal]')if c['data-proposal']!='v08'];assert cards,'Existing selector missing'
 old=s.select_one('[data-proposal="v08"]')
 if old:old.decompose()
 card=copy.deepcopy(cards[-1]);card['data-proposal']='v08'
 for a in card.select('a[href]'):a['href']=rel('entwuerfe/v08/shop/index.html'if'/shop/'in a['href']else'entwuerfe/v08/index.html',page)
 for a in card.select('[aria-label]'):a['aria-label']=a['aria-label'].replace('06B','08').replace('06A','08')
 for img in card.select('img'):
  area='shop'if'shop'in img['src']else'restaurant';img['src']=rel('assets/proposals/v08-'+area+'.webp',page);img['alt']=('Tienda'if area=='shop'else'Restaurant')+' · Collage & Papier';img['loading']='eager'
 card.select_one('.number').string='MODELL 08';card.h2.string='Collage & Papier';card.select_one('.idea-copy p').string='Eigenständige Komposition nach der Bildreferenz: große Fotocollage, zentrale Typografie und Tienda-Notiz. Papier, Fotokopie und ruhige Bewegung im ganzen Auftritt.'
 for b in card.select('[data-open-pair]'):b['data-open-pair']='v08'
 s.select_one('#ideen').append(card);data=s.select_one('#proposal-data');v=[x for x in json.loads(data.string)if x['id']!='v08'];v.append({'id':'v08','title':'Modell 08 · Collage & Papier','restaurant':rel('entwuerfe/v08/index.html',page),'shop':rel('entwuerfe/v08/shop/index.html',page)});data.string=json.dumps(v,ensure_ascii=False)
 note=s.select_one('.intro-note p')
 if note:note.string='Die bisherigen Stile bleiben erhalten. Modell 08 ergänzt die Auswahl als eigenständige Komposition. Keine Variante ist vorab ausgewählt.'
 file.write_text(str(s))
def build():
 assert SOURCE.is_dir(),'Source pages missing'
 for name in ['model08.css','model08.js']:shutil.copyfile(MODEL/name,A/name)
 shared=ROOT/'shared'
 if(shared/'features.js').exists():
  text=(shared/'features.js').read_text().replace('function safeURL(value,allowImage=false)',"config.root=new URL(config.root,location.href).href;config.shop=new URL(config.shop||'#',location.href).href;\n function safeURL(value,allowImage=false)")
  (A/'features.js').write_text(text);shutil.copyfile(shared/'features.css',A/'features.css')
 pages=[]
 for source in sorted(SOURCE.rglob('*.html')):
  sub=source.relative_to(SOURCE);target=DEST/sub;page=target.relative_to(SITE).as_posix();s=parse(source.read_text().replace('entwuerfe/v6a/','entwuerfe/v08/').replace('Entwurf 06A','Modell 08'))
  s.body['class']=['model08'];s.title.string=s.title.get_text()+' · Collage & Papier'
  for badge in s.select('.scene-star'):badge.decompose()
  for el in s.select('.proposal-nav span'):el.string='Modell 08'
  for el in s.select('.footer-bottom span'):el.string='Modell 08 · Collage & Papier · Designvorschau'
  css=s.new_tag('link',rel='stylesheet',href=rel('assets/model08.css',page));s.head.append(css);js=s.new_tag('script',src=rel('assets/model08.js',page),defer='');s.head.append(js)
  if sub.as_posix()=='index.html':
   s.select_one('section.hero').replace_with(parse(HERO).section);s.select_one('#besuch').insert_before(parse(EVENTS).section)
   for p in s.find_all('p'):
    if'Tebi'in p.get_text():p.string='Küche Dienstag–Samstag bis ca. 22 Uhr. Reservierungen über unseren bestehenden Buchungszugang.'
   add_optional_content(s,page)
  if sub.as_posix()=='shop/index.html':
   s.select_one('.shop-hero').replace_with(parse(SHOP).section)
   if not s.select_one('#sortiment'):s.select_one('.product-card').parent['id']='sortiment'
  target.parent.mkdir(parents=True,exist_ok=True);target.write_text(str(s));pages.append(page)
 for file in [SITE/'index.html',SITE/'entwuerfe/index.html']:add_card(file)
 config=A/'proposals.json'
 if config.exists():
  data=[x for x in json.loads(config.read_text())if x['id']!='v08'];data.append({'id':'v08','num':'08','title':'Collage & Papier','paper':'#eeeadd','ink':'#1c1b18','accent':'#29241f','radius':'0'});config.write_text(json.dumps(data,ensure_ascii=False,indent=2))
 report={'model':'08','new_models':1,'previous_models_preserved':True,'pages':pages,'uses_local_assets_only':True};out=ROOT/'reports/model08';out.mkdir(parents=True,exist_ok=True);(out/'build.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
if __name__=='__main__':build()
