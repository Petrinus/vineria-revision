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
(()=>{
const board=document.querySelector('.replica-board');
if(!board)return;
function align(){board.style.transform='none';const r=board.getBoundingClientRect();if(r.width>0)board.style.transform='translate('+String(Math.round(r.x)-r.x)+'px,'+String(Math.round(r.y)-r.y)+'px)';}
align();window.addEventListener('resize',align);
})();
'''
with (A/'lab-ui.js').open('a')as f:f.write(js)
