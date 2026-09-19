'use strict';
// Shared management preview. All edits remain local; this is not a publishing API.
(async () => {
  if (!document.body.hasAttribute('data-management-preview')) return;
  const $ = s => document.querySelector(s), key = 'vineria-management-local-preview-v1';
  const esc = v => String(v ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const clone = v => JSON.parse(JSON.stringify(v));
  const uid = () => 'id-' + (globalThis.crypto?.randomUUID?.() || Date.now().toString(36) + Math.random().toString(36).slice(2));
  const labels = {wochenkarte:'Wochenkarte',klassiker:'Unsere Klassiker',conservas:'Konserven',embutidos:'Chorizo & Cecina',weisswein:'Weißwein',rotwein:'Rotwein'};
  const money = n => new Intl.NumberFormat('de-DE',{style:'currency',currency:'EUR'}).format(Number(n || 0)/100);
  const safeId = s => typeof s === 'string' && !['__proto__','prototype','constructor'].includes(s);
  let data, original, undo = null, baseline = null, tab = 'menu', dirty = false, pendingPhotos = 0;
  let picked = {menu:'',products:''}, showCategories = false, showPreview = false;
  const photoJobs = new WeakMap();
  $('#admin-entry').hidden = true; $('#admin-preview').hidden = false;
  const list = $('#admin-list'), select = $('#admin-category'), status = $('#save-state');
  function say(text) { status.textContent = text; }
  function changed() { dirty = true; say('Ungespeicherter Entwurf · nur in diesem Browser.'); if(showPreview) renderPreview(); }
  function normalize(raw) {
    const d = clone(raw); d.schemaVersion = 2;
    d.menu = Object.fromEntries(Object.entries(d.menu || {}).filter(([k,v]) => safeId(k) && Array.isArray(v)));
    Object.values(d.menu).forEach(rows => rows.forEach(r => { r.id ||= uid(); r.visible = r.visible !== false; }));
    d.products = Array.isArray(d.products) ? d.products : [];
    d.team = Array.isArray(d.team) ? d.team : [];
    d.products.forEach(r => { r.id ||= uid(); r.category ||= 'conservas'; r.visible = r.visible !== false; });
    // Read drafts produced by both earlier management implementations.
    d.products.forEach(r => {
      if(!r.imageData && r.image_data) r.imageData = r.image_data;
      if(r.imageRemoved) { r.image = ''; r.imageData = ''; }
    });
    d.categories ||= {};
    if(!Array.isArray(d.categories.menu) && Array.isArray(d.menuCategories)) d.categories.menu = d.menuCategories.map(c => ({...c,visible:c.active!==false}));
    if(!Array.isArray(d.categories.products) && Array.isArray(d.shopCategories)) d.categories.products = d.shopCategories.map(c => ({...c,visible:c.active!==false}));
    for (const scope of ['menu','products']) {
      const ids = scope === 'menu' ? Object.keys(d.menu) : [...new Set(d.products.map(p => p.category))];
      const previous = d.categories[scope];
      const cats = Array.isArray(previous) ? previous.filter(c => c && safeId(c.id)) : ids.map(id => ({id,name:labels[id] || id,visible:true}));
      const seen = new Set(); d.categories[scope] = cats.filter(c => !seen.has(c.id) && seen.add(c.id));
      ids.forEach(id => { if(safeId(id) && !d.categories[scope].some(c => c.id === id)) d.categories[scope].push({id,name:labels[id] || id,visible:true}); });
      d.categories[scope].forEach(c => { c.name = String(c.name || labels[c.id] || c.id); c.visible = c.visible !== false; if(scope === 'menu') d.menu[c.id] ||= []; });
    }
    return d;
  }
  try {
    const response = await fetch('../assets/catalog.json'); if(!response.ok) throw Error('catalog');
    const c = await response.json();
    original = normalize({menu:Object.fromEntries(Object.entries(c.menu).map(([k,v]) => [k,v.map(x => ({name:x[0],description:x[1],price:x[2],visible:true}))])),products:c.products,team:[{name:'Buñol',role:'Verwaltung',active:true},{name:'Kraft',role:'Verwaltung',active:true}]});
    try { baseline = localStorage.getItem(key); const stored = baseline && JSON.parse(baseline); data = stored?.menu && Array.isArray(stored.products) ? normalize(stored) : clone(original); }
    catch { data = clone(original); say('Gespeicherte Daten konnten nicht gelesen werden. Vor dem Zurücksetzen bitte prüfen.'); }
  } catch { list.innerHTML = '<p class="empty-state">Die Beispieldaten konnten nicht geladen werden. Bitte den Web-Link neu laden.</p>'; return; }
  const style = document.createElement('style');
  style.textContent = `.mgmt-panel{border:1px solid #c9c5bc;padding:20px;margin:18px 0;background:#fffdf7}.mgmt-panel h2{font-size:25px}.mgmt-note{font:12px/1.6 Arial,sans-serif;color:#57534c}.mgmt-cats{display:grid;gap:14px}.mgmt-cat{border-top:1px solid #d5d0c5;padding:14px 0;display:flex;gap:12px;align-items:center;flex-wrap:wrap}.mgmt-cat input[type=text]{min-width:170px;flex:1}.mgmt-cat label{font-size:12px}.mgmt-actions{display:flex;gap:9px;align-items:center;flex-wrap:wrap}.mgmt-panel button,.mgmt-delete,.mgmt-photo button{cursor:pointer;padding:8px 12px;border:1px solid #8d8178;background:transparent;color:inherit;font:13px Arial,sans-serif}.mgmt-delete{color:#8b233f;align-self:start}.mgmt-detail{grid-column:1/-1;border-top:1px solid #ddd6cb;padding-top:14px}.mgmt-detail summary{cursor:pointer;font-weight:bold}.mgmt-grid{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-top:15px}.mgmt-grid label{display:block;min-width:0;font-size:12px}.mgmt-grid input,.mgmt-grid textarea,.mgmt-grid select,.mgmt-panel input,.mgmt-panel select{box-sizing:border-box;width:100%;padding:9px;border:1px solid #c5bdb0;background:#fff;color:#222;font:14px Arial,sans-serif}.mgmt-panel input[type=checkbox]{width:auto}.mgmt-grid textarea{min-height:75px}.mgmt-photo{margin-top:18px}.mgmt-photo img,.mgmt-customer img{width:150px;height:150px;object-fit:contain;border:1px solid #ddd;background:#fff}.mgmt-photo input{max-width:100%}.mgmt-customer{display:grid;gap:18px}.mgmt-customer article{padding:18px;border:1px solid #d5d0c5}.mgmt-customer h3{margin:4px 0 8px}.mgmt-customer p{white-space:pre-wrap}.mgmt-marker{font:12px Arial,sans-serif;color:#6d4c32}.edit-row{grid-template-columns:minmax(0,1fr) 110px 85px 44px!important}.edit-row>*{min-width:0}.edit-row input[type=checkbox]{width:auto!important}.mgmt-wide{grid-column:1/-1}button:focus-visible,select:focus-visible,input:focus-visible,summary:focus-visible{outline:3px solid #802a40;outline-offset:3px}@media(max-width:650px){.edit-row{grid-template-columns:minmax(0,1fr) 85px!important}.mgmt-detail{grid-column:1/-1}.mgmt-grid{grid-template-columns:1fr}.mgmt-panel{padding:14px}.mgmt-cat{align-items:flex-start}.mgmt-cat>input{flex-basis:100%}.mgmt-cat select{max-width:100%}}`;
  document.head.append(style);
  const marker = document.createElement('p'); marker.className = 'mgmt-marker'; marker.textContent = 'Verwaltung · Revision 2 · Kategorien, Löschen, Produktfotos'; $('#admin-preview').prepend(marker);
  const manage = document.createElement('button'); manage.type = 'button'; manage.className = 'button outline'; manage.id = 'manage-categories'; manage.textContent = 'Kategorien verwalten'; manage.setAttribute('aria-expanded','false'); manage.setAttribute('aria-controls','category-manager'); $('#add-row').before(manage);
  const undoButton = document.createElement('button'); undoButton.type='button'; undoButton.className='button outline'; undoButton.id='undo-management'; undoButton.textContent='Letzte Löschung rückgängig'; undoButton.hidden=true; manage.after(undoButton);
  function remember() { undo=clone(data); undoButton.hidden=false; }
  undoButton.onclick=()=>{if(!undo || !confirm('Stand vor der letzten Löschung wiederherstellen? Auch spätere Bearbeitungen werden zurückgenommen.'))return;data=normalize(undo);undo=null;undoButton.hidden=true;changed();render();};
  const manager = document.createElement('section'); manager.id = 'category-manager'; manager.className = 'mgmt-panel'; manager.hidden = true; list.before(manager);
  const previewButton = document.createElement('button'); previewButton.type = 'button'; previewButton.className = 'button outline'; previewButton.id = 'customer-preview-button'; previewButton.textContent = 'Kundensicht prüfen'; previewButton.setAttribute('aria-expanded','false'); $('#save-demo').after(previewButton);
  const preview = document.createElement('section'); preview.id = 'customer-preview'; preview.className = 'mgmt-panel'; preview.hidden = true; $('#admin-preview').append(preview);
  const exportButton = document.createElement('button'); exportButton.className = 'text-button'; exportButton.type = 'button'; exportButton.textContent = 'Entwurf als JSON sichern'; $('#reset-demo').after(exportButton);
  $('#save-demo').textContent = 'Entwurf lokal speichern';
  function cats() { return data.categories[tab] || []; }
  function entries(scope,id) { return scope === 'menu' ? data.menu[id] || [] : data.products.filter(p => p.category === id); }
  function rows() { return tab === 'menu' ? data.menu[picked.menu] || [] : tab === 'products' ? data.products.filter(p => !picked.products || p.category === picked.products) : data.team; }
  function options(items,selected,all=false) { return (all ? '<option value="">Alle Produkte</option>' : '') + items.map(c => `<option value="${esc(c.id)}" ${c.id===selected?'selected':''}>${esc(c.name)}${c.visible===false?' (ausgeblendet)':''}</option>`).join(''); }
  function imageUrl(row) {
    if(/^data:image\/(jpeg|png|webp);base64,[a-z0-9+/=]+$/i.test(row.imageData || '')) return row.imageData;
    if(typeof row.image === 'string' && /^assets\/[a-z0-9_./-]+$/i.test(row.image) && !row.image.includes('..')) return new URL('../'+row.image,location.href).href;
    return '';
  }
  function field(name,label,value,area=false) { return `<label>${label}${area ? `<textarea data-field="${name}" maxlength="5000">${esc(value)}</textarea>` : `<input data-field="${name}" value="${esc(value)}" maxlength="250">`}</label>`; }
  function renderCategories() {
    manager.hidden = !showCategories || tab === 'team'; manage.setAttribute('aria-expanded',String(!manager.hidden)); if(manager.hidden) return;
    manager.innerHTML = `<h2>${tab==='menu'?'Bereiche der Speisekarte':'Kategorien der Tienda'}</h2><p class="mgmt-note">Umbenennen erhält alle Einträge. Ausblenden blendet auch den Inhalt aus. Gefüllte Kategorien erst in eine andere Kategorie verschieben, dann löschen.</p><div class="mgmt-cats">${cats().map((c,i) => `<div class="mgmt-cat" data-cat="${esc(c.id)}"><input type="text" data-cat-name aria-label="Kategoriename ${i+1}" required maxlength="120" value="${esc(c.name)}"><label><input type="checkbox" data-cat-visible ${c.visible?'checked':''}> Aktiv</label><span>${entries(tab,c.id).length} Einträge</span><div class="mgmt-actions"><button type="button" data-move="-1" aria-label="Kategorie nach oben" ${i===0?'disabled':''}>↑</button><button type="button" data-move="1" aria-label="Kategorie nach unten" ${i===cats().length-1?'disabled':''}>↓</button><button type="button" data-delete-category aria-label="Kategorie löschen">×</button></div>${entries(tab,c.id).length ? `<label>Vor dem Löschen verschieben nach<select data-target aria-label="Zielkategorie"><option value="">Ziel wählen …</option>${options(cats().filter(x=>x.id!==c.id),'')}</select></label>` : ''}</div>`).join('')}</div><button type="button" id="add-category">+ Neue Kategorie</button>`;
    manager.querySelectorAll('[data-cat]').forEach(el => {
      const c = cats().find(c=>c.id===el.dataset.cat);
      el.querySelector('[data-cat-name]').onchange = e => { if(!e.target.value.trim()){e.target.setCustomValidity('Bitte einen Namen eingeben.');e.target.reportValidity();return;} e.target.setCustomValidity('');c.name=e.target.value.trim();changed();render(); };
      el.querySelector('[data-cat-visible]').onchange = e => { c.visible=e.target.checked;changed();render(); };
      el.querySelectorAll('[data-move]').forEach(b => b.onclick = () => { const a=cats(),i=a.indexOf(c),j=i+Number(b.dataset.move);if(j<0||j>=a.length)return;[a[i],a[j]]=[a[j],a[i]];changed();render(); });
      el.querySelector('[data-delete-category]').onclick = () => {
        const count=entries(tab,c.id).length,target=el.querySelector('[data-target]')?.value;
        if(count && !cats().some(x=>x.id===target && x.id!==c.id)){say('Bitte zuerst eine Zielkategorie wählen oder die Einträge einzeln entfernen.');return;}
        if(!confirm(`Kategorie „${c.name}“ löschen?${count?' Die '+count+' Einträge werden in die gewählte Kategorie verschoben.':''}`))return;
        remember();
        if(tab==='menu'){if(count)data.menu[target].push(...data.menu[c.id]);delete data.menu[c.id];}
        else data.products.forEach(p=>{if(p.category===c.id)p.category=target;});
        data.categories[tab]=cats().filter(x=>x.id!==c.id);if(picked[tab]===c.id)picked[tab]=target || '';changed();render();
      };
    });
    $('#add-category').onclick=()=>{const id=uid();cats().push({id,name:'Neue Kategorie',visible:false});if(tab==='menu')data.menu[id]=[];picked[tab]=id;changed();render();const input=manager.querySelector(`[data-cat="${id}"] input`);input.focus();input.select();};
  }
  function renderPreview() {
    preview.hidden = !showPreview || tab === 'team'; if(preview.hidden)return;
    preview.innerHTML = '<h2>Kundensicht · Inhaltsvorschau</h2><p class="mgmt-note">Zeigt diesen lokalen Entwurf, nicht die veröffentlichte Website. Aktive Kategorien und sichtbare Einträge, in der gewählten Reihenfolge. Kein Verkauf.</p>' + cats().filter(c=>c.visible).map(c=>{const visible=entries(tab,c.id).filter(r=>r.visible!==false);return visible.length?`<h3>${esc(c.name)}</h3><div class="mgmt-customer">${visible.map(r=>`<article>${tab==='products'&&imageUrl(r)?`<img src="${esc(imageUrl(r))}" alt="${esc(r.imageAlt || r.name)}">`:''}<h3>${esc(r.name)}</h3><p>${esc(r.description)}</p><strong>${money(r.price)}</strong>${tab==='products'?`<p>${esc(r.pack)}</p>${['ingredients','allergens','nutrition','storage','note'].filter(k=>r[k]).map(k=>`<p><b>${({ingredients:'Zutaten',allergens:'Allergene',nutrition:'Nährwerte',storage:'Lagerung',note:'Information'})[k]}:</b> ${esc(r[k])}</p>`).join('')}`:''}</article>`).join('')}</div>`:'';}).join('');
  }
  function render() {
    const opened = new Set([...list.querySelectorAll('.mgmt-detail[open]')].map(e=>e.dataset.detail));
    const isTeam=tab==='team';$('#category-label').hidden=isTeam;manage.hidden=isTeam;previewButton.hidden=isTeam;
    if(!isTeam){if(tab==='menu'&&!cats().some(c=>c.id===picked.menu))picked.menu=cats()[0]?.id || '';if(tab==='products'&&picked.products&&!cats().some(c=>c.id===picked.products))picked.products='';select.innerHTML=options(cats(),picked[tab],tab==='products');select.disabled=!cats().length;}
    $('#add-row').textContent=isTeam?'Beispielperson hinzufügen +':tab==='menu'?'Gericht hinzufügen +':'Produkt hinzufügen +';$('#add-row').disabled=!isTeam&&!cats().length;
    renderCategories();renderPreview();
    if(isTeam){list.innerHTML='<p class="notice">Team-Demo. Keine echten Konten, Passwörter oder Berechtigungsänderungen.</p>'+data.team.map((r,i)=>`<div class="team-row"><strong>${esc(r.name)}</strong><label>Rolle <select data-role="${i}"><option ${r.role==='Verwaltung'?'selected':''}>Verwaltung</option><option ${r.role==='Redaktion'?'selected':''}>Redaktion</option></select></label><span>Passwort: nur auf dem Server</span></div>`).join('');list.querySelectorAll('[data-role]').forEach(e=>e.onchange=()=>{data.team[Number(e.dataset.role)].role=e.value;changed();});return;}
    const visibleRows=rows();
    list.innerHTML=(cats().find(c=>c.id===picked[tab])?.visible===false?'<p class="mgmt-note">Diese Kategorie ist ausgeblendet. Ihre Einträge bleiben erhalten.</p>':'')+'<div class="edit-list">'+visibleRows.map((r,i)=>`<div class="edit-row" data-row="${i}"><div>${field('name','Name',r.name)}${field('description','Beschreibung',r.description,true)}</div><label>Preis (€)<input data-field="price" aria-label="Preis ${i+1}" type="number" required min="0" max="100000" step="0.01" value="${(Number(r.price || 0)/100).toFixed(2)}"></label><label><input data-field="visible" type="checkbox" ${r.visible!==false?'checked':''}> Sichtbar</label><button type="button" class="mgmt-delete" data-delete-row aria-label="Eintrag löschen">×</button>${tab==='products'?`<details class="mgmt-detail" data-detail="${esc(r.id)}" ${opened.has(r.id)?'open':''}><summary>Produktdaten & Foto bearbeiten</summary><div class="mgmt-grid"><label>Kategorie<select data-field="category">${options(cats(),r.category)}</select></label>${field('pack','Format / Packung',r.pack)}${field('brand','Hersteller / Marke',r.brand)}${field('imageAlt','Bildbeschreibung',r.imageAlt)}${field('ingredients','Zutaten',r.ingredients,true)}${field('allergens','Allergene',r.allergens,true)}${field('nutrition','Nährwerte',r.nutrition,true)}${field('storage','Lagerung',r.storage,true)}${field('note','Weitere Produktinformation',r.note,true)}</div><div class="mgmt-photo">${imageUrl(r)?`<img src="${esc(imageUrl(r))}" alt="${esc(r.imageAlt||r.name)}">`:'<p>Kein Foto ausgewählt.</p>'}<label>Foto hinzufügen / ersetzen<input data-photo type="file" accept="image/jpeg,image/png,image/webp"></label><p class="mgmt-note">Eigene freigegebene Bilder · JPG, PNG, WebP · maximal 12 MB. Speicherung nur in diesem Browser.</p><button type="button" data-remove-photo ${imageUrl(r)?'':'disabled'}>Foto entfernen</button></div></details>`:''}</div>`).join('')+'</div>'+(visibleRows.length?'':'<p class="empty-state">Noch keine Einträge. Kategorie anlegen oder einen Eintrag hinzufügen.</p>');
    list.querySelectorAll('[data-row]').forEach(el=>{
      const r=visibleRows[Number(el.dataset.row)];
      el.querySelectorAll('[data-field]').forEach(e=>e.addEventListener(e.tagName==='SELECT'?'change':'input',()=>{const f=e.dataset.field;if(f==='price'){if(!e.validity.valid)return;r.price=Math.round(Number(e.value)*100);}else r[f]=f==='visible'?e.checked:e.value;changed();if(f==='category')render();}));
      el.querySelector('[data-delete-row]').onclick=()=>{if(!confirm(`„${r.name || 'Eintrag'}“ wirklich löschen? Zum vorübergehenden Ausblenden nur „Sichtbar“ ausschalten.`))return;remember();const target=tab==='menu'?data.menu[picked.menu]:data.products;target.splice(target.indexOf(r),1);changed();render();};
      const file=el.querySelector('[data-photo]');if(file)file.onchange=()=>loadPhoto(file.files[0],r);
      const remove=el.querySelector('[data-remove-photo]');if(remove)remove.onclick=()=>{if(!confirm('Nur das Foto entfernen? Das Produkt bleibt erhalten.'))return;photoJobs.set(r,uid());r.image='';r.imageData='';r.image_data='';r.imageRemoved=true;r.imageAlt='';changed();render();};
    });
  }
  async function loadPhoto(file,row) {
    if(!file)return;
    if(!['image/jpeg','image/png','image/webp'].includes(file.type)||file.size>12*1024*1024){say('Bitte JPG, PNG oder WebP unter 12 MB auswählen.');return;}
    const token=uid();photoJobs.set(row,token);pendingPhotos++;say('Foto wird für den lokalen Entwurf vorbereitet.');const url=URL.createObjectURL(file);
    try {const img=new Image();await new Promise((resolve,reject)=>{img.onload=resolve;img.onerror=reject;img.src=url;});const scale=Math.min(1,1200/Math.max(img.width,img.height));const canvas=document.createElement('canvas');canvas.width=Math.max(1,Math.round(img.width*scale));canvas.height=Math.max(1,Math.round(img.height*scale));const ctx=canvas.getContext('2d');ctx.fillStyle='#ffffff';ctx.fillRect(0,0,canvas.width,canvas.height);ctx.drawImage(img,0,0,canvas.width,canvas.height);if(photoJobs.get(row)!==token)return;row.imageData=canvas.toDataURL('image/jpeg',0.82);row.image='';row.imageRemoved=false;row.imageAlt ||= row.name;changed();render();}
    catch {say('Das Foto konnte nicht gelesen werden. Das bisherige Bild bleibt erhalten.');}
    finally {pendingPhotos--;URL.revokeObjectURL(url);}
  }
  select.onchange=()=>{picked[tab]=select.value;render();};
  manage.onclick=()=>{showCategories=!showCategories;renderCategories();};
  previewButton.onclick=()=>{showPreview=!showPreview;previewButton.setAttribute('aria-expanded',String(showPreview));renderPreview();if(showPreview)preview.scrollIntoView({block:'start'});};
  document.querySelectorAll('[data-admin-tab]').forEach(b=>b.onclick=()=>{tab=b.dataset.adminTab;document.querySelectorAll('[data-admin-tab]').forEach(x=>x.setAttribute('aria-selected',String(x===b)));render();});
  $('#add-row').onclick=()=>{if(tab==='team')data.team.push({name:'Beispielperson '+(data.team.length+1),role:'Redaktion',active:true});else{const r={id:uid(),name:tab==='menu'?'Neues Gericht':'Neues Produkt',description:'',price:0,visible:false};if(tab==='menu')data.menu[picked.menu].push(r);else data.products.push({...r,category:picked.products||cats()[0].id,pack:'',brand:''});}changed();render();const last=list.querySelector('.edit-row:last-child input');last?.focus();last?.select();};
  $('#save-demo').onclick=()=>{
    if(pendingPhotos){say('Bitte die laufende Bildverarbeitung abschließen lassen.');return;}
    const invalid=$('#admin-preview').querySelector('input:invalid,textarea:invalid,select:invalid');if(invalid){invalid.reportValidity();return;}
    try {if(localStorage.getItem(key)!==baseline){say('Der gespeicherte Entwurf wurde in einem anderen Fenster geändert. Bitte diesen Entwurf als JSON sichern und neu laden; nichts wurde überschrieben.');return;}syncCompatibility();const next=JSON.stringify(data);localStorage.setItem(key,next);baseline=next;dirty=false;say('Entwurf lokal gespeichert. Nicht für andere Besucher veröffentlicht.');}
    catch {say('Speicherung nicht möglich oder Browserspeicher voll. Entwurf als JSON sichern; Bilder gegebenenfalls verkleinern.');}
  };
  function syncCompatibility() {
    data.menuCategories=data.categories.menu.map(c=>({id:c.id,name:c.name,active:c.visible}));
    data.shopCategories=data.categories.products.map(c=>({id:c.id,name:c.name,active:c.visible}));
    data.products.forEach(r=>{r.image_data=r.imageData || '';});
  }
  exportButton.onclick=()=>{syncCompatibility();const url=URL.createObjectURL(new Blob([JSON.stringify(data,null,2)],{type:'application/json'})),a=document.createElement('a');a.href=url;a.download='vineria-verwaltung-entwurf.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);};
  $('#reset-demo').onclick=()=>{if(!confirm('Alle lokalen Teständerungen einschließlich Fotos zurücksetzen? Vorher bei Bedarf als JSON sichern.'))return;if(pendingPhotos){say('Zurücksetzen erst nach Abschluss der Bildverarbeitung.');return;}try{localStorage.removeItem(key);baseline=null;data=clone(original);undo=null;undoButton.hidden=true;picked={menu:'',products:''};dirty=false;render();say('Beispieldaten wiederhergestellt. Keine Website geändert.');}catch{say('Browserspeicher nicht erreichbar; es wurde nichts zurückgesetzt.');}};
  window.addEventListener('storage',e=>{if(e.key===key)say('Ein anderer Tab hat den Entwurf geändert. Vor dem Speichern abgleichen oder als JSON sichern.');});
  window.addEventListener('beforeunload',e=>{if(dirty){e.preventDefault();e.returnValue='';}});
  render();
})();
