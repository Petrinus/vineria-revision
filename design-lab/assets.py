"""Approved source crops and graphic variants. Never redraw people or reference icons."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageOps, ImageFilter
import numpy as np, json, io, hashlib
from urllib.request import Request, urlopen
from concurrent.futures import ThreadPoolExecutor
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'site/assets/lab'; OUT.mkdir(parents=True,exist_ok=True)
INPUT=ROOT/'design-lab/input'; INPUT.mkdir(parents=True,exist_ok=True)
POSTS={'wine-shelf':'DSDZcT3DI2I','asparagus':'DKU9PzaMm1w','octopus':'Ckbmq6yMEWS','prawns':'CgpJbcXjyWV','paella':'BuzCKLOho7i','dessert':'BvhPAb1HqoM'}
BOXES={'wordmark':[0,0,256,145],'navigation':[256,0,1217,145],'left-collage':[0,145,603,868],'headline':[604,172,898,564],'intro-copy':[618,570,870,661],'menu-button':[624,674,854,725],'reservation-button':[624,732,854,786],'bottle':[900,110,1217,485],'tienda-note':[918,484,1147,640],'salud':[874,640,1007,731],'facade':[1007,640,1217,868],'olives':[269,919,438,1064],'herbs':[601,920,759,1066],'tin':[989,934,1185,1065],'footer':[0,1086,1217,1280]}
def get(name,url):
 p=INPUT/(name+'.png')
 if not p.exists():
  local=Path('/mnt/data/image.png') if name=='reference' else Path('/mnt/data')/(name+'-cut.png')
  if local.exists():Image.open(local).save(p)
  else:
   with urlopen(Request(url,headers={'User-Agent':'Vineria approved design asset import'}),timeout=40)as r:raw=r.read(18000001)
   if len(raw)>18000000:raise ValueError('Image exceeds limit')
   im=Image.open(io.BytesIO(raw));im.load();im.save(p)
 return name,p

def halftone(image):
 im=image.convert('RGB');im.thumbnail((1400,1400));g=np.asarray(im.convert('L'),dtype=float)
 tone=np.clip((242-g)/225,0,1);tone[tone<.055]=0
 soft=np.asarray(Image.fromarray(np.uint8(tone*255)).filter(ImageFilter.GaussianBlur(.65)))/255
 y,x=np.indices(g.shape);u=(x+y)/2**.5;v=(y-x)/2**.5;pitch=5.8
 dist=np.sqrt(((u/pitch+.5)%1-.5)**2+((v/pitch+.5)%1-.5)**2)
 a=np.clip((np.sqrt(soft/np.pi)-dist)*pitch+.5,0,1)
 a=np.maximum(a,np.clip((tone-.84)*7,0,1));result=Image.new('RGBA',im.size,(0,0,0,0));result.putalpha(Image.fromarray(np.uint8(a*255)));return result

def run():
 sources=json.loads((ROOT/'design-lab/public-images.json').read_text())
 with ThreadPoolExecutor(max_workers=5)as pool: inputs=dict(pool.map(lambda kv:get(*kv),sources.items()))
 reference=Image.open(inputs['reference']).convert('RGBA');assert reference.size==(1217,1280),reference.size
 reference.save(OUT/'reference-original.png');base=reference.copy();d=ImageDraw.Draw(base)
 for name,box in BOXES.items():
  tile=reference.crop(box)
  if name=='footer':
   dr=ImageDraw.Draw(tile);dr.rectangle((290,38,935,128),fill=(45,44,41,255))
  tile.save(OUT/(name+'.webp'),lossless=True)
  d.rectangle((box[0],box[1],box[2]-1,box[3]-1),fill=(0,0,0,0))
 base.save(OUT/'layout-paper.webp',lossless=True)
 reference.crop((815,746,907,849)).save(OUT/'paper-tile.webp',lossless=True)
 reference.crop((825,1121,898,1132)).resize((219,33)).save(OUT/'ink-tile.webp',lossless=True)
 report={'source_sha256':hashlib.sha256(inputs['reference'].read_bytes()).hexdigest(),'source_size':list(reference.size),'crops':BOXES,'text_style':'Raster heading/lettering retained from source; live text uses matching serif and sans families','exceptions':['Correct restaurant contact information replaces mockup placeholder details','Mobile layout reflows for readability'],'graphics':[]}
 for name,code in POSTS.items():
  im=Image.open(inputs[name]).convert('RGB');im.thumbnail((1400,1400));im.save(OUT/(name+'-color.webp'),quality=93)
  bw=halftone(im);bw.save(OUT/(name+'-copy.webp'),lossless=True)
  a=np.asarray(im).min(axis=2);rgba=im.convert('RGBA');rgba.putalpha(Image.fromarray(np.uint8(np.clip((254-a.astype(float))*255/17,0,255))));rgba.save(OUT/(name+'-cut.webp'),quality=93)
  report['graphics'].append({'name':name,'post':code,'color':name+'-color.webp','monochrome':name+'-copy.webp','illustration_not_photo':True})
 for name in ['owner','portrait']:
  im=Image.open(inputs[name]).convert('RGBA');a=im.getchannel('A');assert a.getextrema()[0]==0,name+' needs true alpha'
  box=a.getbbox();im=im.crop(box);im.thumbnail((700,900));im.save(OUT/(name+'-cut.webp'),lossless=True)
  rgb=ImageOps.grayscale(im).convert('RGBA');rgb.putalpha(im.getchannel('A'));rgb.save(OUT/(name+'-mono.webp'),lossless=True)
  report[name]={'source_sha256':hashlib.sha256(inputs[name].read_bytes()).hexdigest(),'segmentation_only':True,'face_regenerated':False,'bbox':box}
 rng=np.random.default_rng(9130);tex=Image.new('RGBA',(1100,800),(0,0,0,0));draw=ImageDraw.Draw(tex)
 for i in range(5300):
  x,y=map(int,[rng.integers(0,1100),rng.integers(0,800)]);r=float(rng.choice([.5,1,1.5,2.5,4,8],p=[.2,.4,.23,.1,.05,.02]));draw.ellipse((x-r,y-r,x+r,y+r),fill=(14,13,12,int(rng.integers(50,170))))
 for i in range(105):
  x,y=map(int,[rng.integers(0,1100),rng.integers(0,800)]);draw.line((x,y,x+int(rng.integers(3,80)),y+int(rng.integers(-12,12))),fill=(15,14,12,70),width=1)
 tex.save(OUT/'ink-dirt.webp',lossless=True)
 (OUT/'extraction.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
 print(json.dumps({'graphics':len(POSTS)*2,'separate_crops':len(BOXES),'owner_and_portrait':True},indent=2))
if __name__=='__main__':run()
