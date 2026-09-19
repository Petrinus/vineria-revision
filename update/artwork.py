"""Reproducible print treatment; preserves approved compositions and original logo."""
from pathlib import Path
from PIL import Image, ImageOps, ImageFilter
import numpy as np, json, math, hashlib, shutil
ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT/'site/assets/approved';DEST.mkdir(parents=True,exist_ok=True)
INPUT=ROOT/'update/input';INPUT.mkdir(parents=True,exist_ok=True)
LOCAL={'pulpo':'pulpo_a_la_gallega_en_cazuela.png','boquerones':'sardellenplatte_mit_oliven_und_kapern.png','paella':'paella_marinera_ilustrada_a_tinta_y_acuarela.png','logo':'A96D2EB7-0321-462C-90AA-B73F82EA2DD3.png','marca-bn':'EB1C34AC-6620-40C9-B449-8856ADF52CFD.png'}
def source(name):
 p=INPUT/(name+'.png')
 if p.exists():return p
 loc=Path('/mnt/data')/LOCAL[name]
 if loc.exists():shutil.copyfile(loc,p);return p
 from urllib.request import Request,urlopen
 urls=json.loads((ROOT/'update/media-inputs.json').read_text())
 with urlopen(Request(urls[name],headers={'User-Agent':'Vineria artwork import'}),timeout=40) as r: raw=r.read(20000000)
 Image.open(__import__('io').BytesIO(raw)).verify()
 p.write_bytes(raw);return p

def screen(im):
 im=ImageOps.exif_transpose(im).convert('RGB');im.thumbnail((1500,1500))
 gray=np.asarray(im.convert('L'),dtype=np.float32)
 tone=np.clip((231-gray)/206,0,1)**.90
 tone[tone<.072]=0
 sm=np.asarray(Image.fromarray(np.uint8(tone*255)).filter(ImageFilter.GaussianBlur(1.35)),dtype=float)/255
 y,x=np.indices(tone.shape);a=np.pi/4
 u=x*np.cos(a)+y*np.sin(a);v=-x*np.sin(a)+y*np.cos(a)
 pitch=8.5
 dx=(u/pitch+.5)%1-.5;dy=(v/pitch+.5)%1-.5
 distance=np.sqrt(dx*dx+dy*dy)
 radius=np.sqrt(sm/np.pi)
 dots=np.clip((radius-distance)*pitch+.5,0,1)
 ink=np.maximum(dots, np.clip((tone-.78)*5.5,0,1))
 rng=np.random.default_rng(20260919)
 grain=rng.random(tone.shape)
 ink[(grain<.009)&(ink>.6)]=0
 alpha=np.uint8(ink*255)
 result=Image.new('RGBA',im.size,(0,0,0,0));result.putalpha(Image.fromarray(alpha))
 return result

if __name__=='__main__':
 report=[]
 for name in ['pulpo','boquerones','paella']:
  p=source(name);im=Image.open(p).convert('RGB');im.thumbnail((1500,1500))
  im.save(DEST/(name+'-color.webp'),quality=90)
  bw=screen(im);bw.save(DEST/(name+'-halftone.webp'),lossless=True)
  bw.save(DEST/(name+'-halftone.png'))
  proof=Image.new('RGBA',bw.size,'white');proof.alpha_composite(bw);proof.convert('RGB').save(DEST/(name+'-proof.jpg'),quality=92)
  assert bw.getchannel('A').getextrema()==(0,255)
  report.append({'name':name,'source_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'rgb_ink':[0,0,0],'alpha':True,'people':False})
 for name in ['logo','marca-bn']:
  p=source(name);shutil.copyfile(p,DEST/(name+'-original.png'))
  im=Image.open(p).convert('RGB');im.thumbnail((1200,1200));im.save(DEST/(name+'.webp'),quality=96)
 (DEST/'provenance.json').write_text(json.dumps({'artworks':report,'people_illustration_used':False,'logo_redrawn':False,'color_originals_preserved':True},indent=2))
