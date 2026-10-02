const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright');

const origin = process.env.SITE_ORIGIN || 'http://127.0.0.1:8769';
const widths = [320, 390, 600, 768, 1024, 1200, 1366, 1440, 1441, 1581, 1680, 1920];

async function inspect(channel) {
  const browser = await chromium.launch({ headless: true, channel });
  const results = [];
  try {
    const page = await browser.newPage();
    for (const width of widths) {
      const height = ({ 320: 700, 1024: 768, 1441: 799, 1581: 1326 })[width] || (width < 768 ? 844 : 801);
      await page.setViewportSize({ width, height });
      const response = await page.goto(`${origin}/house-cleaning/aircon/`, { waitUntil: 'load' });
      assert.equal(response.status(), 200, `${channel} ${width}: page response`);
      await page.evaluate(() => document.fonts.ready);
      assert.equal(await page.locator('main h1').count(), 1, `${channel} ${width}: one page heading`);
      assert.equal(await page.locator('main h1').innerText(), 'エアコンクリーニング');
      assert.equal(await page.locator('#js-floating a').getAttribute('href'), '/cart/');

      const first = await page.evaluate(() => {
        const cart = document.querySelector('#js-floating');
        const box = cart.getBoundingClientRect();
        const heading = document.querySelector('main h1').getBoundingClientRect();
        return { cartClass: cart.className, cartX: box.x, cartY: box.y,
          headingW: heading.width, scrollWidth: document.documentElement.scrollWidth,
          clientWidth: document.documentElement.clientWidth };
      });
      assert.equal(first.headingW, 1, `${channel} ${width}: visually hidden heading`);
      assert.ok(first.scrollWidth <= width + 1, `${channel} ${width}: no horizontal overflow`);
      assert.ok(!first.cartClass.includes('is-visible'), `${channel} ${width}: cart hidden in first view`);

      await page.locator('#service-flow').scrollIntoViewIfNeeded();
      await page.waitForTimeout(700);
      const flow = await page.evaluate(() => {
        const cart = document.querySelector('#js-floating');
        const c = cart.getBoundingClientRect();
        const h = document.querySelector('.c-howto-container').getBoundingClientRect();
        const items = [...document.querySelectorAll('.c-howto__item')].map(item => {
          const r = item.getBoundingClientRect();
          return { x: r.x, right: r.right };
        });
        return { cartClass: cart.className, cartX: c.x, cartY: c.y, cartRight: c.right,
          cartBottom: c.bottom, flowRight: h.right, items,
          scrollWidth: document.documentElement.scrollWidth,
          clientWidth: document.documentElement.clientWidth };
      });
      assert.ok(flow.cartClass.includes('is-visible'), `${channel} ${width}: cart follows content`);
      assert.ok(flow.scrollWidth <= width + 1, `${channel} ${width}: no flow overflow`);
      if (process.env.SCREENSHOT_DIR && [390, 768, 1200, 1440].includes(width)) {
        fs.mkdirSync(process.env.SCREENSHOT_DIR, { recursive: true });
        await page.screenshot({ path: path.join(process.env.SCREENSHOT_DIR, `${channel}-flow-${width}.png`) });
      }
      if (width >= 768) {
        assert.ok(flow.cartRight <= flow.clientWidth + 1, `${channel} ${width}: cart at right edge`);
        assert.ok(flow.items.every(item => item.right <= flow.cartX - 8),
          `${channel} ${width}: flow must clear cart ${JSON.stringify(flow)}`);
      } else {
        assert.ok(flow.cartX >= -1 && flow.cartRight <= width + 1,
          `${channel} ${width}: mobile cart spans viewport`);
        assert.ok(Math.abs(flow.cartBottom - height) <= 2,
          `${channel} ${width}: mobile cart stays on bottom edge`);
      }

      await page.locator('#footer').scrollIntoViewIfNeeded();
      await page.waitForTimeout(700);
      const footer = await page.evaluate(() => {
        const cart = document.querySelector('#js-floating');
        const c = cart.getBoundingClientRect();
        return { className: cart.className, x: c.x, y: c.y,
          clientWidth: document.documentElement.clientWidth };
      });
      assert.ok(footer.className.includes('is-footer-area'), `${channel} ${width}: footer hides cart`);
      assert.ok(width >= 768 ? footer.x >= width - 16 : footer.y >= height - 1,
        `${channel} ${width}: cart fully exits viewport at footer ${JSON.stringify(footer)}`);
      results.push({ width, flow, footer });
    }
  } finally {
    await browser.close();
  }
  return { channel, widths: results.map(result => result.width),
    desktopFlowGap: results.filter(result => result.width >= 768)
      .map(result => ({ width: result.width, gap: Math.round(result.flow.cartX - result.flow.flowRight) })) };
}

(async () => {
  const channels = process.argv.slice(2);
  const results = [];
  for (const channel of channels.length ? channels : ['chrome']) results.push(await inspect(channel));
  console.log(JSON.stringify(results, null, 2));
})().catch(error => { console.error(error); process.exitCode = 1; });
