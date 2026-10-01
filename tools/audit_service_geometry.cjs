const fs = require('fs');
const path = require('path');
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright');

const root = path.resolve(__dirname, '..');
const catalogue = JSON.parse(fs.readFileSync(path.join(root, 'source/service-pages/catalogue.json'), 'utf8'));
const origin = process.env.SITE_ORIGIN || 'http://127.0.0.1:8769';
const out = process.env.GEOMETRY_REPORT || path.join(root, 'source/service-geometry-verification.json');
const widths = [390, 1581];

(async () => {
  const browser = await chromium.launch({ headless: true, channel: 'chrome' });
  const page = await browser.newPage();
  const records = [];
  const failures = [];
  for (const route of Object.keys(catalogue.pages)) {
    for (const width of widths) {
      try {
        await page.setViewportSize({ width, height: width > 800 ? 900 : 844 });
        const response = await page.goto(`${origin}/house-cleaning/${route}/`, { waitUntil: 'load' });
        if (!response || response.status() !== 200) throw new Error(`HTTP ${response?.status()}`);
        await page.evaluate(() => document.fonts.ready);
        const measurement = await page.evaluate(() => {
          const rect = n => {
            if (!n) return null;
            const r = n.getBoundingClientRect();
            return { x: Math.round(r.x), y: Math.round(r.y), width: Math.round(r.width), height: Math.round(r.height), right: Math.round(r.right), bottom: Math.round(r.bottom) };
          };
          const products = [...document.querySelectorAll('main .c-lineup-product')].map((p, index) => {
            const card = p.querySelector('.c-lineup-card');
            const image = card?.querySelector('.c-lineup-card__image');
            const contents = card?.querySelector('.c-lineup-card__contents');
            const footer = card?.querySelector('.c-lineup-card__foot');
            const cta = footer?.querySelector('.c-button');
            const quantity = footer?.querySelector('.js-product-quantity');
            const option = p.querySelector('.c-lineup-options__accordion-trigger');
            const optionBox = p.querySelector('.c-lineup-options');
            return {
              index, id: p.id, heading: card?.querySelector('.c-lineup-card__heading')?.textContent.trim(),
              card: rect(card), image: rect(image), contents: rect(contents), footer: rect(footer),
              cta: rect(cta), quantity: rect(quantity), option: rect(option),
              gapCardOption: optionBox ? Math.round(optionBox.getBoundingClientRect().top - card.getBoundingClientRect().bottom) : null,
              photoRatio: image ? Number((image.getBoundingClientRect().width / image.getBoundingClientRect().height).toFixed(3)) : null,
              optionCards: [...p.querySelectorAll('.c-product-additional-card')].map(rect),
              ctaClass: cta?.className || null
            };
          });
          const concerns = [...document.querySelectorAll('main .c-issue-card__text')].map(n => ({
            text: n.textContent, breaks: n.querySelectorAll('br').length,
            renderedLines: Number((n.getBoundingClientRect().height / parseFloat(getComputedStyle(n).lineHeight)).toFixed(2))
          }));
          const voiceCard = document.querySelector('main .c-voice-card');
          const voiceSection = voiceCard?.closest('section');
          const voice = voiceCard ? {
            count: voiceSection.querySelectorAll('.c-voice-card').length,
            heading: voiceSection.querySelector('h2')?.textContent.trim(),
            subtitleCount: voiceSection.querySelectorAll('.mt20').length,
            logo: getComputedStyle(voiceCard, '::before').backgroundImage,
            rightMark: getComputedStyle(voiceCard, '::after').display,
            mobileHeadingPadding: parseFloat(getComputedStyle(voiceCard.querySelector('h3')).paddingTop)
          } : null;
          return { viewport: innerWidth, scrollWidth: document.documentElement.scrollWidth,
            footerCopyrights: document.querySelectorAll('.c-footer-bottom-nav__copyright,.business-footer__copyright').length,
            concerns, voice, products };
        });
        const options = page.locator('.c-lineup-options__accordion-trigger');
        for (let i = 0; i < await options.count(); i++) {
          const option = options.nth(i);
          if (await option.isVisible() && await option.getAttribute('aria-expanded') !== 'true') {
            await option.click();
            await page.waitForFunction(index => document.querySelectorAll('.c-lineup-options__accordion-trigger')[index].getAttribute('aria-expanded') === 'true', i);
          }
        }
        measurement.optionCards = await page.evaluate(() => [...document.querySelectorAll('main .c-product-additional-card')]
          .filter(card => card.getBoundingClientRect().width > 0)
          .map(card => {
            const description = card.querySelector('.c-product-additional-card__description,.c-additional-option-card__description');
            const range = document.createRange();
            if (description) range.selectNodeContents(description);
            const lineRects = [...range.getClientRects()].filter(r => r.width > 0 && r.height > 0);
            const lines = new Set(lineRects.map(r => Math.round(r.top)));
            const box = card.getBoundingClientRect();
            const foot = card.querySelector('.c-product-additional-card__footer')?.getBoundingClientRect();
            return { id: card.querySelector('input[name="product-id"]')?.value,
              text: description?.textContent.trim(),
              className: description?.className,
              br: description?.querySelectorAll('br').length || 0,
              lines: lines.size,
              descriptionHeight: Math.round(description?.getBoundingClientRect().height || 0),
              width: Math.round(box.width), height: Math.round(box.height),
              footerTop: foot ? Math.round(foot.top) : null };
          }));
        if (measurement.scrollWidth > width + 1) failures.push({ route, width, error: 'horizontal overflow' });
        if (measurement.footerCopyrights) failures.push({ route, width, error: 'footer site name' });
        if (measurement.concerns.length !== 3 || measurement.concerns.some(c => c.breaks !== 1 || c.renderedLines !== 2 || !c.text.endsWith('...')))
          failures.push({ route, width, error: 'concern formatting' });
        if (!measurement.voice || measurement.voice.count !== 6 || measurement.voice.heading !== 'ご利用者様の声'
          || measurement.voice.subtitleCount || !measurement.voice.logo.includes('crystal-clean-home.png')
          || measurement.voice.rightMark !== 'none' || (width === 390 && measurement.voice.mobileHeadingPadding < 28))
          failures.push({ route, width, error: 'voice layout' });
        if ([390, 1581].includes(width) && measurement.optionCards.some(c => c.lines !== 3 || c.br))
          failures.push({ route, width, error: 'option description lines' });
        if (measurement.products.some(p => p.cta && p.cta.width !== (width === 390 ? 188 : 369)))
          failures.push({ route, width, error: 'CTA width' });
        if (width === 1581 && measurement.products.some(p => p.card.height < 482))
          failures.push({ route, width, error: 'product card height' });
        records.push({ route, width, ...measurement });
      } catch (error) {
        failures.push({ route, width, error: error.message });
      }
    }
  }
  await browser.close();
  const report = {
    origin,
    checkedAt: new Date().toISOString(),
    pages: Object.keys(catalogue.pages).length,
    viewportWidths: widths,
    viewportRuns: records.length,
    productCards: records.reduce((n, r) => n + r.products.length, 0),
    optionCards: records.reduce((n, r) => n + r.optionCards.length, 0),
    concernCards: records.reduce((n, r) => n + r.concerns.length, 0),
    voiceCards: records.reduce((n, r) => n + (r.voice?.count || 0), 0),
    failures,
    passed: failures.length === 0
  };
  fs.writeFileSync(out, JSON.stringify(report, null, 2) + '\n');
  console.log(JSON.stringify({ routes: Object.keys(catalogue.pages).length, widthRuns: records.length, cards: records.reduce((n,r) => n+r.products.length,0), failures }));
  process.exitCode = failures.length ? 1 : 0;
})().catch(error => { console.error(error); process.exitCode = 1; });
