"""Import the actual extracted PNGs, not contact sheets, RAW crops or guide masks.
Single-image URLs below are temporary read links to artwork approved for publication.
The generated site uses only local files, never these signed URLs.
"""
from pathlib import Path
from urllib.request import Request,urlopen
from concurrent.futures import ThreadPoolExecutor
from PIL import Image, ImageDraw, ImageFilter
import io,json,hashlib,numpy as np
R=Path(__file__).resolve().parents[1]; OUT=R/'site/assets/responsive10';OUT.mkdir(parents=True,exist_ok=True)
SOURCES={
'bottle-ink':'https://d2jqrm6oza8nb6.cloudfront.net/datasets/26e4b5c1-6947-4138-9a06-685b4f7540a6.png?_jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJrZXlIYXNoIjoiMjA3NjE2Nzk5NWY2YzQzNiIsImJ1Y2tldCI6InJ1bndheS1kYXRhc2V0cyIsInN0YWdlIjoicHJvZCIsImV4cCI6MTc4OTk3OTUxM30.DKIwfj415iXO6Fynhp-3rv0koydZzVzgVPK5RahvEgM',
'conservas':'https://d2jqrm6oza8nb6.cloudfront.net/datasets/93078a03-6973-4855-a5ea-49caeaa4b21b.png?_jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJrZXlIYXNoIjoiNTRiZTcyODRhYjFlNjM2OSIsImJ1Y2tldCI6InJ1bndheS1kYXRhc2V0cyIsInN0YWdlIjoicHJvZCIsImV4cCI6MTc5MDAwNDEwMH0.48y9fgLthgpA1lYf0suvQkgVpTwpK6NmK1yY1iYnVjE',
'herbs':'https://d2jqrm6oza8nb6.cloudfront.net/datasets/aabbc98c-d298-43ea-829f-de4fc10a8c5d.png?_jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJrZXlIYXNoIjoiMDMxZTRhYTU4NjA1ZGYzMCIsImJ1Y2tldCI6InJ1bndheS1kYXRhc2V0cyIsInN0YWdlIjoicHJvZCIsImV4cCI6MTc4OTk5MzYzN30.nrKyulUpcgzMjqzBIhE74SHQWZJeRIdp8hGPFyc8a8o',
'olives':'https://d2jqrm6oza8nb6.cloudfront.net/datasets/899fb3b3-bc73-4aea-ae77-857e9ffd22f8.png?_jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJrZXlIYXNoIjoiYmZmZDExMzY3ZDhmNGEwYyIsImJ1Y2tldCI6InJ1bndheS1kYXRhc2V0cyIsInN0YWdlIjoicHJvZCIsImV4cCI6MTc4OTk5MDA3MH0.1tBrihv9JUtaYsLvlpCAA73C3Ew0oawWYJ163PqdmEk',
'wine-paper':'https://d2jqrm6oza8nb6.cloudfront.net/datasets/1eb711df-9e26-4513-a262-1b155deb4c4b.png?_jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJrZXlIYXNoIjoiZGVjZjlhMjk5MTkzOTJiYiIsImJ1Y2tldCI6InJ1bndheS1kYXRhc2V0cyIsInN0YWdlIjoicHJvZCIsImV4cCI6MTc5MDAwMDE2OX0.pl-bC3stSOB97XBYwUFEIqJGvWjIG0-YdzPhe_5bcN0',
'footer-paint':'https://d2jqrm6oza8nb6.cloudfront.net/datasets/f9b5612e-3308-4eb3-b3ea-284537cc8191.png?_jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJrZXlIYXNoIjoiZjkxM2I3YjRkNWE2NDkxMiIsImJ1Y2tldCI6InJ1bndheS1kYXRhc2V0cyIsInN0YWdlIjoicHJvZCIsImV4cCI6MTc4OTk0NTM5Nn0.9ZkJfqREwDG8SE8w_gcKgOq27aElB0s0S95zi-S9alA'
}
def read_one(pair):
 name,url=pair;p=OUT/(name+'.png')
 if p.exists():raw=p.read_bytes()
 else:
  with urlopen(Request(url,headers={'User-Agent':'Vineria approved asset import'}),timeout=40)as res:raw=res.read(12000001)
  if len(raw)>12000000:raise ValueError('Asset exceeds allowed size')
 im=Image.open(io.BytesIO(raw));im.load();assert im.format=='PNG',name
 rgba=im.convert('RGBA');a=np.array(rgba.getchannel('A'));assert a.min()==0 and a.max()>180,name+' lacks actual transparency'
 arr=np.array(rgba);red=((arr[:,:,0].astype(int)>arr[:,:,1].astype(int)+65)&(arr[:,:,0].astype(int)>arr[:,:,2].astype(int)+65)&(a>150)).sum()
 assert red<max(20,rgba.width*rgba.height*.002),name+' may contain red work guides'
 # Crop only fully transparent exterior padding. Preserve actual artwork and its ink grain.
 box=rgba.getchannel('A').getbbox();rgba=rgba.crop(box);rgba.save(p,optimize=True)
 return {'name':name,'file':p.name,'size':list(rgba.size),'transparent_fraction':round(float(np.mean(a==0)),4),'source_sha256':hashlib.sha256(raw).hexdigest(),'work_guides_detected':False,'method':'provided PNG with original alpha; transparent margins trimmed'}
