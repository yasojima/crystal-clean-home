const fs = require('fs');
const path = require('path');
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright');

const root = path.resolve(__dirname, '..');
const catalogue = JSON.parse(fs.readFileSync(path.join(root, 'source/service-pages/catalogue.json'), 'utf8'));
const origin = process.env.SITE_ORIGIN || 'http://127.0.0.1:8769';
const screenshots = process.env.SCREENSHOT_DIR;
const errors = [];
const checks = [];
const categories = Object.keys(catalogue.pages).filter(route => !route.includes('/'));
const staticReasons = ['/', '/about/', '/quick_cart/option/', '/lab/online_store/detergent/product-303/'];
const fail = (route, width, reason) => errors.push({ route, width, reason });

async function navyState(page) {
  return page.locator('.c-reasons--navy').evaluate(grid => {
    const panels = [...grid.querySelectorAll('.c-reasons__navy')];
    const bounds = panels.map(panel => panel.getBoundingClientRect());
    const plain = panels.every(panel => {
      const style = getComputedStyle(panel);
      return !panel.querySelector('img') && style.backgroundColor === 'rgb(0, 0, 128)' &&
        style.backgroundImage === 'none' && style.filter === 'none' &&
        style.boxShadow === 'none' && (style.backdropFilter === 'none' || !style.backdropFilter);
    });
    const visible = bounds.every(rect => rect.width > 0 && rect.height > 0);
    const separated = bounds.slice(1).every((rect, index) =>
      innerWidth >= 768 ? rect.left >= bounds[index].right + 4 : rect.top >= bounds[index].bottom + 4);
    return { count: panels.length, plain, visible, separated };
  });
}

