(() => {
  const hero = document.querySelector('.home-first-view');
  const header = document.querySelector('.c-header');
  if (!hero || !header) return;
  let frame = 0;
  function updateHeaderSurface() {
    frame = 0;
    document.body.classList.toggle('is-past-home-first-view',
      hero.getBoundingClientRect().bottom <= header.getBoundingClientRect().height);
  }
  function scheduleHeaderSurface() {
    if (!frame) frame = requestAnimationFrame(updateHeaderSurface);
  }
  window.addEventListener('scroll', scheduleHeaderSurface, { passive: true });
  window.addEventListener('resize', scheduleHeaderSurface);
  updateHeaderSurface();
})();
