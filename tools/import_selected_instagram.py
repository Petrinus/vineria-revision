"""Fetch the exact user-selected public Instagram posts.
No login, private API, cookies, credential use, proxy or access-control bypass.
A missing post remains missing; another picture is never substituted.
This importer stores images and a report; it does not change layouts.
"""
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.parse import urlsplit, urljoin
from urllib.error import HTTPError
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup
from PIL import Image, ImageOps, ImageDraw
import hashlib, html, io, json, datetime
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'reports/instagram-selection';OUT.mkdir(parents=True,exist_ok=True)
ASSETS=ROOT/'site/assets/instagram-selected';ASSETS.mkdir(parents=True,exist_ok=True)
SPEC=json.loads((ROOT/'media/instagram-selection.json').read_text())

def get(url,media=False):
    host=(urlsplit(url).hostname or '').lower()
    if media:
        if not (host.endswith('.cdninstagram.com') or host.endswith('.fbcdn.net')):
            raise ValueError('Not an Instagram media host')
    elif host not in ('www.instagram.com','instagram.com'):
        raise ValueError('Not an Instagram page')
    req=Request(url,headers={'User-Agent':'Mozilla/5.0','Accept':'text/html,application/xhtml+xml,image/webp,image/*;q=0.8'})
    with urlopen(req,timeout=16) as response:
        final=response.geturl()
        if '/accounts/login' in final or '/challenge/' in final:
            raise ValueError('Public route requires login or challenge; not followed further')
        raw=response.read(18_000_001 if media else 6_000_001)
        if len(raw)>(18_000_000 if media else 6_000_000):raise ValueError('Response too large')
        return raw,final,response.status

def walk(value):
    if isinstance(value,dict):
        yield value
        for v in value.values():yield from walk(v)
    elif isinstance(value,list):
        for v in value:yield from walk(v)

def candidates(soup,shortcode):
    result=[]
    # Dedicated media element of the public embedded post, never the avatar.
    for image in soup.select('img.EmbeddedMediaImage'):
        src=image.get('src')
        if src:result.append((html.unescape(src),image.get('alt',''),'public-post-embed'))
    for script in soup.find_all('script',type='application/json'):
        try:data=json.loads(script.string or script.get_text())
        except (ValueError,TypeError):continue
        for node in walk(data):
            if node.get('shortcode')!=shortcode and node.get('code')!=shortcode:continue
            src=node.get('display_url') or node.get('display_src')
            if src:result.append((src,node.get('accessibility_caption',''),'matching-shortcode-json'))
            versions=node.get('image_versions2',{}).get('candidates',[])
            versions=sorted(versions,key=lambda x:x.get('width',0)*x.get('height',0),reverse=True)
            for version in versions[:1]:
                if version.get('url'):result.append((version['url'],node.get('accessibility_caption',''),'matching-shortcode-json'))
    canonical=soup.select_one('meta[property="og:url"],link[rel="canonical"]')
    canonical_url=(canonical.get('content')or canonical.get('href',''))if canonical else ''
    if '/'+shortcode+'/' in canonical_url:
        for meta in soup.select('meta[property="og:image"]'):
            if meta.get('content'):result.append((html.unescape(meta['content']),'','matching-canonical-og-image'))
    return result

def fetch_post(post):
    result=dict(post,status='unavailable',attempts=[])
    code=post['shortcode']
    for route in ['https://www.instagram.com/p/'+code+'/embed/captioned/',post['permalink']]:
        attempt={'route':route}
        try:
            raw,final,status=get(route)
            attempt.update(status=status,final_url=final,bytes=len(raw))
            soup=BeautifulSoup(raw.decode('utf-8','replace'),'html.parser')
            attempt['title']=soup.title.get_text(' ',strip=True)[:240]if soup.title else ''
            attempt['visible_excerpt']=soup.get_text(' ',strip=True)[:750]
            options=candidates(soup,code)
            attempt['media_candidates']=len(options)
            for src,alt,evidence in options:
                try:
                    data,_,_=get(src,media=True)
                    image=ImageOps.exif_transpose(Image.open(io.BytesIO(data)));image.load()
                    if min(image.size)<240:raise ValueError('Image is too small for a post photo')
                    if image.width==image.height and image.width<=320:raise ValueError('Possible profile avatar; not accepted')
                    image=image.convert('RGB');image.thumbnail((1600,1600))
                    path=ASSETS/(code+'.webp');image.save(path,quality=90,method=6)
                    result.update(status='downloaded',image='assets/instagram-selected/'+code+'.webp',alt=alt or 'Ausgewählter Beitrag von @'+post['account'],image_source=src,evidence=evidence,width=image.width,height=image.height,sha256=hashlib.sha256(data).hexdigest())
                    caption=soup.select_one('.Caption')
                    if caption:result['caption']=caption.get_text(' ',strip=True)[:1600]
                    result['attempts'].append(attempt)
                    return result
                except Exception as exc:
                    attempt.setdefault('media_errors',[]).append(type(exc).__name__+': '+str(exc)[:220])
        except Exception as exc:
            attempt['error']=type(exc).__name__+': '+str(exc)[:240]
        result['attempts'].append(attempt)
    return result

if __name__=='__main__':
    with ThreadPoolExecutor(max_workers=2)as pool:posts=list(pool.map(fetch_post,SPEC['posts']))
    report={'selection_id':SPEC['selection_id'],'checked_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'posts':posts,'requested':len(posts),'downloaded':sum(x['status']=='downloaded'for x in posts),'live_instagram_connected':False,'layouts_changed':False}
    (OUT/'import.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
    if report['downloaded']:
        sheet=Image.new('RGB',(900,((len(posts)+2)//3)*390),'white');draw=ImageDraw.Draw(sheet)
        for i,post in enumerate(posts):
            x=(i%3)*300;y=(i//3)*390
            if post['status']=='downloaded':
                im=Image.open(ROOT/'site'/post['image']);im.thumbnail((284,330));sheet.paste(im,(x+(300-im.width)//2,y+5))
            draw.text((x+8,y+343),str(post['order'])+' · '+post['shortcode'],fill='black')
            draw.text((x+8,y+363),post['status'],fill='black')
        sheet.save(OUT/'contact-sheet.jpg',quality=93)
    print(json.dumps({'requested':report['requested'],'downloaded':report['downloaded'],'posts':[{'shortcode':p['shortcode'],'status':p['status'],'attempts':p['attempts']}for p in posts]},ensure_ascii=False,indent=2))