(async () => {
  const browser = await chromium.launch({ headless: true, channel: 'chrome' });
  const page = await browser.newPage();
  page.setDefaultTimeout(8000);
  let current = {};
  page.on('pageerror', error => fail(current.route, current.width, error.message));
  page.on('dialog', dialog => dialog.dismiss());
  if (screenshots) fs.mkdirSync(screenshots, { recursive: true });
  const runs = Object.keys(catalogue.pages).flatMap(route => [390, 1440].map(width => ({ route, width })));
  runs.push(...categories.flatMap(route => [320, 768].map(width => ({ route, width }))));
  for (const run of runs) {
    current = run;
    const { route, width } = run;
    try {
      await page.setViewportSize({ width, height: width > 800 ? 1000 : 844 });
      const response = await page.goto(`${origin}/house-cleaning/${route}/`, { waitUntil: 'load' });
      if (response.status() !== 200) fail(route, width, `HTTP ${response.status()}`);
      await page.evaluate(() => document.fonts.ready);
      const layout = await page.evaluate(() => {
        const outside = [...document.querySelectorAll('main *')].filter(n => {
          const r = n.getBoundingClientRect();
          return r.width && r.height && (r.left < -1 || r.right > innerWidth + 1) && getComputedStyle(n).position !== 'fixed';
        }).map(n => n.className).slice(0, 12);
        const broken = [...document.images].filter(i => i.complete && i.naturalWidth === 0).map(i => i.src);
        const emptyIcons = [...document.querySelectorAll('.c-page-anchors .c-illust')].filter(n => getComputedStyle(n).maskImage === 'none').map(n => n.className);
        return { viewport: innerWidth, scrollWidth: document.documentElement.scrollWidth, outside, broken, emptyIcons };
      });
      if (layout.scrollWidth > width + 1) fail(route, width, `horizontal overflow ${JSON.stringify(layout)}`);
      if (layout.broken.length || layout.emptyIcons.length) fail(route, width, JSON.stringify(layout));
      const navy = await navyState(page);
      if (navy.count !== 3 || !navy.plain || !navy.visible || !navy.separated) fail(route, width, `reason navy ${JSON.stringify(navy)}`);
      const voiceOverlap = await page.locator('.c-voice-card').evaluateAll(cards => cards.flatMap((card, index) => {
        const logo = card.querySelector('img');
        const heading = card.querySelector('.c-voice-card__heading');
        if (!logo || !heading) return [];
        const a = logo.getBoundingClientRect();
        const b = heading.getBoundingClientRect();
        return a.left < b.right && a.right > b.left && a.top < b.bottom && a.bottom > b.top ? [index] : [];
      }));
      if (voiceOverlap.length) fail(route, width, `voice heading/logo overlap: ${voiceOverlap.join(',')}`);
      if (route === 'aircon') {
        const sectionCurve = await page.locator('.c-voice-section--bubble-preview').evaluate(section => {
          const edge = getComputedStyle(section, '::after');
          return edge.backgroundColor === 'rgb(255, 255, 255)' &&
            edge.borderTopLeftRadius.startsWith('50%') && edge.borderBottomLeftRadius.startsWith('50%');
        });
        if (!sectionCurve) fail(route, width, 'voice section top/bottom curves');
        const bubbles = await page.locator('.c-voice-bubbles').evaluate(grid => {
          const cards = [...grid.querySelectorAll('.c-voice-card')];
          const rects = cards.map(card => card.getBoundingClientRect());
          return {
            count: cards.length,
            vertical: rects.slice(1).every((rect, index) => rect.top >= rects[index].bottom + 8),
            alternating: rects.every((rect, index) => index === 0 ||
              (index % 2 ? rect.left < rects[index - 1].left : rect.left > rects[index - 1].left)),
            silhouettes: new Set(cards.map(card => getComputedStyle(card, '::before').backgroundImage)).size === 6 &&
              cards.every(card => getComputedStyle(card, '::before').backgroundImage.includes('/voices/')),
            ratings: cards.map(card => card.querySelector('.c-voice-card__stars')?.getAttribute('aria-label')),
            tone: cards.every(card => getComputedStyle(card).backgroundColor === 'rgb(220, 231, 243)')
          };
        });
        if (bubbles.count !== 6 || !bubbles.vertical || !bubbles.alternating || !bubbles.silhouettes ||
            !bubbles.tone || JSON.stringify(bubbles.ratings) !== JSON.stringify([5, 5, 4, 5, 5, 3].map(n => `5つ星中${n}つ星`))) {
          fail(route, width, `voice bubble preview ${JSON.stringify(bubbles)}`);
        }
        const plans = page.locator('#service-sets .c-tab__panel');
        const counts = await plans.evaluateAll(nodes => nodes.map(node => node.querySelectorAll('.c-plan-card').length));
        if (JSON.stringify(counts) !== '[2,1]') fail(route, width, `plan tab card counts: ${counts}`);
        if (width === 1440) {
          const second = page.locator('#service-sets .c-tab__button').nth(1);
          await second.click();
          if (await second.getAttribute('aria-selected') !== 'true' || !await plans.nth(1).isVisible()) {
            fail(route, width, 'ceiling plan tab selection');
          }
        }
      }
      if (categories.includes(route) && [390, 1440].includes(width) && screenshots) {
        await page.screenshot({ path: path.join(screenshots, `${route}-${width}-top.png`) });
      }
      if (width === 1440) {
        const faq = page.locator('.c-faq-accordion__trigger').first();
        await faq.click();
        const faqId = await faq.getAttribute('aria-controls');
        await page.waitForFunction(id => document.getElementById(id).getBoundingClientRect().height > 0, faqId);
        const tabs = page.locator('.c-tab__buttons button');
        if (await tabs.count() > 1) {
          await tabs.nth(1).click();
          if (await tabs.nth(1).getAttribute('aria-selected') !== 'true') fail(route, width, 'tab selection');
        }
        const option = page.locator('.c-lineup-options__accordion-trigger').first();
        if (await option.count()) {
          await option.click();
          const id = await option.getAttribute('aria-controls');
          await page.waitForFunction(id => document.getElementById(id).getBoundingClientRect().height > 0, id);
        }
        const variants = page.locator('.js-room-types');
        for (let i = 0; i < await variants.count(); i++) {
          const select = variants.nth(i);
          const index = await select.locator('option').count() - 1;
          await select.selectOption({ index });
          const result = await select.evaluate((n, index) => {
            const wrap = n.closest('.js-products');
            const switched = [...wrap.querySelectorAll('[data-switch-target]')].map(box => ({ target: box.dataset.switchTarget, active: [...box.children].findIndex(child => child.classList.contains('is-active')) }));
            return { product: wrap.querySelector('[data-product-card="parent"] input[name="product-id"]').value === n.value, switched, index };
          }, index);
          if (!result.product || result.switched.some(s => s.active !== index)) fail(route, width, `variant ${JSON.stringify(result)}`);
          await select.selectOption({ index: 0 });
        }
        const quantity = page.locator('.c-lineup-card .js-product-quantity.is-active select').first();
        if (await quantity.count() && await quantity.locator('option').count() > 1) {
          await quantity.selectOption({ index: 1 });
          if (await quantity.evaluate(n => n.selectedIndex) !== 1) fail(route, width, 'quantity');
        }
        if (categories.includes(route)) {
          const anchor = page.locator('.c-page-anchors a').first();
          const target = await anchor.getAttribute('href');
          await anchor.click();
          await page.waitForFunction(selector => {
            const y = document.querySelector(selector).getBoundingClientRect().top;
            return y >= 0 && y < 150;
          }, target);
        }
      }
      if (categories.includes(route) && [390, 1440].includes(width) && screenshots) {
        await page.locator('.c-lineup-card').first().scrollIntoViewIfNeeded();
        await page.screenshot({ path: path.join(screenshots, `${route}-${width}-product.png`) });
      }
      checks.push({ route, width, passed: !errors.some(e => e.route === route && e.width === width) });
    } catch (error) {
      fail(route, width, error.message);
    }
  }
  for (const route of staticReasons) {
    for (const width of [390, 1440]) {
      current = { route, width };
      try {
        await page.setViewportSize({ width, height: width > 800 ? 1000 : 844 });
        const response = await page.goto(`${origin}${route}`, { waitUntil: 'load' });
        if (response.status() !== 200) fail(route, width, `HTTP ${response.status()}`);
        const navy = await navyState(page);
        if (navy.count !== 3 || !navy.plain || !navy.visible || !navy.separated) fail(route, width, `reason navy ${JSON.stringify(navy)}`);
        if (await page.evaluate(() => document.documentElement.scrollWidth > innerWidth + 1)) fail(route, width, 'horizontal overflow');
        checks.push({ route, width, passed: !errors.some(e => e.route === route && e.width === width) });
      } catch (error) {
        fail(route, width, error.message);
      }
    }
  }
  await browser.close();
  const report = { checked_at: new Date().toISOString(), origin, pages: Object.keys(catalogue.pages).length + staticReasons.length, viewport_runs: runs.length + staticReasons.length * 2, checks, errors, passed: errors.length === 0 };
  fs.writeFileSync(path.join(root, 'source/service-browser-verification.json'), JSON.stringify(report, null, 2) + '\n');
  console.log(JSON.stringify({ pages: report.pages, viewport_runs: report.viewport_runs, passed: report.passed, errors }));
  process.exitCode = errors.length ? 1 : 0;
})().catch(error => { console.error(error); process.exitCode = 1; });
