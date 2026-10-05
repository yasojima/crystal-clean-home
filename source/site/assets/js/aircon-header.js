(() => {
  const button = document.querySelector('.c-header__menu.js-menu-modal-opener');
  const menu = document.querySelector('#menu.c-menu-modal');
  const header = document.querySelector('.c-header');
  const navigation = header?.querySelector('.c-header__navigation');
  if (!button || !menu || !header || !navigation) return;

  const image = button.querySelector('picture img');
  const source = button.querySelector('picture source');
  const closeImage = '/assets/images/header/menu-close.webp';
  const openImage = '/assets/images/header/menu-open_pc.webp';
  const openSource = '/assets/images/header/menu-open_sp.webp';
  const siteMenu = menu.querySelector('.c-site-menu');
  const svgNamespace = 'http://www.w3.org/2000/svg';
  const arrowPaths = {
    down: 'M10.6306 0.630646L5.63065 5.63065C5.56033 5.70087 5.46502 5.74032 5.36565 5.74032C5.26627 5.74032 5.17096 5.70087 5.10065 5.63065L0.100646 0.630646C0.0344058 0.559559 -0.00165568 0.465536 5.84237e-05 0.368385C0.00177253 0.271235 0.0411284 0.178542 0.109835 0.109835C0.178541 0.0411289 0.271234 0.00177253 0.368385 5.84229e-05C0.465535 -0.00165569 0.559559 0.0344063 0.630646 0.100646L5.36565 4.83502L10.1006 0.100646C10.1717 0.0344063 10.2658 -0.00165569 10.3629 5.84229e-05C10.4601 0.00177253 10.5528 0.0411289 10.6215 0.109835C10.6902 0.178542 10.7295 0.271235 10.7312 0.368385C10.7329 0.465536 10.6969 0.559559 10.6306 0.630646Z',
    right: 'M6.82893 4.25725L0.995977 7.89336C0.9144 7.94427 0.810425 7.97894 0.697217 7.993C0.584008 8.00705 0.466655 7.99985 0.360015 7.97231C0.253376 7.94476 0.162244 7.89811 0.0981569 7.83826C0.0340698 7.77842 -9.06601e-05 7.70806 1.80705e-07 7.6361V0.363897C-9.06601e-05 0.29194 0.0340698 0.221584 0.0981569 0.161736C0.162244 0.101888 0.253376 0.0552387 0.360015 0.0276944C0.466655 0.000149987 0.584008 -0.00705118 0.697217 0.00700251C0.810425 0.0210562 0.9144 0.0557328 0.995977 0.106642L6.82893 3.74275C6.88316 3.77652 6.92618 3.81662 6.95554 3.86076C6.98489 3.9049 7 3.95222 7 4C7 4.04778 6.98489 4.0951 6.95554 4.13924C6.92618 4.18338 6.88316 4.22348 6.82893 4.25725Z',
  };

  function arrow(direction) {
    const svg = document.createElementNS(svgNamespace, 'svg');
    svg.setAttribute('viewBox', direction === 'down' ? '0 0 11 6' : '0 0 7 8');
    svg.setAttribute('aria-hidden', 'true');
    svg.setAttribute('focusable', 'false');
    const path = document.createElementNS(svgNamespace, 'path');
    path.setAttribute('d', arrowPaths[direction]);
    path.setAttribute('fill', 'currentColor');
    svg.append(path);
    return svg;
  }

  const footerPhone = document.querySelector('.footer-tel-pc .c-demo-phone');
  const contactDetails = footerPhone?.querySelector('img')?.alt.match(/([\d-]+)。受付時間\s*(.+)$/);
  if (contactDetails) {
    const contact = document.createElement('div');
    contact.className = 'c-header-contact';
    const inquiry = siteMenu.querySelector('a[data-demo-dialog]').cloneNode(false);
    inquiry.className = 'c-header-contact__cta';
    inquiry.textContent = 'お問い合わせはこちら';
    contact.append(inquiry);
    const payments = document.createElement('span');
    payments.className = 'c-header-contact__payments';
    for (const [file, label] of [['visa', 'Visa'], ['master-card', 'Mastercard']]) {
      const logo = document.createElement('img');
      logo.className = 'c-header-contact__payment';
      logo.src = `/assets/images/common-parts/payments/${file}.webp`;
      logo.alt = label;
      payments.append(logo);
    }
    contact.append(payments);
    const phone = footerPhone.querySelector('button, a[href]').cloneNode(false);
    phone.className = 'c-header-contact__phone';
    const phoneMark = document.createElement('span');
    phoneMark.className = 'c-header-contact__mark';
    phoneMark.setAttribute('aria-hidden', 'true');
    phoneMark.style.backgroundImage = `url("${footerPhone.querySelector('img').getAttribute('src')}")`;
    const phoneNumber = document.createElement('span');
    phoneNumber.className = 'c-header-contact__number';
    phoneNumber.textContent = contactDetails[1];
    phone.append(phoneMark, phoneNumber);
    const hours = document.createElement('span');
    hours.className = 'c-header-contact__hours';
    const time = document.createElement('span');
    time.textContent = `受付時間 ${contactDetails[2]}`;
    const days = document.createElement('span');
    days.className = 'c-header-contact__days';
    const daysNote = document.createElement('span');
    daysNote.className = 'c-header-contact__days-note';
    daysNote.textContent = '（年末年始を除く）';
    days.append('年中無休', daysNote);
    hours.append(time, days);
    contact.append(phone, hours);
    header.append(contact);
  }

  const menuEnglish = {
    '/beginner/': 'User Guide',
    '/house-cleaning/aircon/': 'Air Conditioning',
    '/house-cleaning/pack/': 'Pack Service',
    '/house-cleaning/water/': 'Water Areas',
    '/house-cleaning/washer/': 'Washing Machines',
    '/house-cleaning/kitchen/': 'Kitchen',
    '/house-cleaning/room/': 'Rooms',
    '/house-cleaning/coating/': 'Coating',
    '/house-cleaning/others/': 'Others',
  };

  function headingContent(heading, label, englishLabel, prefix) {
    const english = document.createElement('span');
    english.className = `${prefix}__en`;
    english.textContent = englishLabel;
    const title = document.createElement('span');
    title.className = `${prefix}__title`;
    const text = document.createElement('span');
    text.textContent = label;
    title.append(text);
    if (heading.matches('a[href]')) {
      title.append(arrow('right'));
      heading.setAttribute('aria-label', label);
    }
    heading.replaceChildren(english, title);
  }

  function fullMenuSection(name, heading, content) {
    const section = document.createElement('div');
    section.className = `aircon-full-menu__section aircon-full-menu__section--${name}`;
    const head = document.createElement('div');
    head.className = 'aircon-full-menu__head';
    const body = document.createElement('div');
    body.className = 'aircon-full-menu__body';
    const english = menuEnglish[heading.getAttribute('href')] ||
      ({ guide: 'User Guide', business: 'Business' }[name]);
    headingContent(heading, heading.textContent.trim(), english, 'aircon-full-menu');
    head.append(heading);
    body.append(content);
    section.append(head, body);
    return section;
  }

  const serviceLinks = siteMenu.querySelector('.c-house-cleaning-menu');
  const guideHeading = siteMenu.querySelector('[data-guide]');
  const guideLabel = guideHeading.textContent.trim();
  const guideLinks = guideHeading.nextElementSibling;
  const businessHeading = siteMenu.querySelector('[data-others]');
  const businessLinks = businessHeading.nextElementSibling;
  const serviceSubmenus = new Map();
  serviceSubmenus.set('/beginner/', [...guideLinks.querySelectorAll('a[href]')]);
  const serviceSections = [...serviceLinks.children].map(group => {
    const heading = group.querySelector('.c-house-cleaning-menu__link, .c-menu-accordion__link');
    const content = group.querySelector('.c-aircon-details, .c-menu-accordion__content');
    const href = heading.getAttribute('href');
    serviceSubmenus.set(href, [...content.querySelectorAll('a[href]')]);
    heading.className = 'aircon-full-menu__category';
    if (href === '/house-cleaning/water/') heading.textContent = '水回りのお掃除';
    return fullMenuSection('service', heading, content);
  });
  siteMenu.replaceChildren(
    ...serviceSections,
    fullMenuSection('guide', guideHeading, guideLinks),
    fullMenuSection('business', businessHeading, businessLinks),
  );
  menu.querySelectorAll('.aircon-full-menu__body a[href]').forEach(link => {
    const label = document.createElement('span');
    label.className = 'aircon-full-menu__label';
    label.append(...link.childNodes);
    link.replaceChildren(label, arrow('right'));
  });

  button.setAttribute('aria-controls', menu.id);
  button.setAttribute('aria-expanded', 'false');
  menu.setAttribute('aria-hidden', 'true');
  menu.inert = true;
  document.body.append(menu);

  const mega = document.createElement('div');
  mega.className = 'aircon-mega';
  mega.id = 'aircon-mega';
  mega.setAttribute('aria-hidden', 'true');
  header.append(mega);

  function closeMega() {
    mega.classList.remove('is-open');
    mega.setAttribute('aria-hidden', 'true');
    navigation.querySelectorAll('.c-main-menu__item.is-open').forEach(item => {
      item.classList.remove('is-open');
      item.querySelector('.c-main-menu__link').setAttribute('aria-expanded', 'false');
    });
  }

  function submenuLinks(href) {
    return serviceSubmenus.get(href) || [];
  }

  function alignMegaLinks() {
    const navStart = navigation.querySelector('.c-main-menu__item:first-child .c-main-menu__link')?.getBoundingClientRect().left;
    const headingEnd = mega.querySelector('.aircon-mega__heading')?.getBoundingClientRect().right;
    if (navStart == null || headingEnd == null) return;
    mega.style.gap = `${Math.max(0, navStart - headingEnd)}px`;
  }

  function openMega(item) {
    if (menu.classList.contains('is-active') || window.innerWidth < 1400) return;
    const parentLink = item.querySelector('.c-main-menu__link');
    const destination = parentLink.dataset.targetHref;
    const links = submenuLinks(destination);
    if (!links.length) return closeMega();

    const heading = document.createElement('a');
    heading.className = 'aircon-mega__heading';
    heading.href = destination;
    const label = parentLink.querySelector('span').textContent.trim();
    headingContent(heading, destination === '/beginner/' ? guideLabel : label, menuEnglish[destination] || '', 'aircon-mega');

    const list = document.createElement('div');
    list.className = 'aircon-mega__links';
    for (const sourceLink of links) {
      const link = document.createElement('a');
      link.className = 'aircon-mega__link';
      link.href = sourceLink.getAttribute('href');
      const text = document.createElement('span');
      text.textContent = sourceLink.textContent.replace(/\s+/g, ' ').trim();
      link.append(text, arrow('right'));
      if (sourceLink.hasAttribute('data-demo-dialog')) link.setAttribute('data-demo-dialog', '');
      list.append(link);
    }

    mega.replaceChildren(heading, list);
    alignMegaLinks();
    navigation.querySelectorAll('.c-main-menu__item.is-open').forEach(openItem => {
      openItem.classList.remove('is-open');
      openItem.querySelector('.c-main-menu__link').setAttribute('aria-expanded', 'false');
    });
    item.classList.add('is-open');
    parentLink.setAttribute('aria-expanded', 'true');
    mega.classList.add('is-open');
    mega.setAttribute('aria-hidden', 'false');
  }

  navigation.querySelectorAll('.c-main-menu__item').forEach(item => {
    const link = item.querySelector('.c-main-menu__link');
    link.setAttribute('aria-controls', mega.id);
    link.setAttribute('aria-expanded', 'false');
    const label = document.createElement('span');
    label.textContent = link.textContent.trim();
    link.replaceChildren(label, arrow('down'));
    item.addEventListener('mouseenter', () => openMega(item));
    item.addEventListener('focusin', () => openMega(item));
    link.addEventListener('click', () => openMega(item));
  });
  header.addEventListener('mouseleave', closeMega);
  header.addEventListener('focusout', event => {
    if (!header.contains(event.relatedTarget)) closeMega();
  });
  mega.addEventListener('click', event => {
    if (event.target.closest('.aircon-mega__link')) closeMega();
  });
  window.addEventListener('resize', () => {
    if (mega.classList.contains('is-open')) alignMegaLinks();
  });

  let menuOpen = false;
  const mobileHeader = window.matchMedia('(max-width: 767.98px)');
  const mobileFooter = document.querySelector('.c-footer--aircon');
  const mobileFooterPhone = mobileFooter?.querySelector('.footer-tel-sp');
  const footerRows = [...(mobileFooter?.querySelectorAll('.aircon-footer-menu__row') || [])];
  const mobileFooterSocial = mobileFooter?.querySelector('.u-sp-only > .c-footer-top-nav__item:last-child');
  const footerBottomNav = mobileFooter?.querySelector('.c-footer__bottom-nav');
  const floatingCart = document.querySelector('#js-floating');
  const corporateFloating = document.querySelector('.c-corporate-floating');
  let lastScrollY = window.scrollY;
  let visibleScrollY = lastScrollY;
  let scrollIdleTimer;
  let touchActive = false;
  const scrollIdleDelay = 450;

  function sizeDesktopFooterLinks() {
    if (mobileHeader.matches || !mobileFooter || !footerBottomNav) return;
    const nav = mobileFooter.querySelector('.c-footer__top-nav');
    const column = nav?.lastElementChild;
    const lists = column && [...column.querySelectorAll('.c-aircon-footer__coating-links, .c-aircon-footer__other-links')];
    if (!lists?.length) return;
    const outerHeight = element => {
      const style = getComputedStyle(element);
      return element.getBoundingClientRect().height + parseFloat(style.marginTop) + parseFloat(style.marginBottom);
    };
    const setRows = (list, rows) => {
      list.style.setProperty('--footer-list-rows', String(Math.max(1, rows)));
      list.classList.toggle('is-single-column', rows >= list.children.length);
    };
    const options = lists.map(list => {
      const count = list.children.length;
      const choices = [];
      for (let rows = Math.max(1, Math.ceil(count / 2)); rows <= Math.max(1, count); rows++) {
        setRows(list, rows);
        choices.push({ rows, height: outerHeight(list) });
      }
      return choices;
    });
    const navStyle = getComputedStyle(nav);
    const frameBudget = parseFloat(getComputedStyle(mobileFooter).minHeight) -
      outerHeight(mobileFooter.querySelector('.footer-tel-pc')) - outerHeight(footerBottomNav) -
      parseFloat(navStyle.paddingTop) - parseFloat(navStyle.paddingBottom);
    const otherColumns = [...nav.children].slice(0, -1).map(item =>
      [...item.children].reduce((sum, child) => sum + outerHeight(child), 0));
    const budget = Math.max(frameBudget, ...otherColumns);
    const fixedHeight = column.getBoundingClientRect().height - lists.reduce((sum, list) => sum + outerHeight(list), 0);
    let selected = options.map(choices => choices[0]);
    // Fill the smaller list vertically, then use the remaining height for the larger list.
    const priority = lists.map((list, index) => index).sort((a, b) => lists[a].children.length - lists[b].children.length);
    for (const index of priority) {
      for (const option of options[index]) {
        const total = fixedHeight + option.height + selected.reduce((sum, choice, other) => sum + (other === index ? 0 : choice.height), 0);
        if (total <= budget + .5) selected[index] = option;
      }
    }
    lists.forEach((list, index) => setRows(list, selected[index].rows));
  }

  let footerLayoutFrame = 0;
  function scheduleDesktopFooterLinks() {
    if (footerLayoutFrame) return;
    footerLayoutFrame = requestAnimationFrame(() => {
      footerLayoutFrame = 0;
      sizeDesktopFooterLinks();
    });
  }
  footerPhone?.querySelector('img')?.addEventListener('load', scheduleDesktopFooterLinks, { once: true });
  const desktopFooterLists = mobileFooter?.querySelectorAll('.c-aircon-footer__coating-links, .c-aircon-footer__other-links');
  desktopFooterLists?.forEach(list => new MutationObserver(scheduleDesktopFooterLinks)
    .observe(list, { childList: true, subtree: true, characterData: true }));

  function sizeFooterRows() {
    if (!mobileHeader.matches || !mobileFooterPhone || !mobileFooterSocial || !footerBottomNav || !footerRows.length) return;
    // Only measure the fixed blocks. Detail panels never affect the heading budget.
    const fixedHeight = [mobileFooterPhone, mobileFooterSocial, footerBottomNav]
      .reduce((sum, item) => sum + item.getBoundingClientRect().height, 0) +
      footerRows.reduce((sum, row) => {
        const style = getComputedStyle(row);
        return sum + parseFloat(style.borderTopWidth) + parseFloat(style.borderBottomWidth);
      }, 0);
    mobileFooter.style.setProperty('--aircon-footer-fixed-height', `${fixedHeight}px`);
    mobileFooter.style.setProperty('--aircon-footer-row-count', String(footerRows.length));
  }

  mobileFooterPhone?.querySelector('img')?.addEventListener('load', () => {
    sizeFooterRows();
    updateFooterVisibility();
  }, { once: true });
  document.fonts?.ready.then(() => {
    sizeDesktopFooterLinks();
    sizeFooterRows();
    updateFooterVisibility();
  });
  sizeFooterRows();
  sizeDesktopFooterLinks();

  function updateFooterVisibility() {
    const footerRect = mobileFooter?.getBoundingClientRect();
    corporateFloating?.classList.toggle('is-site-footer-hidden', Boolean(footerRect &&
      footerRect.top < window.innerHeight && footerRect.bottom > 0));
    floatingCart?.classList.toggle('is-mobile-footer-hidden', mobileHeader.matches &&
      mobileFooter && mobileFooter.getBoundingClientRect().top < window.innerHeight);
    const atFooterEnd = mobileHeader.matches && !menuOpen && footerRect &&
      footerRect.bottom <= window.innerHeight + 1 && footerRect.bottom > 0;
    header.classList.toggle('is-footer-visible', Boolean(atFooterEnd));
    if (atFooterEnd) header.classList.remove('is-scroll-hidden');
  }

  function showHeader() {
    window.clearTimeout(scrollIdleTimer);
    header.classList.remove('is-scroll-hidden');
    updateFooterVisibility();
    lastScrollY = Math.max(0, window.scrollY);
    visibleScrollY = lastScrollY;
  }

  function scheduleHeaderReturn() {
    window.clearTimeout(scrollIdleTimer);
    if (touchActive || !mobileHeader.matches || menuOpen) return;
    scrollIdleTimer = window.setTimeout(() => {
      if (!touchActive) showHeader();
    }, scrollIdleDelay);
  }

  window.addEventListener('scroll', () => {
    const currentY = Math.max(0, window.scrollY);
    updateFooterVisibility();
    if (!mobileHeader.matches || menuOpen) {
      showHeader();
      return;
    }
    if (currentY === lastScrollY) return;
    lastScrollY = currentY;
    window.clearTimeout(scrollIdleTimer);
    if (!header.classList.contains('is-footer-visible') && Math.abs(currentY - visibleScrollY) >= 8) header.classList.add('is-scroll-hidden');
    scheduleHeaderReturn();
  }, { passive: true });
  document.addEventListener('scrollend', scheduleHeaderReturn);
  document.addEventListener('touchstart', event => {
    if (!mobileHeader.matches || menuOpen) return;
    touchActive = event.touches.length > 0;
    window.clearTimeout(scrollIdleTimer);
  }, { passive: true });
  function endTouch(event) {
    touchActive = event.touches.length > 0;
    if (!touchActive) scheduleHeaderReturn();
  }
  document.addEventListener('touchend', endTouch, { passive: true });
  document.addEventListener('touchcancel', endTouch, { passive: true });
  mobileHeader.addEventListener('change', () => {
    sizeFooterRows();
    showHeader();
  });
  window.addEventListener('resize', () => {
    scheduleDesktopFooterLinks();
    sizeFooterRows();
    updateFooterVisibility();
  });

  function setMenuOpen(open) {
    if (menuOpen === open) return;
    menuOpen = open;
    if (open) showHeader();
    if (open) closeMega();
    menu.classList.toggle('is-active', open);
    menu.setAttribute('aria-hidden', String(!open));
    menu.inert = !open;
    document.body.classList.toggle('aircon-menu-open', open);
    button.classList.toggle('is-open', open);
    button.setAttribute('aria-expanded', String(open));
    button.setAttribute('aria-label', open ? 'メニューを閉じる' : 'メニューを開く');
    if (image) image.src = open ? closeImage : openImage;
    if (source) source.srcset = open ? closeImage : openSource;
    if (open) menu.querySelector('.c-menu-modal__main-content').scrollTop = 0;
    updateFooterVisibility();
  }

  button.addEventListener('click', event => {
    event.preventDefault();
    event.stopImmediatePropagation();
    setMenuOpen(!menuOpen);
  }, true);

  menu.addEventListener('click', event => {
    const link = event.target.closest('.aircon-full-menu__body a[href]');
    if (link) {
      const destination = new URL(link.href);
      if (destination.pathname === location.pathname && destination.hash) setMenuOpen(false);
      return;
    }
    if (event.target.closest('.aircon-full-menu__section')) return;
    event.preventDefault();
    event.stopImmediatePropagation();
    setMenuOpen(false);
  }, true);

  document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && menuOpen) {
      setMenuOpen(false);
      button.focus();
    } else if (event.key === 'Escape' && mega.classList.contains('is-open')) {
      closeMega();
      navigation.querySelector('.c-main-menu__item .c-main-menu__link')?.focus();
    }
  });
  showHeader();
})();
