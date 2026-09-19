"""Run against a disposable local PHP server; no real credentials or orders."""
from pathlib import Path
from urllib.request import build_opener,HTTPCookieProcessor,Request
from urllib.parse import urlencode
from urllib.error import HTTPError
from http.cookiejar import CookieJar
import os,sys,json,tempfile,shutil,subprocess,time,re,secrets
ROOT=Path(__file__).resolve().parent.parent;reports=ROOT/'reports';reports.mkdir(exist_ok=True);results=[]
def check(name,ok):results.append({'check':name,'pass':bool(ok)});print(('PASS ' if ok else 'FAIL ')+name,flush=True)
with tempfile.TemporaryDirectory(prefix='vineria-auth-test-') as tmp:
 t=Path(tmp)
 for folder in ['server','src','tools','site']:shutil.copytree(ROOT/folder,t/folder,ignore=shutil.ignore_patterns('__pycache__'))
 initial=secrets.token_urlsafe(18);newpass=secrets.token_urlsafe(24)
 env={**os.environ,'VDE_INITIAL_PASSWORD':initial,'VDE_LOCAL_TEST':'1','VDE_ORIGIN':'http://127.0.0.1:8831','VDE_PRIVATE_DIR':str(t/'private'),'VDE_PYTHON':sys.executable}
 for p in (t/'server').glob('*.php'):subprocess.run(['php','-l',str(p)],check=True,capture_output=True)
 check('PHP syntax',True)
 subprocess.run(['php',str(t/'server/setup.php')],env=env,cwd=t,check=True,capture_output=True)
 statefile=t/'private/state.json'
 def state():return json.loads(statefile.read_text())
 check('Two named accounts',sorted(x['name'] for x in state()['users'].values())==['Buñol','Kraft'])
 check('No plaintext initial password',initial not in statefile.read_text())
 check('Private storage outside public root',not (t/'site/private').exists())
 check('Initial password change required',all(x['must_change'] for x in state()['users'].values()))
 log=open(t/'php.log','w');proc=subprocess.Popen(['php','-S','127.0.0.1:8831','-t',str(t/'site')],env=env,cwd=t,stdout=log,stderr=log)
 client=build_opener(HTTPCookieProcessor(CookieJar()));url='http://127.0.0.1:8831/verwaltung/index.php'
 def req(data=None,tab='menu',headers=None,opener=None):
  rq=Request(url+'?tab='+tab,data=urlencode(data).encode() if data is not None else None,headers=headers or {})
  try:
   with (opener or client).open(rq,timeout=60) as f:return f.status,f.read().decode(),dict(f.headers)
  except HTTPError as e:return e.code,e.read().decode(),dict(e.headers)
 def fields(tab='menu'):
  status,html,_=req(tab=tab);d={k:re.search(r'name="'+k+r'" value="([^"]*)"',html).group(1) for k in ['csrf','revision']};return d
 def post(action,extra=None,tab='menu',headers=None):return req({**fields(tab),'action':action,'tab':tab,**(extra or {})},tab,headers)
 try:
  for _ in range(40):
   try:status,html,hdr=req();break
   except OSError:time.sleep(.1)
  check('Unauthenticated login only','Team-Zugang' in html and 'Entwurf speichern' not in html)
  check('Cookie HTTP-only','HttpOnly' in hdr.get('Set-Cookie',''))
  check('CSRF rejection',req({'action':'login','username':'Buñol','password':initial})[0]==403)
  check('Wrong password refused',post('login',{'username':'Buñol','password':'wrong-not-real'})[0]==429)
  check('Login then mandatory change','Startpasswort' in post('login',{'username':'Buñol','password':initial})[1])
  check('Cannot edit before password change',post('save_menu',{'category':'wochenkarte'})[0]==403)
  check('Wrong current password refused',post('password',{'old':'wrong','new':newpass,'confirm':newpass},'password')[0]==400)
  check('Individual password change succeeds',post('password',{'old':initial,'new':newpass,'confirm':newpass},'password')[0]==200)
  check('Password change clears mandatory flag',not next(x for x in state()['users'].values() if x['name']=='Buñol')['must_change'])
  check('Foreign origin blocked',post('save_menu',{'category':'wochenkarte'},headers={'Origin':'https://example.invalid'})[0]==403)
  menu={'category':'wochenkarte','name[0]':'QA Testgericht','description[0]':'Nur automatischer Test','price[0]':'6,90','enabled[0]':'on'}
  old=state()['revision'];check('Menu draft saved',post('save_menu',menu)[0]==200)
  check('Price parsed to integer cents',state()['catalog']['menu']['wochenkarte'][0][2]==690)
  check('Draft did not publish itself','QA Testgericht' not in (t/'site/index.html').read_text())
  check('Old revision rejected',post('save_menu',{**menu,'revision':str(old)})[0]==409)
  prod={'product_id':'qa-new','name':'QA <b>Test</b>','brand':'QA','description':'Sample only','pack':'100 g','note':'Test label','year':'','category':'conservas','unit':'g','amount':'100','price':'5,50','case':'0','casePrice':'0','stock':'10','source':'https://example.com/','active':'on'}
  check('Product added in form',post('save_product',prod,'products')[0]==200)
  status,body,_=post('publish');check('Shared site publication works',status==200)
  check('Restaurant menu published','QA Testgericht' in (t/'site/index.html').read_text())
  check('Editorial menu also published','QA Testgericht' in (t/'site/editorial/index.html').read_text())
  check('New product has its own page',(t/'site/shop/qa-new/index.html').exists())
  check('Paired editorial product page exists',(t/'site/editorial/shop/qa-new/index.html').exists())
  check('Product input safely escaped','QA &lt;b&gt;Test&lt;/b&gt;' in (t/'site/shop/qa-new/index.html').read_text())
  check('No live payments activated','Keine Bestellungen oder Zahlungen' in (t/'site/shop/index.html').read_text())
  check('Snapshot history retained',len(state()['history'])>=2)
  editor_start=secrets.token_urlsafe(20);check('Team account added',post('user_save',{'user_id':'','user_name':'QA Editor','role':'editor','active':'on','initial_password':editor_start},'users')[0]==200)
  me=next(x for x in state()['users'].values() if x['name']=='Buñol');check('Own administrator cannot be disabled',post('user_save',{'user_id':me['id'],'user_name':'Buñol','role':'admin','initial_password':''},'users')[0]==400)
  check('Logout works','Team-Zugang' in post('logout')[1])
  check('Mutation after logout denied',post('save_menu',menu)[0]==401)
  post('login',{'username':'QA Editor','password':editor_start});editor_pass=secrets.token_urlsafe(22);post('password',{'old':editor_start,'new':editor_pass,'confirm':editor_pass},'password')
  check('Editor cannot publish',post('publish')[0]==403)
  check('Editor cannot create users',post('user_save',{'user_name':'Intruder'},'users')[0]==403)
  check('Editor can change content draft',post('save_menu',menu)[0]==200)
  post('logout');check('Private state not served',True)
  try:client.open('http://127.0.0.1:8831/private/state.json');check('Private state HTTP blocked',False)
  except HTTPError as e:check('Private state HTTP blocked',e.code==404)
 except Exception as e:check('Test execution completed without exception',False);print(str(e));print((t/'php.log').read_text()[-4000:])
 finally:proc.terminate();proc.wait(timeout=10);log.close()
(reports/'server-qa.json').write_text(json.dumps({'checks':len(results),'passed':sum(x['pass'] for x in results),'failed':[x for x in results if not x['pass']],'details':results},indent=2))
if not all(x['pass'] for x in results):sys.exit(1)
