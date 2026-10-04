const fs = require('fs');
const path = require('path');
const assert = require('assert/strict');
const { chromium, webkit } = require('C:/Users/yasoj/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const root = path.resolve(__dirname, '..');
const phase = process.argv[2] || 'local';
const output = path.resolve(process.argv[3] || 'evidence/2026-10-05/home-first-view');
const engine = process.env.SITE_ENGINE || 'chrome';
const sizes = (process.env.SITE_SIZES || '320x568,390x844,414x688,1439x803,1919x1093,1440x1973').split(',').map(s => s.split('x').map(Number));
const origin = 'https://yasojima.github.io';
(async () => {
  fs.mkdirSync(output, { recursive: true });
  const browser = await (engine === 'webkit' ? webkit : chromium).launch(engine === 'webkit' ? { headless: true } : { channel: 'chrome', headless: true });
  const results = [];
  try {
    for (const [width, height] of sizes) {
      const context = await browser.newContext({ viewport: { width, height }, isMobile: width < 768, hasTouch: width < 768 });
      const page = await context.newPage();
      if (phase === 'local') await page.route(origin + '/**', async route => {
        const u = new URL(route.request().url());
        const file = path.join(root, 'source/site', u.pathname + (u.pathname.endsWith('/') ? 'index.html' : ''));
        if (fs.existsSync(file)) await route.fulfill({ path: file });
        else await route.continue();
      });
      assert.equal((await page.goto(origin + '/?home-first-view=2026100520', { waitUntil: 'domcontentloaded' })).status(), 200);
      await page.evaluate(async () => {
        await Promise.race([document.fonts.ready, new Promise(resolve => setTimeout(resolve, 5000))]);
        await document.querySelector('.c-header__logo img').decode();
      });
      const initial = await page.evaluate(() => {
        const hero = document.querySelector('.home-first-view').getBoundingClientRect();
        const header = document.querySelector('.c-header');
        const label = document.querySelector('.home-first-view__label').getBoundingClientRect();
        return { width: innerWidth, height: innerHeight, heroTop: hero.top, heroWidth: hero.width, heroHeight: hero.height, headerTop: header.getBoundingClientRect().top, headerBottom: header.getBoundingClientRect().bottom, headerPosition: getComputedStyle(header).position, headerBackground: getComputedStyle(header).backgroundColor, labelTop: label.top, labelBottom: label.bottom, pageWidth: document.documentElement.scrollWidth, menus: [...header.querySelectorAll('.c-main-menu__link')].map(e => e.textContent.trim()), videos: document.querySelectorAll('video').length, anchors: document.querySelectorAll('#first-view').length };
      });
      const expectedHeight = width <= height * 1.25 ? width / 1.25 : Math.max(500, height);
      assert.ok(Math.abs(initial.heroHeight - expectedHeight) < 1, JSON.stringify(initial));
      assert.equal(initial.heroTop, 0);
      assert.equal(initial.headerTop, 0);
      assert.equal(initial.headerPosition, 'fixed');
      assert.equal(initial.headerBackground, 'rgba(0, 0, 0, 0)');
      assert.ok(initial.labelTop >= initial.headerBottom && initial.labelBottom <= initial.heroHeight);
      assert.ok(initial.pageWidth <= width + 1);
      assert.equal(initial.menus.length, 9);
      assert.equal(initial.videos, 0);
      assert.equal(initial.anchors, 1);
      await page.screenshot({ path: path.join(output, `${phase}-${engine}-${width}x${height}.png`) });
      if (width >= 768) {
        await page.locator('.c-main-menu__link').first().click();
        assert.ok(await page.locator('.aircon-mega.is-open').isVisible());
        assert.notEqual(await page.locator('.aircon-mega__link').first().evaluate(e => getComputedStyle(e).color), 'rgb(255, 255, 255)');
        await page.keyboard.press('Escape');
      }
      const button = page.locator('.c-header__menu.js-menu-modal-opener');
      await button.click();
      assert.equal(await button.getAttribute('aria-expanded'), 'true');
      await button.click();
      assert.equal(await button.getAttribute('aria-expanded'), 'false');
      await page.evaluate(() => scrollTo({ top: document.documentElement.scrollHeight, behavior: 'instant' }));
      await page.waitForTimeout(750);
      const footer = await page.evaluate(() => ({ headerTop: document.querySelector('.c-header').getBoundingClientRect().top, headerBottom: document.querySelector('.c-header').getBoundingClientRect().bottom, headerBackground: getComputedStyle(document.querySelector('.c-header')).backgroundColor, footerTop: document.querySelector('footer.c-footer').getBoundingClientRect().top, footerBottom: document.querySelector('footer.c-footer').getBoundingClientRect().bottom, viewportHeight: innerHeight, pastHero: document.body.classList.contains('is-past-home-first-view') }));
      assert.ok(footer.pastHero);
      assert.equal(footer.headerBackground, 'rgb(255, 255, 255)');
      assert.ok(footer.headerTop >= -1 && footer.footerTop >= footer.headerBottom - 1 && footer.footerBottom <= height + 1, JSON.stringify(footer));
      await page.evaluate(() => scrollTo({ top: 0, behavior: 'instant' }));
      await page.waitForTimeout(750);
      assert.equal(await page.locator('.c-header').evaluate(e => getComputedStyle(e).backgroundColor), 'rgba(0, 0, 0, 0)');
      results.push({ width, height, initial, footer, passed: true });
      console.log(`${phase} ${engine}: ${results.length}/${sizes.length} passed`);
      await context.close();
    }
  } finally { await browser.close(); }
  fs.writeFileSync(path.join(output, `${phase}-${engine}.json`), JSON.stringify({ checkedAt: new Date().toISOString(), phase, engine, passed: true, results }, null, 2) + '\n');
})().catch(error => { console.error(error); process.exitCode = 1; });
