const fs=require('fs'),path=require('path'),assert=require('assert/strict');
const {chromium}=require('C:/Users/yasoj/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const origin=process.argv[2]||'http://127.0.0.1:8773';
const out=path.resolve(__dirname,'../evidence/2026-10-07/responsive-content',origin.startsWith('http://127.')?'mobile-local':'public');
async function align(page,selector){
  await page.locator(selector).evaluate(e=>scrollTo({top:e.getBoundingClientRect().top+scrollY-document.querySelector('header.c-header').offsetHeight,behavior:'instant'}));
  await page.waitForTimeout(450);
}
(async()=>{
  fs.mkdirSync(out,{recursive:true});const browser=await chromium.launch({channel:'chrome',headless:true}),records=[],errors=[];
  try{
    for(const [width,height,isMobile] of [[1280,551,false],[414,688,true],[320,568,true]]){
      const context=await browser.newContext({viewport:{width,height},isMobile,hasTouch:isMobile,deviceScaleFactor:1});const page=await context.newPage();
      page.on('pageerror',e=>errors.push({width,message:e.message}));
      await page.route('**/*',r=>{const host=new URL(r.request().url()).hostname;return host===new URL(origin).hostname||['fonts.googleapis.com','fonts.gstatic.com'].includes(host)?r.continue():r.abort();});
      for(const route of process.argv.includes('--footer-only')?['/']:['/beginner/','/house-cleaning/water/','/quick_cart/','/cart/','/']){
        await page.goto(origin+route,{waitUntil:'load'});await page.evaluate(()=>document.fonts.ready);
        const record={route,width,height,isMobile,...await page.evaluate(()=>({overflow:document.documentElement.scrollWidth-document.documentElement.clientWidth,headerHeight:document.querySelector('header.c-header').offsetHeight}))};
        assert(record.overflow<=1);
        if(route==='/beginner/'){
          const links=await page.locator('.lp-estimate-button').evaluateAll(es=>es.map(e=>e.getAttribute('href')));assert.equal(links.length,6);assert(links.every(h=>h==='/quick_cart/'));
          await page.locator('#lp-case-tab-1').click();assert.equal(await page.locator('#lp-case-tab-1').getAttribute('aria-selected'),'true');assert(await page.locator('#lp-case-panel-1').isVisible());
          await page.locator('#lp-case-tab-0').click();const slider=page.locator('#lp-case-panel-0 [role="slider"]');
          const before=Number(await slider.getAttribute('aria-valuenow'));await slider.press('ArrowRight');assert.equal(Number(await slider.getAttribute('aria-valuenow')),before+5);
          await align(page,'#first-cases');await page.screenshot({path:path.join(out,`lp-cases-${width}.jpg`),quality:76});
          await align(page,'#first-introduction');await page.screenshot({path:path.join(out,`lp-opening-${width}.jpg`),quality:76});
          await page.locator('.lp-estimate-button').first().click();await page.waitForURL(origin+'/quick_cart/');assert(await page.locator('main').isVisible());record.comparisonAndEstimate=true;
        }
        if(route==='/house-cleaning/water/'){
          record.cards=await page.locator('.p-page-anchors__cards > a').evaluateAll(es=>es.map(e=>({y:e.getBoundingClientRect().y,height:e.getBoundingClientRect().height,href:e.getAttribute('href')})));
          record.columns=record.cards.filter(c=>Math.abs(c.y-record.cards[0].y)<1).length;assert.equal(record.columns,isMobile?2:4);assert.equal(record.cards.length,6);
          await align(page,'.c-service-selector');await page.screenshot({path:path.join(out,`water-${width}.jpg`),quality:76});
        }
        if(route==='/quick_cart/')await page.screenshot({path:path.join(out,`estimate-${width}.jpg`),quality:76});
        if(route==='/'){
          await page.evaluate(async()=>{document.querySelectorAll('footer img').forEach(i=>i.loading='eager');await Promise.all([...document.querySelectorAll('footer img')].map(i=>i.decode()));scrollTo({top:document.documentElement.scrollHeight,behavior:'instant'});});await page.waitForTimeout(450);
          record.socialIcons=await page.locator('footer .c-footer-sns:visible img').evaluateAll(es=>es.filter(i=>i.naturalWidth>0&&i.getBoundingClientRect().width>0).length);assert.equal(record.socialIcons,5);
          record.footer=await page.evaluate(()=>{const h=document.querySelector('header.c-header').getBoundingClientRect(),f=document.querySelector('footer').getBoundingClientRect();return{overlap:Math.max(0,h.bottom-f.top),end:innerHeight-f.bottom,floatingHidden:getComputedStyle(document.querySelector('.home-quick-estimate')).visibility==='hidden'};});
          assert(record.footer.overlap<=1&&Math.abs(record.footer.end)<=1&&record.footer.floatingHidden);await page.screenshot({path:path.join(out,`footer-${width}.jpg`),quality:76});
        }
        record.passed=true;records.push(record);
      }
      await context.close();
    }
    const report={origin,records,errors,passed:!errors.length};fs.writeFileSync(path.join(out,process.argv.includes('--footer-only')?'footer-images.json':'checks.json'),JSON.stringify(report,null,2));console.log(JSON.stringify({conditions:records.length,passed:report.passed,errors}));assert(report.passed);
  }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
