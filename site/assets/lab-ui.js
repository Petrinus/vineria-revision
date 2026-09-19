/* Public design-preview UI. No network writes, authentication or payments. */
'use strict';
(()=>{
 const q=(s,r=document)=>r.querySelector(s),all=(s,r=document)=>[...r.querySelectorAll(s)];
 function fullMenu(button,on){const host=button.closest('[data-complete-menu]')?.querySelector('[data-live-menu]');if(!host)return;button.setAttribute('aria-pressed',String(on));button.textContent=on?'Nach Bereichen anzeigen':'Gesamte Karte anzeigen';all('.live-menu-panel',host).forEach((p,i)=>p.hidden=on?false:i!==0);all('[data-live-tab]',host).forEach((t,i)=>t.setAttribute('aria-selected',String(!on&&i===0)));}
 all('[data-full-menu]').forEach(b=>{b.onclick=()=>fullMenu(b,b.getAttribute('aria-pressed')!=='true');const host=b.closest('[data-complete-menu]')?.querySelector('[data-live-menu]');host?.addEventListener('click',e=>{if(e.target.closest('[data-live-tab]')){b.setAttribute('aria-pressed','false');b.textContent='Gesamte Karte anzeigen';}});fullMenu(b,true);});
 all('[data-lab-toggle]').forEach(b=>b.onclick=()=>{const nav=document.getElementById(b.getAttribute('aria-controls'));const open=b.getAttribute('aria-expanded')!=='true';b.setAttribute('aria-expanded',String(open));nav?.classList.toggle('is-open',open);});
 const dialog=q('#replica-dialog');let opener=null;
 function openPanel(name,from){if(!dialog)return;const pane=name==='weine'?'speisekarte':name;const target=all('[data-panel]',dialog).find(x=>x.dataset.panel===pane);if(!target)return;if(!dialog.open)opener=from||document.activeElement;all('[data-panel]',dialog).forEach(s=>s.hidden=s!==target);q('#replica-dialog-title').textContent=target.dataset.label||pane;if(!dialog.open)dialog.showModal();dialog.scrollTop=0;if(name==='weine')q('[data-live-tab="live-weisswein"]',target)?.click();q('[data-close-panel]',dialog).focus();}
 all('[data-open-panel]').forEach(a=>a.addEventListener('click',ev=>{if(ev.metaKey||ev.ctrlKey)return;ev.preventDefault();openPanel(a.dataset.openPanel,a);}));
 if(dialog){q('[data-close-panel]',dialog).addEventListener('click',()=>dialog.close());dialog.addEventListener('close',()=>opener?.focus());dialog.addEventListener('click',ev=>{const a=ev.target.closest('a[href^="#"]');if(a&&!a.dataset.openPanel){const name=a.getAttribute('href').slice(1);if(all('[data-panel]',dialog).some(x=>x.dataset.panel===name)){ev.preventDefault();openPanel(name,a);}}});if(location.hash)openPanel(decodeURIComponent(location.hash.slice(1)));}
 else{const wine=()=>{q('#speisekarte')?.scrollIntoView();q('[data-live-tab="live-weisswein"]')?.click();};all('a[href$="#weine"]').forEach(a=>a.addEventListener('click',ev=>{const u=new URL(a.href);if(u.pathname===location.pathname){ev.preventDefault();wine();}}));if(location.hash==='#weine')wine();}
 all('[data-art-slider]').forEach(stage=>{const frames=all('[data-art-frame]',stage);if(!frames.length)return;let n=0,paused=matchMedia('(prefers-reduced-motion:reduce)').matches;const pause=q('[data-art-pause]',stage);function draw(){frames.forEach((im,i)=>{im.hidden=i!==n;im.setAttribute('aria-hidden',String(i!==n));});q('[data-art-count]',stage).textContent=String(n+1).padStart(2,'0')+' / '+frames.length;pause.textContent=paused?'Abspielen':'Pause';pause.setAttribute('aria-pressed',String(paused));}q('[data-art-next]',stage).onclick=()=>{n=(n+1)%frames.length;draw();};q('[data-art-prev]',stage).onclick=()=>{n=(n+frames.length-1)%frames.length;draw();};pause.onclick=()=>{paused=!paused;draw();};setInterval(()=>{if(!paused&&!document.hidden){n=(n+1)%frames.length;draw();}},6500);draw();});
})();

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
