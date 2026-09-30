(() => {
  'use strict';

  function mount() {
    if (document.getElementById('viewport-hud')) return;

    const hud = document.createElement('div');
    hud.id = 'viewport-hud';
    hud.setAttribute('aria-hidden', 'true');
    hud.style.cssText = [
      'all:initial', 'display:block', 'position:fixed', 'right:1px', 'bottom:1px',
      'z-index:2147483647', 'box-sizing:border-box', 'padding:2px 4px',
      'border-radius:2px', 'background:#111', 'color:#fff',
      'font:10px/14px ui-monospace,SFMono-Regular,Consolas,monospace',
      'white-space:nowrap', 'pointer-events:none', 'user-select:none'
    ].join(';');
    document.body.appendChild(hud);

    function update() {
      const width = window.innerWidth;
      const height = window.innerHeight;
      const breakpoint = width < 768 ? 'MOBILE' : width < 1024 ? 'TABLET' : 'DESKTOP';
      hud.textContent = `${width} × ${height} px | ${breakpoint}`;
    }

    let frame = 0;
    window.addEventListener('resize', () => {
      if (frame) return;
      frame = window.requestAnimationFrame(() => {
        frame = 0;
        update();
      });
    }, { passive: true });
    update();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', mount, { once: true });
  } else {
    mount();
  }
})();