def save_rgba(name,im):
 box=im.getchannel('A').getbbox();im=im.crop(box);im.save(OUT/(name+'.png'),optimize=True)
def run():
 with ThreadPoolExecutor(max_workers=4)as ex:report=list(ex.map(read_one,SOURCES.items()))
 original=Image.open(R/'site/assets/lab/reference-original.png').convert('RGB')
 def ink(name,box,threshold=172):
  src=original.crop(box);g=np.array(src.convert('L')).astype(float);alpha=np.uint8(np.clip((threshold-g)/(threshold-32)*255,0,255));out=Image.new('RGBA',src.size,(30,29,25,0));out.putalpha(Image.fromarray(alpha));save_rgba(name,out)
 ink('wordmark',(16,2,247,142),182)
 ink('good-wine',(59,155,284,313),171)
 ink('salud',(884,649,1004,719),165)
 # An irregular, feathered photograph silhouette instead of a rectangular screenshot tile.
 box=(0,313,600,870);im=original.crop(box).convert('RGBA');mask=Image.new('L',im.size,0);draw=ImageDraw.Draw(mask)
 pts=[(0,17),(52,0),(131,11),(215,28),(322,5),(430,0),(549,11),(575,155),(585,277),(598,475),(565,506),(481,536),(387,523),(296,552),(164,535),(79,550),(0,520)]
 draw.polygon(pts,fill=255);im.putalpha(mask.filter(ImageFilter.GaussianBlur(.6)));save_rgba('toast-photo',im)
 # Physical masking provides torn-paper edges around the Tienda note; printed letters retained.
 box=(918,484,1148,641);im=original.crop(box).convert('RGBA');mask=Image.new('L',im.size,0);ImageDraw.Draw(mask).polygon([(3,1),(219,7),(228,132),(202,138),(160,151),(107,147),(48,155),(2,140)],fill=255);im.putalpha(mask);save_rgba('tienda-note',im)
 # Paper background is continuous multi-scale grain, not repeated screenshot squares.
 rng=np.random.default_rng(412);size=(1600,1600)
 low=Image.fromarray(np.uint8(rng.uniform(90,166,(28,28)))).resize(size,Image.Resampling.BICUBIC).filter(ImageFilter.GaussianBlur(24))
 mid=Image.fromarray(np.uint8(rng.uniform(98,158,(220,220)))).resize(size,Image.Resampling.BICUBIC)
 grain=(np.array(low).astype(float)-128)*.12+(np.array(mid).astype(float)-128)*.075+rng.normal(0,1.2,(1600,1600))
 paper=np.stack([235+grain,229+grain,214+grain],axis=2).clip(0,255).astype('uint8');Image.fromarray(paper).save(OUT/'paper-grain.jpg',quality=88)
 # A footer edge can grow independently from the real HTML footer text.
 ft=Image.open(OUT/'footer-paint.png').convert('RGBA');ft.crop((0,0,ft.width,min(100,ft.height))).save(OUT/'footer-edge.png')
 sheet=Image.new('RGB',(1200,750),(234,228,214));d=ImageDraw.Draw(sheet)
 names=['bottle-ink','conservas','herbs','olives','wine-paper','tienda-note']
 for i,name in enumerate(names):
  im=Image.open(OUT/(name+'.png')).convert('RGBA');im.thumbnail((350,310));x=(i%3)*400+(400-im.width)//2;y=(i//3)*375+20;sheet.paste(im,(x,y),im);d.text(((i%3)*400+20,(i//3)*375+345),name,fill=(25,25,25))
 sheet.save(OUT/'layers-on-paper.jpg',quality=92)
 audit={'layers':report,'guides_and_raw_in_site':False,'paper_background':'continuous multiscale paper grain, no tiled screenshot','photo':'same supplied photograph with irregular mask, no regenerated faces','footer':'provided reconstructed paint, not unrecoverable original hidden pixels'}
 (OUT/'asset-audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2));print(json.dumps(audit,ensure_ascii=False))
if __name__=='__main__':run()
