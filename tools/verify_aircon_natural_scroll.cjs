const fs = require('fs');
const assert = require('assert/strict');
const { chromium, webkit } = require(process.env.PLAYWRIGHT_MODULE);
const base = process.argv[2] || 'http://127.0.0.1:8769';
const output = process.argv[3] || 'evidence/2026-10-03/local/aircon-footer-free-scroll-behavior.json';
(async () => {
  const results = [];
  for (const [engine, type] of [['Chrome', chromium], ['WebKit', webkit]]) {
    const browser = await type.launch({ headless: true, ...(engine === 'Chrome' ? { channel: 'chrome' } : {}) });
    try {
      for (const width of [320, 375, 414, 430]) {
        const page = await browser.newPage({ viewport: { width, height: 688 }, isMobile: true, hasTouch: true });
        const errors = [];
        page.on('pageerror', e => errors.push(e.message));
        await page.goto(base + '/house-cleaning/aircon/', { waitUntil: 'load' });
        const state = () => page.evaluate(() => {
          const footer = document.querySelector('#footer');
          const nav = footer.querySelector('.c-footer__bottom-nav');
          const root = getComputedStyle(document.documentElement);
          return { snap: root.scrollSnapType, overscroll: root.getPropertyValue('overscroll-behavior-y') || 'unsupported',
            navSnap: getComputedStyle(nav).scrollSnapAlign,
            footerHeight: footer.getBoundingClientRect().height,
            phoneTop: footer.querySelector('.footer-tel-sp').getBoundingClientRect().top,
            navBottom: nav.getBoundingClientRect().bottom,
            overflow: document.documentElement.scrollWidth - innerWidth };
        });
        const initial = await state();
        assert(initial.snap === 'none' && initial.navSnap === 'none');
        assert(['auto', 'unsupported'].includes(initial.overscroll));
        await page.evaluate(() => document.fonts.ready);
        await page.evaluate(() => scrollTo({ top: document.documentElement.scrollHeight, behavior: 'instant' }));
        await page.waitForTimeout(1000);
        // Image decoding may change preceding content; this fixture sets the final inspection position.
        await page.evaluate(() => scrollTo({ top: document.documentElement.scrollHeight, behavior: 'instant' }));
        await page.waitForTimeout(700);
        const closed = await state();
        assert(Math.abs(closed.phoneTop) < 1 && Math.abs(closed.navBottom - 688) < 1);
        assert(closed.overflow <= 1);
        await page.locator('.aircon-footer-menu__row').nth(1).locator('.js-accordion-trigger').nth(1).tap();
        await page.waitForTimeout(400);
        const opened = await state();
        assert(opened.snap === 'none' && opened.navSnap === 'none' && ['auto', 'unsupported'].includes(opened.overscroll));
        assert.deepEqual(errors, []);
        results.push({ engine, width, closed, opened, errors });
        await page.close();
      }
    } finally { await browser.close(); }
  }
  fs.writeFileSync(output, JSON.stringify({ base, passed: true, results,
    limits: 'Hidden desktop Chrome/WebKit verifies natural scroll settings and steady layout. Native iPhone overscroll and toolbar movement are left to the browser.' }, null, 2) + '\n');
  console.log(JSON.stringify({ base, passed: true, cases: results.length }));
})().catch(e => { console.error(e); process.exit(1); });
