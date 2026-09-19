"""Final artwork treatment: black ink with real alpha, not white rectangles."""
from pathlib import Path
from urllib.request import Request,urlopen
from PIL import Image,ImageOps
import json,io,re
A=Path('site/assets');A.mkdir(parents=True,exist_ok=True)
plate_url='https://dnznrvs05pmza.cloudfront.net/gpt_image_2_5_flare/d03ac954-a979-4c3a-8fdd-51adc477e8b3/Transform_the_real_chickpea_and_avocado_salad_in__realplate_into_a_sophisticated_monochrome_editoria_0.png?_jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJrZXlIYXNoIjoiMWMyMmIxMWQzNDgzYzFjMSIsImJ1Y2tldCI6InJ1bndheS10YXNrLWFydGlmYWN0cyIsInN0YWdlIjoicHJvZCIsImV4cCI6MTc4OTg5NDgxM30.ODRiLFlxpK1mtZXvmiAyHK2uadX8QjUk-BMsDc5ii8o'
if not (A/'plate.webp').exists():
    with urlopen(Request(plate_url,headers={'User-Agent':'Vineria authorised review builder'}),timeout=35) as r: raw=r.read(15000000)
    im=ImageOps.exif_transpose(Image.open(io.BytesIO(raw))).convert('RGB');im.thumbnail((1300,1300));im.save(A/'plate.webp',quality=88)
for name in ['collage','paper','wine-art','plate']:
    src=A/(name+'.webp');dest=A/(name+'-ink.webp')
    if not src.exists():continue
    gray=ImageOps.grayscale(Image.open(src));alpha=gray.point(lambda v:0 if v>=246 else min(255,round((246-v)*255/228)))
    ink=Image.new('RGBA',gray.size,(18,19,16,0));ink.putalpha(alpha);ink.save(dest,quality=88,method=6)
for f in Path('site').rglob('*.html'):
    t=f.read_text().replace('loading="lazy"','loading="eager"')
    for name in ['collage','wine-art']:t=t.replace('assets/'+name+'.webp','assets/'+name+'-ink.webp')
    if f.name=='index.html' and f.parent in [Path('site'),Path('site/editorial')]:
        pattern=r'(<div class="teaser-image">)(.*?)(<span class="tape")'
        def teaser(m):
            b=m.group(2).replace('wine-art-ink.webp','plate-ink.webp').replace('Künstlerische Illustration einer Weinflasche mit zwei Gläsern','Künstlerischer Fotokopie-Ausschnitt des Originalgerichts der Vineria')
            return m.group(1)+b+m.group(3)
        t=re.sub(pattern,teaser,t,flags=re.S)
    if 'entwuerfe' in f.parts:
        t=t.replace('Papiergrafik und Weinillustration wurden für diesen Entwurf generiert.','Papiergrafik und Weinillustration wurden für diesen Entwurf generiert. Das Teller-Motiv ist eine grafische Bearbeitung der auf der Restaurant-Website veröffentlichten Kichererbsensalat-Aufnahme; es ist ausdrücklich als Illustration zu verstehen.')
    f.write_text(t)
css=A/'site.css';text=css.read_text().replace("url('paper.webp')","url('paper-ink.webp')")
text+='''\n/* Transparent ink originals; rectangular image backgrounds are removed. */
.scene:before{background-color:transparent;opacity:.5}.cutout img[src*="-ink"]{clip-path:none;width:100%;object-fit:contain;filter:none;mix-blend-mode:normal}.scene .cutout{pointer-events:none}.teaser-image>img{filter:none;mix-blend-mode:normal}.scene-controls{z-index:5}.scene-caption{z-index:5}.fanzine-corner{pointer-events:none}.editorial .scene:before{opacity:.1}.editorial .teaser-image>img{filter:none}.gallery img{background:transparent}
'''
css.write_text(text)
manifest=A/'media.json'
records=json.loads(manifest.read_text()) if manifest.exists() else []
records=[x for x in records if not x.get('file','').endswith('-ink.webp')]
for name in ['collage','paper','wine-art','plate']:
    records.append({'file':name+'-ink.webp','kind':'art','source':'Generated illustration with black-ink alpha treatment; not a documentary photograph','based_on':'Original chickpea salad photo from vineriaytapas.de' if name=='plate' else ('Two user-supplied Vineria portraits' if name=='collage' else 'Original graphic for the project')})
for row in records:
    if '/templates/' in row.get('source',''):row['kind']='template_asset_unused_in_design'
manifest.write_text(json.dumps(records,ensure_ascii=False,indent=2))
print('Artwork refined: true alpha, no white frames, all review images eager.')
