'use strict';
(()=>{
 const seed=document.getElementById('vde-content-seed');if(!seed)return;
 const cfg=JSON.parse(seed.textContent),KEY='vineria-review-content-v3',clone=x=>JSON.parse(JSON.stringify(x));
 const root=new URL(cfg.root,location.href),shop=new URL(cfg.shop||'shop/index.html',location.href);
 const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
 const money=v=>(Number(v||0)/100).toLocaleString('de-DE',{style:'currency',currency:'EUR'});
 let data=clone(cfg.content);
 try{const saved=JSON.parse(localStorage.getItem(KEY)||'null');if(saved?.schema===3&&Array.isArray(saved.sections)&&Array.isArray(saved.products)&&saved.news&&saved.instagram)data=saved;}catch{}

 // User-selected Instagram set: refresh only gallery assets, not other local content.
 const approvedGallery=cfg.content.instagram;
 if(approvedGallery?.selection_id&&data.instagram.selection_id!==approvedGallery.selection_id){
   data.instagram={...data.instagram,selection_id:approvedGallery.selection_id,items:clone(approvedGallery.items),count:approvedGallery.count,connected:false,display_mode:'curated_local_selection'};
 }
 function url(value){if(!value)return '';if(/^data:image\/(jpeg|png|webp);base64,[A-Za-z0-9+/=]+$/.test(value))return value;try{const u=new URL(value,root);return ['http:','https:'].includes(u.protocol)||u.protocol==='file:'&&location.protocol==='file:'?u.href:'';}catch{return '';}}
 function active(p){return p.visible!==false;}
 function detail(p){return new URL('produkt/index.html?id='+encodeURIComponent(p.id),shop).href;}
 function photo(p){const src=url(p.image);return src?`<img src="${esc(src)}" alt="${esc(p.imageAlt||p.name)}" loading="lazy" data-real-product="${esc(p.id)}">`:`<span class="vde-no-photo">${esc(p.name||'Produkt')}</span>`;}
 function buy(p){return `<div class="buy-row"><span class="price" data-price>${money(p.price)}</span><span class="note">${p.pickup?'Nur Abholung':'Beispielpreis'}</span></div><div class="unit" data-unit>${p.amount>0?money(Math.round(p.price*1000/p.amount))+(p.unit==='ml'?'/l':'/kg'):''} · zzgl. Versand</div><select data-variant aria-label="Format für ${esc(p.name)}"><option value="single">${esc(p.pack||'Einheit')} · ${money(p.price)}</option>${p.case>0?`<option value="case">${p.case} × ${esc(p.pack)} · ${money(p.casePrice)}</option>`:''}</select><button class="btn" data-add="${esc(p.id)}">In den Warenkorb +</button>`;}
 function card(p){return `<article class="product-card" data-product="${esc(p.id)}" data-category="${esc(p.category)}"><a href="${esc(detail(p))}"><div class="product-art real-product-photo ${p.unit==='ml'?'photo-wine':'photo-pack'}">${photo(p)}</div></a><div class="eyebrow">${esc([p.brand,p.pack].filter(Boolean).join(' · '))}</div><h2><a href="${esc(detail(p))}">${esc(p.name)}</a></h2><p>${esc(p.description)}</p>${buy(p)}</article>`;}
 function menu(){const host=document.querySelector('[data-live-menu]');if(!host)return;const sections=data.sections.filter(active);host.replaceChildren();host.hidden=!sections.length;if(!sections.length)return;
 const tabs=document.createElement('div');tabs.className='tabs live-tabs';tabs.setAttribute('role','tablist');tabs.setAttribute('aria-label','Speisekarte');host.append(tabs);
 for(const section of sections){const id='live-'+section.id;const b=document.createElement('button');b.type='button';b.id='tab-'+id;b.textContent=section.label;b.setAttribute('role','tab');b.setAttribute('aria-controls',id);b.dataset.liveTab=id;tabs.append(b);const panel=document.createElement('section');panel.className='live-menu-panel';panel.id=id;panel.setAttribute('role','tabpanel');panel.setAttribute('aria-labelledby',b.id);panel.innerHTML=`<h3>${esc(section.label)}</h3><div class="live-menu-rows">${section.items.filter(active).map(r=>`<article class="live-menu-item"><div><h4>${esc(r.name)}</h4><p>${esc(r.description)}</p></div><span class="price">${money(r.price)}</span></article>`).join('')||'<p>Zurzeit keine Einträge.</p>'}</div>`;host.append(panel);}
 const buttons=[...tabs.children];function choose(i,focus=false){buttons.forEach((b,n)=>{b.setAttribute('aria-selected',String(n===i));b.tabIndex=n===i?0:-1;document.getElementById(b.dataset.liveTab).hidden=n!==i;});if(focus)buttons[i].focus();}
 buttons.forEach((b,i)=>{b.onclick=()=>choose(i);b.onkeydown=e=>{if(!['ArrowRight','ArrowLeft','Home','End'].includes(e.key))return;e.preventDefault();choose(e.key==='Home'?0:e.key==='End'?buttons.length-1:(i+(e.key==='ArrowRight'?1:buttons.length-1))%buttons.length,true);};});choose(0);
 }
 function extras(){const news=document.querySelector('[data-live-news]');if(news){const now=Date.now(),items=data.news.items.filter(n=>active(n)&&(!n.starts||Date.parse(n.starts)<=now)&&(!n.ends||Date.parse(n.ends)>now)).slice(0,data.news.limit);news.hidden=!data.news.enabled||!items.length;news.innerHTML='<p class="eyebrow">Aktuelles aus der Vineria</p><div class="live-news-grid">'+items.map(n=>`<article class="live-news-card ${n.image?'':'text-only'}">${url(n.image)?`<img src="${esc(url(n.image))}" alt="${esc(n.imageAlt||n.title)}" loading="eager">`:''}<div>${n.example?'<small>GESTALTUNGSBEISPIEL · kein bestätigter Termin</small>':''}<h3>${esc(n.title)}</h3><p>${esc(n.text).replace(/\n/g,'<br>')}</p>${n.link&&url(n.link)?`<a href="${esc(url(n.link))}" rel="noopener">${esc(n.linkLabel||'Mehr erfahren')} ↗</a>`:''}</div></article>`).join('')+'</div>';}

 const ig=document.querySelector('[data-live-instagram]');
 if(ig){
  ig.hidden=!data.instagram.enabled;
  const rows=data.instagram.items.slice(0,data.instagram.count);
  const sourceLink=x=>{try{const u=new URL(x.permalink);return ['www.instagram.com','instagram.com'].includes(u.hostname)&&u.protocol==='https:'?u.href:'https://www.instagram.com/'+encodeURIComponent(x.account||'vineria.del.este')+'/';}catch{return 'https://www.instagram.com/vineria.del.este/';}};
  ig.innerHTML='<div class="live-instagram-head"><div><p class="eyebrow">Einblicke</p><h2>Die Vineria in Bildern.</h2></div><div class="live-instagram-accounts"><a href="https://www.instagram.com/vineria.del.este/" target="_blank" rel="noopener noreferrer">@vineria.del.este ↗</a><a href="https://www.instagram.com/vineriadeleste/" target="_blank" rel="noopener noreferrer">@vineriadeleste ↗</a></div></div>'
   +'<div class="live-instagram-grid" data-photo-count="'+rows.length+'">'+rows.map(x=>'<a data-selected-instagram="'+esc(x.id||'')+'" href="'+esc(sourceLink(x))+'" target="_blank" rel="noopener noreferrer"><img src="'+esc(url(x.image))+'" alt="'+esc(x.alt)+'" loading="lazy"></a>').join('')+'</div>'
   +'<p class="live-note">Ausgewählte Originalaufnahmen aus beiden Instagram-Profilen. Jeder Bildlink führt zum zugehörigen Beitrag. Diese Auswahl ist lokal gespeichert; noch kein automatisch aktualisierter Instagram-Feed.</p>';
 }
}
 function storefront(){if(!window.VDE)return;window.VDE.products=data.products.filter(active);const grid=document.querySelector('.products');if(grid){grid.innerHTML=window.VDE.products.map(card).join('');const filters=document.querySelector('.filters');if(filters){const cats=[...new Set(window.VDE.products.map(p=>p.category))],labels={conservas:'Konserven',embutidos:'Wurst & Cecina',weisswein:'Weißwein',rotwein:'Rotwein'};filters.innerHTML='<button data-filter="all" aria-pressed="true">Alles</button>'+cats.map(x=>`<button data-filter="${esc(x)}" aria-pressed="false">${esc(labels[x]||x)}</button>`).join('');}}
 const holder=document.querySelector('[data-live-product]');if(holder){const id=new URLSearchParams(location.search).get('id')||cfg.product;const p=data.products.find(x=>x.id===id&&active(x));holder.innerHTML=p?`<div class="product-art real-product-photo ${p.unit==='ml'?'photo-wine':'photo-pack'}">${photo(p)}</div><div data-product="${esc(p.id)}"><p class="eyebrow">${esc(p.brand)}</p><h1>${esc(p.name)}</h1><p>${esc(p.description)}</p>${buy(p)}<p class="live-note">${esc(p.note||'Kennzeichnung und Verfügbarkeit vor Verkaufsstart bestätigen.')}</p></div>`:`<section><h1>Zurzeit nicht verfügbar.</h1><a class="btn" href="${esc(shop.href)}">Zur Tienda</a></section>`;}}
 function save(next){localStorage.setItem(KEY,JSON.stringify(next));data=clone(next);window.dispatchEvent(new CustomEvent('vde:content-change'));}
 window.VdeReview={state:()=>clone(data),defaults:()=>clone(cfg.content),save,reset:()=>{localStorage.removeItem(KEY);data=clone(cfg.content);},esc,money,url,KEY};
 menu();extras();storefront();
 window.addEventListener('storage',e=>{if(e.key===KEY)location.reload();});
})();
