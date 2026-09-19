"""Apply the verified six-post selection without rebuilding or restyling any design.
The public gallery is a local, curated selection, not a connected live feed.
"""
from pathlib import Path
from bs4 import BeautifulSoup
from html import escape
import json,posixpath,re
ROOT=Path(__file__).resolve().parents[1];SITE=ROOT/'site';A=SITE/'assets'
REPORT=ROOT/'reports/instagram-selection';REPORT.mkdir(parents=True,exist_ok=True)
selection=json.loads((ROOT/'media/instagram-selection.json').read_text())
imported=json.loads((REPORT/'import.json').read_text())
posts=imported['posts']
assert len(posts)==6 and all(p['status']=='downloaded' for p in posts),'Do not replace the gallery with missing or substituted pictures'
assert [p['permalink'] for p in posts]==[p['permalink'] for p in selection['posts']]
labels={
 'DSDZcT3DI2I':'Wein & Tapas · Vineria del Este',
 'DKU9PzaMm1w':'Weißer Spargel mit Oliven, getrockneten Tomaten und Kapernvinaigrette',
 'Ckbmq6yMEWS':'Gegrillter Oktopus mit Apfel-Kartoffel-Püree',
 'CgpJbcXjyWV':'Sommergrill · Vineria del Este',
 'BuzCKLOho7i':'Ausgewählte Aufnahme aus @vineriadeleste · 9. März 2019',
 'BvhPAb1HqoM':'Ausgewählte Aufnahme aus @vineriadeleste · 27. März 2019'
}
items=[]
for p in posts:
    assert (SITE/p['image']).is_file()
    items.append({'id':p['shortcode'],'image':p['image'],'alt':labels[p['shortcode']],'permalink':p['permalink'],'account':p['account'],'source':'user_selected_instagram_post','source_sha256':p['sha256']})
curated={'selection_id':selection['selection_id'],'count':6,'connected':False,'display_mode':'curated_local_selection','items':items}
(ROOT/'media/instagram-curated.json').write_text(json.dumps(curated,ensure_ascii=False,indent=2))
(A/'instagram-selected/selection.json').write_text(json.dumps(curated,ensure_ascii=False,indent=2))

# Preserve menu/product/news edits when an older browser-local gallery is still stored.
MIGRATION="""
 // User-selected Instagram set: refresh only gallery assets, not other local content.
 const approvedGallery=cfg.content.instagram;
 if(approvedGallery?.selection_id&&data.instagram.selection_id!==approvedGallery.selection_id){
   data.instagram={...data.instagram,selection_id:approvedGallery.selection_id,items:clone(approvedGallery.items),count:approvedGallery.count,connected:false,display_mode:'curated_local_selection'};
 }
"""
GALLERY="""
 const ig=document.querySelector('[data-live-instagram]');
 if(ig){
  ig.hidden=!data.instagram.enabled;
  const rows=data.instagram.items.slice(0,data.instagram.count);
  const sourceLink=x=>{try{const u=new URL(x.permalink);return ['www.instagram.com','instagram.com'].includes(u.hostname)&&u.protocol==='https:'?u.href:'https://www.instagram.com/'+encodeURIComponent(x.account||'vineria.del.este')+'/';}catch{return 'https://www.instagram.com/vineria.del.este/';}};
  ig.innerHTML='<div class="live-instagram-head"><div><p class="eyebrow">Einblicke</p><h2>Die Vineria in Bildern.</h2></div><div class="live-instagram-accounts"><a href="https://www.instagram.com/vineria.del.este/" target="_blank" rel="noopener noreferrer">@vineria.del.este ↗</a><a href="https://www.instagram.com/vineriadeleste/" target="_blank" rel="noopener noreferrer">@vineriadeleste ↗</a></div></div>'
   +'<div class="live-instagram-grid" data-photo-count="'+rows.length+'">'+rows.map(x=>'<a data-selected-instagram="'+esc(x.id||'')+'" href="'+esc(sourceLink(x))+'" target="_blank" rel="noopener noreferrer"><img src="'+esc(url(x.image))+'" alt="'+esc(x.alt)+'" loading="lazy"></a>').join('')+'</div>'
   +'<p class="live-note">Ausgewählte Originalaufnahmen aus beiden Instagram-Profilen. Jeder Bildlink führt zum zugehörigen Beitrag. Diese Auswahl ist lokal gespeichert; noch kein automatisch aktualisierter Instagram-Feed.</p>';
 }
}
"""
for path in [ROOT/'update/content-engine.js',A/'content-engine.js']:
    text=path.read_text()
    if '// User-selected Instagram set:' not in text:
        text=text.replace(' function url(value)',MIGRATION+' function url(value)',1)
    start=text.index(" const ig=document.querySelector('[data-live-instagram]');")
    end=text.index('\n function storefront()',start)
    text=text[:start]+GALLERY.rstrip()+text[end:]
    path.write_text(text)

new_option='<option value="6" ${data.instagram.count===6?\'selected\':\'\'}>6 Fotos · ausgewählte Beiträge</option>'
media_options=''.join('<option value="'+escape(x['image'],quote=True)+'">Instagram · '+escape(x['alt'])+'</option>' for x in items)
for path in [ROOT/'update/control.js',A/'control.js']:
    text=path.read_text()
    needle='<option value="8" ${data.instagram.count===8?\'selected\':\'\'}>8 Fotos</option>'
    if '>6 Fotos · ausgewählte Beiträge</option>' not in text:
        assert needle in text
        text=text.replace(needle,new_option+needle,1)
    if 'assets/instagram-selected/DSDZcT3DI2I.webp' not in text:
        needle='<option value="">Bild auswählen …</option>'
        assert needle in text
        text=text.replace(needle,needle+media_options,1)
    text=text.replace('Hier werden eigene vorhandene Fotos als Vorschau benutzt; keine Instagram-Passwörter eingeben.','Hier werden die sechs ausdrücklich ausgewählten Beiträge aus beiden Restaurantprofilen angezeigt; keine Instagram-Passwörter eingeben.')
    path.write_text(text)

