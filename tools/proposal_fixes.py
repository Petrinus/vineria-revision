"""Small rendering fixes applied after building the independent proposal catalogue."""
from pathlib import Path
from bs4 import BeautifulSoup
root=Path('site')
for path in root.rglob('*.html'):
    soup=BeautifulSoup(path.read_text(), 'html.parser')
    for image in soup.select('img'):
        image['loading']='eager'
    for star in soup.select('.scene-star'):
        star.decompose()
    if path.relative_to(root).as_posix() == 'entwuerfe/v1/index.html':
        style=soup.new_tag('style',id='narrow-screen-typography')
        style.string='@media(max-width:360px){.hero h1{font-size:clamp(54px,18vw,64px)}.hero>*{min-width:0}.actions>.pill{max-width:100%;white-space:normal}.nav .brand{max-width:100%}}'
        soup.head.append(style)
    path.write_text(str(soup))
print('Applied narrow-screen typography, eagerly loaded comparison images and removed standalone stars.')
