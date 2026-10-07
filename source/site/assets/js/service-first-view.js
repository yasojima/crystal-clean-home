(() => {
  const header = document.querySelector('.c-header');
  const frames = [...document.querySelectorAll('.c-service-page .c-first-view')];
  if (!header || !frames.length) return;
  let pending = false;
  const px = value => `${Math.max(0, value).toFixed(3)}px`;
  const set = (element, name, value) => {
    if (element.style.getPropertyValue(name) !== value) element.style.setProperty(name, value);
  };
  const fit = () => {
    pending = false;
    const headerHeight = header.getBoundingClientRect().height;
    frames.forEach(frame => {
      const hero = frame.querySelector('.c-house-cleaning-mv--check');
      const selector = frame.querySelector('.c-service-selector');
      const cards = frame.querySelector('.p-page-anchors__cards');
      if (!hero || !selector || !cards) return;
      const budget = Math.max(0, Math.min(window.innerHeight, 800) - headerHeight - 16);
      set(frame, '--first-view-height', px(budget));
      set(frame, '--selector-cards-height', 'none');
      const text = hero.querySelector('.c-house-cleaning-mv__text');
      const projection = parseFloat(getComputedStyle(hero).getPropertyValue('--hero-projection'));
      const minimum = Math.max(112, (text?.getBoundingClientRect().height || 0) + projection + 16);
      const measure = space => {
        set(frame, '--first-view-selector-space', px(space));
        return selector.getBoundingClientRect().height;
      };
      let space = window.innerWidth < 768 ? 24 : 36;
      let selectorHeight = measure(space);
      if (selectorHeight + minimum > budget) {
        let low = 4, high = space;
        for (let i = 0; i < 8; i++) {
          const middle = (low + high) / 2;
          if (measure(middle) + minimum <= budget) low = middle;
          else high = middle;
        }
        space = low;
        selectorHeight = measure(space);
      }
      if (selectorHeight + minimum > budget && cards.children.length) {
        const gridHeight = cards.getBoundingClientRect().height;
        const allowance = Math.max(64, budget - minimum - (selectorHeight - gridHeight));
        const bounds = [...cards.children].map(card => card.getBoundingClientRect());
        const top = Math.min(...bounds.map(rect => rect.top));
        const rowEnds = [...new Set(bounds.map(rect => rect.bottom - top))].sort((a, b) => a - b);
        const visible = rowEnds.filter(end => end <= allowance + 1);
        set(frame, '--selector-cards-height', px(visible.length ? visible.at(-1) : rowEnds[0]));
        selectorHeight = selector.getBoundingClientRect().height;
      }
      const maximum = window.innerWidth < 768 ? 184 : 315;
      set(frame, '--banner-height', px(Math.max(minimum, Math.min(maximum, budget - selectorHeight))));
    });
  };
  const schedule = () => {
    if (pending) return;
    pending = true;
    requestAnimationFrame(fit);
  };
  const observer = new ResizeObserver(schedule);
  observer.observe(header);
  frames.forEach(frame => {
    observer.observe(frame);
    for (const element of frame.querySelectorAll('.p-page-anchors__heading,.p-page-anchors__cards')) observer.observe(element);
    new MutationObserver(schedule).observe(frame, {childList: true, subtree: true, characterData: true});
  });
  window.addEventListener('resize', schedule, {passive: true});
  window.addEventListener('pageshow', schedule);
  document.fonts.ready.then(schedule);
  fit();
})();
