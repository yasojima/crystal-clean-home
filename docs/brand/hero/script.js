(() => {
  const hero = document.querySelector('#cch-hero');
  if (!hero) return;
  const header = document.querySelector('#header');
  if (header) {
    const syncHeaderHeight = () => hero.style.setProperty('--hero-header-height', header.getBoundingClientRect().height + 'px');
    syncHeaderHeight();
    new ResizeObserver(syncHeaderHeight).observe(header);
  }
  const lenis = new Lenis({
    autoRaf: true,
    duration: 2,
    virtualScroll: ({event}) => {
      const nativeInput = event.composedPath().some(node => node instanceof Element && node.matches('#header, dialog, .simulation'));
      const nativeMode = nativeInput || document.documentElement.classList.contains('cch-header-drawer-open') || document.querySelector('dialog[open]');
      if (nativeMode) {
        lenis.reset();
        return false;
      }
      return true;
    }
  });
  gsap.registerPlugin(ScrollTrigger);
  lenis.on('scroll', ScrollTrigger.update);
  gsap.utils.toArray('#cch-hero .js-imgScale').forEach(function(mvImage) {
    const pImage = mvImage.querySelector('img');
    gsap.fromTo(pImage, {yPercent: 0}, {
      yPercent: 0,
      ease: Linear.easeNone,
      scrollTrigger: {
        trigger: mvImage,
        start: 'top bottom',
        end: 'bottom top',
        scrub: true
      }
    });
  });
})();
