const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const http = require('node:http');
const vm = require('node:vm');
const {chromium, webkit} = require('C:/Users/yasoj/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const root = path.resolve(__dirname, '../source/site');
const output = path.resolve(__dirname, '../evidence/2026-10-05/cart-audit');
const core = require(path.join(root, 'assets/js/cart-core.js'));
const sandbox = {window: {}};
vm.runInNewContext(fs.readFileSync(path.join(root, 'assets/js/cart-catalogue.js'), 'utf8'), sandbox);
const catalogue = JSON.parse(JSON.stringify(sandbox.window.CCH_CART_CATALOGUE));
const storageKey = 'cch-cart-v1';

function checkArithmetic() {
  let checks = 0;
  for (const [key, item] of Object.entries(catalogue.items)) {
    assert.equal(item.quote, false, key + ' lacks a price');
    for (const quantity of [...Array.from({length: 30}, (_, i) => i + 1), 9999]) {
      const lines = item.parentKey ? [{key: item.parentKey, quantity: 1}] : [];
      lines.push({key, quantity});
      const summary = core.calculate(lines, catalogue);
      const price = quantity >= (item.tiers[1]?.min || Infinity) ? item.tiers[1].price : item.tiers[0].price;
      const expected = price * quantity + (item.parentKey ? catalogue.items[item.parentKey].tiers[0].price : 0);
      assert.equal(summary.total, expected, key + ' × ' + quantity);
      assert.equal(summary.subtotal + summary.tax, expected);
      assert.equal(summary.tax, Math.floor(expected / 11));
      checks++;
    }
  }
  let lines = core.change([], 'product:1', 1, catalogue, true);
  assert.equal(core.calculate(lines, catalogue).total, 13200);
  lines = core.change(lines, 'product:1', 1, catalogue, true);
  assert.equal(core.calculate(lines, catalogue).total, 22000);
  lines = core.change(lines, 'option:1:1', 2, catalogue, true);
  assert.equal(core.calculate(lines, catalogue).total, 39600);
  lines = core.change(lines, 'product:1', 1, catalogue);
  assert.equal(core.calculate(lines, catalogue).total, 30800);
  lines = core.change(lines, 'product:1', 0, catalogue);
  assert.deepEqual(lines, []);
  assert.throws(() => core.change([], 'option:1:1', 1, catalogue), /対象サービス/);
  assert.equal(core.calculate([{key:'product:1',quantity:1},{key:'product:2',quantity:1}], catalogue).total, 31900);
  assert.equal(core.calculate([{key:'product:1',quantity:1},{key:'plan:2_159',quantity:1}], catalogue).total, 40700);
  assert.equal(core.calculate([{key:'product:1',quantity:1},{key:'product:3',quantity:1}], catalogue).total, 40700);
  for (const value of [-1, 1.5, Infinity, NaN, '', '1a', 10000]) assert.throws(() => core.quantity(value));
  assert.throws(() => core.calculate([{key: 'made-up', quantity: 1}], catalogue));
  const mixed = Object.entries(catalogue.items).filter(([, item]) => !item.parentKey).map(([key]) => ({key, quantity: 2}));
  for (const [key, item] of Object.entries(catalogue.items)) if (item.parentKey) mixed.push({key, quantity: 3});
  const expected = mixed.reduce((sum, line) => {
    const p = catalogue.items[line.key];
    return sum + (line.quantity > 1 && p.tiers.length > 1 ? p.tiers[1].price : p.tiers[0].price) * line.quantity;
  }, 0);
  assert.equal(core.calculate(mixed, catalogue).total, expected);
  return {checks, mixedItems: mixed.length, mixedTotal: expected};
}

function serve() {
  const server = http.createServer((req, res) => {
    let file = path.join(root, decodeURIComponent(new URL(req.url, 'http://local').pathname));
    if (file.endsWith(path.sep)) file += 'index.html';
    try {
      res.setHeader('Content-Type', ({'.html':'text/html; charset=utf-8','.js':'text/javascript; charset=utf-8','.css':'text/css','.svg':'image/svg+xml','.webp':'image/webp','.png':'image/png','.jpg':'image/jpeg'})[path.extname(file)] || 'application/octet-stream');
      res.end(fs.readFileSync(file));
    } catch { res.statusCode = 404; res.end(); }
  });
  return new Promise(resolve => server.listen(0, '127.0.0.1', () => resolve(server)));
}

async function exerciseAll(page) {
  return page.evaluate(() => {
    const cat = window.CCH_CART_CATALOGUE;
    const results = [];
    const route = location.pathname;
    const quick = route.startsWith('/quick_cart/');
    const office = route.startsWith('/office/');
    const allCards = [...document.querySelectorAll('.js-product-card')];
    const bindings = cat.pages[route];
    const reset = fixture => {
      document.querySelector('#cch-cart-dialog')?.close();
      localStorage.setItem('cch-cart-v1', JSON.stringify({version: 1, lines: fixture}));
      document.querySelectorAll('.c-counter__input').forEach(input => input.value = '0');
      window.CCHCart.refresh();
    };
    const selectVariant = (card, index) => {
      const select = card.querySelector('.js-room-types');
      if (select) { select.selectedIndex = index; select.dispatchEvent(new Event('change', {bubbles: true})); }
    };
    function displayPrices(card, variant) {
      let node = card;
      if (card.querySelector('.js-room-types')) node = card.querySelector('[data-switch-target="prices"], .js-price').children[variant];
      return [...node.querySelectorAll('.c-price__text, .c-plan-price__text')].filter(e => !e.closest('dialog')).map(e => ({
        amount: Number(e.textContent.replace(/[^0-9]/g, '')),
        threshold: Number(e.closest('[data-text]')?.dataset.text.match(/(\d+)(?:台|セット)以上/)?.[1] || 1)
      }));
    }
    for (const binding of bindings) {
      const card = allCards[binding.index];
      for (let variant = 0; variant < binding.keys.length; variant++) {
        const key = binding.keys[variant];
        const item = cat.items[key];
        if (item.parentKey) {
          const parent = bindings.find(b => b.keys.includes(item.parentKey));
          if (parent) selectVariant(allCards[parent.index], parent.keys.indexOf(item.parentKey));
        }
        selectVariant(card, variant);
        const amounts = displayPrices(card, variant);
        if (!amounts.length) throw new Error(key + ': missing displayed price');
        const quantitySelect = card.querySelectorAll('.js-product-quantity select')[variant];
        const counter = card.querySelectorAll('.c-counter__input')[variant];
        const max = quantitySelect ? Number(quantitySelect.options[quantitySelect.options.length - 1].value) : counter ? Number(counter.max) : 1;
        for (const quantity of [...new Set([1, Math.min(2, max), max])]) {
          const fixture = item.parentKey ? [{key: item.parentKey, quantity: 1}] : [];
          reset(fixture);
          if (quantitySelect) {
            quantitySelect.value = String(quantity);
            quantitySelect.dispatchEvent(new Event('change', {bubbles: true}));
          }
          if (counter) {
            if (quick) {
              const plus = counter.closest('.js-counter').querySelector('[data-type="increment"]');
              for (let i = 0; i < quantity; i++) plus.click();
            } else counter.value = String(quantity);
          }
          if (office) document.getElementById('js-add-cart').click();
          else if (!quick) card.querySelector('.js-add-cart').click();
          const selected = [...amounts].reverse().find(p => p.threshold <= quantity);
          const parentPrice = item.parentKey ? cat.items[item.parentKey].tiers[0].price : 0;
          const expected = selected.amount * quantity + parentPrice;
          const actual = window.CCHCart.getSummary();
          const displayed = document.querySelector('#js-floating-total-quantity, .js-total-amount');
          const displayedAmount = displayed ? Number(displayed.textContent.replace(/[^0-9]/g, '')) : null;
          if (actual.total !== expected || (displayed && displayedAmount !== expected)) {
            throw new Error(JSON.stringify({key, quantity, expected, actual: actual.total, displayedAmount, dialog: document.querySelector('#cch-cart-dialog')?.textContent}));
          }
          if (actual.details.find(d => d.key === key)?.quantity !== quantity) throw new Error(key + ': wrong quantity');
          results.push({key, quantity, expected, actual: actual.total});
        }
      }
    }
    reset([]);
    return results;
  });
}

async function nativeFlow(page, base) {
  await page.goto(base + '/house-cleaning/aircon/', {waitUntil: 'domcontentloaded'});
  await page.evaluate(() => { localStorage.removeItem('cch-cart-v1'); window.CCHCart.refresh(); });
  const first = page.locator('.js-product-card[data-product-card="parent"]').first();
  await first.locator('select').selectOption('2');
  await first.locator('.js-add-cart').click();
  await page.locator('[data-cart-close]').click();
  const wrapper = page.locator('.js-products').first();
  await wrapper.locator('.c-lineup-options__accordion-trigger').click();
  const option = wrapper.locator('[data-product-card="option"]').first();
  await option.locator('select').selectOption('2');
  await option.locator('.js-add-cart').click();
  await page.locator('#cch-cart-dialog a').click();
  await page.waitForURL('**/cart/');
  assert.equal(await page.locator('[data-cart-total]').textContent(), '39,600円');
  await page.locator('[data-cart-set="product:1"]').fill('1');
  await page.locator('[data-cart-set="product:1"]').press('Tab');
  assert.equal(await page.locator('[data-cart-total]').textContent(), '30,800円');
  await page.reload({waitUntil: 'domcontentloaded'});
  assert.equal(await page.locator('[data-cart-total]').textContent(), '30,800円');
  await page.screenshot({path: path.join(output, `${process.env.CART_ENGINE || 'chromium'}-${page.viewportSize().width}-cart.png`)});
  await page.locator('a[href="/quick_cart/option/"]').click();
  await page.waitForURL('**/quick_cart/option/');
  await page.locator('[data-cart-set="option:1:28"]').fill('2');
  await page.locator('[data-cart-set="option:1:28"]').press('Tab');
  assert.equal(await page.locator('[data-cart-total]').textContent(), '41,800円');
  await page.goto(base + '/quick_cart/aircon/', {waitUntil: 'domcontentloaded'});
  assert.equal(await page.locator('.c-counter__input').first().inputValue(), '1');
  await page.locator('.js-counter-button[data-type="increment"]').first().click();
  assert.equal(await page.locator('.js-total-amount').textContent(), '50,600');
  await page.locator('#js-next-button').click();
  await page.waitForURL('**/quick_cart/option/');
  await page.goto(base + '/cart/', {waitUntil: 'domcontentloaded'});
  await page.locator('[data-cart-remove="product:1"]').click();
  assert.equal(await page.locator('[data-cart-line]').count(), 0);
  assert.match(await page.locator('[data-cart-content]').textContent(), /カートが空/);
}

(async () => {
  fs.mkdirSync(output, {recursive: true});
  const arithmetic = checkArithmetic();
  const server = process.env.CART_BASE ? null : await serve();
  const base = process.env.CART_BASE || 'http://127.0.0.1:' + server.address().port;
  const engine = process.env.CART_ENGINE || 'chromium';
  const browser = await (engine === 'webkit' ? webkit : chromium).launch(engine === 'webkit' ? {headless: true} : {channel: 'chrome', headless: true});
  const report = {base, engine, arithmetic, cases: [], interactions: [], errors: [], passed: false};
  try {
    for (const width of [1439, 390]) {
      const context = await browser.newContext({viewport: {width, height: 900}, isMobile: width < 768, hasTouch: width < 768});
      const page = await context.newPage();
      page.setDefaultTimeout(15000);
      const errors = [];
      page.on('pageerror', error => errors.push(error.message));
      page.on('request', request => { if (request.url().includes('/api/v1/')) errors.push('obsolete API: ' + request.url()); });
      for (const route of Object.keys(catalogue.pages)) {
        await page.goto(base + route, {waitUntil: 'domcontentloaded'});
        const checks = await exerciseAll(page);
        report.cases.push({route, width, checks});
        console.log(JSON.stringify({engine, width, route, checks: checks.length}));
      }
      await nativeFlow(page, base);
      const layout = await page.evaluate(() => ({width: innerWidth, scrollWidth: document.documentElement.scrollWidth}));
      assert(layout.scrollWidth <= layout.width + 1, 'horizontal overflow');
      assert.deepEqual(errors, []);
      report.interactions.push({width, passed: true});
      await context.close();
    }
    report.passed = true;
  } catch (error) { report.errors.push(error.stack); console.error(error); process.exitCode = 1; }
  finally {
    fs.writeFileSync(path.join(output, `${process.env.CART_BASE ? 'public' : 'local'}-${engine}.json`), JSON.stringify(report, null, 2));
    await browser.close();
    if (server) server.close();
  }
  console.log(JSON.stringify({passed: report.passed, engine, pages: report.cases.length, operations: report.cases.reduce((n, c) => n + c.checks.length, 0), arithmetic}));
})();
