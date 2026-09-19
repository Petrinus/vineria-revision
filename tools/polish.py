"""Final non-destructive enhancements to both compiled review themes."""
from pathlib import Path
import os,json,html,re
R=Path(os.environ.get('VDE_OUTPUT','site'));A=R/'assets'
catalogue=json.loads((A/'catalog.json').read_text())
products={p['id']:p for p in catalogue['products']}
def box_labels(text,p):
 if not p.get('case'):return text
 label=html.escape(str(p['case'])+' × '+p['pack'])
 text=text.replace('6 × 0,75 l',label)
 text=text.replace('Karton: 6 Flaschen à 0,75 l',html.escape('Karton: '+str(p['case'])+' Einheiten à '+p['pack']))
 return text
css='''.cutout img[src*="photo-4b6ccc01af"]{width:76%;clip-path:polygon(24% 1%,59% 0,80% 7%,96% 27%,99% 52%,90% 77%,73% 95%,37% 99%,11% 81%,0 56%,5% 27%);object-fit:cover}.scene[data-paused="true"] .scene-star{animation-play-state:paused}.gallery{grid-template-columns:1fr .8fr 1fr .85fr}.gallery figure img{height:310px}.gallery figure:nth-child(4){transform:rotate(2deg)}.editorial .gallery figure{transform:none}.food-caption{font-size:9px}@media(max-width:700px){.gallery{grid-template-columns:1fr 1fr;gap:22px 16px}.gallery figure:last-child{grid-column:auto}.gallery figure:last-child img{height:230px}.gallery figure img{height:230px}.gallery figure:nth-child(4){transform:rotate(-2deg)}.editorial .gallery figure{transform:none}}'''
(A/'polish.css').write_text(css)
(A/'polish.js').write_text('''document.querySelectorAll('[data-slideshow]').forEach(scene=>{const b=scene.querySelector('[data-pause]');const update=()=>scene.dataset.paused=b.getAttribute('aria-pressed');new MutationObserver(update).observe(b,{attributes:true,attributeFilter:['aria-pressed']});update();});(()=>{const ids={'mod-100':'vineria','mod-101':'speisekarte','mod-151':'speisekarte','mod-102':'besuch'};const go=()=>{const id=ids[location.hash.slice(1)];if(id)document.getElementById(id)?.scrollIntoView();};addEventListener('hashchange',go);go();})();''')
for f in R.rglob('*.html'):
 p=f.relative_to(R);root='../'*(len(p.parts)-1);s=f.read_text()
 if 'polish.css' not in s:s=s.replace('</head>',f'<link rel="stylesheet" href="{root}assets/polish.css"><script defer src="{root}assets/polish.js"></script></head>')
 if p.as_posix() in ['index.html','editorial/index.html'] and (A/'photo-4b6ccc01af.webp').exists():
  image=f'<img src="{root}assets/photo-4b6ccc01af.webp" alt="Originalaufnahme des Kichererbsensalats von der Restaurant-Website" loading="lazy" decoding="async">'
  if 'data-original-dish' not in s:
   s=s.replace('<span class="scene-star"',f'<div class="cutout" data-original-dish>{image}</div><span class="scene-star"',1)
   s=s.replace('01 / 03','01 / 04')
   marker='<figcaption>Ein guter Abend fängt hier an.</figcaption></figure></div>'
   s=s.replace(marker,'<figcaption>Ein guter Abend fängt hier an.</figcaption></figure><figure>'+image+'<figcaption>Ein Teller aus der Vineria.</figcaption></figure></div>')
 if 'shop' in p.parts:
  for ident,product in products.items():
   pattern=r'<article class="product-card" data-product="'+re.escape(ident)+r'".*?</article>'
   s=re.sub(pattern,lambda m:box_labels(m.group(0),product),s,flags=re.S)
  if p.parent.name in products:s=box_labels(s,products[p.parent.name])
 f.write_text(s)
manifest={'review_mode':True,'intended_production_domain':'https://vineriaytapas.de','routes':{'/':'Restaurant','/shop/':'Independent shop homepage','/shop/<product>/':'Product landing pages','/verwaltung/':'PHP authenticated management; not active on GitHub/CDN'},'legacy_anchors':{'mod-100':'vineria','mod-101':'speisekarte','mod-151':'speisekarte','mod-102':'besuch'},'indexing':'Review pages remain noindex; remove only after operator, content, image rights, product labels and checkout are approved.'}
(A/'deployment-plan.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
print('Applied paired-theme photo, motion and catalogue refinements.')
