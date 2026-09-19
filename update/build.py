"""Update all eight current designs in place. No new design, login or live payments."""
from pathlib import Path
from bs4 import BeautifulSoup
import json,posixpath,re,shutil,copy
ROOT=Path(__file__).resolve().parents[1];SITE=ROOT/'site';A=SITE/'assets'
IDS=['v1','v2','v3','v4','v5','v6a','v6b','v08']
COLORS={'v1':('#f6f1e7','#542631','28px'),'v2':('#f4eedf','#752c35','0'),'v3':('#f5f0e4','#923b4e','0'),'v4':('#f5f0e4','#923b4e','0'),'v5':('#f5f0e4','#923b4e','0'),'v6a':('#f7f6f1','#171717','0'),'v6b':('#f5f0e4','#89354b','0'),'v08':('#eeeadd','#29241f','0')}
def rel(p,page):return posixpath.relpath(p,posixpath.dirname(page)or'.')
def parse(text):return BeautifulSoup(text,'html.parser')
def content():
 cat=json.loads((A/'catalog.json').read_text());labels={'wochenkarte':'Wochenkarte','klassiker':'Unsere Klassiker','weisswein':'Weißwein','rotwein':'Rotwein'}
 result={'schema':3,'sections':[{'id':k,'label':labels.get(k,k),'visible':True,'items':[{'id':k+'-'+str(i),'name':r[0],'description':r[1],'price':r[2],'visible':True}for i,r in enumerate(v)]}for k,v in cat['menu'].items()], 'products':[dict(p,visible=True)for p in cat['products']], 'news':{'enabled':True,'limit':2,'items':[{'id':'paella-beispiel','title':'Diesen Sonntag: Paella','text':'Ein großer Tisch, eine Paella zum Teilen und ein gutes Glas dazu.\nTermin und Uhrzeit nach Absprache.','image':'assets/approved/paella-halftone.webp','visible':True,'example':True,'starts':'','ends':'','link':'https://vineriaytapas.de/#tebi-reservations','linkLabel':'Tisch anfragen'}]}, 'instagram':{'enabled':True,'count':4,'connected':False,'items':[{'image':'assets/terrasse.webp','alt':'Vor der Vineria'},{'image':'assets/bar.webp','alt':'An der Bar'},{'image':'assets/photo-4b6ccc01af.webp','alt':'Kichererbsensalat'},{'image':'assets/portrait.webp','alt':'Ein Moment aus der Vineria'}]}}
 # preserve-selected-instagram
 selected=ROOT/'media/instagram-curated.json'
 if selected.is_file():result['instagram'].update(json.loads(selected.read_text()))
 return result

CONTROL='''<p class="eyebrow">GEMEINSAME INHALTE · ACHT GESTALTUNGSSTILE</p><h1>Die Verwaltung.</h1><p class="control-help">Bedienvorschau: Änderungen werden in diesem Browser gespeichert und in allen acht Entwürfen angezeigt. Für alle Besucher gespeicherte Inhalte, Benutzer und Kennwörter benötigen die Installation im geschützten Joomla-System. Keine echten Zugangsdaten hier eingeben.</p><div class="control-tabs" role="tablist" aria-label="Verwaltungsbereiche"><button data-control-tab="menu" role="tab">Speisekarte</button><button data-control-tab="sections" role="tab">Menübereiche</button><button data-control-tab="products" role="tab">Produkte</button><button data-control-tab="news" role="tab">Nachrichten</button><button data-control-tab="instagram" role="tab">Instagram</button><button data-control-tab="team" role="tab">Team</button></div><div class="control-toolbar"><button id="control-add">Hinzufügen +</button><button id="control-undo">Löschung rückgängig</button></div><div id="vde-control"></div><div class="control-toolbar"><button id="control-save" class="primary">Für alle Entwürfe übernehmen</button><button id="control-reset">Teständerungen zurücksetzen</button><span id="control-status" role="status">Keine öffentliche Veröffentlichung. Acht Stile, ein gemeinsamer Inhalt.</span></div>'''

