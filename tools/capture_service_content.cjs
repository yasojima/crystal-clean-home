const fs = require('fs');
const path = require('path');
const assert = require('assert/strict');
const {chromium} = require(process.env.PLAYWRIGHT_MODULE || 'C:/Users/yasoj/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const sharp = require('C:/Users/yasoj/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/sharp');
const root = path.resolve(__dirname, '..');
const origin = process.argv[2] || 'http://127.0.0.1:8769';
const output = process.argv[3] || 'evidence/2026-10-04/local/service-content';
const assets = JSON.parse(fs.readFileSync(path.join(root, 'source/service-pages/scene-assets.json'), 'utf8'));
const balance = JSON.parse(fs.readFileSync(path.join(root, 'evidence/2026-10-04/local/service-content-balance.json'), 'utf8'));
const active = Object.entries(assets).filter(([, data]) => balance.photo_uses[data.asset]);
fs.mkdirSync(output, {recursive: true});

(async () => {
  const cells = [];
  for (let i = 0; i < active.length; i++) {
    const [name, data] = active[i];
    const photo = await sharp(path.join(root, 'source/site', data.asset)).resize(216, 140, {fit: 'inside', background: '#fff'}).toBuffer();
    const label = Buffer.from(`<svg width="232" height="32"><text x="8" y="23" font-family="Arial" font-size="13">${name}</text></svg>`);
    const cell = await sharp({create: {width: 232, height: 184, channels: 3, background: '#fff'}}).composite([{input: photo, top: 8, left: 8}, {input: label, top: 148, left: 0}]).png().toBuffer();
    cells.push({input: cell, top: Math.floor(i / 5) * 196 + 12, left: i % 5 * 244 + 12});
  }
  await sharp({create: {width: 1232, height: Math.ceil(active.length / 5) * 196 + 12, channels: 3, background: '#eee'}}).composite(cells).png().toFile(path.join(output, 'active-service-photo-inventory.png'));
  const browser = await chromium.launch({channel: 'chrome', headless: true});
  const records = [];
  try {
    for (const width of [414, 1440]) {
      const page = await browser.newPage({viewport: {width, height: width === 414 ? 688 : 900}, isMobile: width === 414, hasTouch: width === 414});
      for (const route of ['washer/side', 'water/ulblo', 'room/wallpaper-dyeing', 'pack', 'kitchen', 'room', 'coating']) {
        const response = await page.goto(`${origin}/house-cleaning/${route}/`, {waitUntil: 'load'});
        assert.equal(response.status(), 200);
        await page.evaluate(async () => {
          await document.fonts.ready;
          const imgs = [...document.querySelectorAll('main img')];
          imgs.forEach(img => img.loading = 'eager');
          await Promise.all(imgs.map(img => img.decode()));
        });
        const sections = route.includes('/') ? [['photo', '#service-introduction'], ['voices', '.c-voice-section--bubble-preview']] : [['voices', '.c-voice-section--bubble-preview']];
        for (const [name, selector] of sections) {
          const file = path.join(output, `${route.replaceAll('/', '-')}-${name}-${width}.png`);
          await page.locator(selector).screenshot({path: file, style: '.c-header, #js-floating, #viewport-hud {visibility: hidden !important;}'});
          records.push({route, width, name, file});
        }
      }
      await page.close();
    }
  } finally {
    await browser.close();
  }
  fs.writeFileSync(path.join(output, 'service-content-screens.json'), JSON.stringify({checked_at: new Date().toISOString(), origin, photo_assets: active.length, records}, null, 2) + '\n');
  console.log(JSON.stringify({origin, photo_assets: active.length, screens: records.length}));
})().catch(error => {console.error(error); process.exitCode = 1;});
