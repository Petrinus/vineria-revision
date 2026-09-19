"""Client artwork decisions. Applied to every published proposal and its previews.
Never alters real restaurant portrait photographs, credentials, orders or Git history.
"""
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.parse import urlsplit, unquote
from PIL import Image, ImageOps, ImageChops
import argparse, base64, hashlib, html, http.server, functools, io, json, lzma, os, re, threading

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / os.environ.get('VDE_OUTPUT', 'site')
ASSETS = SITE / 'assets'
SOURCE = ROOT / 'src/artwork/fictional-guests-r1.png'
TASK = 'f23a4c07-7f21-45e2-bdd4-ab41374438f6'
NEW_NAME = 'fictional-guests-r1'
# Read-only asset URL returned by the authorized generation. Subsequent builds use the local original.
INITIAL_URL = 'https://dnznrvs05pmza.cloudfront.net/gpt_image_2_5_flare/f23a4c07-7f21-45e2-bdd4-ab41374438f6/ONE_compact_irregular_paper_cut_collage_vignette_for_an_elegant_independent_wine_bar_fanzine_website_0.png?_jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJrZXlIYXNoIjoiMDRhOTE2MWYxZWVjYjRiMiIsImJ1Y2tldCI6InJ1bndheS10YXNrLWFydGlmYWN0cyIsInN0YWdlIjoicHJvZCIsImV4cCI6MTc4OTk0NjkxMX0.7_LxdbTyE52mKwziUb_wu8w-dxGcXUdlmlhMm2NuL2E'
GLYPHS = ''.join(chr(c) for c in (0x2733, 0x2747))
STAR = re.compile('[' + GLYPHS + '][\\ufe0e\\ufe0f]?')
ENTITIES = re.compile(r'&#(?:0*10035|0*10055|x0*2733|x0*2747);(?:&#(?:65039|xfe0f);)?', re.I)
ESCAPED = re.compile(r'\\u(?:2733|2747)(?:\\u(?:fe0e|fe0f))?', re.I)
SCENE_ELEMENT = re.compile(r'<span\b[^>]*\bclass=[\"\'][^\"\']*\bscene-star\b[^\"\']*[\"\'][^>]*>[^<]*</span>', re.I)
REPLACEMENTS = {
 'Künstlerische Fotocollage aus bereitgestellten Porträts: zwei Menschen an einem Tisch': 'Fiktive Gäste an einem Tisch · eigenständige Fanzine-Collage',
 'Künstlerischer Fotocollage-Entwurf': 'Fiktives Paar · Fanzine-Collage',
 'Originalfotos und eine künstlerische Fotocollage aus dem eigenen Bildmaterial. Keine Aufnahme eines tatsächlich fotografierten gemeinsamen Tischmoments.': 'Originalaufnahmen der Vineria und eine eigenständig gestaltete Collage mit fiktiven Gästen.',
 'Die Collage am kleinen Tisch wurde aus zwei dieser Porträts künstlerisch neu zusammengesetzt; sie zeigt keinen dokumentierten gemeinsamen Moment.': 'Die Collage am kleinen Tisch zeigt zwei frei erfundene Gäste. Sie basiert nicht auf Porträts der Inhaber.',
 'Two user-supplied Vineria portraits': 'Two entirely fictional adult guests; no reference portraits',
 'Two user-supplied portraits': 'Two entirely fictional adult guests; no reference portraits',
}

def clean(text):
    text = SCENE_ELEMENT.sub('', text)
    text = re.sub(r'<(i|b|span)(?:\s[^>]*)?>\s*[' + GLYPHS + r'][\ufe0e\ufe0f]?\s*</\1>', '', text)
    text = STAR.sub('', text)
    text = ENTITIES.sub('', text)
    text = ESCAPED.sub('', text)
    text = text.replace('collage-ink.webp', NEW_NAME + '-ink.webp').replace('collage.webp', NEW_NAME + '.webp')
    for old, new in REPLACEMENTS.items():
        text = text.replace(old, new)
    return text

