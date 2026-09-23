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
      panel.querySelectorAll('a[href]').forEach(source=>{const li=document.createElement('li');li.className='cch-os-menu-accordion-content__item';const link=document.createElement('a');link.className='cch-os-site-menu-link';link.href=source.href;link.textContent=source.textContent.trim();li.append(link);group.querySelector('ul').append(li);});
      const list=document.createElement('ul');list.className='cch-os-house-cleaning-menu';const li=document.createElement('li');li.className='cch-os-house-cleaning-menu__item';li.append(group);list.append(li);nav.append(list);
    }else{const ul=document.createElement('ul');ul.className=index===0?'cch-os-site-menu__bold-links cch-os-bold-links cch-os-bold-links--services':'';const li=document.createElement('li');li.className='cch-os-bold-links__item';const a=document.createElement('a');a.className=index===0?'cch-os-bold-links__link':'cch-os-site-menu-link';a.href=trigger.href;a.textContent=trigger.textContent.trim();li.append(a);ul.append(li);nav.append(ul);}
  });
  document.body.append(rail,dialog);
  const menu=rail.querySelector('button');
  function closeMenu(){dialog.classList.add('is-hidden');dialog.setAttribute('aria-hidden','true');menu.setAttribute('aria-expanded','false');dialog.addEventListener('animationend',()=>{dialog.classList.remove('is-active');document.documentElement.classList.remove('cch-rail-open');menu.focus({preventScroll:true});},{once:true});}
  menu.addEventListener('click',()=>{dialog.classList.remove('is-hidden');dialog.classList.add('is-active');document.documentElement.classList.add('cch-rail-open');dialog.setAttribute('aria-hidden','false');menu.setAttribute('aria-expanded','true');});
  dialog.querySelector('.cch-os-menu-modal__closer').addEventListener('click',closeMenu);
  dialog.querySelector('.cch-os-menu-modal__backdrop').addEventListener('click',closeMenu);
  dialog.querySelector('.cch-os-menu-modal__main-content').addEventListener('click',e=>e.stopPropagation());
  document.addEventListener('keydown',e=>{if(e.key==='Escape'&&dialog.classList.contains('is-active'))closeMenu();});
  const mobile=matchMedia('(max-width:992px)');
  const updateMenu=()=>menu.classList.toggle('is-awaiting-scroll',!mobile.matches&&header.getBoundingClientRect().bottom>0);
  new IntersectionObserver(updateMenu).observe(header);mobile.addEventListener('change',updateMenu);updateMenu();

})();

// K's DEVELOP778 footer branch: hide on scroll, return after 500 ms,
// and dock at the footer. Source: k-hairsalon.jp/3.2/js/cmn.js, 2026-09-23.
(() => {
  const footer = document.querySelector('footer');
  if (!footer || document.getElementById('cch-bottom-bar')) return;
  const bar = document.createElement('div');
  bar.id = 'cch-bottom-bar'; bar.className = 'DEVELOP778 scrolled'; bar.dataset.pattern = '1';
  bar.innerHTML = '<div class="fixbtnwrap"><div class="inner"><div class="fixbtntel"><span data-tel><svg aria-hidden="true"><use href="/crystal-clean-home/brand/header/k-icons.svg#icon-tel"></use></svg>000-0000-0000<i class="teli">クリスタルクリーンホーム</i></span><p>［受付時間］8:00〜17:00（年中無休）※年末年始を除く</p></div><div class="contents_btn01"><a href="/crystal-clean-home/contact/"><span>お問い合わせはこちら</span></a><a href="/crystal-clean-home/cart/"><span>お見積りはこちら</span></a></div><div id="cch-bottom-top" class="cch-bottom-top"><a href="#" aria-label="ページトップへ移動"></a></div></div></div>';
  footer.before(bar);
  const wrap = bar.querySelector('.fixbtnwrap');
  let timer;
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
      if (scrolling) timer = setTimeout(() => { wrap.style.bottom = '0'; }, 500);
    }
  }
  window.addEventListener('scroll', () => positionBar(true), {passive:true});
  window.addEventListener('resize', () => positionBar(false));
  bar.querySelector('.cch-bottom-top a').addEventListener('click', e => {
    e.preventDefault(); window.scrollTo({top:0, behavior:matchMedia('(prefers-reduced-motion:reduce)').matches?'instant':'smooth'});
  });
  positionBar(false);
  setTimeout(() => { wrap.style.transform = 'translateY(0)'; }, 500);
})();

