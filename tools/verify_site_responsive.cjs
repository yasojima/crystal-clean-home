const fs = require('fs');
const path = require('path');
const assert = require('assert/strict');
const { chromium, webkit } = require(process.env.PLAYWRIGHT_MODULE || 'C:/Users/yasoj/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const root = path.resolve(__dirname, '..');
const site = path.join(root, 'source/site');
const phase = process.argv[2] || 'local';
const output = path.resolve(process.argv[3] || 'evidence/2026-10-05/site-responsive');
const origin = 'https://yasojima.github.io';
const engine = process.env.SITE_ENGINE || 'chrome';
const types = { '.html': 'text/html', '.css': 'text/css', '.js': 'text/javascript', '.svg': 'image/svg+xml', '.webp': 'image/webp', '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.woff2': 'font/woff2', '.woff': 'font/woff', '.json': 'application/json' };
function htmlFiles(dir) {
  return fs.readdirSync(dir, { withFileTypes: true }).flatMap(entry => entry.isDirectory() ? htmlFiles(path.join(dir, entry.name)) : entry.name.endsWith('.html') ? [path.join(dir, entry.name)] : []);
}
const allRoutes = htmlFiles(site).map(file => '/' + path.relative(site, file).replaceAll('\\', '/').replace(/index\.html$/, ''));
const routes = process.env.SITE_ROUTES ? process.env.SITE_ROUTES.split(',') : allRoutes;
const sizes = (process.env.SITE_SIZES || '1440x1100,390x844').split(',').map(size => size.split('x').map(Number));

(async () => {
  fs.mkdirSync(output, { recursive: true });
  const browser = await (engine === 'webkit' ? webkit : chromium).launch(engine === 'webkit' ? { headless: true } : { channel: 'chrome', headless: true });
  const results = [];
  const pairs = {};
  let next = 0;
  const cases = routes.flatMap(route => sizes.map(([width, height]) => ({ route, width, height })));
  async function worker() {
    while (next < cases.length) {
      const { route, width, height } = cases[next++];
      const context = await browser.newContext({ viewport: { width, height }, isMobile: width < 768, hasTouch: width < 768 });
      const page = await context.newPage();
      page.setDefaultTimeout(30000);
      if (phase === 'local') await page.route(origin + '/**', async request => {
        const pathname = decodeURIComponent(new URL(request.request().url()).pathname);
        const file = path.join(site, pathname + (pathname.endsWith('/') ? 'index.html' : ''));
        if (fs.existsSync(file) && fs.statSync(file).isFile()) await request.fulfill({ body: fs.readFileSync(file), contentType: types[path.extname(file)] || 'application/octet-stream' });
        else await request.continue();
      });
      const response = await page.goto(origin + route + '?responsive=2026100513', { waitUntil: 'domcontentloaded' });
      assert.equal(response.status(), 200, route);
      await page.evaluate(async () => {
        await document.fonts.ready;
        await Promise.all([...document.querySelectorAll('main img, footer.c-footer img')].map(img => { img.loading = 'eager'; return img.decode().catch(() => {}); }));
      });
      const data = await page.evaluate(() => {
        const footer = document.querySelector('footer.c-footer');
        const rect = element => { const r = element.getBoundingClientRect(); return { x: r.x, y: r.y, width: r.width, height: r.height }; };
        const normalized = text => text.replace(/\s+/g, ' ').trim();
        const main = document.querySelector('main');
        const walker = document.createTreeWalker(main, NodeFilter.SHOW_TEXT);
        const text = [];
        let node;
        while ((node = walker.nextNode())) {
          const value = normalized(node.textContent);
          const parent = node.parentElement;
          if (!value || parent.closest('script,style,dialog,[role="dialog"],.c-floating-buttons,.c-corporate-floating')) continue;
          if (parent.closest('[role="tabpanel"]')) { text.push(value); continue; }
          let visible = true;
          for (let ancestor = parent; ancestor && ancestor !== main; ancestor = ancestor.parentElement) {
            const style = getComputedStyle(ancestor);
            if (style.display === 'none' || style.visibility === 'hidden' || ancestor.getAttribute('aria-hidden') === 'true' || (style.overflowY === 'hidden' && ancestor.getBoundingClientRect().height === 0)) { visible = false; break; }
          }
          if (visible) text.push(value);
        }
        const details = selector => [...footer.querySelectorAll(selector + ' .c-footer-global-links a')].map(link => [normalized(link.textContent), link.getAttribute('href')]);
        return {
          pageWidth: document.documentElement.scrollWidth,
          mainText: [...new Set(text)].sort(),
          desktopDetails: details('.u-pc-only'), mobileDetails: details('.u-sp-only'),
          footers: document.querySelectorAll('footer.c-footer').length,
          rows: footer.querySelectorAll('.aircon-footer-menu__row').length,
          mainImages: [...main.querySelectorAll('img')].filter(img => img.getBoundingClientRect().width && img.getBoundingClientRect().height).map(img => ({ src: img.getAttribute('src'), loaded: img.complete && img.naturalWidth > 0 })),
          footer: rect(footer)
        };
      });
      const issues = [];
      if (data.pageWidth > width + 1) issues.push({ type: 'horizontal-overflow', pageWidth: data.pageWidth });
      if (data.footers !== 1 || data.rows !== 5) issues.push({ type: 'shared-footer-structure' });
      if (JSON.stringify(data.desktopDetails.slice().sort()) !== JSON.stringify(data.mobileDetails.slice().sort())) issues.push({ type: 'footer-content-parity' });
      const unloaded = data.mainImages.filter(img => !img.loaded);
      if (unloaded.length) issues.push({ type: 'images-unloaded', images: unloaded });
      await page.evaluate(() => scrollTo({ top: document.documentElement.scrollHeight, behavior: 'instant' }));
      await page.waitForTimeout(500);
      await page.evaluate(() => scrollTo({ top: document.documentElement.scrollHeight, behavior: 'instant' }));
      await page.waitForTimeout(750);
      const geometry = await page.evaluate(() => {
        const footer = document.querySelector('footer.c-footer'), f = footer.getBoundingClientRect();
        const header = document.querySelector('.c-header').getBoundingClientRect();
        const support = footer.querySelector('.c-aircon-footer__support-start');
        const phone = footer.querySelector(innerWidth >= 768 ? '.footer-tel-pc' : '.footer-tel-sp').getBoundingClientRect();
        const headings = [...footer.querySelectorAll('.aircon-footer-menu .c-footer-item-heading')];
        const fixedHeight = parseFloat(footer.style.getPropertyValue('--aircon-footer-fixed-height')) || 0;
        const cartHidden = [...document.querySelectorAll('.c-floating-buttons a,.c-floating-buttons button,.c-corporate-floating a')].every(el => {
          const style = getComputedStyle(el), r = el.getBoundingClientRect();
          for (let ancestor = el.parentElement; ancestor; ancestor = ancestor.parentElement) {
            const parentStyle = getComputedStyle(ancestor);
            if (parentStyle.opacity === '0' || parentStyle.visibility === 'hidden' || parentStyle.display === 'none') return true;
          }
          const viewportWidth = document.scrollingElement.clientWidth;
          if (style.visibility === 'hidden' || style.display === 'none' || style.opacity === '0' || r.width <= 0 || r.height <= 0 || r.top >= innerHeight - 1 || r.bottom <= 1 || r.left >= viewportWidth - 1 || r.right <= 1) return true;
          const left = Math.max(0, r.left), right = Math.min(innerWidth, r.right), top = Math.max(0, r.top), bottom = Math.min(innerHeight, r.bottom);
          return [.1, .5, .9].every(x => [.1, .5, .9].every(y => !el.contains(document.elementFromPoint(left + (right - left) * x, top + (bottom - top) * y))));
        });
        return { viewportHeight: innerHeight, viewportWidth: innerWidth, clientWidth: document.documentElement.clientWidth, height: f.height, top: f.top, bottom: f.bottom, headerHeight: header.height, supportGap: innerWidth >= 768 ? support.getBoundingClientRect().top - support.previousElementSibling.getBoundingClientRect().bottom : null, phoneHeight: phone.height, minMobileHeight: fixedHeight + 56 * 5, rowHeights: headings.map(el => el.getBoundingClientRect().height), cartHidden, ...(cartHidden ? {} : { cartDetails: [...document.querySelectorAll('.c-floating-buttons a,.c-floating-buttons button,.c-corporate-floating a')].map(el => { const r = el.getBoundingClientRect(); const p = el.closest('.c-floating-buttons,.c-corporate-floating'); return { text: el.textContent.trim(), x: r.x, y: r.y, width: r.width, height: r.height, parent: p.className, transform: getComputedStyle(p).transform }; }) }) };
      });
      if (geometry.bottom > geometry.viewportHeight + 1) issues.push({ type: 'footer-bottom-clipped', ...geometry });
      if (width >= 1024 && geometry.height > Math.min(height, 1100) - geometry.headerHeight + 1) issues.push({ type: 'footer-exceeds-frame', ...geometry });
      if (width < 768 && geometry.height > Math.max(Math.min(height, 1100), geometry.minMobileHeight) + 1) issues.push({ type: 'mobile-footer-stretched', ...geometry });
      if (height > 800 && width >= 768 && geometry.supportGap > 17) issues.push({ type: 'support-gap-stretched', ...geometry });
      if (!geometry.cartHidden) issues.push({ type: 'floating-ui-over-footer' });
      if (process.env.SITE_INTERACTIONS === '1' && width < 768) {
        for (const tab of await page.locator('main [role="tab"]').all()) {
          if (!await tab.isVisible()) continue;
          await tab.click();
          const target = await tab.getAttribute('aria-controls');
          if (target) assert.ok(await page.locator('#' + target).isVisible(), `${route}: tab ${target}`);
        }
        for (const trigger of await page.locator('.aircon-footer-menu .js-accordion-trigger').all()) {
          await trigger.click();
          await page.waitForTimeout(330);
          assert.equal(await trigger.getAttribute('aria-expanded'), 'true', route);
          const content = page.locator('#' + await trigger.getAttribute('aria-controls'));
          assert.ok(await content.isVisible(), route);
          assert.ok(await content.evaluate(el => el.getBoundingClientRect().height > 0), route);
          await trigger.click();
          await page.waitForTimeout(330);
          assert.equal(await trigger.getAttribute('aria-expanded'), 'false', route);
        }
        await page.evaluate(() => scrollTo({ top: document.documentElement.scrollHeight, behavior: 'instant' }));
        await page.waitForTimeout(500);
      }
      if (process.env.SITE_SCREENSHOTS === '1') await page.screenshot({ path: path.join(output, `${engine}-${width}x${height}-${route === '/' ? 'home' : route.replaceAll('/', '-').slice(1, -1)}.png`) });
      pairs[route] ||= {};
      pairs[route][width >= 768 ? 'desktop' : 'mobile'] = data.mainText;
      const result = { route, width, height, issues, geometry, mainImages: data.mainImages.length, desktopDetails: data.desktopDetails.length, mobileDetails: data.mobileDetails.length };
      results.push(result);
      if (issues.length) console.log(JSON.stringify(result));
      await context.close();
      if (results.length % 20 === 0) console.log(`${engine}: ${results.length}/${cases.length} checked`);
    }
  }
  try { await Promise.all(Array.from({ length: Number(process.env.SITE_WORKERS || 3) }, worker)); } finally { await browser.close(); }
  const parity = Object.entries(pairs).filter(([, pair]) => pair.desktop && pair.mobile).map(([route, pair]) => ({ route, desktopOnly: pair.desktop.filter(text => !pair.mobile.includes(text)), mobileOnly: pair.mobile.filter(text => !pair.desktop.includes(text)) }));
  const failures = results.filter(result => result.issues.length);
  fs.writeFileSync(path.join(output, `${phase}-${engine}.json`), JSON.stringify({ checkedAt: new Date().toISOString(), phase, engine, passed: failures.length === 0 && parity.every(p => p.desktopOnly.length === 0), results, parity }, null, 2) + '\n');
  console.log(JSON.stringify({ cases: results.length, failures: failures.length, parityDifferences: parity.filter(p => p.desktopOnly.length || p.mobileOnly.length) }));
  if ((failures.length || parity.some(p => p.desktopOnly.length)) && process.env.SITE_INSPECT !== '1') process.exitCode = 1;
})().catch(error => { console.error(error); process.exitCode = 1; });
