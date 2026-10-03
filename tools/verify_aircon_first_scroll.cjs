const fs = require('fs');
const assert = require('assert/strict');
const { chromium, webkit } = require(process.env.PLAYWRIGHT_MODULE);
const base = process.argv[2] || 'http://127.0.0.1:8769';
const output = process.argv[3] || 'evidence/2026-10-03/local/aircon-footer-first-scroll-browser.json';
const results = [];
let checks = 0;
function check(condition, message) { assert(condition, message); checks++; }

async function state(page) {
  return page.evaluate(() => {
    const footer = document.querySelector('#footer');
    const phone = footer.querySelector('.footer-tel-sp');
    const social = footer.querySelector('.u-sp-only > .c-footer-top-nav__item:last-child');
    const nav = footer.querySelector('.c-footer__bottom-nav');
    const rect = element => {
      const r = element.getBoundingClientRect();
      return { top: r.top, bottom: r.bottom, height: r.height };
    };
    return {
      y: scrollY, maxY: document.documentElement.scrollHeight - innerHeight,
      height: innerHeight, footer: rect(footer), phone: rect(phone), social: rect(social), nav: rect(nav),
      snap: getComputedStyle(nav).scrollSnapAlign,
      headerBottom: document.querySelector('.c-header').getBoundingClientRect().bottom,
      cart: getComputedStyle(document.querySelector('#js-floating')).visibility,
      overflow: document.documentElement.scrollWidth - innerWidth,
      calls: window.__productScrollCalls,
    };
  });
}

function framed(s) {
  check(Math.abs(s.phone.top) < 1, 'phone starts at viewport top after one arrival');
  check(Math.abs(s.nav.bottom - s.height) < 1, 'last links end at viewport bottom');
  check(Math.abs(s.y - s.maxY) < 1, 'still at page end without a second scroll');
  check(s.headerBottom <= 1 && s.cart === 'hidden', 'header and cart do not cover footer');
  check(s.overflow <= 1 && s.calls.length === 0, 'no overflow or product scroll call');
}

(async () => {
  for (const [engine, type] of [['Chrome', chromium], ['WebKit', webkit]]) {
    const browser = await type.launch({ headless: true, ...(engine === 'Chrome' ? { channel: 'chrome' } : {}) });
    try {
      for (const width of [320, 375, 414, 430]) {
        const page = await browser.newPage({ viewport: { width, height: 688 }, isMobile: true, hasTouch: true });
        const errors = [];
        page.on('pageerror', error => errors.push(error.message));
        await page.addInitScript(() => {
          window.__productScrollCalls = [];
          for (const name of ['scrollTo', 'scrollBy', 'scroll']) {
            const original = window[name].bind(window);
            window[name] = (...args) => {
              if (!window.__fixtureScroll) window.__productScrollCalls.push(name);
              return original(...args);
            };
          }
        });
        await page.goto(base + '/house-cleaning/aircon/', { waitUntil: 'load' });
        await page.evaluate(() => {
          window.__fixtureScroll = true;
          scrollTo({ top: document.documentElement.scrollHeight, behavior: 'instant' });
          window.__fixtureScroll = false;
        });
        await page.waitForTimeout(1000);
        const first = await state(page);
        framed(first);
        const heights = [];
        for (const height of [720, 760, 832, 760, 720, 688]) {
          await page.setViewportSize({ width, height });
          await page.waitForTimeout(350);
          const s = await state(page);
          framed(s);
          check(Math.abs(s.phone.height - first.phone.height) < 1 && Math.abs(s.social.height - first.social.height) < 1,
            'phone and social spacing stays fixed');
          heights.push(s);
        }
        // Model a toolbar resize followed by a late dynamic-unit update.
        const delayed = await page.addStyleTag({ content: '@media(max-width:767.98px){.c-footer--aircon{--aircon-footer-viewport-height:688px}}' });
        await page.setViewportSize({ width, height: 832 });
        await page.waitForTimeout(300);
        await delayed.evaluate(element => element.remove());
        await page.waitForTimeout(700);
        const delayedResult = await state(page);
        framed(delayedResult);
        await page.screenshot({ path: output.replace('.json', `-${engine}-${width}-832.png`) });
        await page.setViewportSize({ width, height: 688 });
        await page.waitForTimeout(700);
        // Opening details removes the only snap target so every detail remains freely scrollable.
        await page.locator('.aircon-footer-menu__row').nth(1).locator('.js-accordion-trigger').nth(1).tap();
        await page.waitForTimeout(400);
        check((await state(page)).snap === 'none', 'no snapping when details are open');
        await page.locator('.aircon-footer-menu__row').nth(1).locator('.js-accordion-trigger').nth(1).tap();
        await page.waitForTimeout(400);
        check((await state(page)).snap === 'end', 'end target returns on close');
        await page.evaluate(() => {
          window.__fixtureScroll = true;
          scrollTo({ top: 1800, behavior: 'instant' });
          window.__fixtureScroll = false;
        });
        await page.waitForTimeout(800);
        const middle = await state(page);
        check(middle.y < middle.maxY - 1000, 'middle of page remains accessible');
        await page.locator('.c-header__menu').tap();
        check(await page.locator('#menu').evaluate(e => e.classList.contains('is-active')), 'MENU opens');
        await page.locator('.c-header__menu').tap();
        check(!await page.locator('#menu').evaluate(e => e.classList.contains('is-active')), 'MENU closes');
        check((await state(page)).y < middle.maxY - 1000, 'MENU close does not pull page to end');
        if (engine === 'Chrome' && width === 414) {
          await page.evaluate(() => {
            window.__fixtureScroll = true;
            scrollTo({ top: document.documentElement.scrollHeight - innerHeight - 250, behavior: 'instant' });
            window.__fixtureScroll = false;
          });
          await page.waitForTimeout(700);
          const cdp = await page.context().newCDPSession(page);
          await cdp.send('Input.dispatchTouchEvent', { type: 'touchStart', touchPoints: [{ x: 205, y: 590 }] });
          for (let i = 1; i <= 10; i++) {
            await cdp.send('Input.dispatchTouchEvent', { type: 'touchMove', touchPoints: [{ x: 205, y: 590 - 48 * i }] });
            await page.waitForTimeout(35);
          }
          await cdp.send('Input.dispatchTouchEvent', { type: 'touchEnd', touchPoints: [] });
          await page.setViewportSize({ width, height: 832 });
          await page.waitForTimeout(1000);
          const oneGesture = await state(page);
          framed(oneGesture);
          results.push({ engine, width, oneGesture });
        }
        check(errors.length === 0, 'no JavaScript errors');
        results.push({ engine, width, first, heights, delayedResult, middle, errors });
        await page.close();
      }
    } finally { await browser.close(); }
  }
  const report = { base, passed: true, checks, results,
    limits: 'Hidden desktop Chrome and WebKit. Viewport changes and delayed CSS updates model toolbar geometry; native iPhone toolbar and rubber-band timing require device confirmation.' };
  fs.writeFileSync(output, JSON.stringify(report, null, 2) + '\n');
  console.log(JSON.stringify({ base, passed: true, checks }));
})().catch(error => { console.error(error); process.exit(1); });
