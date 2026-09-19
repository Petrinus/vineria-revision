'use strict';
(()=>{
 const one=(s,r=document)=>r.querySelector(s),all=(s,r=document)=>Array.from(r.querySelectorAll(s));
 const toggle=one('.v10-menu-toggle'),nav=one('#v10-navigation');
 function closeNav(){if(!toggle||!nav)return;toggle.setAttribute('aria-expanded','false');nav.classList.remove('is-open');}
 toggle?.addEventListener('click',()=>{const on=toggle.getAttribute('aria-expanded')!=='true';toggle.setAttribute('aria-expanded',String(on));nav.classList.toggle('is-open',on);});
 nav?.addEventListener('click',e=>{if(e.target.closest('a'))closeNav();});
 document.addEventListener('keydown',e=>{if(e.key==='Escape'&&toggle?.getAttribute('aria-expanded')==='true'){closeNav();toggle.focus();}});
 const full=one('[data-full-menu]'),menu=one('[data-live-menu]');
 function showAll(on){if(!menu||!full)return;full.setAttribute('aria-pressed',String(on));full.textContent=on?'Nach Bereichen anzeigen':'Gesamte Karte anzeigen';const tabs=all('[data-live-tab]',menu);all('.live-menu-panel',menu).forEach((panel,i)=>panel.hidden=!on&&i!==0);tabs.forEach((tab,i)=>{tab.setAttribute('aria-selected',String(!on&&i===0));tab.tabIndex=i===0?0:-1;});}
 full?.addEventListener('click',()=>showAll(full.getAttribute('aria-pressed')!=='true'));
 menu?.addEventListener('click',e=>{if(e.target.closest('[data-live-tab]')&&full){full.setAttribute('aria-pressed','false');full.textContent='Gesamte Karte anzeigen';}});
 function wine(){const tab=one('[data-live-tab="live-weisswein"]');tab?.click();one('#speisekarte')?.scrollIntoView({behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'instant':'smooth',block:'start'});}
 all('a[href$="#weine"]').forEach(a=>a.addEventListener('click',e=>{const u=new URL(a.href);if(u.pathname===location.pathname&&!e.ctrlKey&&!e.metaKey){e.preventDefault();closeNav();history.replaceState(null,'','#weine');wine();}}));
 showAll(true);if(location.hash==='#weine')wine();
 all('[data-events-form]').forEach(form=>{const date=form.elements.namedItem('date');if(date){const now=new Date();date.min=[now.getFullYear(),String(now.getMonth()+1).padStart(2,'0'),String(now.getDate()).padStart(2,'0')].join('-');}
  form.addEventListener('submit',e=>{e.preventDefault();if(!form.reportValidity())return;const d=new FormData(form);const lines=['Anfrage: '+d.get('type'),'Name: '+d.get('name'),'Personen: '+d.get('people'),'Datum: '+d.get('date'),'Uhrzeit: '+(d.get('time')||'Noch offen'),'E-Mail: '+d.get('email'),'Telefon: '+(d.get('phone')||'Nicht angegeben'),'Antwort bevorzugt: '+d.get('reply'),'','Wünsche:',String(d.get('message')||'')];const out=one('[role=status]',form);out.textContent='Die Anfrage wird in Eurem E-Mail-Programm geöffnet. Bitte dort prüfen und absenden. Diese Vorschau hat noch nichts verschickt.';location.href='mailto:vineriadeleste@gmail.com?subject='+encodeURIComponent('Vineria · '+d.get('type')+' · '+d.get('date'))+'&body='+encodeURIComponent(lines.join('\n'));});
 });
})();