// Original accordion animation classes from osoujihonpo common.js.
(()=>{class T{constructor(){this.ANIMATING_CLASS="is-sliding",this.SPACING_MARGIN_PROPS=["padding-top","padding-bottom","margin-top","margin-bottom"],this.TRANSITION_PROPS=["transition-property","transition-duration","transition-timing-function"],this.slideUp=(e,t=300)=>{if(!this.canAnimate(e))return;e.classList.add(this.ANIMATING_CLASS),e.style.height=`${e.offsetHeight}px`,e.offsetHeight,this.setTransitionPropsValue(e,t);const s=["height",...this.SPACING_MARGIN_PROPS];this.setStylePropsValueToZero(e,s),setTimeout((()=>{const t=["display","height","overflow",...this.SPACING_MARGIN_PROPS,...this.TRANSITION_PROPS];this.removeStyleProps(e,t),e.classList.remove(this.ANIMATING_CLASS)}),t)}}slideDown(e,t=300){if(!this.canAnimate(e))return;e.classList.add(this.ANIMATING_CLASS),e.style.removeProperty("display");const s=window.getComputedStyle(e).display;e.style.display="none"!==s?s:"block";const i=e.offsetHeight,n=["height",...this.SPACING_MARGIN_PROPS];this.setStylePropsValueToZero(e,n),e.offsetHeight,e.style.height=`${i}px`,e.style.overflow="hidden",this.setTransitionPropsValue(e,t),this.removeStyleProps(e,this.SPACING_MARGIN_PROPS),setTimeout((()=>{const t=["height","overflow",...this.TRANSITION_PROPS];this.removeStyleProps(e,t),e.classList.remove(this.ANIMATING_CLASS)}),t)}slideToggle(e,t=300){this.isVisible(e)?this.slideUp(e,t):this.slideDown(e,t)}canAnimate(e){return!e.classList.contains(this.ANIMATING_CLASS)}isVisible(e){return"none"!==window.getComputedStyle(e).display}setTransitionPropsValue(e,t){const s=["height",...this.SPACING_MARGIN_PROPS].join(",");e.style.transitionProperty=s,e.style.transitionDuration=`${t}ms`,e.style.transitionTimingFunction="ease"}setStylePropsValueToZero(e,t){for(const s of t)e.style.setProperty(s,"0")}removeStyleProps(e,t){for(const s of t)e.style.removeProperty(s)}}class y extends T{constructor(e=300){super(),this.ANIMATION_CLASS="is-sliding",this.ACCORDION_CLASS="js-accordion",this.ACCORDION_TRIGGER_CLASS="js-accordion-trigger",this.animationDuration=e,this.init()}init(){const e=document.querySelectorAll(`#cch-side-menu .${this.ACCORDION_CLASS}`);e.length>0&&e.forEach((e=>{const t="true"===e.dataset.simpleType;e.querySelectorAll(`.${this.ACCORDION_TRIGGER_CLASS}`).forEach((e=>{e.addEventListener("click",(e=>this.accordion(t,e)))}))}))}accordion(e,t){const s=t.currentTarget,i=s.getAttribute("aria-controls"),n=document.getElementById(i);if(!(null==n?void 0:n.classList.contains(this.ANIMATION_CLASS))){if(!e){const e=s.closest(`.${this.ACCORDION_CLASS}`),t=null==e?void 0:e.querySelectorAll(`.${this.ACCORDION_TRIGGER_CLASS}:not([aria-controls="${i}"])`);null==t||t.forEach((e=>{const t=e.getAttribute("aria-controls"),s=document.getElementById(t);this.closeAccordion(e,s),this.slideUp(s,this.animationDuration)}))}"true"===s.getAttribute("aria-expanded")?this.closeAccordion(s,n):this.openAccordion(s,n)}}openAccordion(e,t){e.setAttribute("aria-expanded","true"),t.setAttribute("aria-hidden","false");const s=e.dataset.closedText;s&&(e.innerHTML=s),this.slideDown(t,this.animationDuration)}closeAccordion(e,t){e.setAttribute("aria-expanded","false"),t.setAttribute("aria-hidden","true");const s=e.dataset.openedText;s&&(e.innerHTML=s),this.slideUp(t,this.animationDuration)}}new y;})();
