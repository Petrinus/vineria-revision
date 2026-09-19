"""Rebuild content in an isolated project. Only compiled public files are promoted."""
from pathlib import Path
import os,sys,json,shutil,tempfile,subprocess
root=Path(__file__).resolve().parent.parent
if len(sys.argv)!=2:raise SystemExit('Expected one private catalogue path')
source=Path(sys.argv[1]).resolve();private=Path(os.environ.get('VDE_PRIVATE_DIR',root/'private')).resolve()
if source.parent!=private or not source.is_file():raise SystemExit('Unapproved input path')
data=json.loads(source.read_text())
if not isinstance(data.get('menu'),dict) or not isinstance(data.get('products'),list):raise SystemExit('Invalid catalogue')
site=root/'site';stage=Path(tempfile.mkdtemp(prefix='publish-',dir=private));output=stage/'site'
try:
 # Trusted build code is copied unchanged; form data is always a separate JSON file.
 for folder in ['tools','src']:
  shutil.copytree(root/folder,stage/folder,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
 shutil.copytree(site/'assets',output/'assets')
 (stage/'src/catalog.json').write_text(json.dumps(data,ensure_ascii=False,indent=2))
 env={**os.environ,'VDE_OUTPUT':str(output),'VDE_CATALOG':str(stage/'src/catalog.json')}
 for script in ['build.py','polish.py']:
  path=stage/'tools'/script
  if not path.exists():continue
  result=subprocess.run([sys.executable,str(path)],cwd=stage,env=env,capture_output=True,text=True,timeout=120)
  if result.returncode:raise RuntimeError(script+' failed: '+result.stderr[-2000:])
 for essential in ['index.html','shop/index.html','editorial/index.html','assets/site.js']:
  if not (output/essential).is_file():raise RuntimeError('Build missing '+essential)
 for f in output.rglob('*'):
  if not f.is_file():continue
  rel=f.relative_to(output);target=site/rel;target.parent.mkdir(parents=True,exist_ok=True)
  # Temporary sibling ensures atomic replacement even when private storage is another mount.
  fd,temp=tempfile.mkstemp(prefix='.vde-publish-',dir=target.parent);os.close(fd)
  try:
   shutil.copyfile(f,temp);os.chmod(temp,0o644);os.replace(temp,target)
  finally:
   if os.path.exists(temp):os.unlink(temp)
 valid={p['id'] for p in data['products']}
 for prefix in ['shop','editorial/shop']:
  for d in (site/prefix).iterdir():
   if d.is_dir() and d.name not in valid:shutil.rmtree(d)
 print('Published',len(data['products']),'products and',sum(map(len,data['menu'].values())),'menu entries to both themes; payments remain disabled.')
finally:shutil.rmtree(stage,ignore_errors=True)
