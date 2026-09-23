(() => {
  'use strict';
  if (document.getElementById('viewport-hud')) return;
  const hud = document.createElement('div');
  hud.id = 'viewport-hud';
  hud.setAttribute('aria-hidden', 'true');
  const shadow = hud.attachShadow({mode: 'open'});
  shadow.innerHTML = `<style>
    :host{all:initial!important;position:fixed!important;inset:auto 1px 1px auto!important;margin:0!important;padding:0!important;border:0!important;background:transparent!important;overflow:visible!important;z-index:2147483647!important;pointer-events:none!important;width:max-content!important;height:auto!important}
    span{display:block;box-sizing:border-box;background:#111;color:#fff;padding:1px 3px;border-radius:2px;box-shadow:none;font:8px/1.1 ui-monospace,SFMono-Regular,Consolas,monospace;white-space:nowrap;pointer-events:none}
    @media print{:host{display:none!important}}
  </style><span></span>`;
  const label = shadow.querySelector('span');
  function update() {
    const width = window.innerWidth;
    const height = window.innerHeight;
    const breakpoint = width <= 640 ? 'MOBILE' : width <= 992 ? 'TABLET' : 'DESKTOP';
    label.textContent = `${width} × ${height} px · ${breakpoint}`;
  }
  document.body.append(hud);
  if (typeof hud.showPopover === 'function') {
    hud.setAttribute('popover', 'manual');
    hud.showPopover();
    // Keep the non-interactive label above dialogs in the browser top layer.
    document.addEventListener('toggle', event => {
      if (event.target !== hud && event.newState === 'open') {
        hud.hidePopover();
        hud.showPopover();
      }
    }, true);
  }
  update();
  window.addEventListener('resize', update, {passive: true});
  window.visualViewport?.addEventListener('resize', update, {passive: true});
})();
