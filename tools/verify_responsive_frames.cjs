const fs = require('fs');
const path = require('path');
const assert = require('assert/strict');
const { chromium, webkit } = require(process.env.PLAYWRIGHT_MODULE || 'C:/Users/yasoj/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const root = path.resolve(__dirname, '..');
const catalogue = JSON.parse(fs.readFileSync(path.join(root, 'source/service-pages/catalogue.json'), 'utf8'));
const origin = process.argv[2] || 'http://127.0.0.1:8769';
const output = path.resolve(process.argv[3] || 'evidence/2026-10-04/responsive-frames/local');
const routes = process.env.FRAME_ROUTES === 'all' ? Object.keys(catalogue.pages) : (process.env.FRAME_ROUTES || 'aircon,pack,water,washer,kitchen,room,coating,others').split(',');
const sizes = (process.env.FRAME_SIZES || '1024x600,1280x551,1366x650,1440x800,1920x1080,320x568,375x667,390x844,414x688,414x832,430x932,768x1024,1440x1973').split(',').map(s => s.split('x').map(Number));
const engine = process.env.FRAME_ENGINE || 'chrome';
const screenshotRoutes = (process.env.FRAME_SCREENSHOTS || 'pack').split(',');
const checks = [];

(async () => {
  fs.mkdirSync(output, { recursive: true });
  const browser = await (engine === 'webkit' ? webkit : chromium).launch(engine === 'webkit' ? {} : { channel: 'chrome', headless: true });
  try {
    const page = await browser.newPage();
    page.setDefaultTimeout(20000);
    for (const [width, height] of sizes) {
      await page.setViewportSize({ width, height });
      for (const route of routes) {
        assert(catalogue.pages[route], `Unknown service route: ${route}`);
        await page.goto(`${origin}/house-cleaning/${route}/`, { waitUntil: 'load' });
        await page.evaluate(async () => {
          await document.fonts.ready;
          const images = [...document.querySelectorAll('main img')];
          await Promise.all(images.map(img => { img.loading = 'eager'; return img.decode().catch(() => {}); }));
        });
        const measurement = await page.evaluate(() => {
          const visible = n => n.getBoundingClientRect().width > 0 && n.getBoundingClientRect().height > 0 && !n.closest('[hidden]');
          const rect = n => { const r = n.getBoundingClientRect(); return { x: r.x, y: r.y, width: r.width, height: r.height }; };
          const issues = [];
          const sections = {};
          for (const selector of ['.c-header', '.c-first-view', '.c-house-cleaning-mv', '.c-house-cleaning-mv__image', '.c-house-cleaning-mv__text', '.c-service-selector', '.c-issue-list', '.c-compare-image-tab__compare-image', '.c-reasons', '.c-lineup-card', '.recommend-plan-cards', '.c-voice-bubbles', '.c-faq-accordion', '.c-howto', '.c-house-cleaning-links', '.c-footer--aircon']) {
            const n = document.querySelector(selector);
            if (n) sections[selector] = rect(n);
          }
          const textSelector = '.c-house-cleaning-mv__text,.c-category-simple-card__text,.c-issue-card__text,.c-tab__button,.c-reason-card__heading,.c-reason-card__description,.c-lineup-card__heading,.c-lineup-card__description,.c-lineup-card__price,.c-bracket-heading__text,.c-plan-card__heading,.c-plan-card__description,.c-plan-card-detail__option,.c-plan-card-list-item__body,.c-voice-card__text,.c-howto__heading,.c-howto__description';
          for (const n of [...document.querySelectorAll(textSelector)].filter(visible)) {
            const r = n.getBoundingClientRect(), range = document.createRange();
            range.selectNodeContents(n);
            if ([...range.getClientRects()].some(t => t.width > 0 && (t.left < r.left - 2 || t.right > r.right + 2))) issues.push({ type: 'text-overflow', selector: n.className, text: n.textContent.trim().slice(0, 120), rect: rect(n) });
          }
          const images = [...document.querySelectorAll('main img')].filter(visible);
          for (const img of images) if (!img.complete || !img.naturalWidth) issues.push({ type: 'image-unloaded', src: img.getAttribute('src') });
          const photo = sections['.c-house-cleaning-mv__image'];
          if (!photo || photo.height < 100) issues.push({ type: 'hero-photo-collapsed', photo });
          const hero = sections['.c-house-cleaning-mv'], text = sections['.c-house-cleaning-mv__text'];
          if (text && (text.y < hero.y - 1 || text.y + text.height > hero.y + hero.height - 30)) issues.push({ type: 'hero-copy-outside', hero, text });
          const heroText = document.querySelector('.c-house-cleaning-mv__text');
          if (text && text.height > parseFloat(getComputedStyle(heroText).lineHeight) * 2 + 1) issues.push({ type: 'hero-copy-exceeds-two-lines', text: heroText.textContent.trim() });
          if (document.documentElement.scrollWidth > innerWidth + 1) issues.push({ type: 'page-horizontal-overflow', width: document.documentElement.scrollWidth });
          return { sections, issues, imageCount: images.length };
        });
        const slug = route.replaceAll('/', '-');
        if (screenshotRoutes.includes(route)) await page.screenshot({ path: path.join(output, `${width}x${height}-${slug}-top.png`) });
        await page.evaluate(() => scrollTo({ top: document.documentElement.scrollHeight, behavior: 'instant' }));
        await page.waitForTimeout(220);
        measurement.footer = await page.locator('.c-footer--aircon').evaluate(n => {
          const r = n.getBoundingClientRect();
          const header = document.querySelector('.c-header').getBoundingClientRect();
          const bottom = n.querySelector('.c-footer__bottom-nav').getBoundingClientRect();
          const support = n.querySelector('.c-aircon-footer__support-start');
          return { top: r.top, height: r.height, bottom: bottom.bottom, headerHeight: header.height, fitsBelowHeader: r.height <= innerHeight - header.height + 1, fitsViewport: r.height <= innerHeight + 1, supportGap: support.getBoundingClientRect().top - support.previousElementSibling.getBoundingClientRect().bottom };
        });
        if (screenshotRoutes.includes(route)) await page.screenshot({ path: path.join(output, `${width}x${height}-${slug}-footer.png`) });
        if (width >= 1024 && [[1024,600],[1280,551],[1366,650],[1440,800],[1920,1080]].some(([w,h]) => w === width && h === height) && !measurement.footer.fitsBelowHeader) measurement.issues.push({ type: 'desktop-footer-exceeds-frame', ...measurement.footer });
        if (width >= 1200 && height > 1100 && measurement.footer.height > 1100 - measurement.footer.headerHeight + 1) measurement.issues.push({ type: 'footer-overstretched', ...measurement.footer });
        if (width < 768 && measurement.footer.height > Math.min(height, 1100) + 1 && height >= 688) measurement.issues.push({ type: 'mobile-footer-overstretched', ...measurement.footer });
        if (measurement.footer.bottom > height + 1) measurement.issues.push({ type: 'footer-bottom-clipped' });
        checks.push({ route, width, height, ...measurement });
        if (measurement.issues.length) console.log(JSON.stringify({ route, width, height, issues: measurement.issues }));
      }
      console.log(`${engine}: ${width}x${height}: ${routes.length} pages checked`);
      fs.writeFileSync(path.join(output, 'verification.json'), JSON.stringify({ checkedAt: new Date().toISOString(), origin, engine, passed: checks.every(c => !c.issues.length), checks }, null, 2));
    }
  } finally { await browser.close(); }
  const failures = checks.filter(c => c.issues.length);
  console.log(JSON.stringify({ total: checks.length, failures: failures.length }));
  if (failures.length && process.env.FRAME_INSPECT !== '1') process.exitCode = 1;
})().catch(error => { console.error(error); process.exitCode = 1; });
