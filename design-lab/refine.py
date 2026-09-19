from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
A=ROOT/'site/assets'
css='''
.lab09 .punk-copy,.lab09 .punk-stage,.lab09 .lab-shop-lead>div{min-width:0}
@media(max-width:760px){
.lab09 .punk-hero{grid-template-columns:minmax(0,1fr)}
.lab09 .punk-copy h1{font-size:clamp(66px,21vw,104px)}
.lab09 .punk-copy{padding-right:0}
.lab09 .punk-food{left:7%;right:auto;width:86%;transform:rotate(5deg)}
.lab09 .lab-shop-lead{grid-template-columns:minmax(0,1fr)}
.lab09 .lab-shop-art{transform:rotate(1deg);margin-inline:8px}
.lab09 .lab-shop-art img{width:90%;margin-inline:auto;display:block;transform:rotate(-2deg)}
.lab09 .footer-top{min-width:0}
.lab09 .footer .footer-word{font-size:clamp(44px,12vw,66px)}
}
'''
with (A/'lab.css').open('a')as f:f.write(css)
js='''
/* Whole-pixel positioning at the reference's native size; proportional at smaller sizes. */
(()=>{
const board=document.querySelector('.replica-board');
if(!board)return;
const pieces=[...board.querySelectorAll('.ref-piece')].map(el=>({el,left:el.style.left,top:el.style.top,width:el.style.width,height:el.style.height}));
function align(){
board.style.transform='none';board.style.left='0px';board.style.top='0px';
const r=board.getBoundingClientRect();
if(r.width<=0)return;
board.style.left=String(Math.round(r.x)-r.x)+'px';board.style.top=String(Math.round(r.y)-r.y)+'px';
for(const p of pieces){
for(const key of ['left','top','width','height']){
const dim=key==='left'||key==='width'?r.width:r.height;
p.el.style[key]=r.width===1217?String(Math.round(parseFloat(p[key])*dim/100))+'px':p[key];
}}
}
align();window.addEventListener('resize',align);
})();
'''
with (A/'lab-ui.js').open('a')as f:f.write(js)
