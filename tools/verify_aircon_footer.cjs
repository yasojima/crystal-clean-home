const fs = require('fs');
const path = require('path');
const assert = require('assert/strict');
const { chromium } = require(process.env.PLAYWRIGHT_MODULE);

(async () => {
  const local = process.env.VERIFY_LOCAL !== '0';
  const root = path.resolve('source/site');
  const out = path.resolve('evidence/2026-10-02', local ? 'local' : 'public');
  fs.mkdirSync(out, { recursive: true });
  const browser = await chromium.launch({ headless: true, channel: 'chrome' });
  const results = [];

  for (const width of [1440, 1280, 1024, 768, 390, 320]) {
    const context = await browser.newContext({ viewport: { width, height: 800 } });
    const page = await context.newPage();
    page.setDefaultTimeout(7000);
    const errors = [];
    page.on('pageerror', error => errors.push(error.message));
    if (local) {
      await page.route('https://yasojima.github.io/**', async route => {
        let relative = decodeURIComponent(new URL(route.request().url()).pathname);
        if (relative.endsWith('/')) relative += 'index.html';
        const file = path.join(root, relative);
        if (fs.existsSync(file) && fs.statSync(file).isFile()) return route.fulfill({ path: file });
        return route.continue();
      });
    }
    await page.goto('https://yasojima.github.io/house-cleaning/aircon/?v=2026100253', { waitUntil: 'networkidle' });
    await page.evaluate(() => document.fonts.ready);
    assert.equal(await page.locator('.c-main-menu__link').first().textContent(), 'エアコン');
    assert.deepEqual(await page.locator('.aircon-full-menu__section--guide .aircon-full-menu__body a').allTextContents(),
      ['ハウスクリーニングについて', 'はじめての方へ', 'お問い合わせ']);
    const categoryColor = await page.evaluate(() => {
      const faq = document.querySelector('#service-faq');
      const categories = document.querySelector('.c-house-cleaning-links').closest('section');
      return { faq: getComputedStyle(faq).backgroundColor, categories: getComputedStyle(categories).backgroundColor };
    });
    assert.equal(categoryColor.categories, categoryColor.faq);
    if (width === 1440) {
      await page.locator('.c-house-cleaning-links').scrollIntoViewIfNeeded();
      await page.screenshot({ path: path.join(out, 'aircon-categories-1440.png') });
      await page.evaluate(() => scrollTo({ top: 0, behavior: 'instant' }));
    }

    const coating = await page.evaluate(() => {
      const read = selector => [...document.querySelectorAll(selector)].map(a => ({
        href: a.getAttribute('href'), text: a.textContent.replace(/\s+/g, ' ').trim(),
      }));
      return {
        menu: read('#menu-accordion_7 a[href]'),
        desktop: read('.u-pc-only .c-aircon-footer__coating-links a[href]'),
        mobile: read('.u-sp-only .c-aircon-footer__coating-links a[href]'),
      };
    });
    assert.equal(coating.menu.length, 8);
    assert.deepEqual(coating.desktop.map(link => link.text), coating.menu.map(link => link.text));
    assert.deepEqual(coating.mobile, coating.desktop);

    if (width >= 1400) {
      await page.locator('.c-main-menu__item').first().hover();
      await page.waitForTimeout(450);
      assert.equal(await page.locator('.aircon-mega__heading').getAttribute('href'), '/about/');
      assert.equal(await page.locator('.aircon-mega__heading .aircon-mega__en').textContent(), 'User Guide');
      assert.deepEqual(await page.locator('.aircon-mega__link').allTextContents(),
        ['ハウスクリーニングについて', 'はじめての方へ', 'お問い合わせ']);
      const beforeClick = page.url();
      await page.locator('.c-main-menu__link').first().click();
      assert.equal(page.url(), beforeClick);
      assert.equal(await page.locator('.aircon-mega').getAttribute('aria-hidden'), 'false');
      assert.equal(await page.locator('.c-main-menu__link').first().getAttribute('aria-expanded'), 'true');
      const navLine = await page.locator('.c-main-menu__link').first().evaluate(node => ({
        text: getComputedStyle(node).color,
        line: getComputedStyle(node, '::after').backgroundImage,
      }));
      assert.equal(navLine.text, 'rgb(0, 91, 172)');
      assert(navLine.line.includes('linear-gradient') && navLine.line.includes('248, 251, 255'));
      const colors = await page.evaluate(() => ({
        nav: getComputedStyle(document.querySelector('.c-main-menu__link')).color,
        heading: getComputedStyle(document.querySelector('.aircon-mega.is-open .aircon-mega__heading')).color,
        link: getComputedStyle(document.querySelector('.aircon-mega.is-open .aircon-mega__link')).color,
      }));
      assert(Object.values(colors).every(color => color === 'rgb(0, 91, 172)'), JSON.stringify(colors));
      await page.screenshot({ path: path.join(out, `aircon-footer-mega-${width}.png`) });
      await page.mouse.move(20, 450);
    }

    await page.locator('.c-header__menu').click();
    await page.waitForTimeout(450);
    const fullMenuColors = await page.evaluate(() => ({
      heading: getComputedStyle(document.querySelector('.aircon-full-menu__head .aircon-full-menu__category')).color,
      link: getComputedStyle(document.querySelector('.aircon-full-menu__body a[href]')).color,
    }));
    assert(Object.values(fullMenuColors).every(color => color === 'rgb(0, 91, 172)'), JSON.stringify(fullMenuColors));
    await page.locator('.aircon-full-menu__section--guide .aircon-full-menu__body a').first().hover();
    const fullMenuLine = await page.locator('.aircon-full-menu__section--guide .aircon-full-menu__body a').first().evaluate(node => ({
      text: getComputedStyle(node).color,
      line: getComputedStyle(node, '::before').backgroundImage,
    }));
    assert.equal(fullMenuLine.text, 'rgb(0, 91, 172)');
    assert(fullMenuLine.line.includes('linear-gradient') && fullMenuLine.line.includes('248, 251, 255'));
    if (width === 1440) await page.screenshot({ path: path.join(out, 'aircon-full-menu-1440.png') });
    await page.keyboard.press('Escape');

    if (width < 768) {
      await page.locator('button[aria-controls="footer-accordion_coating"]').click();
      assert.equal(await page.locator('#footer-accordion_coating a:visible').count(), 8);
      await page.waitForTimeout(800);
      await page.locator('button[aria-controls="footer-accordion_coating"]').click();
      await page.waitForTimeout(800);
      const closed = await page.evaluate(() => {
        const button = document.querySelector('button[aria-controls="footer-accordion_coating"]');
        const content = document.querySelector('#footer-accordion_coating');
        return { expanded: button.getAttribute('aria-expanded'), display: getComputedStyle(content).display, height: content.getBoundingClientRect().height };
      });
      assert.equal(closed.expanded, 'false', JSON.stringify({ width, closed }));
      assert(closed.height < 1, JSON.stringify({ width, closed }));
    }

    await page.evaluate(() => scrollTo({ top: 1e9, behavior: 'instant' }));
    await page.waitForTimeout(100);
    const geometry = await page.evaluate(() => {
      const rect = selector => document.querySelector(selector).getBoundingClientRect();
      const header = rect('.c-header');
      const footer = rect('#footer');
      const button = rect('.c-footer__page-top');
      const menu = rect('.c-header__menu');
      const number = document.querySelector('.c-header-contact__number');
      const hours = document.querySelector('.c-header-contact__hours');
      const mark = document.querySelector('.c-header-contact__mark');
      return {
        headerBottom: header.bottom,
        footerTop: footer.top,
        footerBottom: footer.bottom,
        buttonCenter: button.left + button.width / 2,
        menuCenter: menu.left + menu.width / 2,
        buttonColor: getComputedStyle(document.querySelector('.c-footer__page-top')).backgroundColor,
        numberColor: getComputedStyle(number).color,
        hoursColor: getComputedStyle(hours).color,
        markFilter: getComputedStyle(mark).filter,
        overflow: document.documentElement.scrollWidth > innerWidth,
      };
    });
    assert.equal(geometry.buttonColor, 'rgb(0, 0, 0)');
    assert.equal(geometry.numberColor, 'rgb(0, 91, 172)');
    assert.equal(geometry.hoursColor, 'rgb(0, 0, 0)');
    assert.equal(geometry.markFilter, 'none');
    assert.equal(geometry.overflow, false);
    assert(Math.abs(geometry.buttonCenter - geometry.menuCenter) <= 1);
    if (width >= 768) assert(Math.abs(geometry.footerTop - geometry.headerBottom) <= 1, JSON.stringify(geometry));
    await page.screenshot({ path: path.join(out, `aircon-footer-${width}.png`) });

    await page.locator('.c-footer__page-top').click();
    await page.waitForFunction(() => scrollY < 0.5, null, { timeout: 4000 });
    assert.equal(new URL(page.url()).hash, '#first-view');
    const firstView = await page.evaluate(() => {
      const header = document.querySelector('.c-header').getBoundingClientRect();
      const first = document.querySelector('#first-view').getBoundingClientRect();
      const cards = document.querySelector('.p-page-anchors__cards').getBoundingClientRect();
      return { headerBottom: header.bottom, firstTop: first.top, cardsBottom: cards.bottom };
    });
    assert(Math.abs(firstView.firstTop - firstView.headerBottom) <= 1, JSON.stringify(firstView));
    assert(firstView.cardsBottom <= 800, JSON.stringify(firstView));
    if (width === 1440 || width === 390) await page.screenshot({ path: path.join(out, `aircon-first-view-${width}.png`) });
    if (width === 1440) {
      const detailLinks = await page.locator('.aircon-full-menu__section--service .aircon-full-menu__body a[href]').evaluateAll(links => links.map(link => link.getAttribute('href')));
      for (const href of detailLinks) {
        const destination = new URL(href, page.url());
        assert(destination.hash, href);
        const file = path.join(root, decodeURIComponent(destination.pathname).replace(/^\/+/, ''), 'index.html');
        assert(fs.existsSync(file), href);
        assert(fs.readFileSync(file, 'utf8').includes(`id="${destination.hash.slice(1)}"`), href);
      }
      await page.locator('.c-main-menu__item').nth(1).hover();
      assert.deepEqual(await page.locator('.aircon-mega__link').evaluateAll(links => links.map(link => link.getAttribute('href'))),
        ['/house-cleaning/aircon/#lineup01', '/house-cleaning/aircon/#lineup02']);
      await page.locator('.aircon-mega__link').first().click();
      await page.waitForFunction(() => location.hash === '#lineup01' && Math.abs(document.querySelector('#lineup01').getBoundingClientRect().top - document.querySelector('.c-header').getBoundingClientRect().bottom) <= 1, null, { timeout: 4000 });
      await page.locator('.c-header__menu').click();
      await page.locator('.aircon-full-menu__section--service').first().locator('.aircon-full-menu__body a').first().click();
      await page.waitForFunction(() => document.querySelector('#menu').getAttribute('aria-hidden') === 'true');
      await page.locator('.c-main-menu__item').nth(2).hover();
      await page.locator('.aircon-mega__heading').click();
      await page.waitForURL('**/house-cleaning/pack/');
    }
    assert.deepEqual(errors, []);
    results.push({ width, coatingLinks: coating.menu.length, fullMenuColors, geometry, errors });
    await context.close();
  }
  fs.writeFileSync(path.join(out, 'aircon-footer.json'), JSON.stringify({ local, results }, null, 2));
  console.log(JSON.stringify({ local, widths: results.map(result => result.width), coatingLinks: 8, errors: [] }));
  await browser.close();
})().catch(error => { console.error(error); process.exit(1); });
