'use strict';
(()=>{
 const reduced=matchMedia('(prefers-reduced-motion: reduce)');
 document.querySelectorAll('[data-collage-slides]').forEach(scene=>{
  const frames=[...scene.querySelectorAll('.photo-layer')],pause=scene.querySelector('[data-collage-pause]'),count=scene.querySelector('[data-collage-count]');let index=0,manualPause=false,timer=null,onscreen=true;
  function show(n){index=(n+frames.length)%frames.length;frames.forEach((f,i)=>{f.classList.toggle('is-visible',i===index);f.setAttribute('aria-hidden',String(i!==index))});if(count)count.textContent=String(index+1).padStart(2,'0')+' / '+String(frames.length).padStart(2,'0')}
  function start(){clearInterval(timer);if(!reduced.matches&&!manualPause&&!document.hidden&&onscreen&&frames.length>1)timer=setInterval(()=>show(index+1),6500);if(pause){pause.textContent=manualPause?'Abspielen':'Pause';pause.setAttribute('aria-pressed',String(manualPause))}}
  scene.querySelector('[data-collage-prev]')?.addEventListener('click',()=>{show(index-1);start()});scene.querySelector('[data-collage-next]')?.addEventListener('click',()=>{show(index+1);start()});pause?.addEventListener('click',()=>{manualPause=!manualPause;start()});document.addEventListener('visibilitychange',start);reduced.addEventListener('change',start);new IntersectionObserver(es=>{onscreen=es[0].isIntersecting;start()},{threshold:.05}).observe(scene);show(0);start();
 });
 const form=document.querySelector('[data-events-form]');if(form){
  const date=form.elements.namedItem('date'),out=form.querySelector('[role=status]');if(date){const now=new Date();date.min=[now.getFullYear(),String(now.getMonth()+1).padStart(2,'0'),String(now.getDate()).padStart(2,'0')].join('-')}
  form.addEventListener('submit',e=>{e.preventDefault();if(!form.reportValidity())return;const d=new FormData(form);const lines=['Anfrage: '+d.get('type'),'Name: '+d.get('name'),'Personen: '+d.get('people'),'Wunschdatum: '+d.get('date'),'Uhrzeit: '+(d.get('time')||'Noch offen'),'E-Mail: '+d.get('email'),'Telefon: '+(d.get('phone')||'Nicht angegeben'),'Antwort bevorzugt: '+d.get('reply'),'','Wünsche:',''+d.get('message')];const url='mailto:vineriadeleste@gmail.com?subject='+encodeURIComponent('Vineria · '+d.get('type')+' · '+d.get('date'))+'&body='+encodeURIComponent(lines.join('\n'));out.textContent='Die Anfrage wird in Eurem E-Mail-Programm geöffnet. Bitte dort prüfen und absenden. Hier wurde noch nichts versendet.';location.href=url;});
 }
})();
