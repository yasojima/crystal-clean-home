/* The shared product library owns pointer dragging and tab switching. */
(() => {
  const root = document.getElementById('cch-first-lp');
  if (!root) return;
  root.querySelectorAll('.js-tab-buttons').forEach(group => {
    const tabs = [...group.querySelectorAll('[role="tab"]')];
    group.addEventListener('keydown', event => {
      const current = tabs.indexOf(event.target);
      if (current < 0) return;
      let next;
      if (event.key === 'ArrowRight') next = (current + 1) % tabs.length;
      if (event.key === 'ArrowLeft') next = (current + tabs.length - 1) % tabs.length;
      if (event.key === 'Home') next = 0;
      if (event.key === 'End') next = tabs.length - 1;
      if (next === undefined) return;
      event.preventDefault();
      tabs[next].click();
      tabs[next].focus();
    });
  });
  function enhanceSliders() {
    root.querySelectorAll('.js-compare-image').forEach(view => {
      const control = view.querySelector('.icv__control');
      const wrapper = view.querySelector('.icv__wrapper');
      if (!control || !wrapper || control.hasAttribute('role')) return;
      control.setAttribute('role', 'slider');
      control.setAttribute('tabindex', '0');
      control.setAttribute('aria-label', 'BeforeとAfterの比較位置');
      control.setAttribute('aria-valuemin', '0');
      control.setAttribute('aria-valuemax', '100');
      const reflect = () => {
        const match = control.style.left.match(/([\d.]+)%/);
        const value = match ? Math.round(Number(match[1])) : 50;
        control.setAttribute('aria-valuenow', String(value));
        control.setAttribute('aria-valuetext', 'Before ' + value + '％、After ' + (100 - value) + '％');
      };
      reflect();
      new MutationObserver(reflect).observe(control, {attributes:true, attributeFilter:['style']});
      control.addEventListener('keydown', event => {
        let value = Number(control.getAttribute('aria-valuenow'));
        const step = event.shiftKey ? 10 : 5;
        if (event.key === 'ArrowRight') value += step;
        else if (event.key === 'ArrowLeft') value -= step;
        else if (event.key === 'Home') value = 0;
        else if (event.key === 'End') value = 100;
        else return;
        event.preventDefault();
        value = Math.max(0, Math.min(100, value));
        wrapper.style.width = 'calc(100% - ' + value + '%)';
        control.style.left = 'calc(' + value + '% - 25px)';
      });
      const before = view.querySelector('.icv__label-before');
      const after = view.querySelector('.icv__label-after');
      if (before) before.textContent = 'Before';
      if (after) after.textContent = 'After';
    });
  }
  enhanceSliders();
  window.addEventListener('load', enhanceSliders, {once:true});
  root.querySelectorAll('a[href^="#"]').forEach(link => {
    link.addEventListener('click', event => {
      const target = document.getElementById(link.hash.slice(1));
      if (!target) return;
      event.preventDefault();
      target.setAttribute('tabindex', '-1');
      target.focus({preventScroll:true});
      target.scrollIntoView({behavior:matchMedia('(prefers-reduced-motion: reduce)').matches ? 'instant' : 'smooth',block:'start'});
      history.replaceState(null, '', link.hash);
    });
  });
})();
