(() => {
  'use strict';
  const header = document.querySelector('#header.cch-header');
  if (!header || document.querySelector('.cch-side-rail')) return;
  const base = '/crystal-clean-home/';
  const rail = document.createElement('aside');
  rail.className = 'cch-side-rail';
  rail.setAttribute('aria-label', 'メニューとお見積り');
  rail.innerHTML = '<button class="cch-rail-menu" type="button" aria-label="メニューを開く" aria-haspopup="dialog" aria-controls="cch-side-menu" aria-expanded="false"><span class="cch-menu-lines" aria-hidden="true"></span><span>MENU</span></button><a class="cch-rail-cart" href="'+base+'cart/" aria-label="お見積り内容を確認"><svg viewBox="0 0 32 30" aria-hidden="true"><path d="M2 2h4l3 19h19M7 6l23 2-3 11H9"/><circle cx="11" cy="26" r="2"/><circle cx="26" cy="26" r="2"/></svg><span class="cch-cart-count" hidden></span><span>お見積り</span><small class="cch-cart-amount"></small></a>';
  const dialog = document.createElement('dialog');
  dialog.className = 'cch-drawer'; dialog.id = 'cch-side-menu';
  dialog.setAttribute('aria-labelledby', 'cch-drawer-title');
  dialog.innerHTML = '<div class="cch-drawer-head"><h2 class="cch-drawer-title" id="cch-drawer-title">MENU</h2><button class="cch-drawer-close" type="button" aria-label="メニューを閉じる">×</button></div><nav class="cch-drawer-links" aria-label="サイト全体メニュー"></nav>';
  const nav = dialog.querySelector('nav');
  function copyLink(source) { const a = document.createElement('a'); a.href = source.href; a.textContent = source.textContent.trim(); return a; }
  header.querySelectorAll('.menu>ul>li').forEach(item => {
    const trigger = item.querySelector(':scope>a');
    const panel = item.querySelector('.dropdown_menu');
    if (!panel) { if (trigger?.hasAttribute('href')) nav.append(copyLink(trigger)); return; }
    const details = document.createElement('details'), summary = document.createElement('summary'), body = document.createElement('div');
    summary.textContent = trigger.textContent.trim(); body.className = 'cch-drawer-services';
    panel.querySelectorAll('h3,a[href]').forEach(source => {
      if (source.tagName === 'H3') { const h = document.createElement('h3'); h.textContent = source.textContent; body.append(h); }
      else body.append(copyLink(source));
    });
    details.append(summary, body); nav.append(details);
  });
  document.body.append(rail, dialog);
  const menu = rail.querySelector('button');
  menu.addEventListener('click', () => { dialog.showModal(); menu.setAttribute('aria-expanded','true'); document.documentElement.classList.add('cch-rail-open'); });
  dialog.querySelector('.cch-drawer-close').addEventListener('click', () => dialog.close());
  dialog.addEventListener('click', e => { if(e.target===dialog){const r=dialog.getBoundingClientRect();if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom)dialog.close();} });
  dialog.addEventListener('close', () => { document.documentElement.classList.remove('cch-rail-open'); menu.setAttribute('aria-expanded','false'); menu.focus({preventScroll:true}); });
  dialog.querySelectorAll('a').forEach(a => a.addEventListener('click', () => dialog.close()));
  const mobile = matchMedia('(max-width:992px)');
  const updateMenu = () => menu.classList.toggle('is-awaiting-scroll', !mobile.matches && header.getBoundingClientRect().bottom > 0);
  new IntersectionObserver(updateMenu).observe(header); mobile.addEventListener('change', updateMenu); updateMenu();
  let map;
  function renderCart() {
    if (!map) return;
    let cart; try { cart = CCHCart.clean(JSON.parse(localStorage.getItem('cch-estimate-cart-v1')||'[]'),map); } catch { cart=[]; }
    const t=CCHCart.totals(cart,map), count=cart.reduce((n,l)=>n+l.qty,0), badge=rail.querySelector('.cch-cart-count');
    badge.textContent=count; badge.hidden=!count;
    const amount=t.total.toLocaleString('ja-JP')+'円'+(t.quote?'〜':'');
    rail.querySelector('.cch-cart-amount').textContent=count?amount:'';
    rail.querySelector('.cch-rail-cart').setAttribute('aria-label','お見積り内容を確認：'+count+'点、'+amount+(t.quote?'、個別見積りを含む':''));
  }
  async function prepareCart() {
    try {
      if (!window.CCHCart) await new Promise((resolve,reject)=>{ const s=document.createElement('script');s.src=base+'brand/shop/cart-core.js';s.onload=resolve;s.onerror=reject;document.head.append(s); });
      const embedded=document.getElementById('shop-catalog');
      let data;if(embedded)data=JSON.parse(embedded.textContent);else{const response=await fetch(base+'reference/catalog.json');if(!response.ok)throw new Error('catalog');data=await response.json();}
      map=CCHCart.index(data);renderCart();
    } catch { /* The cart link remains available if the summary cannot load. */ }
  }
  window.addEventListener('pageshow',renderCart);window.addEventListener('storage',renderCart);window.addEventListener('cch-cart-change',renderCart);
  prepareCart();
})();
