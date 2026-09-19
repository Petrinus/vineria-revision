"""Server-side rebuild; fixed local program, never shell commands from form input."""
from pathlib import Path
import os,sys,json,shutil,tempfile,ast
root=Path(__file__).resolve().parent.parent
if len(sys.argv)!=2:raise SystemExit('Expected one private catalogue path')
source=Path(sys.argv[1]).resolve();private=Path(os.environ.get('VDE_PRIVATE_DIR',root/'private')).resolve()
if source.parent!=private or not source.is_file():raise SystemExit('Unapproved input path')
data=json.loads(source.read_text());assert isinstance(data.get('menu'),dict) and isinstance(data.get('products'),list)
site=root/'site';stage=Path(tempfile.mkdtemp(prefix='publish-',dir=private))
try:
 shutil.copytree(site/'assets',stage/'assets')
 # Adapt only fixed file locations in the reviewed builder. User content remains JSON data.
 text=(root/'tools/build.py').read_text()
 old_root="R=Path('site')";old_data="D=json.loads(Path('src/catalog.json').read_text())"
 if old_root not in text or old_data not in text:raise RuntimeError('Builder has changed; review path adapters before publishing')
 text=text.replace(old_root,"R=Path(os.environ['VDE_OUTPUT'])",1).replace(old_data,"D=json.loads(Path(os.environ['VDE_CATALOG']).read_text())",1)
 ast.parse(text);os.environ['VDE_OUTPUT']=str(stage);os.environ['VDE_CATALOG']=str(source);os.chdir(root)
 exec(compile(text,str(root/'tools/build.py'),'exec'),{'__name__':'__main__'})
 if (root/'tools/polish.py').exists():
  text=(root/'tools/polish.py').read_text();exec(compile(text,str(root/'tools/polish.py'),'exec'),{'__name__':'__main__'})
 for f in stage.rglob('*'):
  if not f.is_file():continue
  rel=f.relative_to(stage);target=site/rel;target.parent.mkdir(parents=True,exist_ok=True);os.replace(f,target)
 valid={p['id'] for p in data['products']}
 for prefix in ['shop','editorial/shop']:
  for d in (site/prefix).iterdir():
   if d.is_dir() and d.name not in valid:shutil.rmtree(d)
 print('Published',len(data['products']),'products and',sum(map(len,data['menu'].values())),'menu entries to both themes; payments remain disabled.')
finally:shutil.rmtree(stage,ignore_errors=True)
