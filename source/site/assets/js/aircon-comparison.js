(() => {
  for (const comparison of document.querySelectorAll('.c-aircon-compare')) {
    const line = document.createElement('span');
    line.className = 'c-aircon-compare__line';
    line.setAttribute('aria-hidden', 'true');

    const handle = document.createElement('span');
    handle.className = 'c-aircon-compare__handle';
    handle.setAttribute('role', 'slider');
    handle.setAttribute('tabindex', '0');
    handle.setAttribute('aria-label', '清掃前後の比較');
    handle.setAttribute('aria-valuemin', '0');
    handle.setAttribute('aria-valuemax', '100');

    const before = document.createElement('span');
    before.className = 'c-aircon-compare__label c-aircon-compare__label--before';
    before.textContent = 'Before';
    const after = document.createElement('span');
    after.className = 'c-aircon-compare__label c-aircon-compare__label--after';
    after.textContent = 'After';
    comparison.append(line, handle, before, after);

    let split = 50;
    let activePointer = null;

    const update = value => {
      split = Math.max(0, Math.min(100, value));
      comparison.style.setProperty('--compare-split', `${split}%`);
      handle.setAttribute('aria-valuenow', String(Math.round(split)));
      handle.setAttribute('aria-valuetext', `清掃前${Math.round(split)}%、清掃後${Math.round(100 - split)}%`);

      const width = comparison.getBoundingClientRect().width;
      if (!width) return;
      before.hidden = false;
      after.hidden = false;
      const beforeWidth = before.offsetWidth;
      const afterWidth = after.offsetWidth;
      before.hidden = width * split / 100 < beforeWidth + 24;
      after.hidden = width * (100 - split) / 100 < afterWidth + 24;
    };

    const moveTo = clientX => {
      const rect = comparison.getBoundingClientRect();
      if (rect.width) update((clientX - rect.left) / rect.width * 100);
    };

    comparison.addEventListener('pointerdown', event => {
      if (event.button !== 0) return;
      activePointer = event.pointerId;
      comparison.setPointerCapture(activePointer);
      moveTo(event.clientX);
      event.preventDefault();
    });
    comparison.addEventListener('pointermove', event => {
      if (event.pointerId === activePointer) moveTo(event.clientX);
    });
    const endDrag = event => {
      if (event.pointerId !== activePointer) return;
      if (comparison.hasPointerCapture(activePointer)) comparison.releasePointerCapture(activePointer);
      activePointer = null;
    };
    comparison.addEventListener('pointerup', endDrag);
    comparison.addEventListener('pointercancel', endDrag);

    handle.addEventListener('keydown', event => {
      const step = event.shiftKey ? 10 : 2;
      const value = {
        ArrowLeft: split - step,
        ArrowDown: split - step,
        ArrowRight: split + step,
        ArrowUp: split + step,
        Home: 0,
        End: 100,
      }[event.key];
      if (value === undefined) return;
      update(value);
      event.preventDefault();
    });

    new ResizeObserver(() => update(split)).observe(comparison);
    update(split);
  }
})();
