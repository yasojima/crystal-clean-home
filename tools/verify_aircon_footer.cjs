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

    const coating = await page.evaluate(() => {
      const read = selector => [...document.querySelectorAll(selector)].map(a => a.getAttribute('href'));
      return {
        menu: read('#menu-accordion_7 a[href]'),
        desktop: read('.u-pc-only .c-aircon-footer__coating-links a[href]'),
        mobile: read('.u-sp-only .c-aircon-footer__coating-links a[href]'),
      };
    });
    assert.equal(coating.menu.length, 8);
    assert.deepEqual(coating.desktop, coating.menu);
    assert.deepEqual(coating.mobile, coating.menu);

    if (width >= 1400) {
      await page.locator('.c-main-menu__item').first().hover();
      await page.waitForTimeout(450);
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
    assert.equal(geometry.hoursColor, 'rgb(0, 91, 172)');
    assert.equal(geometry.markFilter, 'none');
    assert.equal(geometry.overflow, false);
    assert(Math.abs(geometry.buttonCenter - geometry.menuCenter) <= 1);
    if (width >= 768) assert(Math.abs(geometry.footerTop - geometry.headerBottom) <= 1, JSON.stringify(geometry));
    await page.screenshot({ path: path.join(out, `aircon-footer-${width}.png`) });

    await page.locator('.c-footer__page-top').click();
    await page.waitForFunction(() => scrollY < 3, null, { timeout: 4000 });
    assert.deepEqual(errors, []);
    results.push({ width, coatingLinks: coating.menu.length, fullMenuColors, geometry, errors });
    await context.close();
  }
  fs.writeFileSync(path.join(out, 'aircon-footer.json'), JSON.stringify({ local, results }, null, 2));
  console.log(JSON.stringify({ local, widths: results.map(result => result.width), coatingLinks: 8, errors: [] }));
  await browser.close();
})().catch(error => { console.error(error); process.exit(1); });
