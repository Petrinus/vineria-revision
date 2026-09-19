"""Download only approved media. No credentials or customer data are imported."""
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.parse import urljoin, urlparse
from html.parser import HTMLParser
from PIL import Image, ImageOps
import json, io, re, hashlib
OUT=Path('site/assets'); OUT.mkdir(parents=True,exist_ok=True)
SOURCES=Path('tools/media-sources.json')
def fetch(url):
    with urlopen(Request(url,headers={'User-Agent':'Mozilla/5.0 (Vineria authorised design review)'}),timeout=25) as f:
        data=f.read(16000001)
        if len(data)>16000000: raise ValueError('asset too large')
        return data
records=[]
if SOURCES.exists():
    for name,url in json.loads(SOURCES.read_text()).items():
        target=OUT/(name+'.webp')
        if not target.exists():
            im=ImageOps.exif_transpose(Image.open(io.BytesIO(fetch(url)))).convert('RGB')
            im.thumbnail((1500,1500)); im.save(target,quality=85)
        records.append({'file':target.name,'source':'User-supplied photograph via approved upload' if name in ['bar','portrait','terrasse'] else 'Generated graphic, not documentary photography','kind':'original' if name in ['bar','portrait','terrasse'] else 'art'})
class Parser(HTMLParser):
    def __init__(self): super().__init__(); self.images=[]; self.css=[]; self.links=[]; self.scripts=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='img':
            for k in ['src','data-src']:
                if a.get(k): self.images.append(a[k])
        if tag=='link' and a.get('rel')=='stylesheet': self.css.append(a.get('href',''))
        if tag=='a': self.links.append(a.get('href',''))
        if tag=='script': self.scripts.append(a.get('src',''))
base='https://vineriaytapas.de/'
cached=OUT/'website-media.json'
if cached.exists(): records+=json.loads(cached.read_text())
else:
    public=[]
    try:
        html=fetch(base).decode('utf-8','replace'); p=Parser();p.feed(html)
        blocks=[(base,html)]
        for u in p.css:
            u=urljoin(base,u)
            if urlparse(u).hostname not in ['vineriaytapas.de','www.vineriaytapas.de']:continue
            try:blocks.append((u,fetch(u).decode('utf-8','replace')))
            except Exception:pass
        images=[urljoin(base,u) for u in p.images]
        for u,txt in blocks:
            images += [urljoin(u,x.strip(' \"\'')) for x in re.findall(r'url\(([^)]+)\)',txt)]
            images += [urljoin(base,x) for x in re.findall(r'[\"\']([^\"\']+\.(?:jpg|jpeg|png|webp))[\"\']',txt,re.I)]
        for url in dict.fromkeys(images):
            if urlparse(url).hostname not in ['vineriaytapas.de','www.vineriaytapas.de']:continue
            if not re.search(r'\.(png|jpe?g|webp|gif)(\?|$)',url,re.I):continue
            try:
                raw=fetch(url); im=ImageOps.exif_transpose(Image.open(io.BytesIO(raw))).convert('RGBA')
                w,h=im.size
                if max(w,h)<100:continue
                name='web-'+hashlib.sha256(url.encode()).hexdigest()[:10]+'.webp'; im.thumbnail((1600,1600));im.save(OUT/name,quality=87)
                public.append({'file':name,'source':url,'width':w,'height':h,'kind':'logo' if 'logo' in url.lower() else 'original'})
            except Exception as e:print('Media skipped:',url,str(e)[:80])
        (OUT/'website-links.json').write_text(json.dumps({'links':p.links,'scripts':p.scripts},ensure_ascii=False,indent=2))
        cached.write_text(json.dumps(public,ensure_ascii=False,indent=2));records+=public
    except Exception as e:print('Website import:',str(e))
(OUT/'media.json').write_text(json.dumps(records,ensure_ascii=False,indent=2))
print(json.dumps(records,ensure_ascii=False,indent=2))
