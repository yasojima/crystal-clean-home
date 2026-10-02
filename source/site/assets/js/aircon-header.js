(() => {
  const button = document.querySelector('.c-header__menu.js-menu-modal-opener');
  const menu = document.querySelector('#menu.c-menu-modal');
  const header = document.querySelector('.c-header');
  const navigation = header?.querySelector('.c-header__navigation');
  if (!button || !menu || !header || !navigation) return;

  const image = button.querySelector('picture img');
  const source = button.querySelector('picture source');
  const closer = menu.querySelector('.c-menu-modal__closer');
  const closeImage = '/assets/images/header/menu-close.webp';
  const openImage = '/assets/images/header/menu-open_pc.webp';
  const openSource = '/assets/images/header/menu-open_sp.webp';
  const siteMenu = menu.querySelector('.c-site-menu');

  function fullMenuSection(name, heading, content) {
    const section = document.createElement('div');
    section.className = `aircon-full-menu__section aircon-full-menu__section--${name}`;
    const head = document.createElement('div');
    head.className = 'aircon-full-menu__head';
    const body = document.createElement('div');
    body.className = 'aircon-full-menu__body';
    head.append(heading);
    body.append(content);
    section.append(head, body);
    return section;
  }

  const serviceHeading = siteMenu.querySelector('.c-site-menu__bold-links');
  const serviceLinks = siteMenu.querySelector('.c-house-cleaning-menu');
  const guideHeading = siteMenu.querySelector('[data-guide]');
  const guideLinks = guideHeading.nextElementSibling;
  const businessHeading = siteMenu.querySelector('[data-others]');
  const businessLinks = businessHeading.nextElementSibling;
  siteMenu.replaceChildren(
    fullMenuSection('services', serviceHeading, serviceLinks),
    fullMenuSection('guide', guideHeading, guideLinks),
    fullMenuSection('business', businessHeading, businessLinks),
  );

  button.setAttribute('aria-controls', menu.id);
  button.setAttribute('aria-expanded', 'false');
  menu.setAttribute('aria-hidden', 'true');

  const mega = document.createElement('div');
  mega.className = 'aircon-mega';
  mega.setAttribute('aria-hidden', 'true');
  header.append(mega);

  function closeMega() {
    mega.classList.remove('is-open');
    mega.setAttribute('aria-hidden', 'true');
    navigation.querySelectorAll('.c-main-menu__item.is-open').forEach(item => item.classList.remove('is-open'));
  }

  function submenuLinks(href) {
    if (href === '/about/') return [...menu.querySelectorAll('.aircon-full-menu__section--guide .aircon-full-menu__body a[href]')];
    const group = [...menu.querySelectorAll('.c-house-cleaning-menu__item')].find(item =>
      item.querySelector('.c-house-cleaning-menu__link, .c-menu-accordion__link')?.getAttribute('href') === href);
    return group ? [...group.querySelectorAll('.c-aircon-details a[href], .c-menu-accordion__content a[href]')] : [];
  }

  function openMega(item) {
    if (menu.classList.contains('is-active') || window.innerWidth < 1400) return;
    const parentLink = item.querySelector('.c-main-menu__link');
    const links = submenuLinks(parentLink.getAttribute('href'));
    if (!links.length) return closeMega();

    const heading = document.createElement('a');
    heading.className = 'aircon-mega__heading';
    heading.href = parentLink.getAttribute('href');
    heading.textContent = parentLink.textContent.trim();

    const list = document.createElement('div');
    list.className = 'aircon-mega__links';
    for (const sourceLink of links) {
      const link = document.createElement('a');
      link.className = 'aircon-mega__link';
      link.href = sourceLink.getAttribute('href');
      link.textContent = sourceLink.innerText.replace(/\s+/g, ' ').trim();
      if (sourceLink.hasAttribute('data-demo-dialog')) link.setAttribute('data-demo-dialog', '');
      list.append(link);
    }

    mega.replaceChildren(heading, list);
    navigation.querySelectorAll('.c-main-menu__item.is-open').forEach(openItem => openItem.classList.remove('is-open'));
    item.classList.add('is-open');
    mega.classList.add('is-open');
    mega.setAttribute('aria-hidden', 'false');
  }

  navigation.querySelectorAll('.c-main-menu__item').forEach(item => {
    item.addEventListener('mouseenter', () => openMega(item));
    item.addEventListener('focusin', () => openMega(item));
  });
  header.addEventListener('mouseleave', closeMega);
  header.addEventListener('focusout', event => {
    if (!header.contains(event.relatedTarget)) closeMega();
  });

  function update(open) {
    if (open) closeMega();
    document.body.classList.toggle('aircon-menu-open', open);
    button.classList.toggle('is-open', open);
    button.setAttribute('aria-expanded', String(open));
    button.setAttribute('aria-label', open ? 'メニューを閉じる' : 'メニューを開く');
    if (image) image.src = open ? closeImage : openImage;
    if (source) source.srcset = open ? closeImage : openSource;
    if (open) menu.querySelector('.c-menu-modal__main-content').scrollTop = 0;
  }

  button.addEventListener('click', event => {
    if (!menu.classList.contains('is-active') || menu.classList.contains('is-hidden')) return;
    event.stopImmediatePropagation();
    closer.click();
  }, true);

  button.addEventListener('click', () => update(true));
  menu.querySelectorAll('.js-menu-modal-closer').forEach(element => {
    element.addEventListener('click', () => update(false));
  });

  menu.querySelector('.c-menu-modal__main-content').addEventListener('click', event => {
    if (!event.target.closest('.aircon-full-menu__section')) closer.click();
  });

  document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && menu.classList.contains('is-active')) {
      closer.click();
      button.focus();
    } else if (event.key === 'Escape' && mega.classList.contains('is-open')) {
      closeMega();
      navigation.querySelector('.c-main-menu__item .c-main-menu__link')?.focus();
    }
  });
})();
