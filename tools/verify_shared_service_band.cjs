const fs = require('fs'), path = require('path'), assert = require('assert/strict');
const {chromium} = require('C:/Users/yasoj/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const origin = process.argv[2] || 'http://127.0.0.1:8773';
const out = process.argv[3] || 'evidence/2026-10-09/shared-band-correction/local';
const routes = ['/business/cleaning/', ...['aircon','pack','water','washer','kitchen','room','coating','others'].map(r=>`/house-cleaning/${r}/`)];
const sizes = [[1920,1080],[1440,800],[1280,551],[1024,600],[768,800],[414,688],[320,568]];
async function measure(page) {
  return page.evaluate(()=>{
    const frame=document.querySelector('.c-first-view'), band=frame.querySelector('.c-house-cleaning-mv--check');
    const text=band.querySelector('.c-house-cleaning-mv__text'), check=band.querySelector('.c-house-cleaning-mv__check');
    const r=band.getBoundingClientRect(), t=text.getBoundingClientRect(), c=getComputedStyle(band), s=getComputedStyle(text);
    return {width:innerWidth,height:innerHeight,band:{width:r.width,height:r.height,y:r.y},
      style:{background:c.backgroundImage,mask:c.maskImage,maskSize:c.maskSize,maskPosition:c.maskPosition,padding:c.padding,font:s.font,fontFamily:s.fontFamily,color:s.color,lineHeight:s.lineHeight},
      clipped:t.top<r.top-1||t.bottom>check.getBoundingClientRect().top+1||t.left<r.left-1||t.right>r.right+1,
      frameBottom:frame.getBoundingClientRect().bottom,headerBottom:document.querySelector('.c-header').getBoundingClientRect().bottom,
      overflow:Math.max(0,document.documentElement.scrollWidth-document.documentElement.clientWidth)};
  });
}
(async()=>{
  fs.mkdirSync(out,{recursive:true});
  const browser=await chromium.launch({channel:'chrome',headless:true}), page=await browser.newPage();
  const records=[], propagation=[], errors=[];
  page.on('pageerror',e=>errors.push(e.message));
  try {
    for(const [width,height] of sizes){
      await page.setViewportSize({width,height}); let reference;
      for(const route of routes){
        await page.goto(origin+route,{waitUntil:'domcontentloaded'});
        await page.evaluate(()=>document.fonts.ready); await page.waitForTimeout(120);
        const r={route,...await measure(page)};
        assert(!r.clipped,`Band text escapes at ${route} ${width}`);
        assert(r.overflow<=1,`Horizontal overflow at ${route} ${width}`);
        assert(r.frameBottom<=Math.min(height,800)+1,`First view escapes at ${route} ${width}`);
        assert(r.band.y>=r.headerBottom-1);
        if(reference){
          assert(Math.abs(r.band.height-reference.band.height)<1,`Band height differs at ${route} ${width}`);
          assert.deepEqual(r.style,reference.style,`Band style differs at ${route} ${width}`);
        }else reference=r;
        records.push(r);
        if(width===1440||width===414)await page.screenshot({path:path.join(out,`${route.includes('business')?'business':route.split('/')[2]}-${width}.png`)});
      }
    }
    await page.setViewportSize({width:1440,height:800});
    for(const route of routes){
      await page.goto(origin+route,{waitUntil:'domcontentloaded'});
      await page.evaluate(()=>document.fonts.ready);await page.waitForTimeout(120);
      const before=await measure(page);
      await page.evaluate(()=>{
        const sheet=[...document.styleSheets].find(s=>s.href?.includes('/aircon-hero.css'));
        const rule=[...sheet.cssRules].find(r=>r.selectorText==='.c-service-page .c-first-view');
        window.__bandRule=rule;window.__bandPreferred=rule.style.getPropertyValue('--banner-preferred-height');
        rule.style.setProperty('--banner-preferred-height','260px');dispatchEvent(new Event('resize'));
      });
      await page.waitForTimeout(120);const changed=await measure(page);
      assert(Math.abs(changed.band.height-260)<1,`Common height change did not reach ${route}`);
      await page.evaluate(()=>{window.__bandRule.style.setProperty('--banner-preferred-height',window.__bandPreferred);dispatchEvent(new Event('resize'));});
      await page.waitForTimeout(120);const restored=await measure(page);
      assert(Math.abs(restored.band.height-before.band.height)<1);
      propagation.push({route,before:before.band.height,changed:changed.band.height,restored:restored.band.height});
    }
    assert.deepEqual(errors,[]);
    fs.writeFileSync(path.join(out,'report.json'),JSON.stringify({origin,conditions:records.length,records,propagation,errors,passed:true},null,2));
    console.log(JSON.stringify({conditions:records.length,sharedHeightPropagation:propagation.length,passed:true,errors}));
  }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