css='''
/* Six user-selected originals, same gallery and the existing design palette. */
.live-instagram-grid[data-photo-count="6"]{grid-template-columns:repeat(3,minmax(0,1fr))}
.live-instagram-accounts{display:flex;flex-direction:column;align-items:flex-end;gap:8px;font:12px/1.6 Arial,sans-serif;margin-bottom:22px}
@media(max-width:720px){.live-instagram-grid[data-photo-count="6"]{grid-template-columns:repeat(2,minmax(0,1fr))}.live-instagram-accounts{align-items:flex-start}}
'''
for path in [ROOT/'update/content.css',A/'content.css']:
    text=path.read_text()
    if '/* Six user-selected originals' not in text:path.write_text(text+css)

changed=[]
for path in SITE.rglob('*.html'):
    soup=BeautifulSoup(path.read_text(),'html.parser');seed=soup.find(id='vde-content-seed')
    if not seed:continue
    data=json.loads(seed.string);g=data['content']['instagram'];enabled=g.get('enabled',True);g.update(curated);g['enabled']=enabled
    seed.string=json.dumps(data,ensure_ascii=False).replace('<','\\u003c')
    gallery=soup.select_one('[data-live-instagram]')
    if gallery:gallery['id']='instagram'
    if path==SITE/'verwaltung/vorschau.html' and not soup.select_one('[data-photo-selection-link]'):
        a=soup.new_tag('a',href='instagram-auswahl.html');a['data-photo-selection-link']='';a.string='Ausgewählte Instagram-Fotos ansehen ↗';soup.main.insert(2,a)
    path.write_text(str(soup).replace('viewbox=','viewBox=').replace('preserveaspectratio=','preserveAspectRatio='))
    changed.append(path.relative_to(SITE).as_posix())
for path in [A/'review-content.json']:
    data=json.loads(path.read_text());data['instagram'].update(curated);path.write_text(json.dumps(data,ensure_ascii=False,indent=2))

# Make the selection survive future shared-content builds.
path=ROOT/'update/build.py';text=path.read_text()
if '# preserve-selected-instagram' not in text:
    needle=" return {'schema':3,'sections':"
    assert needle in text
    text=text.replace(needle," result={'schema':3,'sections':",1)
    hook="\n # preserve-selected-instagram\n selected=ROOT/'media/instagram-curated.json'\n if selected.is_file():result['instagram'].update(json.loads(selected.read_text()))\n return result\n"
    assert '\nCONTROL=' in text
    text=text.replace('\nCONTROL=',hook+'\nCONTROL=',1)
    path.write_text(text)

# Standalone contact sheet for the team, not a ninth design or a live social feed.
cards=''.join('<article><a href="'+escape(x['permalink'],quote=True)+'" target="_blank" rel="noopener noreferrer"><img src="../'+escape(x['image'],quote=True)+'" alt="'+escape(x['alt'],quote=True)+'"></a><p>'+str(i+1)+' · @'+escape(x['account'])+'</p><h2>'+escape(x['alt'])+'</h2><a href="'+escape(x['permalink'],quote=True)+'" target="_blank" rel="noopener noreferrer">Originalbeitrag öffnen ↗</a></article>'for i,x in enumerate(items))
html='''<!doctype html><html lang="de"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><title>Vineria · Ausgewählte Instagram-Fotos</title><link rel="stylesheet" href="../assets/catalogue.css"><style>main{padding:38px 0}h1{font:48px/1.1 Georgia,serif;letter-spacing:-.04em}.selected-photos{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:24px}.selected-photos article{border:1px solid #d7d5ce;background:#fffdfa;padding:15px}.selected-photos img{width:100%;height:290px;object-fit:contain;background:#efede6}.selected-photos h2{font:23px/1.3 Georgia,serif}.selected-photos p,.selected-photos a{font:12px/1.7 Arial,sans-serif}@media(max-width:800px){.selected-photos{grid-template-columns:1fr 1fr}}@media(max-width:520px){.selected-photos{grid-template-columns:1fr}}</style><body><header class="masthead"><div class="wrap"><a class="wordmark" href="../index.html">Vineria del Este</a><a href="vorschau.html">← Verwaltung</a></div></header><main class="wrap"><p class="eyebrow">DIE SECHS AUSDRÜCKLICH AUSGEWÄHLTEN BEITRÄGE</p><h1>Die Bilderauswahl.</h1><p>Vier Bilder aus @vineria.del.este, zwei aus @vineriadeleste. Gespeicherte Originalaufnahmen, keine Ersatzbilder. Bei einer Mehrbild-Publikation ist hier das zuerst gezeigte Foto übernommen. Dies ist kein automatischer Feed.</p><div class="selected-photos">'''+cards+'''</div><p><a href="../entwuerfe/v08/index.html#instagram">Galerie im Modell 08 ansehen ↗</a></p></main></body></html>'''
(SITE/'verwaltung/instagram-auswahl.html').write_text(html)
report={'selection_id':selection['selection_id'],'requested':6,'incorporated':6,'image_urls':[x['image']for x in items],'permalinks':[x['permalink']for x in items],'default_count':6,'existing_options_preserved':[4,8],'styles':['v1','v2','v3','v4','v5','v6a','v6b','v08'],'html_pages_updated':len(changed),'automatic_instagram_connection':False,'new_models':0}
(REPORT/'integration.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps(report,ensure_ascii=False,indent=2))
