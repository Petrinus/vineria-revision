"""Read-only HTTP delivery checks for the committed client review."""
from pathlib import Path
from urllib.request import Request,urlopen
from bs4 import BeautifulSoup
import json,subprocess,time
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'reports/design-lab';OUT.mkdir(parents=True,exist_ok=True)
revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
base='https://rawcdn.githack.com/Petrinus/vineria-revision/'+revision+'/site/'
report={'revision':revision,'pages':[]}
routes=[('index.html','[data-proposal]',10),('entwuerfe/v09/index.html','.punk-hero',1),('entwuerfe/v09/shop/index.html','.lab-shop-lead',1),('entwuerfe/v10/index.html','.replica-board',1),('entwuerfe/v10/shop/index.html','.lab-shop-lead',1),('verwaltung/vorschau.html','#vde-control',1)]
for route,selector,expected in routes:
 row={'url':base+route,'expected':expected}
 for attempt in range(2):
  try:
   with urlopen(Request(base+route,headers={'User-Agent':'Mozilla/5.0'}),timeout=30)as r:status=r.status;raw=r.read().decode('utf-8')
   doc=BeautifulSoup(raw,'html.parser');row.update(status=status,matching_elements=len(doc.select(selector)),title=doc.title.get_text()if doc.title else '')
   row['verified']=status==200 and row['matching_elements']==expected
   if row['verified']:break
  except Exception as exc:row['error']=str(exc);row['verified']=False
  if attempt==0:time.sleep(2)
 report['pages'].append(row)
report['verified']=all(x['verified']for x in report['pages'])
(OUT/'public.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));(OUT/'published-revision.txt').write_text(revision+'\n');print(json.dumps(report,ensure_ascii=False,indent=2))
if not report['verified']:raise SystemExit('Public delivery did not pass every check')
