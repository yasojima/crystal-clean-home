const fs = require('fs');
const path = require('path');
const assert = require('assert/strict');
const {execFileSync} = require('child_process');
const {chromium} = require('C:/Users/yasoj/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const root = path.resolve(__dirname, '..');
const origin = process.argv[2] || 'http://127.0.0.1:8773';
const publicMode = origin.startsWith('https:');
const out = path.join(root, 'evidence/2026-10-09/lp-complement', publicMode ? 'public' : 'local');
const original = execFileSync('git', ['show', 'ca2541a:source/site/assets/css/beginner-lp.css'], {cwd:root});
const originalHtml = execFileSync('git', ['show', 'ca2541a:source/site/beginner/index.html'], {cwd:root});
const sizes = [[1920,1080],[1442,1646],[1442,804],[1440,800],[1280,551],[1280,900],[1024,600],[993,800],[992,700],[768,800],[767,800],[600,800],[414,688],[390,844],[375,667],[320,568]];
async function settle(page) {
  await page.evaluate(async () => {
    await document.fonts.ready;
    await Promise.all([...document.querySelectorAll('#cch-first-lp img')].map(img => {
      img.loading = 'eager';
      return img.decode().catch(() => {});
    }));
    await new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)));
  });
}
async function metrics(page) {
  return page.evaluate(() => {
    const root = document.getElementById('cch-first-lp');
    const canvas = root.querySelector('.lp-canvas');
    const rect = e => { const r = e.getBoundingClientRect(); return {x:r.x, width:r.width, height:r.height}; };
    const s = getComputedStyle(root);
    const ctAs = [...canvas.querySelectorAll('.lp-estimate-button')].map(e => ({
      href:e.getAttribute('href'), ...rect(e),
      clipped:e.querySelector('.btn-free').scrollWidth > e.querySelector('.btn-free').clientWidth + 1
    }));
    const nodes = [...canvas.querySelectorAll('section,.lp-estimate-button,.lp-opening-actions,.lp-cta-action,.lp-services,.lp-voices')].map(e => {
      const c = getComputedStyle(e);
      return [e.id || e.className, ...Object.values(rect(e)), c.paddingTop, c.paddingBottom, c.fontSize];
    });
    return {
      width:innerWidth, height:innerHeight, root:rect(root), canvas:rect(canvas), ctAs, nodes,
      background:{image:s.backgroundImage, color:s.backgroundColor, size:s.backgroundSize},
      openingMask:getComputedStyle(root.querySelector('h1 > img')).maskImage,
      originalOpacity:getComputedStyle(root.querySelector('h1 > img')).opacity,
      openingPlate:(() => {
        const opening=root.querySelector('.lp-opening-portrait');
        const pseudo=getComputedStyle(opening,'::before');
        const or=opening.getBoundingClientRect(), cr=root.querySelector('#first-cases').getBoundingClientRect();
        const plateWidth=parseFloat(pseudo.backgroundSize), plateHeight=plateWidth*1544/1019;
        return {image:pseudo.backgroundImage,width:parseFloat(pseudo.width),plateWidth,plateHeight,compareTop:(cr.top-or.top)/plateHeight,compareBottom:(cr.bottom-or.top)/plateHeight};
      })(),
      nativeImages:[...root.querySelectorAll('img')].map(e => {const r=e.getBoundingClientRect();return {src:e.getAttribute('src'),x:r.x,y:r.y+scrollY,width:r.width,height:r.height};}),
      overflow:document.documentElement.scrollWidth - document.documentElement.clientWidth
    };
  });
}
(async () => {
  fs.mkdirSync(out, {recursive:true});
  const browser = await chromium.launch({channel:'chrome', headless:true});
  const page = await browser.newPage();
  const errors = [];
  const failedResponses = [];
  page.on('pageerror', e => errors.push(e.message));
  page.on('response', r => { if (r.status() >= 400 && new URL(r.url()).origin === new URL(origin).origin) failedResponses.push({url:r.url(), status:r.status()}); });
  let useOriginal = false;
  await page.route('**/beginner/**', r => useOriginal ? r.fulfill({body:originalHtml, contentType:'text/html'}) : r.continue());
  await page.route('**/assets/css/beginner-lp.css*', r => useOriginal ? r.fulfill({body:original, contentType:'text/css'}) : r.continue());
  const records = [];
  const geometryPreservation = [];
  try {
    await page.goto(origin + '/beginner/?lp_width=2026100907', {waitUntil:'load'});
    await page.evaluate(async () => {
      for (const img of document.querySelectorAll('#cch-first-lp img')) {
        img.loading = 'eager';
        await img.decode().catch(() => {});
      }
      const bg = new Image();
      bg.src = '/assets/images/first-lp/art/opening-wide.png';
      await bg.decode();
    });
    for (const [width,height] of [...sizes, ...[...sizes].reverse()]) {
      await page.setViewportSize({width,height});
      await settle(page);
      const current = await metrics(page);
      const pc = width >= 768;
      const expected = pc ? Math.min(1120, current.root.width - 48) : current.root.width;
      assert(Math.abs(current.canvas.width - expected) <= 1, width + 'x' + height + ': content width');
      assert(Math.abs(current.canvas.x - current.root.x - (current.root.width - current.canvas.width)/2) <= 1, width + ': centered content');
      assert(current.overflow <= 1, width + ': page overflow');
      assert.equal(current.ctAs.length, 6);
      for (const cta of current.ctAs) {
        assert.equal(cta.href, '/quick_cart/');
        assert(cta.height >= 44 && !cta.clipped, width + ': CTA usable');
        assert(cta.x >= current.canvas.x - 1 && cta.x + cta.width <= current.canvas.x + current.canvas.width + 1, width + ': CTA within content');
      }
      if (pc) {
        assert.equal(current.background.image, 'none');
        assert.equal(current.openingMask, 'none');
        assert.equal(current.originalOpacity, '0');
        assert(current.openingPlate.image.includes('opening-wide.png'));
        assert(current.openingPlate.width >= current.root.width);
        assert(current.openingPlate.plateWidth >= current.root.width, width + ': single artwork covers full width');
        assert(current.openingPlate.compareTop >= .505 && current.openingPlate.compareBottom <= .739, width + ': comparison must fit between headline and offer');
      } else {
        assert.equal(current.background.image, 'none');
        assert.equal(current.openingMask, 'none');
        assert.equal(current.originalOpacity, '1');
        assert.equal(current.openingPlate.image, 'none');
      }
      delete current.nodes;
      records.push(current);
    }
    const short = records.find(r => r.width === 1280 && r.height === 551);
    const tall = records.find(r => r.width === 1280 && r.height === 900);
    assert.deepEqual(short.canvas, tall.canvas, 'height must not narrow the content');
    console.log(JSON.stringify({origin, layoutConditions:records.length, passed:true}));
    if (!publicMode) {
      for (const [width,height] of sizes) {
        await page.setViewportSize({width,height});
        await settle(page);
        const after = await metrics(page);
        useOriginal = true;
        await page.reload({waitUntil:'load'});
        await settle(page);
        const before = await metrics(page);
        assert.deepEqual(after.canvas, before.canvas, width + ': content changed');
        assert.deepEqual(after.nodes, before.nodes, width + ': sections changed');
        assert.deepEqual(after.ctAs, before.ctAs, width + ': CTAs changed');
        assert.equal(after.nativeImages.length,before.nativeImages.length);
        for(let i=0;i<before.nativeImages.length;i++){assert.equal(after.nativeImages[i].src,before.nativeImages[i].src);for(const key of ['x','y','width','height'])assert(Math.abs(after.nativeImages[i][key]-before.nativeImages[i][key])<.1,width+': original image '+i+' '+key+' moved or stretched');}
        geometryPreservation.push({width,height,unchanged:true});
        useOriginal = false;
        await page.reload({waitUntil:'load'});
        await settle(page);
      }
    }
    const interactions = [];
    for (const [width,height] of [[1442,804],[768,800],[414,688],[320,568]]) {
      await page.setViewportSize({width,height});
      await page.goto(origin + '/beginner/', {waitUntil:'load'});
      const firstTab = page.locator('#lp-case-tab-0');
      const secondTab = page.locator('#lp-case-tab-1');
      await secondTab.click();
      assert.equal(await secondTab.getAttribute('aria-selected'), 'true');
      assert(await page.locator('#lp-case-panel-1').isVisible());
      await secondTab.press('ArrowLeft');
      assert.equal(await firstTab.getAttribute('aria-selected'), 'true');
      assert(await page.locator('#lp-case-panel-0').isVisible());
      const slider = page.locator('#lp-case-panel-0 [role="slider"]');
      await slider.press('End');
      await page.waitForFunction(() => document.querySelector('#lp-case-panel-0 [role="slider"]').getAttribute('aria-valuenow') === '100');
      await slider.press('Home');
      await page.waitForFunction(() => document.querySelector('#lp-case-panel-0 [role="slider"]').getAttribute('aria-valuenow') === '0');
      await slider.press('ArrowRight');
      await page.waitForFunction(() => document.querySelector('#lp-case-panel-0 [role="slider"]').getAttribute('aria-valuenow') === '5');
      const faq = page.locator('#first-faq details').first();
      await faq.locator('summary').click();
      assert(await faq.evaluate(e => e.open));
      await faq.locator('summary').click();
      assert(!(await faq.evaluate(e => e.open)));
      await page.locator('.lp-estimate-button').first().focus();
      await Promise.all([page.waitForURL('**/quick_cart/'), page.keyboard.press('Enter')]);
      interactions.push({width,height,tabs:true,comparisonKeyboard:true,faq:true,estimateNavigation:true});
    }
    for (const [width,height,anchor,label] of [
      [1442,1646,'#first-introduction','opening-tall'],
      [1440,800,'#first-introduction','opening-1440'],
      [1440,800,'#first-comic','comic'],
      [1440,800,'#cleaning-approach','quality'],
      [1440,800,'#infection-prevention','hygiene-top'],
      [1440,800,'#infection-prevention@0.45','hygiene-middle'],
      [1920,1080,'#infection-prevention@0.45','hygiene-large'],
      [1440,800,'#first-concerns','concerns-top'],
      [1440,800,'#first-concerns@0.3','concerns-middle'],
      [1440,800,'#first-voices','voices'],
      [1440,800,'#first-faq','faq'],
      [1440,800,'.cta-final','final-top'],
      [1440,800,'.cta-final@0.4','final-middle'],
      [1280,551,'.cta-final@0.5','final-short'],
      [414,688,'#infection-prevention','hygiene-mobile'],
      [414,688,'#first-voices','voices-mobile'],
      [414,688,'.cta-final@0.3','final-mobile'],
      [320,568,'#infection-prevention','hygiene-small'],
      [1442,804,'#first-introduction','opening-1442'],
      [1280,551,'#first-introduction','opening-1280'],
      [414,688,'#first-introduction','opening-mobile'],
      [1442,804,'#first-cases','comparison-1442'],
      [768,800,'#first-introduction','opening-768'],
      [1442,1646,'@offer','offer-tall'],
      [768,800,'@offer','offer-768'],
      [768,800,'#first-services','services-768'],
      [414,688,'#first-faq','faq-mobile']
    ]) {
      await page.setViewportSize({width,height});
      await page.goto(origin + '/beginner/', {waitUntil:'load'});
      if (anchor === '@offer') {
        await page.locator('.lp-opening-portrait').evaluate(e => {
          const plateHeight = parseFloat(getComputedStyle(e, '::before').backgroundSize) * 1544 / 1019;
          scrollTo({top:e.getBoundingClientRect().top + scrollY + plateHeight * .715 - document.querySelector('header').offsetHeight, behavior:'instant'});
        });
      } else {
        const [selector,fraction='0']=anchor.split('@');
        await page.locator(selector).evaluate((e,f) => scrollTo({top:e.getBoundingClientRect().top + scrollY + e.offsetHeight*f - document.querySelector('header').offsetHeight, behavior:'instant'}),Number(fraction));
      }
      await settle(page);
      await page.screenshot({path:path.join(out, label + '.png')});
    }
    assert.equal(errors.length, 0, JSON.stringify(errors));
    assert.equal(failedResponses.length, 0, JSON.stringify(failedResponses));
    const report = {origin, baseline:'ca2541a', conditions:records.length, records, geometryPreservation, interactions, errors, failedResponses, passed:true};
    fs.writeFileSync(path.join(out,'report.json'), JSON.stringify(report,null,2) + '\n');
    console.log(JSON.stringify({origin,conditions:records.length,geometryPreservation:geometryPreservation.length,interactions:interactions.length,passed:true}));
  } finally { await browser.close(); }
})().catch(e => { console.error(e); process.exitCode = 1; });
