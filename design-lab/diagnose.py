from pathlib import Path
from playwright.sync_api import sync_playwright
from PIL import Image
import numpy as np,json,io,functools,http.server,threading
ROOT=Path(__file__).resolve().parents[1];SITE=ROOT/'site';OUT=ROOT/'reports/design-lab';OUT.mkdir(parents=True,exist_ok=True)
handler=functools.partial(http.server.SimpleHTTPRequestHandler,directory=str(SITE))
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),handler)
threading.Thread(target=server.serve_forever,daemon=True).start()
base=f'http://127.0.0.1:{server.server_port}/';report={}
try:
 with sync_playwright()as p:
  browser=p.chromium.launch();page=browser.new_page(viewport={'width':320,'height':900},reduced_motion='reduce')
  for route in ['entwuerfe/v09/index.html','entwuerfe/v09/shop/index.html']:
   page.goto(base+route,wait_until='networkidle')
   report[route]=page.locator('body *').evaluate_all('(xs)=>xs.map(e=>{const r=e.getBoundingClientRect();return {tag:e.tagName,cls:String(e.className),text:e.textContent.slice(0,50),x:r.x,right:r.right,w:r.width}}).filter(x=>x.w>0&&(x.right>innerWidth+1||x.x< -1)).slice(0,40)')
  page.set_viewport_size({'width':1440,'height':1000})
  page.goto(base+'entwuerfe/v10/index.html',wait_until='networkidle');page.mouse.move(0,0)
  board=page.locator('.replica-board');report['bounds']=board.bounding_box()
  report['pieces']=board.locator('[data-source-piece]').evaluate_all('(xs)=>xs.map(e=>({name:e.dataset.sourcePiece,x:e.getBoundingClientRect().x,y:e.getBoundingClientRect().y,width:e.getBoundingClientRect().width,height:e.getBoundingClientRect().height}))')
  actual=Image.open(io.BytesIO(board.screenshot())).convert('RGB').resize((1217,1280))
  reference=Image.open(SITE/'assets/lab/reference-original.png').convert('RGB').resize((1217,1280))
  a=np.asarray(actual,dtype=float);b=np.asarray(reference,dtype=float)
  report['row_error']=[{'from':i,'mae':round(float(np.mean(np.abs(a[i:i+100]-b[i:i+100]))),3)}for i in range(0,1280,100)]
  side=Image.new('RGB',(1460,768),'white');side.paste(reference.resize((730,768)),(0,0));side.paste(actual.resize((730,768)),(730,0));side.save(OUT/'v10-side-by-side.jpg',quality=94)
  for name,route in [('v09-home','entwuerfe/v09/index.html'),('v09-shop','entwuerfe/v09/shop/index.html')]:
   page.goto(base+route,wait_until='networkidle');im=Image.open(io.BytesIO(page.screenshot()));im.thumbnail((1000,750));im.convert('RGB').save(OUT/(name+'-small.jpg'),quality=94)
  browser.close()
finally:
 server.shutdown();(OUT/'diagnostics.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False,indent=2))
