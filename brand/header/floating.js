(()=>{const l=document.createElement('link');l.rel='stylesheet';l.href='/crystal-clean-home/brand/header/bottom-bar.css?v=bar-solid-links1';document.head.append(l)})();
(() => {
  'use strict';
  const header = document.querySelector('#header.cch-header');
  if (!header || document.querySelector('.cch-side-rail')) return;
  const base = '/crystal-clean-home/';
  const rail = document.createElement('aside');
  rail.className = 'cch-side-rail';
  rail.setAttribute('aria-label', 'メニューとお見積り');
  rail.innerHTML = '<button class="cch-rail-menu" type="button" aria-label="メニューを開く" aria-haspopup="dialog" aria-controls="cch-side-menu" aria-expanded="false"><span class="cch-menu-lines" aria-hidden="true"></span><span>MENU</span></button><a class="cch-rail-cart" href="'+base+'cart/" aria-label="お見積り内容を確認"><svg viewBox="0 0 32 30" aria-hidden="true"><path d="M2 2h4l3 19h19M7 6l23 2-3 11H9"/><circle cx="11" cy="26" r="2"/><circle cx="26" cy="26" r="2"/></svg><span class="cch-cart-count" hidden></span><span>お見積り</span><small class="cch-cart-amount"></small></a>';
  rail.querySelector('button').innerHTML='<img src="'+base+'reference/assets/images/header/menu-open_pc.webp" alt="MENU" width="72" height="72">';
  rail.querySelector('.cch-rail-cart').remove();
  rail.setAttribute('aria-label','メニュー');
  const dialog=document.createElement('div');
  dialog.id='cch-side-menu';dialog.className='cch-os-menu-modal';dialog.setAttribute('aria-hidden','true');dialog.setAttribute('role','dialog');dialog.setAttribute('aria-label','サイト全体メニュー');
  dialog.innerHTML='<div class="cch-os-menu-modal__backdrop"><div class="cch-os-menu-modal__main-content"><button class="cch-os-menu-modal__closer" aria-label="メニューを閉じる"><img src="'+base+'reference/assets/images/header/menu-close.webp" alt="CLOSE" width="58" height="58"></button><nav class="cch-os-site-menu" aria-label="サイト全体メニュー"></nav></div></div>';
  const nav=dialog.querySelector('nav');
  header.querySelectorAll('.menu>ul>li').forEach((item,index)=>{
    const trigger=item.querySelector(':scope>a'), panel=item.querySelector('.dropdown_menu');
    if(!trigger)return;
    if(panel){
      const group=document.createElement('div');group.className='cch-os-menu-accordion js-accordion';group.dataset.simpleType='true';
      group.innerHTML='<p class="cch-os-menu-accordion__heading"><a class="cch-os-menu-accordion__link" href="'+base+'services/">'+trigger.textContent.trim()+'</a><button class="cch-os-menu-accordion__trigger js-accordion-trigger" aria-label="サービスと料金の詳細を開閉" aria-controls="cch-menu-services" aria-expanded="false" type="button"></button></p><ul class="cch-os-menu-accordion__content cch-os-menu-accordion-content" id="cch-menu-services"></ul>';
      panel.querySelectorAll('a[href]').forEach(source=>{const li=document.createElement('li');li.className='cch-os-menu-accordion-content__item';const link=document.createElement('a');link.className='cch-os-site-menu-link';link.setAttribute('href',source.getAttribute('href'));link.textContent=source.textContent.trim();li.append(link);group.querySelector('ul').append(li);});
      const list=document.createElement('ul');list.className='cch-os-house-cleaning-menu';const li=document.createElement('li');li.className='cch-os-house-cleaning-menu__item';li.append(group);list.append(li);nav.append(list);
    }else{const ul=document.createElement('ul');ul.className=index===0?'cch-os-site-menu__bold-links cch-os-bold-links cch-os-bold-links--services':'';const li=document.createElement('li');li.className='cch-os-bold-links__item';const a=document.createElement('a');a.className=index===0?'cch-os-bold-links__link':'cch-os-site-menu-link';a.setAttribute('href',trigger.getAttribute('href'));a.textContent=trigger.textContent.trim();li.append(a);ul.append(li);nav.append(ul);}
  });
  const links=document.createElement('div');links.className='cch-menu-links';links.append(...nav.children);nav.append(links);
  links.querySelectorAll(':scope>ul>li>a,.cch-os-menu-accordion__link').forEach(link=>{const label=document.createElement('span');label.className='cch-menu-label';label.textContent=link.textContent;link.replaceChildren(label)});
  const utilities=document.createElement('div');utilities.className='cch-menu-utilities';nav.append(utilities);
  function fitMenu(){const viewport=window.visualViewport;dialog.style.setProperty('--menu-screen-height',(viewport?.height||innerHeight)+'px');dialog.style.setProperty('--menu-screen-top',(viewport?.offsetTop||0)+'px')}
  window.addEventListener('resize',fitMenu);window.visualViewport?.addEventListener('resize',fitMenu);fitMenu();
  document.body.append(rail,dialog);
  const menu=rail.querySelector('button');
  function closeMenu(){if(dialog.classList.contains('is-hidden'))return;dialog.classList.add('is-hidden');dialog.setAttribute('aria-hidden','true');menu.setAttribute('aria-expanded','false');dialog.addEventListener('animationend',()=>{dialog.classList.remove('is-active');document.documentElement.classList.remove('cch-rail-open');document.dispatchEvent(new CustomEvent('cch-menu-change',{detail:{open:false}}));menu.focus({preventScroll:true});},{once:true});}
  menu.addEventListener('click',()=>{dialog.classList.remove('is-hidden');dialog.classList.add('is-active');document.documentElement.classList.add('cch-rail-open');dialog.setAttribute('aria-hidden','false');menu.setAttribute('aria-expanded','true');fitMenu();document.dispatchEvent(new CustomEvent('cch-menu-change',{detail:{open:true}}));dialog.querySelector('.cch-os-menu-modal__closer').focus({preventScroll:true});});
  dialog.querySelector('.cch-os-menu-modal__closer').addEventListener('click',closeMenu);
  dialog.querySelector('.cch-os-menu-modal__backdrop').addEventListener('click',closeMenu);
  dialog.querySelector('.cch-os-menu-modal__main-content').addEventListener('click',e=>e.stopPropagation());
  document.addEventListener('keydown',e=>{if(e.key==='Escape'&&dialog.classList.contains('is-active'))closeMenu();});
  const mobile=matchMedia('(max-width:992px)');
  const updateMenu=()=>menu.classList.toggle('is-awaiting-scroll',document.documentElement.dataset.cchPage==='home'&&!mobile.matches&&header.getBoundingClientRect().bottom>0);
  new IntersectionObserver(updateMenu).observe(header);mobile.addEventListener('change',updateMenu);updateMenu();

})();