def build():
 data=content();(A/'review-content.json').write_text(json.dumps(data,ensure_ascii=False,indent=2))
 for name in ['content-engine.js','control.js','content.css']:shutil.copyfile(ROOT/'update'/name,A/name)
 for ident in IDS:
  base=SITE/'entwuerfe'/ident/'shop';generic=base/'produkt/index.html';generic.parent.mkdir(exist_ok=True)
  generic.write_text((base/'mejillones/index.html').read_text())
 pages=[]
 for f in SITE.rglob('*.html'):
  page=f.relative_to(SITE).as_posix();s=parse(f.read_text())
  if not s.head or not s.body:continue
  mat=re.search(r'entwuerfe/(v[1-5]|v6[ab]|v08)/',page);ident=mat[1]if mat else('v6b'if page.startswith('editorial/')else'v6a')
  restaurant=bool(mat and page==f'entwuerfe/{ident}/index.html')or page in ['fanzine/index.html','editorial/index.html']
  admin=page=='verwaltung/vorschau.html';has_shop='/shop/'in page or page.startswith('shop/');commercial=has_shop or any(x in page for x in ['/warenkorb/','/checkout/'])or page.startswith(('warenkorb/','checkout/'))
  for brand in s.select('a.brand,a.logo'):
   brand.clear();brand['class']=list(dict.fromkeys(brand.get('class',[])+['original-brand']));brand['aria-label']='Vineria del Este · Startseite'
   img=s.new_tag('img',src=rel('assets/approved/logo.webp',page),alt='Vineria del Este · Vinos y Pintxos',width='1200',height='334');brand.append(img)
  for e in s.select('.scene-star'):e.decompose()
  for img in s.select('img[src]'):
   if re.search(r'/collage(?:-ink)?\.webp',img['src']):img['src']=rel('assets/approved/pulpo-halftone.webp',page);img['alt']='Pulpo · Fotokopiegrafik nach der freigegebenen Illustration'
  for cap in s.select('.scene-caption'):cap.string='Originalfotos der Vineria und grafische Tellerstudien.'
  for old in s.select('#vde-content-seed,script[data-live-engine],link[data-live-css]'):old.decompose()
  for old in s.select('script[src$="features.js"],#vde-shared-data'):old.decompose()
  for old in s.select('[data-vde-news],[data-vde-instagram],[data-live-news],[data-live-instagram],.fanzine-gallery'):old.decompose()
  if restaurant:
   sec=s.select_one('section#karte,section#speisekarte,section#carta,section#menu');assert sec,page
   header=sec.select_one('.section-head,.section-top,.section-heading');saved=copy.deepcopy(header)if header else None
   sec.clear();wrap=s.new_tag('div')
   if 'menu-section'in sec.get('class',[]):wrap['class']=['wrap']
   if saved:
    for p in saved.find_all('p'):
     if 'Ausschnitt'in p.get_text():p.string='Die vollständige Karte: Wochenangebote, Klassiker und unsere Weine.'
    wrap.append(saved)
   host=s.new_tag('div');host['data-live-menu']=''
   for cat in data['sections']:
    h=s.new_tag('h3');h.string=cat['label'];host.append(h)
    for row in cat['items']:
     item=s.new_tag('p');item.string=row['name']+' — '+str(row['price']/100).replace('.',',')+' € · '+row['description'];host.append(item)
   wrap.append(host);sec.append(wrap)
   main=s.main;news=s.new_tag('section');news['data-live-news']='';main.insert(0,news)
   ig=s.new_tag('section');ig['data-live-instagram']='';main.append(ig)
   if ident in ['v6a','v08']:
    teaser=s.select_one('.teaser-image img')
    if teaser:teaser['src']=rel('assets/approved/boquerones-halftone.webp',page);teaser['alt']='Boquerones · Halftone-Illustration'
    paired=s.select_one('[data-paired-shop]')
    if paired and not paired.select_one('.dish-print'):
     im=s.new_tag('img',src=rel('assets/approved/boquerones-halftone.webp',page),alt='',loading='lazy');im['class']=['dish-print','plate-rotation'];paired.insert(1,im)
    intro=s.select_one('.intro')
    if ident=='v08'and intro and not intro.select_one('.dish-print'):
     im=s.new_tag('img',src=rel('assets/approved/pulpo-halftone.webp',page),alt='',loading='lazy');im['class']=['dish-print','plate-rotation'];intro.append(im)
   pages.append(page)
  product=None
  if has_shop and f.parent.name!='shop':
   det=s.select_one('section.detail')
   if det:
    product=f.parent.name if f.parent.name!='produkt'else None
    det.clear();det.attrs.pop('data-product',None);det['data-live-product']=''
    bc=s.select_one('.breadcrumb')
    if bc:
     bc.clear();a=s.new_tag('a',href='../index.html');a.string='← Tienda';bc.append(a)
  if admin:
   s.main.clear()
   for el in list(parse(CONTROL).contents):s.main.append(el)
   for old in s.select('script[src$="management-preview.js"],script[src$="control.js"]'):old.decompose()
  if restaurant or commercial or admin:
   script=s.new_tag('script',id='vde-content-seed',type='application/json');script.string=json.dumps({'root':rel('index.html',page).removesuffix('index.html'),'shop':rel(f'entwuerfe/{ident}/shop/index.html',page),'product':product,'content':data},ensure_ascii=False).replace('<','\\u003c')
   s.head.append(script)
   js=s.new_tag('script',src=rel('assets/content-engine.js',page),defer='');js['data-live-engine']=''
   site_script=s.select_one('script[src$="site.js"]')
   if site_script:site_script.insert_before(js)
   else:s.head.append(js)
   if admin:s.head.append(s.new_tag('script',src=rel('assets/control.js',page),defer=''))
  if restaurant or commercial or admin or s.select_one('.original-brand'):
   paper,accent,radius=COLORS[ident]
   st=s.new_tag('style');st.string=f'body{{--vde-paper:{paper};--vde-accent:{accent};--vde-radius:{radius};--vde-line:#c3bcaf}}';s.head.append(st)
   css=s.new_tag('link',rel='stylesheet',href=rel('assets/content.css',page));css['data-live-css']='';s.head.append(css)
  for text in s.find_all(string=True):
   if text.parent.name in ['script','style']:continue
   t=str(text)
   t=t.replace('Produktgrafiken sind keine Fotos der verkauften Packungen.','Produktbilder dienen der Designvorschau.').replace('Abbildung: grafischer Platzhalter. Kein Originalproduktfoto.','Produktabbildung zur Designvorschau.')
   t=t.replace('Die Collage am kleinen Tisch wurde aus zwei dieser Porträts künstlerisch neu zusammengesetzt; sie zeigt keinen dokumentierten gemeinsamen Moment.','Die abgelehnte Personencollage wird nicht mehr verwendet.')
   if t!=str(text):text.replace_with(t)
  f.write_text(str(s).replace('viewbox=','viewBox=').replace('preserveaspectratio=','preserveAspectRatio='))
 assert len([x for x in pages if x.startswith('entwuerfe/')])==8,pages
 (ROOT/'reports/halftone').mkdir(parents=True,exist_ok=True)
 (ROOT/'reports/halftone/build.json').write_text(json.dumps({'models':IDS,'restaurant_pages':pages,'menu_entries':sum(len(s['items'])for s in data['sections']),'products':len(data['products']),'management':'browser-only review; Joomla integration pending','new_models':0},indent=2))
 skill=ROOT/'skills/joomla-vineria/SKILL.md'
 if skill.exists():skill.write_text(skill.read_text().replace('name: jo om la-vineria','name: joomla-vineria'))
if __name__=='__main__':build()
