(() => {
  'use strict';
  const header = document.querySelector('#header.cch-header');
  if (!header) return;
  const nav = header.querySelector('#navArea');
  const toggle = nav.querySelector('.toggle_btn');
  const navigation = nav.querySelector('nav');
  const desktop = matchMedia('(min-width:993px)');
  const items = [...nav.querySelectorAll('.menu>ul>li')];
  const entries = items.map(item => ({item, trigger:item.querySelector(':scope>a'), panel:item.querySelector(':scope>.dropdown_menu')})).filter(entry => entry.panel);
  function closeMenus() {
    entries.forEach(({item,trigger,panel}) => {
      item.classList.remove('is-open');
      trigger.setAttribute('aria-expanded','false');
      panel.inert = true;
    });
  }
  function openMenu(entry) {
    closeMenus();
    entry.item.classList.add('is-open');
    entry.trigger.setAttribute('aria-expanded','true');
    entry.panel.inert = false;
  }
  function setDrawer(open) {
    document.documentElement.classList.toggle('cch-header-drawer-open',open && !desktop.matches);
    nav.classList.toggle('open',open);
    toggle.setAttribute('aria-expanded',String(open));
    toggle.setAttribute('aria-label',open ? 'メニューを閉じる' : 'メニューを開く');
    navigation.inert = !desktop.matches && !open;
    if (!open) closeMenus();
  }
  entries.forEach((entry,index) => {
    const {trigger,panel,item} = entry;
    panel.id = 'cch-header-panel-'+index;
    trigger.setAttribute('role','button');
    trigger.setAttribute('tabindex','0');
    trigger.setAttribute('aria-controls',panel.id);
    trigger.setAttribute('aria-expanded','false');
    panel.inert = true;
    item.addEventListener('mouseenter',() => {if(desktop.matches) openMenu(entry);});
    trigger.addEventListener('click',event => {
      event.preventDefault();
      item.classList.contains('is-open') ? closeMenus() : openMenu(entry);
    });
    trigger.addEventListener('keydown',event => {
      if (['Enter',' ','ArrowDown'].includes(event.key)) {
        event.preventDefault();
        if(event.key==='ArrowDown') {openMenu(entry);panel.querySelector('a')?.focus();}
        else trigger.click();
      }
    });
  });
  items.filter(item => !item.querySelector(':scope>.dropdown_menu')).forEach(item => item.addEventListener('mouseenter',() => {if(desktop.matches) closeMenus();}));
  header.querySelector('.h_top')?.addEventListener('mouseenter',() => {if(desktop.matches) closeMenus();});
  header.addEventListener('mouseleave',() => {if(desktop.matches) closeMenus();});
  header.addEventListener('focusout',event => {if(desktop.matches && !entries.some(({item})=>item.contains(event.relatedTarget))) closeMenus();});
  navigation.id = 'cch-header-navigation';
  toggle.setAttribute('role','button');
  toggle.setAttribute('tabindex','0');
  toggle.setAttribute('aria-controls',navigation.id);
  toggle.addEventListener('click',() => setDrawer(!nav.classList.contains('open')));
  toggle.addEventListener('keydown',event => {if(['Enter',' '].includes(event.key)){event.preventDefault();toggle.click();}});
  navigation.addEventListener('click',event => {if(event.target.closest('a[href]')) setDrawer(false);});
  document.addEventListener('keydown',event => {
    if (event.key === 'Escape') {
      const active = entries.find(({item})=>item.classList.contains('is-open'));
      if (nav.classList.contains('open')) {setDrawer(false);toggle.focus();}
      else if(active) {closeMenus();active.trigger.focus();}
    }
    if(event.key==='Tab' && !desktop.matches && nav.classList.contains('open')) {
      const focusable = [...navigation.querySelectorAll('a[href],[tabindex="0"],button'),toggle].filter(el=>!el.closest('[inert]') && el.getClientRects().length);
      const first=focusable[0],last=focusable[focusable.length-1];
      if(event.shiftKey && document.activeElement===first){event.preventDefault();last.focus();}
      else if(!event.shiftKey && document.activeElement===last){event.preventDefault();first.focus();}
    }
  });
  document.addEventListener('click',event => {if(!header.contains(event.target)){closeMenus();if(nav.classList.contains('open')) setDrawer(false);}});
  desktop.addEventListener('change',() => {setDrawer(false);navigation.inert=!desktop.matches;});
  new ResizeObserver(() => header.style.setProperty('--header-height',header.offsetHeight+'px')).observe(header);
  setDrawer(false);
})();
