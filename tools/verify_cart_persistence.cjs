const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const http = require('node:http');
const {chromium, webkit} = require('C:/Users/yasoj/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const root = path.resolve(__dirname, '../source/site');
const out = path.resolve(__dirname, '../evidence/2026-10-05/cart-audit');
const engine = process.env.CART_ENGINE || 'chromium';
function pages(dir) { return fs.readdirSync(dir, {withFileTypes: true}).flatMap(e => e.isDirectory() ? pages(path.join(dir, e.name)) : e.name.endsWith('.html') ? [path.join(dir, e.name)] : []); }
const routes = pages(root).map(file => '/' + path.relative(root, file).replaceAll('\\', '/').replace(/index\.html$/, ''));
const fixture = [{key:'product:1',quantity:1},{key:'product:2',quantity:1},{key:'product:3',quantity:2},{key:'option:3:42',quantity:2}];

(async () => {
  const server = http.createServer((req, res) => {
    let file = path.join(root, decodeURIComponent(new URL(req.url, 'http://local').pathname));
    if (file.endsWith(path.sep)) file += 'index.html';
    try { res.setHeader('Content-Type', ({'.html':'text/html; charset=utf-8','.js':'text/javascript; charset=utf-8','.css':'text/css','.svg':'image/svg+xml'})[path.extname(file)] || 'application/octet-stream'); res.end(fs.readFileSync(file)); }
    catch { res.statusCode = 404; res.end(); }
  });
  if (!process.env.CART_BASE) await new Promise(r => server.listen(0, '127.0.0.1', r));
  const base = process.env.CART_BASE || 'http://127.0.0.1:' + server.address().port;
  const browser = await (engine === 'webkit' ? webkit : chromium).launch(engine === 'webkit' ? {} : {channel:'chrome'});
  const report = {engine, base, pages:[], edges:[], errors:[], passed:false};
  try {
    for (const width of [1439,390]) {
      const context = await browser.newContext({viewport:{width,height:900},isMobile:width<768,hasTouch:width<768});
      await context.route('**/*', route => ['image','font','media'].includes(route.request().resourceType()) ? route.abort() : route.continue());
      const page = await context.newPage();
      page.on('pageerror', e => report.errors.push(e.message));
      await page.goto(base+'/',{waitUntil:'domcontentloaded'});
      await page.evaluate(f => localStorage.setItem('cch-cart-v1',JSON.stringify({version:1,lines:f})),fixture);
      for (const route of routes) {
        await page.goto(base+route,{waitUntil:'domcontentloaded'});
        const result = await page.evaluate(() => ({...window.CCHCart.getSummary(), visibleTotals:[...document.querySelectorAll('#js-floating-total-quantity,.js-total-amount')].map(e=>Number(e.textContent.replace(/[^0-9]/g,'')))}));
        assert.equal(result.total,97900,route);
        assert.equal(result.count,6,route);
        assert(result.visibleTotals.every(total=>total===97900),route+' displayed total');
        report.pages.push({width,route,total:result.total,count:result.count});
      }
      await page.goto(base+'/cart/',{waitUntil:'domcontentloaded'});
      const second = await context.newPage();
      await second.goto(base+'/house-cleaning/aircon/',{waitUntil:'domcontentloaded'});
      await page.locator('[data-cart-set="product:1"]').fill('3');
      await page.locator('[data-cart-set="product:1"]').press('Tab');
      await second.waitForFunction(()=>document.querySelector('#js-floating-total-quantity').textContent==='119,900');
      assert.equal(await second.evaluate(()=>window.CCHCart.getSummary().total),119900);
      await page.locator('[data-cart-set="product:1"]').fill('1.5');
      await page.locator('[data-cart-set="product:1"]').press('Tab');
      assert.match(await page.locator('#cch-cart-dialog').textContent(),/整数/);
      assert.equal(await page.evaluate(()=>window.CCHCart.getSummary().total),119900);
      await page.locator('[data-cart-close]').click();
      await page.locator('[data-cart-remove="option:3:42"]').click();
      assert.equal(await page.evaluate(()=>window.CCHCart.getSummary().total),108900);
      await page.goto(base+'/quick_cart/aircon/',{waitUntil:'domcontentloaded'});
      await page.evaluate(()=>{const b=document.querySelector('.js-counter-button[data-type="increment"]');for(let i=0;i<10;i++)b.click();});
      assert.equal(await page.locator('.c-counter__input').first().inputValue(),'13');
      await page.goto(base+'/');
      await page.goBack({waitUntil:'domcontentloaded'});
      assert.equal(await page.locator('.c-counter__input').first().inputValue(),'13');
      report.edges.push({width,mixedTypes:true,crossTab:true,invalidQuantity:true,optionRemoval:true,rapidCounter:true,backNavigation:true});
      await context.close();
    }
    const bad = await browser.newContext();
    await bad.addInitScript(()=>{localStorage.setItem('cch-cart-v1','broken json');});
    const badPage=await bad.newPage();
    await badPage.goto(base+'/cart/',{waitUntil:'domcontentloaded'});
    assert.match(await badPage.locator('#cch-cart-dialog').textContent(),/読み込めません/);
    await bad.close();
    const denied=await browser.newContext();
    await denied.addInitScript(()=>{Storage.prototype.setItem=function(){throw new DOMException('QuotaExceededError','QuotaExceededError')};});
    const deniedPage=await denied.newPage();
    await deniedPage.goto(base+'/house-cleaning/aircon/',{waitUntil:'domcontentloaded'});
    await deniedPage.locator('.js-add-cart').first().click();
    assert.match(await deniedPage.locator('#cch-cart-dialog').textContent(),/保存できません/);
    assert.equal(await deniedPage.locator('#js-floating-total-quantity').textContent(),'0');
    await denied.close();
    report.edges.push({corruptStorage:true,storageFailure:true});
    assert.deepEqual(report.errors,[]);
    report.passed=true;
  } catch(error){report.errors.push(error.stack);console.error(error);process.exitCode=1;}
  finally {fs.writeFileSync(path.join(out,`${process.env.CART_BASE?'public':'local'}-${engine}-persistence.json`),JSON.stringify(report,null,2));await browser.close();server.close();}
  console.log(JSON.stringify({passed:report.passed,pages:report.pages.length,edges:report.edges,errors:report.errors}));
})();