// Hide while scrolling, return after the configured delay, and dock above the footer.
(() => {
  const footer = document.querySelector('footer');
  if (!footer || document.getElementById('cch-bottom-bar')) return;
  const bar = document.createElement('div');
  bar.id = 'cch-bottom-bar'; bar.className = 'DEVELOP778 scrolled'; bar.dataset.pattern = '1';
  bar.innerHTML = '<div class="fixbtnwrap"><div class="inner"><div class="fixbtntel"><span data-tel><svg aria-hidden="true"><use href="/crystal-clean-home/brand/header/k-icons.svg#icon-tel"></use></svg>000-0000-0000<i class="teli" style="color:#000!important">※営業電話は業務に支障をきたす為、ご遠慮ください。</i></span><p>［受付時間］8:00〜17:00（年中無休）※年末年始を除く</p></div><div class="contents_btn01"><button type="button" class="cch-bottom-cart" aria-label="お見積り概要を表示する" aria-expanded="false" aria-controls="cch-cart-popup"><img src="/crystal-clean-home/brand/header/cart-mark.svg?v=red1" alt="" width="24" height="24"><span>お見積り</span></button><a href="/crystal-clean-home/contact/"><span>お問い合わせはこちら</span></a></div><div id="cch-bottom-top" class="cch-bottom-top"><a href="#" aria-label="ページトップへ移動"></a></div></div></div>';
  footer.before(bar);
  const utilities=document.querySelector('.cch-menu-utilities');
  if(utilities){
    const social=document.createElement('div');social.className='cch-menu-social';social.setAttribute('aria-label','SNS（リンク未設定）');
    for(const [id,label] of [['x','X'],['instagram','Instagram'],['tiktok','TikTok'],['youtube','YouTube']]){const icon=document.createElement('span');icon.title=label+'（リンク未設定）';icon.innerHTML='<img src="/crystal-clean-home/brand/shared-ui/social/'+id+'.png" alt="'+label+'" width="36" height="36">';social.append(icon)}
    const details=document.createElement('div');details.className='cch-menu-contact';details.setAttribute('aria-label','連絡先・受付時間');
    const phone=document.createElement('p');phone.className='cch-menu-phone';phone.textContent=bar.querySelector('[data-tel]').childNodes[1].textContent.trim();
    const hours=document.createElement('p');hours.className='cch-menu-hours';hours.textContent=bar.querySelector('.fixbtntel p').textContent;
    const actions=document.createElement('div');actions.className='cch-menu-actions';actions.innerHTML='<a href="/crystal-clean-home/contact/">お問い合わせはこちら</a><a class="cch-menu-estimate" href="/crystal-clean-home/cart/"><img src="/crystal-clean-home/brand/header/cart-mark.svg?v=red1" alt="" width="20" height="20">お見積りはこちら</a>';
    actions.prepend(actions.querySelector('.cch-menu-estimate'));details.append(phone,hours,actions);utilities.append(social,details);
  }
  const headerPayments=document.querySelector('#header .cch-payments');
  if(headerPayments){const hours=bar.querySelector('.fixbtntel>p');const group=document.createElement('div');group.className='cch-bar-hours';hours.before(group);group.append(hours);const payments=headerPayments.cloneNode(true);payments.classList.add('cch-bar-payments');payments.querySelector('.cch-payments-label')?.remove();group.append(payments)}
  const wrap = bar.querySelector('.fixbtnwrap');
  const popup = document.createElement('div');
  popup.id='cch-cart-popup'; popup.className='c-cart-popup';
  popup.innerHTML='<a class="c-cart-popup__link" href="/crystal-clean-home/cart/">カートの中身を確認する</a><p class="c-cart-popup__overview">現在<span data-count>0</span>点のメニューが入っています。</p><p class="c-cart-popup__price">合計金額 ¥<span data-amount>0</span>（税込）</p>';
  wrap.append(popup);
  const cartButton=bar.querySelector('.cch-bottom-cart');
  // Toggle without a transition to match the popup interaction.
  cartButton.addEventListener('click',()=>{popup.classList.toggle('is-active');cartButton.setAttribute('aria-expanded',String(popup.classList.contains('is-active')));positionPopup();updateCart();});
  function closeCartPopup(){popup.classList.remove('is-active');cartButton.setAttribute('aria-expanded','false');}
  document.addEventListener('click',event=>{if(!popup.contains(event.target)&&!cartButton.contains(event.target))closeCartPopup();});
  document.addEventListener('keydown',event=>{if(event.key==='Escape'&&popup.classList.contains('is-active')){closeCartPopup();cartButton.focus({preventScroll:true});}});
  const deviceUI=()=>window.CCHDeviceUI?.[matchMedia('(max-width:992px)').matches?'mobile':'desktop']||{};
  function positionPopup(){const settings=deviceUI(),width=settings.cartPopupWidth||322,r=cartButton.getBoundingClientRect(),w=wrap.getBoundingClientRect();popup.style.width=width+'px';popup.style.left=Math.max(5,Math.min(w.width-width,r.right-w.left-width+22))+'px';popup.style.bottom=(w.bottom-r.top+(settings.cartPopupGap||20))+'px';popup.style.setProperty('--cart-tip-right',Math.max(16,Math.min(282,parseFloat(popup.style.left)+310-(r.left-w.left+r.width/2)))+'px');}
  let cartIndex;
  const cartReady=(async()=>{if(!window.CCHCart)await new Promise((resolve,reject)=>{const script=document.createElement('script');script.src='/crystal-clean-home/brand/shop/cart-core.js';script.onload=resolve;script.onerror=reject;document.head.append(script)});if(!window.CCHReferenceCatalog)await new Promise((resolve,reject)=>{const script=document.createElement('script');script.src='/crystal-clean-home/reference/catalog.js';script.onload=resolve;script.onerror=reject;document.head.append(script)});cartIndex=CCHCart.index(window.CCHReferenceCatalog)})();
  async function updateCart(){try{await cartReady;const cart=CCHCart.clean(JSON.parse(localStorage.getItem('cch-estimate-cart-v1')||'[]'),cartIndex),totals=CCHCart.totals(cart,cartIndex);popup.querySelector('[data-count]').textContent=cart.reduce((n,l)=>n+l.qty,0);popup.querySelector('[data-amount]').textContent=totals.total.toLocaleString()+(totals.quote?'＋個別見積り':'')}catch(error){console.error('Cart summary:',error);popup.querySelector('[data-amount]').textContent='—'}}
  window.addEventListener('cch-cart-change',updateCart);window.addEventListener('storage',updateCart);window.addEventListener('pageshow',updateCart);window.addEventListener('resize',positionPopup);updateCart();
  let timer;
  document.addEventListener('cch-menu-change',event=>{bar.inert=event.detail.open;bar.setAttribute('aria-hidden',String(event.detail.open));if(event.detail.open){clearTimeout(timer);closeCartPopup()}else positionBar(false)});
  function positionBar(scrolling) {
    const h = wrap.getBoundingClientRect().height;
    bar.style.height = h + 'px';
    const top = bar.getBoundingClientRect().top + window.scrollY;
    clearTimeout(timer);
    if (scrollY + innerHeight >= top + h) {
      bar.style.position = 'relative';
      Object.assign(wrap.style, {position:'absolute', bottom:'auto', top:'0'});
    } else {
      bar.style.position = 'inherit';
      Object.assign(wrap.style, {position:'fixed', bottom:scrolling ? -h+'px' : '0', top:'auto'});
      if (scrolling) timer = setTimeout(() => { wrap.style.bottom = '0'; }, deviceUI().barReturnDelay??500);
    }
  }
  window.addEventListener('scroll', () => positionBar(true), {passive:true});
  window.addEventListener('resize', () => positionBar(false));
  bar.querySelector('.cch-bottom-top a').addEventListener('click', e => {
    e.preventDefault(); window.scrollTo({top:0, behavior:matchMedia('(prefers-reduced-motion:reduce)').matches?'instant':'smooth'});
  });
  positionBar(false);
  setTimeout(() => { wrap.style.transform = 'translateY(0)'; }, deviceUI().barReturnDelay??500);
})();

