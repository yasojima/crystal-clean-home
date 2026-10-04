const fs = require('fs');
const path = require('path');
const assert = require('assert/strict');
const {chromium} = require('C:/Users/yasoj/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const origin = process.argv[2] || 'http://127.0.0.1:8769';
const out = path.resolve(process.argv[3] || 'evidence/2026-10-04/footer-height');

(async () => {
  fs.mkdirSync(out, {recursive: true});
  const browser = await chromium.launch({channel: 'chrome', headless: true});
  const page = await browser.newPage();
  const checks = [];
  try {
    for (const [width, height] of [[1440,800], [1440,1069], [1440,1973], [1280,1973], [1024,1973], [768,1973], [414,688], [414,832]]) {
      await page.setViewportSize({width, height});
      await page.goto(origin + '/house-cleaning/pack/', {waitUntil: 'load'});
      await page.evaluate(async () => {
        await document.fonts.ready;
        scrollTo({top: document.documentElement.scrollHeight, behavior: 'instant'});
      });
      await page.waitForTimeout(400);
      const measurement = await page.locator('.c-footer--aircon').evaluate(footer => {
        const rect = footer.getBoundingClientRect();
        const support = footer.querySelector('.c-aircon-footer__support-start');
        const previous = support?.previousElementSibling;
        return {
          width: innerWidth, height: innerHeight, footerHeight: rect.height, top: rect.top,
          minHeight: getComputedStyle(footer).minHeight,
          supportGap: support && previous ? support.getBoundingClientRect().top - previous.getBoundingClientRect().bottom : null,
          overflow: document.documentElement.scrollWidth > innerWidth + 1,
          navBottom: footer.querySelector('.c-footer__bottom-nav').getBoundingClientRect().bottom,
        };
      });
      assert(!measurement.overflow);
      assert(measurement.navBottom <= height + 1, 'footer bottom not visible');
      if (width >= 1200) {
        assert(measurement.footerHeight <= 800, 'desktop footer stretched beyond content');
        assert(measurement.supportGap < 200, 'support links separated by huge whitespace');
      }
      checks.push(measurement);
      console.log(JSON.stringify(measurement));
      if ([800,1973,688].includes(height)) await page.screenshot({path: path.join(out, `${width}x${height}.png`)});
    }
    assert(Math.abs(checks[0].footerHeight - checks[2].footerHeight) < 1, 'footer grows with tall window');
    fs.writeFileSync(path.join(out, 'verification.json'), JSON.stringify({checkedAt: new Date().toISOString(), origin, passed: true, checks}, null, 2));
  } finally {
    await browser.close();
  }
})().catch(error => {console.error(error); process.exitCode = 1;});
