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
    prevent: node => !!node.closest('#header, dialog, .simulation'),
    virtualScroll: () => !document.documentElement.classList.contains('cch-header-drawer-open') && !document.querySelector('dialog[open]') && window.scrollY < hero.offsetTop + hero.offsetHeight
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
