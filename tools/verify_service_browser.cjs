const fs=require('fs');
const path=require('path');
const assert=require('assert/strict');
const {chromium,webkit}=require(process.env.PLAYWRIGHT_MODULE||'C:/Users/yasoj/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const root=path.resolve(__dirname,'..');
const catalogue=JSON.parse(fs.readFileSync(path.join(root,'source/service-pages/catalogue.json'),'utf8'));
const voices=JSON.parse(fs.readFileSync(path.join(root,'source/service-pages/voices.json'),'utf8')).pages;
const origin=process.argv[2]||'http://127.0.0.1:8769';
const output=process.argv[3]||'evidence/2026-10-03/local/service-format';
const mode=process.argv[4]||'all';
const widths=mode==='breakpoints'?[320,375,768,1024]:[414,1440];
const routes=Object.keys(catalogue.pages).filter(r=>(mode!=='breakpoints'||!r.includes('/'))&&(!process.env.SERVICE_ROUTES||process.env.SERVICE_ROUTES.split(',').includes(r)));
fs.mkdirSync(output,{recursive:true});
async function settle(page){
 await page.waitForLoadState('load');
 await page.evaluate(async()=>{document.querySelectorAll('main img').forEach(img=>img.loading='eager');await document.fonts.ready;await Promise.all([...document.querySelectorAll('main img')].map(img=>img.decode().catch(()=>{})));});
 await page.waitForFunction(()=>[...document.querySelectorAll('main img')].every(img=>img.complete));
}
async function bring(page,locator){
 await locator.evaluate(e=>scrollTo({top:scrollY+e.getBoundingClientRect().top-innerHeight*.35,behavior:'instant'}));
 await page.waitForTimeout(550);
}
(async()=>{
 const checks=[],errors=[];
 for(const [engine,launch] of [['Chrome',()=>chromium.launch({channel:'chrome',headless:true})],['WebKit',()=>webkit.launch({headless:true})]]){
  const browser=await launch();
  try{
   for(const width of widths){
    const context=await browser.newContext({viewport:{width,height:width<768?688:800},isMobile:width<768,hasTouch:width<768});
    const page=await context.newPage();page.setDefaultTimeout(8000);await page.addInitScript(()=>localStorage.clear());
    for(const route of routes){
     const runtime=[],failedRequests=[];const listener=e=>runtime.push(e.message),requestListener=r=>failedRequests.push({url:r.url(),reason:r.failure()?.errorText});page.on('pageerror',listener);page.on('requestfailed',requestListener);
     const result={engine,route,width,passed:false};
     try{
      const response=await page.goto(`${origin}/house-cleaning/${route}/`,{waitUntil:'domcontentloaded'});assert.equal(response.status(),200);await settle(page);
      assert.equal(await page.locator('main[data-service-layout="shared-v2"]').count(),1);
      const layout=await page.evaluate(()=>{
       const main=document.querySelector('main'),labels=[...main.querySelectorAll('.c-category-simple-card__text,.c-tab__button,.c-voice-card__nickname')].filter(e=>e.getBoundingClientRect().height);
       return {viewport:innerWidth,scrollWidth:document.documentElement.scrollWidth,
        clippedLabels:labels.filter(e=>e.scrollWidth>e.clientWidth+2).map(e=>e.textContent),
        broken:[...main.querySelectorAll('img')].filter(i=>!i.naturalWidth).map(i=>i.getAttribute('src')),
        icons:[...main.querySelectorAll('.c-page-anchors .c-illust')].filter(e=>getComputedStyle(e).maskImage==='none').map(e=>e.className),
        profiles:main.querySelectorAll('.c-voice-card__profile').length,firstViews:document.querySelectorAll('#first-view').length,
        reasonColor:getComputedStyle(main.querySelector('.c-reasons__navy')).backgroundColor,
        reasonSize:[...main.querySelectorAll('.c-reasons__card')].map(e=>{const r=e.getBoundingClientRect();return {width:r.width,height:r.height}}),
        plan:(()=>{const t=main.querySelector('.c-bracket-heading__text');if(!t)return null;const range=document.createRange();range.selectNodeContents(t);return {text:t.textContent,lines:[...range.getClientRects()].length}})(),
        voices:[...main.querySelectorAll('.c-voice-card')].map(e=>({name:e.querySelector('.c-voice-card__nickname').textContent,rating:e.querySelector('.c-voice-card__stars').getAttribute('aria-label'),avatar:getComputedStyle(e,'::before').backgroundImage}))};
      });
      result.layout=layout;
      assert(layout.scrollWidth<=layout.viewport+1,`horizontal overflow: ${layout.scrollWidth}`);
      assert.deepEqual(layout.clippedLabels,[],'labels clipped');assert.deepEqual(layout.broken,[],'broken image');assert.deepEqual(layout.icons,[],'empty icon');
      assert.equal(layout.profiles,6);assert.equal(layout.firstViews,1);assert.equal(layout.reasonColor,'rgb(38, 69, 116)');
      assert(layout.reasonSize.every(r=>r.width<=305&&Math.abs(r.width-r.height)<2),'reason circles');
      assert.deepEqual(layout.voices.map(v=>v.name),voices[route].map(v=>v.nickname));assert.deepEqual(layout.voices.map(v=>v.rating),voices[route].map(v=>`5つ星中${v.rating}つ星`));assert(layout.voices.every(v=>v.avatar.includes('/voices/')));
      if(layout.plan){assert.equal(layout.plan.text,'人気の組み合わせプラン');assert.equal(layout.plan.lines,1);}
      if(!route.includes('/'))await page.screenshot({path:path.join(output,`${engine}-${width}-${route}-top.png`)});
      if(mode==='all'){
       const anchor=page.locator('.c-page-anchors a').last(),target=await anchor.getAttribute('href');await anchor.click();await page.waitForFunction(id=>{const y=document.querySelector(id).getBoundingClientRect().top;return y>=-1&&y<180},target);
       const faq=page.locator('.c-faq-accordion__trigger').first();await faq.click();assert.equal(await faq.getAttribute('aria-expanded'),'true');await page.waitForFunction(id=>document.getElementById(id).getBoundingClientRect().height>10,await faq.getAttribute('aria-controls'));await faq.click();
       const tabs=page.locator('#service-introduction .c-tab__button'),tab=tabs.last();if(await tabs.count()>1){await bring(page,tab);await tab.click();}assert.equal(await tab.getAttribute('aria-selected'),'true');assert(await page.locator('#'+await tab.getAttribute('aria-controls')).isVisible());
       const variants=page.locator('.js-room-types');
       for(let i=0;i<await variants.count();i++){
        const select=variants.nth(i),index=await select.locator('option').count()-1;await select.selectOption({index});
        const state=await select.evaluate(n=>{const wrap=n.closest('.js-products');return {index:n.selectedIndex,id:wrap.querySelector('[data-product-card="parent"] input[name="product-id"]').value,value:n.value,panels:[...wrap.querySelectorAll('[data-switch-target]')].map(box=>[...box.children].findIndex(child=>child.classList.contains('is-active')))}});
        assert.equal(state.id,state.value);assert(state.panels.every(p=>p===state.index));await select.selectOption({index:0});
       }
       const option=page.locator('.c-lineup-options__accordion-trigger').first();if(await option.count()){await option.click();assert.equal(await option.getAttribute('aria-expanded'),'true');await page.waitForFunction(id=>document.getElementById(id).getBoundingClientRect().height>10,await option.getAttribute('aria-controls'));await option.click();}
       const quantity=page.locator('.c-lineup-card .js-product-quantity.is-active select').first();if(await quantity.count()&&await quantity.locator('option').count()>1){await quantity.selectOption({index:1});assert.equal(await quantity.evaluate(n=>n.selectedIndex),1);await quantity.selectOption({index:0});}
       const cart=page.locator('.c-lineup-card .js-add-cart').first();if(await cart.count())assert(await cart.isEnabled(),'cart control disabled');
       await page.evaluate(()=>scrollTo({top:document.documentElement.scrollHeight,behavior:'instant'}));await page.waitForTimeout(400);
       if(width<768){
        const cartHidden=await page.locator('#js-floating').evaluate(e=>{const s=getComputedStyle(e),r=e.getBoundingClientRect();return s.visibility==='hidden'||s.display==='none'||Number(s.opacity)===0||r.top>=innerHeight});
        assert(cartHidden,'cart still visible in footer');
        const buttons=page.locator('.aircon-footer-menu__row .js-accordion-trigger');
        for(const index of [0,1,2,3,4,5,6,7,8,9]){
         const button=buttons.nth(index);await button.tap();await page.waitForTimeout(350);assert.equal(await button.getAttribute('aria-expanded'),'true',`footer panel ${index}`);const panel=page.locator('#'+await button.getAttribute('aria-controls'));
         assert.equal(await panel.locator('.aircon-footer-menu__detail-heading').count(),0);assert.equal(await panel.evaluate(e=>Math.round(e.getBoundingClientRect().width)),width);assert(await buttons.nth(index%2?index-1:index+1).isVisible(),'neighbor heading disappeared');await button.tap();await page.waitForTimeout(350);assert.equal(await button.getAttribute('aria-expanded'),'false',`footer close ${index}`);
        }
       }
      }
      assert.deepEqual(runtime,[],'runtime errors');result.passed=true;
     }catch(e){const reason=e.message;errors.push({engine,route,width,reason,stack:e.stack,failedRequests});result.reason=reason;console.log(JSON.stringify({FAIL:route,engine,width,reason,stack:e.stack,failedRequests}));await page.screenshot({path:path.join(output,`FAIL-${engine}-${width}-${route.replaceAll('/','-')}.png`)}).catch(()=>{});}
     page.off('pageerror',listener);page.off('requestfailed',requestListener);checks.push(result);
    }
    await context.close();console.log(JSON.stringify({engine,width,completed:routes.length}));
   }
  }finally{await browser.close();}
 }
 const report={checked_at:new Date().toISOString(),origin,mode,pages:routes.length,cases:checks.length,passed:!errors.length,checks,errors};fs.writeFileSync(path.join(output,'service-browser-verification.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify({pages:routes.length,cases:checks.length,passed:report.passed,errors:errors.length}));process.exitCode=errors.length?1:0;
})().catch(e=>{console.error(e);process.exitCode=1});