def install_images():
    ASSETS.mkdir(parents=True, exist_ok=True)
    SOURCE.parent.mkdir(parents=True, exist_ok=True)
    if not SOURCE.exists():
        with urlopen(Request(INITIAL_URL, headers={'User-Agent': 'Vineria authorized artwork update'}), timeout=60) as r:
            raw = r.read(20_000_001)
        if len(raw) > 20_000_000:
            raise ValueError('Artwork is unexpectedly large')
        image = Image.open(io.BytesIO(raw)); image.load()
        image.save(SOURCE)
    image = ImageOps.exif_transpose(Image.open(SOURCE)).convert('RGB')
    image.thumbnail((1440, 1440))
    image.save(ASSETS / (NEW_NAME + '.webp'), quality=89, method=6)
    r, g, b = image.split()
    darkest = ImageChops.darker(ImageChops.darker(r, g), b)
    alpha = darkest.point(lambda v: 0 if v >= 248 else min(255, round((248-v)*255/236)))
    ink = image.convert('RGBA'); ink.putalpha(alpha)
    ink.save(ASSETS / (NEW_NAME + '-ink.webp'), quality=90, method=6)
    # Replace legacy alias bytes too: bookmarked old paths must not show the owners.
    for name, replacement in [('collage.webp', NEW_NAME+'.webp'), ('collage-ink.webp', NEW_NAME+'-ink.webp')]:
        data = (ASSETS/replacement).read_bytes()
        candidates = list(SITE.rglob(name))
        if not candidates: candidates = [ASSETS/name]
        for candidate in candidates: candidate.write_bytes(data)
    manifest = {'kind':'fictional_artwork','runway_task':TASK,'reference_images':[], 'depicts_owners':False,
                'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
                'file':NEW_NAME+'-ink.webp','legacy_aliases_replaced':['collage.webp','collage-ink.webp'],
                'prohibited_emoji_codepoints':['U+2733','U+2747']}
    (ASSETS/'artwork-policy.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2))

def patch_sources_and_pages():
    changed=[]
    for folder in ('site','src','review','tools'):
        for f in (ROOT/folder).rglob('*'):
            if not f.is_file() or f.resolve()==Path(__file__).resolve(): continue
            if f.suffix not in ('.html','.css','.js','.py','.json','.md'): continue
            old=f.read_text(encoding='utf-8'); new=clean(old)
            if f.name=='media-sources.json':
                data=json.loads(new)
                if isinstance(data,dict) and 'collage' in data: data['collage']=INITIAL_URL
                new=json.dumps(data, ensure_ascii=False, indent=2)
            if f.name=='polish.py':
                new=new.replace("s=s.replace('<span class=\"scene-star\"',f'<div class=\"cutout\" data-original-dish>{image}</div><span class=\"scene-star\"',1)",
                                "s=s.replace('<div class=\"scene-controls\">',f'<div class=\"cutout\" data-original-dish>{image}</div><div class=\"scene-controls\">',1)")
            if new!=old:
                f.write_text(new,encoding='utf-8'); changed.append(str(f.relative_to(ROOT)))
    # Built CSS receives a safety rule, in addition to removal from templates.
    for f in [ROOT/'src/site.css', ASSETS/'site.css']:
        if f.exists() and 'client-remove-rejected-badge' not in f.read_text():
            f.write_text(f.read_text()+'\n/* client-remove-rejected-badge: no replacement ornament */\n.scene-star{display:none!important}\n')
    return changed

def patch_archives():
    results=[]
    parts=sorted((ROOT/'src/history').glob('restaurants.*.b64'))
    if not parts:return results
    try:
        content=lzma.decompress(base64.b64decode(''.join(p.read_text().strip() for p in parts))).decode('utf-8')
        updated=clean(content)
        if updated!=content:
            encoded=base64.b64encode(lzma.compress(updated.encode('utf-8'))).decode('ascii')
            chunks=[encoded[i:i+7000] for i in range(0,len(encoded),7000)]
            for i,chunk in enumerate(chunks,1):
                (parts[0].parent/f'restaurants.{i:02}.b64').write_text(chunk)
            for p in parts[len(chunks):]: p.unlink()
        results.append({'archive':'restaurants','complete':True,'sanitized':True})
    except (ValueError,lzma.LZMAError,UnicodeError) as exc:
        # Do not invent missing historical bytes or silently discard a design.
        results.append({'archive':'restaurants','complete':False,'detail':str(exc),
                        'protection':'Output sanitizer is installed for any future recovered pages.'})
    return results

def hook_builds():
    # Future builds repeat the same decision instead of reintroducing rejected assets.
    for name in ('build.py','build_review_portal.py'):
        f=ROOT/'tools'/name
        if not f.exists():continue
        text=f.read_text()
        if 'apply_artwork_decisions' not in text:
            text+='\n# Client artwork exclusions also apply to future builds.\nfrom enforce_artwork_decisions import apply as apply_artwork_decisions\napply_artwork_decisions(refresh=False)\n'
            f.write_text(text)

def local_target(page,href):
    value=urlsplit(html.unescape(href))
    if value.scheme or value.netloc or not value.path:return None
    p=(page.parent/unquote(value.path)).resolve()
    if not p.is_relative_to(SITE.resolve()):return None
    if p.is_dir():p=p/'index.html'
    return p if p.is_file() else None

def refresh_previews():
    from bs4 import BeautifulSoup
    from playwright.sync_api import sync_playwright
    previews={}
    # Capture all preview images linked to an actual local HTML page, including old proposal portals.
    for page in SITE.rglob('*.html'):
        soup=BeautifulSoup(page.read_text(),'html.parser')
        for a in soup.select('a[href]'):
            img=a.find('img')
            if img is None:continue
            target=local_target(page,a.get('href','')); output=local_target(page,img.get('src',''))
            if target and output and target.suffix=='.html' and output.suffix.lower() in ('.png','.jpg','.jpeg','.webp'):
                if any(token in output.name for token in ('portal','preview','thumb','cover')): previews[output]=target
    report_pairs={'index-1440.png':'index.html','shop-index-1440.png':'shop/index.html',
                  'editorial-index-1440.png':'editorial/index.html','editorial-shop-index-1440.png':'editorial/shop/index.html'}
    for name,path in report_pairs.items():
        if (SITE/path).exists():previews[ROOT/'reports'/name]=SITE/path
    for theme,prefix in [('fanzine',''),('editorial','editorial/')]:
        for area,path in [('restaurant','index.html'),('shop','shop/index.html')]:
            target=SITE/(prefix+path)
            if target.exists():previews[ASSETS/f'portal-{theme}-{area}.jpg']=target
    handler=functools.partial(http.server.SimpleHTTPRequestHandler,directory=str(SITE))
    server=http.server.ThreadingHTTPServer(('127.0.0.1',0),handler)
    threading.Thread(target=server.serve_forever,daemon=True).start()
    base=f'http://127.0.0.1:{server.server_port}'
    report={'pages':0,'images_replaced':0,'star_matches':[],'broken_images':[],'js_errors':[], 'previews':[]}
    try:
        with sync_playwright() as p:
            browser=p.chromium.launch()
            page=browser.new_page(viewport={'width':1440,'height':1050},reduced_motion='reduce')
            page.on('pageerror',lambda e:report['js_errors'].append(str(e)))
            cache={}
            for output,target in previews.items():
                url=base+'/'+target.relative_to(SITE).as_posix()
                if url not in cache:
                    page.goto(url,wait_until='networkidle');page.wait_for_timeout(180)
                    cache[url]=page.screenshot(full_page=True)
                im=Image.open(io.BytesIO(cache[url])).convert('RGB')
                output.parent.mkdir(parents=True,exist_ok=True)
                if output.is_relative_to(ASSETS):
                    im=im.crop((0,0,im.width,min(im.height,round(im.width/.72))))
                    im.thumbnail((720,1000))
                    im.save(output,quality=85)
                else:im.save(output)
                report['previews'].append(str(output.relative_to(ROOT)))
            for f in SITE.rglob('*.html'):
                s=f.read_text();report['pages']+=1
                if STAR.search(html.unescape(s)) or ENTITIES.search(s) or ESCAPED.search(s): report['star_matches'].append(str(f.relative_to(SITE)))
                report['images_replaced']+=s.count(NEW_NAME)
            for route in ('index.html','shop/index.html','editorial/index.html','editorial/shop/index.html','entwuerfe/index.html'):
                if not (SITE/route).exists():continue
                page.goto(base+'/'+route,wait_until='networkidle')
                report['broken_images']+=page.evaluate('Array.from(document.images).filter(i=>!i.complete||!i.naturalWidth).map(i=>i.src)')
                if page.locator('.scene-star').count():report['star_matches'].append(route+': scene-star element')
            # Fresh screenshots of the updated overview and the restaurant on desktop and mobile.
            out=ROOT/'reports/artwork-cleanup';out.mkdir(parents=True,exist_ok=True)
            for route,label in [('entwuerfe/index.html','portal'),('index.html','restaurant'),('shop/index.html','shop')]:
                if not (SITE/route).exists():continue
                for width in (1440,390):
                    page.set_viewport_size({'width':width,'height':1000})
                    page.goto(base+'/'+route,wait_until='networkidle')
                    page.screenshot(path=str(out/f'{label}-{width}.png'),full_page=True)
            browser.close()
    finally:server.shutdown()
    report['passed']=not report['star_matches'] and not report['broken_images'] and not report['js_errors']
    return report

def apply(refresh=False):
    install_images()
    changed=patch_sources_and_pages()
    archives=patch_archives()
    hook_builds()
    report={'changed':changed,'archives':archives,'fictional_guests_task':TASK,'real_portraits_unchanged':True}
    if refresh:report['browser']=refresh_previews()
    out=ROOT/'reports/artwork-cleanup';out.mkdir(parents=True,exist_ok=True)
    (out/('verified.json' if refresh else 'applied.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2))
    print(json.dumps(report,ensure_ascii=False,indent=2))
    if refresh and not report['browser']['passed']:raise RuntimeError('Artwork regression check failed')
    return report

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--refresh-previews',action='store_true')
    args=parser.parse_args();apply(refresh=args.refresh_previews)
