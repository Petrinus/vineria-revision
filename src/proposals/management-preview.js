'use strict';
/* Shared management preview. Drafts stay local: no live shop, accounts or publication. */
(async()=>{
 if(!document.body.hasAttribute('data-management-preview'))return;
 const $=s=>document.querySelector(s), esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
 const key='vineria-management-local-preview-v1', list=$('#admin-list'), select=$('#admin-category'), status=$('#save-state');
 const labels={wochenkarte:'Wochenkarte',klassiker:'Klassiker',weisswein:'Weißwein',rotwein:'Rotwein',conservas:'Konserven',embutidos:'Chorizo & Cecina'};
 const id=()=> 'item-'+crypto.randomUUID(), clone=x=>structuredClone(x);
 let data,original,tab='menu',filter='',undo=null,changed=false;
 function say(t){status.textContent=t;}
 function dirty(){changed=true;say('Ungespeicherter Entwurf · nur in diesem Browser. Keine Veröffentlichung.');}
 function normalize(d){
  if(!d||!d.menu||Array.isArray(d.menu)||!Array.isArray(d.products)||!Array.isArray(d.team))throw Error('Invalid draft');
  for(const rows of Object.values(d.menu)){if(!Array.isArray(rows))throw Error('Invalid menu');for(const x of rows){x.id||=id();x.visible=x.visible!==false;}}
  for(const x of d.products){x.id||=id();x.category||='sonstiges';x.visible=x.visible!==false;}
  d.menuCategories??=Object.keys(d.menu).map(k=>({id:k,name:labels[k]||k,active:true}));
  d.shopCategories??=[...new Set(d.products.map(x=>x.category))].map(k=>({id:k,name:labels[k]||k,active:true}));
  if(!Array.isArray(d.menuCategories)||!Array.isArray(d.shopCategories))throw Error('Invalid categories');
  for(const k of Object.keys(d.menu))if(!d.menuCategories.some(c=>c.id===k))d.menuCategories.push({id:k,name:labels[k]||k,active:true});
  for(const p of d.products)if(!d.shopCategories.some(c=>c.id===p.category))d.shopCategories.push({id:p.category,name:labels[p.category]||p.category,active:true});
  for(const c of d.menuCategories)if(!Object.hasOwn(d.menu,c.id))d.menu[c.id]=[];
  return d;
 }
 try{
  const r=await fetch('../assets/catalog.json');if(!r.ok)throw Error('Catalog unavailable');const c=await r.json();
  original=normalize({menu:Object.fromEntries(Object.entries(c.menu).map(([k,v])=>[k,v.map(x=>({name:x[0],description:x[1],price:x[2],visible:true}))])),products:c.products.map(x=>({...x,visible:true})),team:[{name:'Buñol',role:'Verwaltung',active:true},{name:'Kraft',role:'Verwaltung',active:true}]});
  data=clone(original);try{const saved=localStorage.getItem(key);if(saved)data=normalize(JSON.parse(saved));}catch{say('Gespeicherter Entwurf nicht lesbar. Beispieldaten geladen; vorhandener Speicher wurde nicht überschrieben.');}
 }catch{list.innerHTML='<p class="empty-state">Die Beispieldaten konnten nicht geladen werden. Bitte den Web-Link erneut öffnen.</p>';return;}
 $('#admin-entry').hidden=true;$('#admin-preview').hidden=false;
 const style=document.createElement('style');style.textContent=`.management-tools{display:flex;flex-wrap:wrap;gap:10px;margin:18px 0}.category-manager{border:1px solid #ccc4b8;padding:20px;margin:20px 0;background:#fffdf7}.category-line{display:grid;grid-template-columns:minmax(120px,1fr) auto auto;gap:12px;border-top:1px solid #ddd5c9;padding:14px 0}.category-line input[type=text],.category-line select,.product-fields input,.product-fields select,.product-fields textarea{width:100%;padding:9px;border:1px solid #bcb5aa;background:#fff;font:inherit;color:#252525}.category-line .category-actions{display:flex;gap:7px;align-items:center;flex-wrap:wrap}.category-line .category-move{grid-column:1/-1;font-size:12px}.management-tools button,.category-manager button,.row-delete,.photo-clear{min-height:38px;padding:7px 12px;border:1px solid #8a3047;background:transparent;color:#70243a;cursor:pointer}.row-delete{float:right;font-size:17px;margin-bottom:8px}.row-delete:focus-visible,.category-manager button:focus-visible{outline:3px solid #8a3047;outline-offset:3px}.edit-row{position:relative}.product-fields{grid-column:1/-1;display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:15px;border-top:1px solid #ddd5c9;padding-top:15px}.product-fields label{display:block}.product-photo{grid-column:1/-1;display:flex;align-items:center;gap:16px;flex-wrap:wrap}.product-photo img{width:100px;height:100px;object-fit:contain;background:#fff;border:1px solid #ddd}.product-photo input{max-width:100%}.category-manager [hidden],.management-tools [hidden]{display:none!important}.category-manager small{font-size:12px}.management-version{font-size:12px;margin:10px 0;color:#64594d}@media(max-width:650px){.category-line{grid-template-columns:1fr}.category-line .category-move{grid-column:auto}.product-fields{grid-template-columns:1fr}.product-fields input,.product-fields textarea,.category-line input{font-size:16px}}`;
 document.head.append(style);
 const tools=document.createElement('div');tools.className='management-tools';tools.innerHTML='<button type="button" id="manage-categories">Bereiche verwalten</button><button type="button" id="undo-management" hidden>Letzte Löschung rückgängig</button>';
 list.before(tools);const panel=document.createElement('section');panel.className='category-manager';panel.hidden=true;panel.setAttribute('aria-label','Bereiche und Kategorien verwalten');list.before(panel);
 const version=document.createElement('p');version.className='management-version';version.textContent='Bearbeitungsstand: 19.09.2026 · Kategorien, Löschen & Produktfotos · Lokaler Entwurf';tools.before(version);
 function cats(){return tab==='menu'?data.menuCategories:data.shopCategories;}
 function options(value,all=false){return (all?'<option value="">Alle Produkte</option>':'')+cats().map(c=>`<option value="${esc(c.id)}" ${value===c.id?'selected':''}>${esc(c.name)}${c.active===false?' (ausgeblendet)':''}</option>`).join('');}
 function categorySelect(){if(tab==='team')return;if(!cats().some(c=>c.id===filter))filter=tab==='menu'?(cats()[0]?.id||''):'';select.innerHTML=options(filter,tab==='products');select.value=filter;}
 function count(c){return tab==='menu'?(data.menu[c.id]||[]).length:data.products.filter(p=>p.category===c.id).length;}
 function remember(){undo=clone(data);$('#undo-management').hidden=false;}
 function renderCategories(){
  if(panel.hidden||tab==='team')return;
  panel.innerHTML=`<h2>${tab==='menu'?'Bereiche der Speisekarte':'Kategorien der Tienda'}</h2><p>Umbenennen verändert keine Einträge. Ausblenden behält alle Inhalte. Gefüllte Bereiche vor dem Löschen einem anderen Bereich zuordnen.</p><button type="button" data-add-category>+ ${tab==='menu'?'Bereich':'Kategorie'}</button>`+cats().map((c,i)=>`<div class="category-line" data-category-id="${esc(c.id)}"><label>Name<input type="text" data-category-name value="${esc(c.name)}" maxlength="120" aria-label="Kategoriename ${i+1}"></label><label><input type="checkbox" data-category-active ${c.active!==false?'checked':''}> Aktiv</label><div class="category-actions"><button type="button" data-category-up ${i===0?'disabled':''} aria-label="${esc(c.name)} nach oben">↑</button><button type="button" data-category-down ${i===cats().length-1?'disabled':''} aria-label="${esc(c.name)} nach unten">↓</button><button type="button" data-delete-category aria-label="${esc(c.name)} löschen">×</button></div><label class="category-move">${count(c)} Einträge · Beim Löschen verschieben nach <select data-category-target><option value="">Ziel auswählen</option>${cats().filter(x=>x.id!==c.id).map(x=>`<option value="${esc(x.id)}">${esc(x.name)}</option>`).join('')}</select></label></div>`).join('');
 }
 function entries(){return tab==='menu'?(data.menu[filter]||[]).map((x,i)=>({x,i})):data.products.map((x,i)=>({x,i})).filter(({x})=>!filter||x.category===filter);}
 function imageSrc(x){if(x.image_data&&/^data:image\/(jpeg|png|webp);base64,/.test(x.image_data))return x.image_data;if(x.imageRemoved)return '';return /^assets\/[a-zA-Z0-9/_.-]+$/.test(x.image||'')?'../'+x.image:'';}
 function field(name,label,x,area=false){return `<label>${label}${area?`<textarea data-field="${name}" maxlength="5000">${esc(x[name])}</textarea>`:`<input data-field="${name}" value="${esc(x[name])}" maxlength="250">`}</label>`;}
 function render(){
  $('#category-label').hidden=tab==='team';$('#manage-categories').hidden=tab==='team';$('#manage-categories').textContent=tab==='menu'?'Bereiche verwalten':'Kategorien verwalten';
  $('#add-row').textContent=tab==='team'?'Beispielperson hinzufügen +':tab==='menu'?'Gericht hinzufügen +':'Produkt hinzufügen +';
  $('#add-row').disabled=tab==='menu'&&!data.menuCategories.length;
  if(tab==='team'){
   panel.hidden=true;list.innerHTML='<p class="notice">Nur Beispielkonten. Echte Konten und Passwörter gehören ausschließlich in die geschützte Serververwaltung.</p>'+data.team.map((x,i)=>`<div class="team-row"><strong>${esc(x.name)}</strong><label>Rolle <select data-role="${i}"><option ${x.role==='Verwaltung'?'selected':''}>Verwaltung</option><option ${x.role==='Redaktion'?'selected':''}>Redaktion</option></select></label><span>Passwort: nur auf dem Server</span></div>`).join('');return;
  }
  categorySelect();renderCategories();
  const rows=entries();list.innerHTML='<div class="edit-list">'+(rows.length?rows.map(({x,i})=>`<div class="edit-row" data-index="${i}"><div><button type="button" class="row-delete" data-delete-row aria-label="${esc(x.name||'Eintrag')} löschen" title="Eintrag löschen">×</button>${field('name','Name',x)}${field('description','Beschreibung',x,true)}</div><label>Preis (€)<input data-field="price" aria-label="Preis ${i+1}" type="number" min="0" step="0.01" value="${((Number(x.price)||0)/100).toFixed(2)}"></label><label><input data-field="visible" type="checkbox" ${x.visible!==false?'checked':''}> Sichtbar</label>${tab==='products'?`<div class="product-fields"><label>Kategorie<select data-field="category">${options(x.category)}</select></label>${field('pack','Format / Inhalt',x)}${field('brand','Hersteller / Marke',x)}${field('note','Weitere Produktinformationen',x,true)}${field('ingredients','Zutaten',x,true)}${field('allergens','Allergene',x,true)}<div class="product-photo">${imageSrc(x)?`<img src="${esc(imageSrc(x))}" alt="${esc(x.name)}">`:'<span>Kein Produktfoto</span>'}<label>Produktfoto hinzufügen / ersetzen<input type="file" data-photo accept="image/jpeg,image/png,image/webp"></label><button type="button" class="photo-clear" data-clear-photo>Foto entfernen</button><small>Nur freigegebene Bilder. Max. 12 MB; auf 1200 Pixel verkleinert. Wird nicht hochgeladen.</small></div></div>`:''}</div>`).join(''):'<p class="empty-state">Keine Einträge in dieser Auswahl. Über „Verwalten“ einen Bereich anlegen oder einen Eintrag hinzufügen.</p>')+'</div>';
 }
 $('#manage-categories').onclick=()=>{panel.hidden=!panel.hidden;renderCategories();};
 panel.addEventListener('input',e=>{const row=e.target.closest('[data-category-id]');if(!row)return;const c=cats().find(x=>x.id===row.dataset.categoryId);if(e.target.hasAttribute('data-category-name')){c.name=e.target.value;categorySelect();dirty();}if(e.target.hasAttribute('data-category-active')){c.active=e.target.checked;categorySelect();dirty();}});
 panel.addEventListener('click',e=>{
  const b=e.target.closest('button');if(!b)return;
  if(b.hasAttribute('data-add-category')){const name=prompt(tab==='menu'?'Name des neuen Bereichs:':'Name der neuen Kategorie:');if(!name?.trim())return;const c={id:id(),name:name.trim(),active:true};cats().push(c);if(tab==='menu')data.menu[c.id]=[];filter=c.id;render();dirty();return;}
  const row=b.closest('[data-category-id]');if(!row)return;const a=cats(),i=a.findIndex(x=>x.id===row.dataset.categoryId),c=a[i];if(!c)return;
  if(b.hasAttribute('data-delete-category')){const n=count(c),target=row.querySelector('[data-category-target]').value;if(n&&!a.some(x=>x.id===target&&x.id!==c.id)){say('Bitte zuerst einen Zielbereich auswählen. Keine Inhalte wurden gelöscht.');return;}if(!confirm(`„${c.name}“ löschen?${n?' '+n+' Einträge werden verschoben.':''}`))return;remember();if(tab==='menu'){if(n)data.menu[target].push(...data.menu[c.id]);delete data.menu[c.id];}else for(const p of data.products)if(p.category===c.id)p.category=target;a.splice(i,1);}
  else{const j=b.hasAttribute('data-category-up')?i-1:b.hasAttribute('data-category-down')?i+1:i;if(j<0||j>=a.length)return;[a[i],a[j]]=[a[j],a[i]];}
  render();dirty();
 });
 list.addEventListener('input',e=>{
  if(e.target.hasAttribute('data-role')){data.team[+e.target.dataset.role].role=e.target.value;dirty();return;}
  const f=e.target.dataset.field,row=e.target.closest('[data-index]');if(!f||!row)return;const x=tab==='menu'?data.menu[filter][+row.dataset.index]:data.products[+row.dataset.index];
  if(f==='price'){if(!e.target.checkValidity()||!Number.isFinite(e.target.valueAsNumber)){e.target.setAttribute('aria-invalid','true');say('Bitte einen gültigen Preis ab 0 eingeben.');return;}e.target.removeAttribute('aria-invalid');x.price=Math.round(e.target.valueAsNumber*100);}else x[f]=f==='visible'?e.target.checked:e.target.value;
  dirty();if(f==='category')render();
 });
 list.addEventListener('click',e=>{const b=e.target.closest('button'),row=b?.closest('[data-index]');if(!row)return;const a=tab==='menu'?data.menu[filter]:data.products,i=+row.dataset.index,x=a[i];if(b.hasAttribute('data-delete-row')){if(!confirm(`„${x.name||'Eintrag'}“ löschen?`))return;remember();a.splice(i,1);render();dirty();}if(b.hasAttribute('data-clear-photo')){x.image_data='';x.imageRemoved=true;render();dirty();}});
 async function resizePhoto(file){
  if(!['image/jpeg','image/png','image/webp'].includes(file.type)||file.size>12*1024*1024)throw Error('Bitte JPG, PNG oder WebP unter 12 MB wählen.');
  const url=URL.createObjectURL(file);try{const img=new Image();img.src=url;await img.decode();const scale=Math.min(1,1200/Math.max(img.width,img.height)),c=document.createElement('canvas');c.width=Math.max(1,Math.round(img.width*scale));c.height=Math.max(1,Math.round(img.height*scale));const ctx=c.getContext('2d');ctx.fillStyle='#ffffff';ctx.fillRect(0,0,c.width,c.height);ctx.drawImage(img,0,0,c.width,c.height);return c.toDataURL('image/jpeg',.82);}finally{URL.revokeObjectURL(url);}
 }
 list.addEventListener('change',async e=>{if(!e.target.hasAttribute('data-photo'))return;const file=e.target.files[0],x=data.products[+e.target.closest('[data-index]').dataset.index];if(!file||!x)return;e.target.disabled=true;try{const image=await resizePhoto(file);if(!data.products.includes(x))return;x.image_data=image;x.imageRemoved=false;dirty();if(tab==='products')render();}catch(err){say(err.message||'Foto konnte nicht verarbeitet werden.');e.target.disabled=false;}});
 select.onchange=()=>{filter=select.value;render();};
 document.querySelectorAll('[data-admin-tab]').forEach(b=>b.onclick=()=>{tab=b.dataset.adminTab;filter='';panel.hidden=true;document.querySelectorAll('[data-admin-tab]').forEach(x=>x.setAttribute('aria-selected',String(x===b)));render();});
 $('#add-row').onclick=()=>{if(tab==='team')data.team.push({name:'Beispielperson '+(data.team.length+1),role:'Redaktion',active:true});else{const x={id:id(),name:'Neuer Eintrag',description:'',price:0,visible:false};if(tab==='menu'){if(!data.menu[filter])return;data.menu[filter].push(x);}else{if(!data.shopCategories.length)data.shopCategories.push({id:id(),name:'Sonstiges',active:true});x.category=filter||data.shopCategories[0].id;x.pack='';data.products.push(x);}}render();dirty();list.querySelector('.edit-row:last-child input[data-field=name]')?.focus();};
 $('#undo-management').onclick=()=>{if(!undo)return;if(!confirm('Stand vor der letzten Löschung wiederherstellen? Auch spätere ungespeicherte Bearbeitungen werden zurückgenommen.'))return;data=undo;undo=null;$('#undo-management').hidden=true;render();dirty();};
 $('#save-demo').textContent='Entwurf speichern';
 $('#save-demo').onclick=()=>{if(list.querySelector('[aria-invalid=true]')||[...data.menuCategories,...data.shopCategories].some(c=>!c.name.trim())){say('Bitte ungültige Preise oder leere Kategorienamen korrigieren.');return;}try{localStorage.setItem(key,JSON.stringify(data));changed=false;say('Entwurf in diesem Browser gespeichert. Noch nicht auf Restaurant- oder Shopseiten veröffentlicht.');}catch{say('Nicht gespeichert: Browserspeicher nicht verfügbar oder voll. Entwurf bleibt geöffnet; Fotos verkleinern oder entfernen.');}};
 $('#reset-demo').onclick=()=>{if(!confirm('Alle lokalen Teständerungen zurücksetzen?'))return;try{localStorage.removeItem(key);}catch{say('Speicher nicht verfügbar. Zurücksetzen abgebrochen.');return;}data=clone(original);filter='';undo=null;changed=false;$('#undo-management').hidden=true;render();say('Beispieldaten wiederhergestellt.');};
 window.addEventListener('beforeunload',e=>{if(changed){e.preventDefault();e.returnValue='';}});
 window.addEventListener('storage',e=>{if(e.key===key)say('Ein anderer Tab hat den Entwurf geändert. Vor dem Überschreiben bitte prüfen; diese Ansicht wurde nicht ersetzt.');});
 render();
})();
