const fs = require('fs');
const path = require('path');
const assert = require('assert/strict');
const {chromium, webkit} = require(process.env.PLAYWRIGHT_MODULE || 'C:/Users/yasoj/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const root = path.resolve(__dirname, '..');
const flow = JSON.parse(fs.readFileSync(path.join(root, 'source/service-pages/copy.json'), 'utf8')).categories.aircon.flow;
const origin = process.argv[2] || 'http://127.0.0.1:8769';
const output = process.argv[3] || 'evidence/2026-10-04/aircon-flow/local';
const sizes = [[1024,600],[1280,551],[1366,650],[1440,800],[1440,1010],[1689,800],[1690,800],[1920,1080],[768,1024],[600,800],[320,568],[375,667],[414,688],[430,932]];
fs.mkdirSync(output, {recursive:true});
(async () => {
  const checks = [];
  for (const [engine, launch] of [['Chrome', () => chromium.launch({channel:'chrome',headless:true})], ['WebKit', () => webkit.launch({headless:true})]]) {
    const browser = await launch();
    try {
      for (const [width,height] of sizes) {
        const context = await browser.newContext({viewport:{width,height},isMobile:width<768,hasTouch:width<768});
        const page = await context.newPage();
        const errors = [];
        page.on('pageerror', error => errors.push(error.message));
        const response = await page.goto(`${origin}/house-cleaning/aircon/#service-flow`, {waitUntil:'load'});
        assert.equal(response.status(),200);
        await page.evaluate(async () => { await document.fonts.ready; });
        const section = page.locator('#service-flow');
        await page.waitForTimeout(500);
        assert(await section.locator('h2').evaluate(node=>node.getBoundingClientRect().top>=document.querySelector('.c-header').getBoundingClientRect().bottom),'anchor hides heading behind header');
        const result = await section.evaluate(node => {
          const rect = n => {const r=n.getBoundingClientRect();return {left:r.left,right:r.right,top:r.top,bottom:r.bottom,width:r.width,height:r.height};};
          const lines = n => {
            const walker=document.createTreeWalker(n,NodeFilter.SHOW_TEXT),result=[];let text;
            while((text=walker.nextNode())){
              const range=document.createRange();range.selectNodeContents(text);
              result.push(...[...range.getClientRects()].filter(r=>r.height>0).map(r=>({left:r.left,right:r.right,top:r.top,bottom:r.bottom})));
            }
            return result;
          };
          const items=[...node.querySelectorAll('.c-howto__item')].map(n=>({rect:rect(n),icon:rect(n.querySelector('.c-howto__visual')),heading:n.querySelector('h3').textContent,description:n.querySelector('.c-howto__description').textContent,text:rect(n.querySelector('.c-howto__description')),lines:lines(n.querySelector('.c-howto__description'))}));
          const payment=node.querySelector('.c-howto__payment');
          const cart=document.querySelector('#js-floating');
          return {items,payment:rect(payment),methods:[...payment.querySelectorAll('li')].map(n=>n.textContent),paymentLines:lines(payment),container:rect(node.querySelector('.c-howto-container')),cart:rect(cart),cartVisible:getComputedStyle(cart).visibility!=='hidden',overflow:document.documentElement.scrollWidth>innerWidth+1};
        });
        assert(!result.overflow, 'horizontal page overflow');
        assert.equal(result.items.length,5);
        assert.deepEqual(result.items.map(i=>[i.heading,i.description]),flow.steps.map(s=>[s[0],s[1].join('')]));
        assert.deepEqual(result.methods,flow.payment_methods);
        for (const item of result.items) {
          assert(item.text.width>120,'description column too narrow');
          assert(item.lines.every(r=>r.left>=item.text.left-1&&r.right<=item.text.right+1),'description clips');
          assert(item.icon.width>0&&Math.abs(item.icon.width/item.icon.height-4/3)<0.01,'icon frame distorted');
          if(width>=1440)assert.equal(item.lines.length,flow.steps[result.items.indexOf(item)][1].length,'desktop phrase breaks differently');
        }
        const rows=[...new Set(result.items.map(i=>Math.round(i.rect.top)))];
        assert.equal(rows.length,width>=1440?1:width>=1200?2:width>=768?3:width>=600?2:5,'unexpected step arrangement');
        if(width>=768)assert(result.items.every(i=>i.rect.right<=result.cart.left-8),`${engine} ${width}x${height}: flow right ${Math.max(...result.items.map(i=>i.rect.right))}, cart left ${result.cart.left}`);
        assert(result.payment.top>=Math.max(...result.items.map(i=>i.rect.bottom))+31,'payment methods not separated below steps');
        assert(result.paymentLines.every(r=>r.left>=result.payment.left-1&&r.right<=result.payment.right+1),'payment methods clip');
        assert.deepEqual(errors,[],'runtime errors');
        if(engine==='Chrome'&&[[1440,1010],[1280,551],[414,688],[320,568]].some(s=>s[0]===width&&s[1]===height)) {
          await page.screenshot({path:path.join(output,`${engine}-${width}x${height}-viewport.png`)});
          await section.screenshot({path:path.join(output,`${engine}-${width}x${height}-section.png`),animations:'disabled',style:'.c-header,#js-floating,#viewport-hud {visibility:hidden!important}'});
        }
        checks.push({engine,width,height,rows:rows.length,...result});
        await context.close();
      }
    } finally {await browser.close();}
  }
  fs.writeFileSync(path.join(output,'verification.json'),JSON.stringify({checkedAt:new Date().toISOString(),origin,passed:true,cases:checks.length,checks},null,2)+'\n');
  console.log(JSON.stringify({origin,cases:checks.length,passed:true}));
})().catch(error=>{console.error(error);process.exitCode=1;});
