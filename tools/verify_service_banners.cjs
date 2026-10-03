const fs = require('fs');
const path = require('path');
const assert = require('assert/strict');
const {execFileSync} = require('child_process');
const {chromium, webkit} = require(process.env.PLAYWRIGHT_MODULE || 'C:/Users/yasoj/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const root = path.resolve(__dirname, '..');
const catalogue = JSON.parse(fs.readFileSync(path.join(root, 'source/service-pages/catalogue.json'), 'utf8'));
const banners = JSON.parse(fs.readFileSync(path.join(root, 'source/service-pages/copy.json'), 'utf8')).banners;
const origin = process.argv[2] || 'http://127.0.0.1:8769';
const output = process.argv[3] || 'evidence/2026-10-04/local/banners';
const baselineCommit = process.env.BANNER_BASELINE || 'c82d2c0';
const baselineCss = execFileSync('git', ['show', `${baselineCommit}:source/site/assets/css/aircon-hero.css`], {cwd: root, encoding: 'utf8'});
const sizes = (process.env.BANNER_SIZES || '1734x1321,1440x800,414x688,320x688').split(',').map(s => {
 const [width, height] = s.split('x').map(Number); return {width, height};
});
const routes = Object.keys(catalogue.pages).filter(r => !process.env.BANNER_ROUTES || process.env.BANNER_ROUTES.split(',').includes(r));
const screenshotRoutes = (process.env.BANNER_SCREENSHOTS || 'aircon,pack,water,washer,kitchen,room,coating,others,water/ulblo,room/wallpaper-dyeing,washer/side').split(',');
fs.mkdirSync(output, {recursive: true});
async function read(page) {
 return page.evaluate(() => {
  const hero = document.querySelector('.c-house-cleaning-mv--check');
  const elements = {hero, image: hero.querySelector('img'), text: hero.querySelector('p'), check: hero.querySelector('.c-house-cleaning-mv__check'), label: hero.querySelector('.c-house-cleaning-mv__check-label')};
  const metrics = {};
  for (const [key, n] of Object.entries(elements)) {
   const r = n.getBoundingClientRect(), s = getComputedStyle(n);
   metrics[key] = {x: r.x, y: r.y, width: r.width, height: r.height, font: s.font, lineHeight: s.lineHeight, color: s.color, padding: s.padding, background: s.backgroundImage, mask: s.maskImage, maskSize: s.maskSize, maskPosition: s.maskPosition, objectFit: s.objectFit, objectPosition: s.objectPosition};
  }
  return {metrics, lines: elements.text.innerText.split('\n'), image: {src: new URL(elements.image.currentSrc).pathname, alt: elements.image.alt, width: elements.image.naturalWidth, height: elements.image.naturalHeight}, heading: hero.querySelector('h1').textContent.trim(), checkText: elements.check.textContent, documentWidth: document.documentElement.scrollWidth, viewportWidth: innerWidth};
 });
}
async function settle(page) {
 await page.evaluate(async () => {await document.fonts.ready; await document.querySelector('.c-house-cleaning-mv--check img').decode();});
}
function near(a, b, label) {assert(Math.abs(a - b) < .1, `${label}: ${a} differs from ${b}`);}
function compare(actual, reference, viewport) {
 for (const key of ['hero', 'image', 'check', 'label']) {
  for (const property of ['x', 'y', 'width', 'height']) near(actual.metrics[key][property], reference.metrics[key][property], `${key}.${property}`);
 }
 for (const key of Object.keys(actual.metrics)) {
  for (const property of ['font', 'lineHeight', 'color', 'padding', 'background', 'mask', 'maskSize', 'objectFit']) assert.equal(actual.metrics[key][property], reference.metrics[key][property], `${key}.${property}`);
 }
 near(actual.metrics.text.y, reference.metrics.text.y, 'text.y');
 near(actual.metrics.text.height, reference.metrics.text.height, 'two-line text.height');
 if (viewport.width < 768) near(actual.metrics.text.x + actual.metrics.text.width / 2, reference.metrics.text.x + reference.metrics.text.width / 2, 'text.center');
 else near(actual.metrics.text.x, reference.metrics.text.x, 'text.left');
 assert(actual.metrics.text.x >= 0 && actual.metrics.text.x + actual.metrics.text.width <= actual.metrics.hero.width + .1, 'text clips horizontally');
 assert(actual.documentWidth <= actual.viewportWidth, 'horizontal overflow');
}
(async () => {
 const results = [], references = [], errors = [];
 const write = () => fs.writeFileSync(path.join(output, 'verification.json'), JSON.stringify({origin, baselineCommit, references, checked: results.length, passed: results.filter(r => r.passed).length, errors, results}, null, 2));
 for (const [engine, launch] of [['Chrome', () => chromium.launch({channel: 'chrome', headless: true})], ['WebKit', () => webkit.launch({headless: true})]].filter(([engine]) => !process.env.BANNER_ENGINES || process.env.BANNER_ENGINES.split(',').includes(engine))) {
  for (const viewport of sizes) {
   const browser = await launch();
   const context = await browser.newContext({viewport, isMobile: viewport.width < 768, hasTouch: viewport.width < 768});
   try {
    const baseline = await context.newPage();
    await baseline.route('**/assets/css/aircon-hero.css*', r => r.fulfill({status: 200, contentType: 'text/css', body: baselineCss}));
    await baseline.goto(`${origin}/house-cleaning/aircon/`, {waitUntil: 'load'}); await settle(baseline);
    const reference = await read(baseline); references.push({engine, viewport, ...reference}); await baseline.close();
    for (const route of routes) {
     const page = await context.newPage(); page.setDefaultTimeout(15000);
     const result = {engine, viewport, route, passed: false};
     const runtime = []; page.on('pageerror', e => runtime.push(e.message));
     try {
      const response = await page.goto(`${origin}/house-cleaning/${route}/`, {waitUntil: 'load'}); assert.equal(response.status(), 200);
      await settle(page); const actual = await read(page); Object.assign(result, actual); compare(actual, reference, viewport);
      assert.deepEqual(actual.lines, banners[route].lines); assert.equal(actual.heading, catalogue.pages[route].title);
      assert.equal(actual.image.src, `/assets/images/service-scenes/${banners[route].scene}.webp`); assert.equal(actual.image.alt, banners[route].alt);
      assert.equal(actual.metrics.image.objectPosition, (banners[route].position || 'right 40%').replace('right', '100%'));
      assert.deepEqual([actual.image.width, actual.image.height], [1536, 1024]); assert.equal(actual.checkText, reference.checkText); assert.deepEqual(runtime, []);
      if (screenshotRoutes.includes('all') || screenshotRoutes.includes(route)) {
       const clip = {x: 0, y: 0, width: actual.metrics.hero.width, height: Math.ceil(actual.metrics.hero.y + actual.metrics.hero.height)};
       const file = `${engine}-${viewport.width}x${viewport.height}-${route.replaceAll('/', '-')}.png`;
       await page.screenshot({path: path.join(output, file), clip}); result.screenshot = file;
      }
      result.passed = true;
     } catch (e) {result.error = e.message; errors.push({engine, viewport, route, error: e.message});}
     finally {await page.close(); results.push(result); write();}
    }
   } finally {await browser.close();}
  }
 }
 write(); console.log(JSON.stringify({checked: results.length, passed: results.filter(r => r.passed).length, errors})); process.exitCode = errors.length ? 1 : 0;
})();