// Accordion animation preserves expansion height and spacing.
(()=>{class T{constructor(){this.ANIMATING_CLASS="is-sliding",this.SPACING_MARGIN_PROPS=["padding-top","padding-bottom","margin-top","margin-bottom"],this.TRANSITION_PROPS=["transition-property","transition-duration","transition-timing-function"],this.slideUp=(e,t=300)=>{if(!this.canAnimate(e))return;e.classList.add(this.ANIMATING_CLASS),e.style.height=`${e.offsetHeight}px`,e.offsetHeight,this.setTransitionPropsValue(e,t);const s=["height",...this.SPACING_MARGIN_PROPS];this.setStylePropsValueToZero(e,s),setTimeout((()=>{const t=["display","height","overflow",...this.SPACING_MARGIN_PROPS,...this.TRANSITION_PROPS];this.removeStyleProps(e,t),e.classList.remove(this.ANIMATING_CLASS)}),t)}}slideDown(e,t=300){if(!this.canAnimate(e))return;e.classList.add(this.ANIMATING_CLASS),e.style.removeProperty("display");const s=window.getComputedStyle(e).display;e.style.display="none"!==s?s:"block";const i=e.offsetHeight,n=["height",...this.SPACING_MARGIN_PROPS];this.setStylePropsValueToZero(e,n),e.offsetHeight,e.style.height=`${i}px`,e.style.overflow="hidden",this.setTransitionPropsValue(e,t),this.removeStyleProps(e,this.SPACING_MARGIN_PROPS),setTimeout((()=>{const t=["height","overflow",...this.TRANSITION_PROPS];this.removeStyleProps(e,t),e.classList.remove(this.ANIMATING_CLASS)}),t)}slideToggle(e,t=300){this.isVisible(e)?this.slideUp(e,t):this.slideDown(e,t)}canAnimate(e){return!e.classList.contains(this.ANIMATING_CLASS)}isVisible(e){return"none"!==window.getComputedStyle(e).display}setTransitionPropsValue(e,t){const s=["height",...this.SPACING_MARGIN_PROPS].join(",");e.style.transitionProperty=s,e.style.transitionDuration=`${t}ms`,e.style.transitionTimingFunction="ease"}setStylePropsValueToZero(e,t){for(const s of t)e.style.setProperty(s,"0")}removeStyleProps(e,t){for(const s of t)e.style.removeProperty(s)}}class y extends T{constructor(e=300){super(),this.ANIMATION_CLASS="is-sliding",this.ACCORDION_CLASS="js-accordion",this.ACCORDION_TRIGGER_CLASS="js-accordion-trigger",this.animationDuration=e,this.init()}init(){const e=document.querySelectorAll(`#cch-side-menu .${this.ACCORDION_CLASS}`);e.length>0&&e.forEach((e=>{const t="true"===e.dataset.simpleType;e.querySelectorAll(`.${this.ACCORDION_TRIGGER_CLASS}`).forEach((e=>{e.addEventListener("click",(e=>this.accordion(t,e)))}))}))}accordion(e,t){const s=t.currentTarget,i=s.getAttribute("aria-controls"),n=document.getElementById(i);if(!(null==n?void 0:n.classList.contains(this.ANIMATION_CLASS))){if(!e){const e=s.closest(`.${this.ACCORDION_CLASS}`),t=null==e?void 0:e.querySelectorAll(`.${this.ACCORDION_TRIGGER_CLASS}:not([aria-controls="${i}"])`);null==t||t.forEach((e=>{const t=e.getAttribute("aria-controls"),s=document.getElementById(t);this.closeAccordion(e,s),this.slideUp(s,this.animationDuration)}))}"true"===s.getAttribute("aria-expanded")?this.closeAccordion(s,n):this.openAccordion(s,n)}}openAccordion(e,t){e.setAttribute("aria-expanded","true"),t.setAttribute("aria-hidden","false");const s=e.dataset.closedText;s&&(e.innerHTML=s),this.slideDown(t,this.animationDuration)}closeAccordion(e,t){e.setAttribute("aria-expanded","false"),t.setAttribute("aria-hidden","true");const s=e.dataset.openedText;s&&(e.innerHTML=s),this.slideUp(t,this.animationDuration)}}new y(window.CCHDeviceUI?.[matchMedia("(max-width:992px)").matches?"mobile":"desktop"]?.accordionDuration||300);})();
