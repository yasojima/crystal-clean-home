(() => {
  const hero = document.querySelector('.home-first-view');
  const header = document.querySelector('.c-header');
  if (!hero || !header) return;
  const actions = document.querySelector('.home-actions');
  const menuButton = header.querySelector('.c-header__menu');
  const socials = document.querySelector('.home-socials');
  const socialToggle = socials?.querySelector('.home-action--social');
  const socialLinks = socials?.querySelector('.home-socials__links');
  const scrollButton = document.querySelector('.home-action--scroll');
  const estimate = document.querySelector('.home-quick-estimate');
  const estimateToggle = estimate?.querySelector('.home-quick-estimate__toggle');
  const estimateLinks = estimate?.querySelector('.home-quick-estimate__links');
  const canHover = matchMedia('(hover: hover) and (pointer: fine)');
  const mobileEstimate = matchMedia('(max-width: 768px)');
  let pinned = false;
  let frame = 0;

  function alignActions() {
    if (!actions || !menuButton) return;
    const menu = menuButton.getBoundingClientRect();
    const size = Math.max(40, menu.width * (6 / 7));
    document.body.style.setProperty('--home-action-size', `${size}px`);
    document.body.style.setProperty('--home-actions-right', `${header.getBoundingClientRect().right - menu.left - menu.width / 2 - size / 2}px`);
    if (estimate) {
      const closeStyle = getComputedStyle(estimateToggle.querySelector('svg'));
      const closeInset = parseFloat(getComputedStyle(estimate).borderRightWidth) + parseFloat(closeStyle.right) + parseFloat(closeStyle.width) / 2;
      estimate.style.setProperty('--home-estimate-right', `${header.getBoundingClientRect().right - menu.left - menu.width / 2 - closeInset}px`);
    }
    const heroHeight = Math.min(hero.offsetHeight, innerHeight);
    const inset = innerWidth < 768 ? 24 : Math.min(64, innerHeight * .075);
    const estimateSpace = estimate ? estimate.offsetHeight + 32 : 56;
    const bottom = Math.max(innerHeight - heroHeight + inset, estimateSpace);
    const gap = parseFloat(getComputedStyle(actions).rowGap);
    const heroTop = hero.getBoundingClientRect().top + scrollY;
    const scrollTop = innerHeight - bottom - size * 2 - gap - heroTop;
    hero.style.setProperty('--home-scroll-top', `${scrollTop}px`);
    hero.style.setProperty('--home-social-top', `${scrollTop + size + gap}px`);
  }

  function setEstimateOpen(open) {
    if (!estimate) return;
    estimate.classList.toggle('is-open', open);
    estimate.classList.toggle('open', open);
    estimateToggle.setAttribute('aria-expanded', String(open));
    estimateLinks.setAttribute('aria-hidden', String(!open));
    estimateLinks.inert = !open;
    alignActions();
  }
  estimateToggle?.addEventListener('click', () => {
    estimate.classList.add('fix');
    setEstimateOpen(!estimate.classList.contains('is-open'));
  });

  // Reuse the reference's one-time reveal after 500px and manual fix/open state.
  function revealEstimate() {
    if (!estimate || !mobileEstimate.matches) return;
    if (scrollY > 500 && !estimate.classList.contains('fixed')) {
      estimate.classList.add('fixed');
      if (!estimate.classList.contains('fix')) setEstimateOpen(true);
    }
  }
  mobileEstimate.addEventListener('change', () => {
    estimate?.classList.remove('fixed', 'fix');
    setEstimateOpen(!mobileEstimate.matches);
    revealEstimate();
  });
  window.addEventListener('scroll', revealEstimate, {passive: true});
  window.addEventListener('load', revealEstimate);
  if (mobileEstimate.matches) {
    setEstimateOpen(false);
    revealEstimate();
  }

  function setSocialOpen(open) {
    if (!socials) return;
    socials.classList.toggle('is-open', open);
    socialToggle.setAttribute('aria-expanded', String(open));
    socialLinks.setAttribute('aria-hidden', String(!open));
    socialLinks.inert = !open;
  }

  if (socialLinks) {
    const footerLinks = document.querySelector('.c-footer-sns').querySelectorAll('.c-footer-sns__item');
    for (const item of [...footerLinks].slice(0, 4)) {
      const copy = item.cloneNode(true);
      copy.className = '';
      socialLinks.append(copy);
    }
    socials.addEventListener('pointerenter', () => {
      if (canHover.matches && !mobileEstimate.matches) setSocialOpen(true);
    });
    socials.addEventListener('pointerleave', () => {
      if (canHover.matches && !mobileEstimate.matches && !pinned) setSocialOpen(false);
    });
    socialToggle.addEventListener('click', () => {
      pinned = !pinned;
      setSocialOpen(pinned);
    });
    socials.addEventListener('focusin', event => {
      if (event.target !== socialToggle) setSocialOpen(true);
    });
    socials.addEventListener('focusout', event => {
      if (!socials.contains(event.relatedTarget) && !pinned) setSocialOpen(false);
    });
    document.addEventListener('pointerdown', event => {
      if (!socials.contains(event.target)) { pinned = false; setSocialOpen(false); }
    });
    document.addEventListener('keydown', event => {
      if (event.key === 'Escape' && socials.classList.contains('is-open')) {
        pinned = false;
        socialToggle.focus({preventScroll: true});
        setSocialOpen(false);
      }
    });
  }

  scrollButton?.addEventListener('click', event => {
    const target = document.querySelector(scrollButton.getAttribute('href'));
    if (!target) return;
    event.preventDefault();
    const top = target.getBoundingClientRect().top + scrollY - header.getBoundingClientRect().height;
    window.scrollTo({top, behavior: 'instant'});
    history.replaceState(null, '', scrollButton.getAttribute('href'));
  });
  function updateHeaderSurface() {
    frame = 0;
    document.body.classList.toggle('is-past-home-first-view',
      hero.getBoundingClientRect().bottom <= header.getBoundingClientRect().height);
  }
  function scheduleHeaderSurface() {
    if (!frame) frame = requestAnimationFrame(updateHeaderSurface);
  }
  window.addEventListener('scroll', scheduleHeaderSurface, { passive: true });
  window.addEventListener('resize', () => { scheduleHeaderSurface(); alignActions(); });
  window.addEventListener('pageshow', alignActions);
  if (menuButton) new ResizeObserver(alignActions).observe(header);
  alignActions();
  updateHeaderSurface();
})();
