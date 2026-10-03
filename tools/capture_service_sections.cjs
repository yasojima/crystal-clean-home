const fs = require('fs');
const path = require('path');
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright');

const origin = process.env.SITE_ORIGIN || 'http://127.0.0.1:8769';
const output = process.env.SCREENSHOT_DIR || path.resolve(__dirname, '..', 'evidence', '2026-10-02');
const reasonRoutes = ['aircon', 'pack', 'water', 'washer', 'kitchen', 'room', 'coating', 'others'];
const staticReasons = [
  { route: 'home', url: '/' },
  { route: 'about', url: '/about/' },
  { route: 'quick-cart-option', url: '/quick_cart/option/' },
  { route: 'lab-product-303', url: '/lab/online_store/detergent/product-303/' },
];
const cases = [
  { route: 'aircon', section: 'top', viewport: true },
  ...reasonRoutes.map(route => ({ route, section: 'reasons', selector: 'section:has(.p-reasons)' })),
  ...staticReasons.map(item => ({ ...item, section: 'reasons', selector: 'section:has(.p-reasons)' })),
  { route: 'aircon', section: 'plans', selector: '#service-sets' },
  { route: 'aircon', section: 'voices', selector: 'section.c-voice-section--bubble-preview' },
  { route: 'room', section: 'voices', selector: 'section:has(.c-voice-card)' },
].filter(item => (!process.env.SECTION_FILTER || item.section === process.env.SECTION_FILTER) &&
  (!process.env.ROUTE_FILTER || item.route === process.env.ROUTE_FILTER));

(async () => {
  fs.mkdirSync(output, { recursive: true });
  const browser = await chromium.launch({ headless: true, channel: 'chrome' });
  const page = await browser.newPage();
  const results = [];
  for (const width of [1581, 390]) {
    await page.setViewportSize({ width, height: width === 1581 ? 1326 : 844 });
    for (const item of cases) {
      const response = await page.goto(`${origin}${item.url || `/house-cleaning/${item.route}/`}`, { waitUntil: 'load' });
      await page.evaluate(() => document.fonts.ready);
      if (item.viewport) {
        await page.locator('.c-house-cleaning-mv img').evaluate(async image => {
          image.loading = 'eager';
          await image.decode();
        });
        await page.evaluate(() => window.scrollTo(0, 0));
        const file = path.join(output, `${item.route}-${item.section}-${width}.png`);
        await page.screenshot({ path: file });
        results.push({ ...item, width, status: response.status(), file, height: width === 1581 ? 1326 : 844 });
        continue;
      }
      const section = page.locator(item.selector).first();
      await section.scrollIntoViewIfNeeded();
      const imageWidths = await section.locator('img').evaluateAll(images => Promise.all(images.map(async image => {
        image.loading = 'eager';
        await image.decode();
        return image.naturalWidth;
      })));
      if (imageWidths.some(width => width === 0)) throw new Error(`Broken image in ${item.route}/${item.section}`);
      const file = path.join(output, `${item.route}-${item.section}-${width}.png`);
      await section.screenshot({ path: file, style: '.c-header, #js-floating, #viewport-hud { visibility: hidden !important; }' });
      const metrics = await section.evaluate((node) => {
        const rect = node.getBoundingClientRect();
        return { width: Math.round(rect.width), height: Math.round(rect.height) };
      });
      results.push({ ...item, width, status: response.status(), file, ...metrics });
    }
  }
  await browser.close();
  fs.writeFileSync(path.join(output, 'service-section-screens.json'), JSON.stringify({ origin, results }, null, 2) + '\n');
  console.log(JSON.stringify({ origin, screens: results.length }));
})().catch(error => { console.error(error); process.exitCode = 1; });
