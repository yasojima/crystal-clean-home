const fs = require('fs');
const path = require('path');
const assert = require('assert/strict');
const { chromium, webkit } = require('C:/Users/yasoj/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const site = path.resolve(__dirname, '../source/site');
const phase = process.argv[2] || 'local';
const output = path.resolve(process.argv[3] || 'evidence/2026-10-05/footer-order');
const origin = 'https://yasojima.github.io';
const mime = { '.html': 'text/html', '.css': 'text/css', '.js': 'text/javascript', '.svg': 'image/svg+xml', '.webp': 'image/webp', '.png': 'image/png', '.woff2': 'font/woff2' };
const selectors = ['.u-pc-only .c-aircon-footer__coating-links', '.u-pc-only .c-aircon-footer__other-links'];

async function measure(page) {
  return page.evaluate(selectors => {
    const footer = document.querySelector('.c-footer--aircon');
    const nav = footer.querySelector('.c-footer__top-nav');
    const rect = el => { const r = el.getBoundingClientRect(); return { x: r.x, y: r.y, width: r.width, height: r.height, right: r.right, bottom: r.bottom }; };
    return {
      width: innerWidth, height: innerHeight, footer: rect(footer), minHeight: parseFloat(getComputedStyle(footer).minHeight),
      columns: [...nav.children].map(rect),
      groups: [...nav.lastElementChild.querySelectorAll('.c-footer-item-heading')].map(el => ({ text: el.textContent.trim(), ...rect(el) })),
      lists: selectors.map(selector => { const list = footer.querySelector(selector); return { selector, ...rect(list), items: [...list.children].map((el, index) => ({ index, text: el.textContent.trim(), fontSize: getComputedStyle(el).fontSize, ...rect(el) })) }; }),
      overflow: document.documentElement.scrollWidth > innerWidth + 1
    };
  }, selectors);
}

function validate(result, naturalHeight = false) {
  assert.equal(result.columns.length, 3);
  assert(!result.overflow, 'page overflow');
  assert.deepEqual(result.groups.map(g => g.text), ['コーティング', 'その他のお掃除', 'ご利用ガイド', 'ビジネス・法人向け']);
  for (const group of result.groups) assert(Math.abs(group.x - result.columns[2].x) < 1, 'category moved out of the third column');
  for (const list of result.lists) {
    assert(list.width > 0 && list.height > 0, 'desktop category is not visible');
    const readingOrder = list.items.slice().sort((a, b) => Math.abs(a.x - b.x) > 1 ? a.x - b.x : a.y - b.y);
    assert.deepEqual(readingOrder.map(item => item.index), list.items.map(item => item.index), 'reading order is not top-to-bottom');
    assert(new Set(list.items.map(item => Math.round(item.x))).size <= 2, 'too many inner columns');
    for (const item of list.items) {
      assert.equal(item.fontSize, '12px');
      assert(item.x >= list.x - 1 && item.right <= list.right + 1 && item.bottom <= list.bottom + 1, 'link outside its category');
    }
    for (let i = 1; i < readingOrder.length; i++) if (Math.abs(readingOrder[i].x - readingOrder[i - 1].x) < 1) {
      assert(readingOrder[i].y >= readingOrder[i - 1].bottom - 1, 'overlapping links');
    }
  }
  if (!naturalHeight && result.width >= 1024) assert(result.footer.height <= result.minHeight + 1, 'footer exceeds the available frame');
}

(async () => {
  fs.mkdirSync(output, { recursive: true });
  const results = [];
  for (const engine of ['chrome', 'webkit']) {
    const browser = await (engine === 'chrome' ? chromium.launch({ channel: 'chrome', headless: true }) : webkit.launch({ headless: true }));
    try {
      const page = await browser.newPage();
      if (phase === 'local') await page.route(origin + '/**', async route => {
        const pathname = new URL(route.request().url()).pathname;
        const file = path.join(site, pathname + (pathname.endsWith('/') ? 'index.html' : ''));
        if (fs.existsSync(file) && fs.statSync(file).isFile()) await route.fulfill({ body: fs.readFileSync(file), contentType: mime[path.extname(file)] || 'application/octet-stream' });
        else await route.continue();
      });
      await page.goto(origin + '/house-cleaning/aircon/?footer-order=2026100514', { waitUntil: 'domcontentloaded' });
      await page.evaluate(async () => { await document.fonts.ready; await Promise.all([...document.querySelectorAll('footer img')].map(img => { img.loading = 'eager'; return img.decode().catch(() => {}); })); });
      const sizes = engine === 'chrome' && phase === 'local' ? [[1024,600],[1280,551],[1366,650],[1440,800],[1439,803],[1919,1093],[1920,1080],[1440,1100],[1440,1973],[768,1024]] : [[1280,551],[1439,803],[1919,1093]];
      for (const [width, height] of sizes) {
        await page.setViewportSize({ width, height });
        await page.waitForTimeout(150);
        const result = await measure(page);
        validate(result);
        if (height === 803) assert.equal(new Set(result.lists[1].items.map(i => Math.round(i.x))).size, 1);
        if (height === 1093) for (const list of result.lists) assert.equal(new Set(list.items.map(i => Math.round(i.x))).size, 1);
        results.push({ engine, case: 'viewport', ...result });
        if ([803,1093].includes(height)) {
          await page.evaluate(() => scrollTo({ top: document.documentElement.scrollHeight, behavior: 'instant' }));
          await page.waitForTimeout(750);
          await page.screenshot({ path: path.join(output, `${phase}-${engine}-${width}x${height}.png`) });
        }
      }
      if (phase === 'local') {
        await page.setViewportSize({ width: 1439, height: 803 });
        const original = await page.evaluate(selectors => selectors.map(selector => document.querySelector(selector).innerHTML), selectors);
        await page.evaluate(selectors => selectors.forEach((selector, index) => {
          const list = document.querySelector(selector), sample = list.firstElementChild.cloneNode(true);
          for (let i = 0; i < (index ? 12 : 20); i++) { const item = sample.cloneNode(true); item.querySelector('a').textContent = '追加項目 ' + i; list.append(item); }
        }), selectors);
        await page.waitForTimeout(150);
        const enlarged = await measure(page); validate(enlarged, true);
        results.push({ engine, case: 'items-increased', ...enlarged });
        await page.evaluate(selectors => selectors.forEach(selector => {
          const list = document.querySelector(selector);
          while (list.children.length > 1) list.lastElementChild.remove();
        }), selectors);
        await page.waitForTimeout(150);
        const reduced = await measure(page); validate(reduced);
        for (let i = 0; i < selectors.length; i++) assert(reduced.lists[i].height < enlarged.lists[i].height, 'list did not shrink');
        assert(reduced.footer.height < enlarged.footer.height, 'footer did not shrink after removing excess items');
        results.push({ engine, case: 'items-reduced', ...reduced });
        await page.evaluate(({ selectors, original }) => selectors.forEach((selector, index) => document.querySelector(selector).innerHTML = original[index]), { selectors, original });
        await page.waitForTimeout(150);
        validate(await measure(page));
      }
    } finally { await browser.close(); }
  }
  fs.writeFileSync(path.join(output, `verification-${phase}.json`), JSON.stringify({ checkedAt: new Date().toISOString(), phase, passed: true, results }, null, 2) + '\n');
  console.log(JSON.stringify({ phase, cases: results.length, passed: true }));
})().catch(error => { console.error(error); process.exitCode = 1; });
