from pathlib import Path
from urllib.request import Request,urlopen
from urllib.parse import urljoin,urlparse
import re,html,json,io
from PIL import Image,ImageOps
root=Path('site/assets'); root.mkdir(parents=True,exist_ok=True)
def read(u):
    with urlopen(Request(u,headers={'User-Agent':'Mozilla/5.0'}),timeout=20) as r:return r.read(12000000)
try:
    base='https://vineriaytapas.de/'
    source=html.unescape(read(base).decode('utf-8','replace')).replace('\\/','/')
    (root/'original-asset-report.txt').write_text('\n'.join(x.strip() for x in source.splitlines() if any(k in x.lower() for k in ['logo','background','slideshow','tebi','<img','data-image'])))
    candidates=re.findall(r'(?:https?://[^\s<>\"\']+|/?(?:images|templates)/[^\s<>\"\']+)\.(?:jpg|jpeg|png|webp|svg)(?:\?[^\s<>\"\']*)?',source,re.I)
    # Also read all stylesheet references, including dynamically compiled template CSS.
    styles=re.findall(r'<link\b[^>]*href=[\"\']([^\"\']+)[\"\'][^>]*>',source,re.I)
    for s in styles:
        u=urljoin(base,s)
        if urlparse(u).hostname not in ['vineriaytapas.de','www.vineriaytapas.de'] or '.css' not in u:continue
        try:
            css=read(u).decode('utf-8','replace')
            candidates += [urljoin(u,v.strip(' \"\'')) for v in re.findall(r'url\(([^)]+)\)',css)]
        except Exception:pass
    imported=[]
    for raw in dict.fromkeys(candidates):
        u=urljoin(base,raw)
        if urlparse(u).hostname not in ['vineriaytapas.de','www.vineriaytapas.de']:continue
        if 'logo' not in u.lower() and '/images/vineriadeleste/' not in u:continue
        try:
            data=read(u)
            if '.svg' in urlparse(u).path.lower():
                if 'logo' in u.lower():
                    svg=data.decode();svg=re.sub(r'<script\b.*?</script>','',svg,flags=re.S|re.I)
                    (root/'original-logo.svg').write_text(svg);imported.append({'file':'original-logo.svg','source':u,'kind':'logo'})
            else:
                im=ImageOps.exif_transpose(Image.open(io.BytesIO(data))).convert('RGBA');w,h=im.size
                if 'logo' in u.lower():name='original-logo.webp'
                else:
                    import hashlib
                    name='photo-'+hashlib.sha256(u.encode()).hexdigest()[:10]+'.webp'
                im.thumbnail((1500,1500));im.save(root/name,quality=88)
                imported.append({'file':name,'source':u,'kind':'logo' if 'logo' in u.lower() else 'photo','width':w,'height':h})
        except Exception as e:print('Brand import skipped',u,str(e)[:100])
    (root/'brand-media.json').write_text(json.dumps(imported,ensure_ascii=False,indent=2));print('Additional media',json.dumps(imported,ensure_ascii=False))
except Exception as e: print('Original branding import',str(e))
