const fs=require('fs'),path=require('path'),assert=require('assert/strict'),{chromium}=require(process.env.PLAYWRIGHT_MODULE);
(async()=>{
 const local=process.env.VERIFY_LOCAL!=='0', root=path.resolve('source/site'), out='evidence/2026-10-02/'+(local?'local':'public');
 const browser=await chromium.launch({headless:true,channel:'chrome'});const results=[];
 for(const width of [1440,768,390,320]){
  const ctx=await browser.newContext({viewport:{width,height:width<768?844:800},hasTouch:width<768});
  const page=await ctx.newPage(), errors=[];page.on('pageerror',e=>errors.push(e.message));
  if(local)await page.route('https://yasojima.github.io/**',async route=>{let rel=decodeURIComponent(new URL(route.request().url()).pathname);if(rel.endsWith('/'))rel+='index.html';const file=path.join(root,rel);if(fs.existsSync(file)&&fs.statSync(file).isFile())return route.fulfill({path:file});return route.continue();});
  await page.goto('https://yasojima.github.io/house-cleaning/aircon/?v=2026100250',{waitUntil:'networkidle'});
  await page.evaluate(()=>document.fonts.ready);
  const capture=async selector=>{await page.locator(selector).evaluate(e=>scrollTo(0,e.getBoundingClientRect().top+scrollY-160));await page.waitForTimeout(700);await page.locator(selector+' img').evaluateAll(imgs=>Promise.all(imgs.map(i=>i.decode().catch(()=>{}))));};
  const photoSources=await page.locator('#product1 .c-lineup-card__image img,#product2 .c-lineup-card__image img,#product3 .c-lineup-card__image img').evaluateAll(imgs=>imgs.map(i=>i.getAttribute('src')));
  assert.equal(new Set(photoSources).size,3);
  const tabs=[];
  for(let i=1;i<=3;i++){
   await page.locator('#service-tab-'+i).click();
   const selector='#service-panel-'+i+' .c-aircon-compare';await capture(selector);
   const loc=page.locator(selector), rect=await loc.boundingBox();
   await page.screenshot({path:out+'/aircon-comparison-'+i+'-'+width+'.png'});
   assert.equal(await loc.locator('.icv__control').count(),0);
   assert.deepEqual(await page.locator('#service-panel-'+i+' .c-aircon-comparison-note').allTextContents(),['汚れの状況により、完全に除去できない場合がございます。','本比較画像は作業の一例です。']);
   const positions=[];
   for(const fraction of [.2,.8,.02,.98]){
    const control=await loc.locator('.c-aircon-compare__handle').boundingBox();
    const start=await page.evaluate(()=>({scrollY,overflow:getComputedStyle(document.body).overflow,rootRight:document.documentElement.getBoundingClientRect().right}));
    await page.mouse.move(control.x+control.width/2,rect.y+rect.height/2);await page.mouse.down();await page.mouse.move(rect.x+rect.width*fraction,rect.y+rect.height/2,{steps:6});
    const held=await page.evaluate(()=>({scrollY,overflow:getComputedStyle(document.body).overflow,rootRight:document.documentElement.getBoundingClientRect().right}));
    await page.mouse.up();await page.mouse.move(10,150);
    const state=await loc.evaluate(e=>({fraction:parseFloat(e.style.getPropertyValue('--compare-split'))/100,labels:[...e.querySelectorAll('.c-aircon-compare__label')].map(n=>({text:n.textContent,hidden:n.hidden})),images:[...e.querySelectorAll('img')].map(n=>({src:n.src,loaded:n.complete&&n.naturalWidth===1536}))}));
    assert(Math.abs(state.fraction-fraction)<.015,JSON.stringify(state));if(fraction<.05)assert.deepEqual(state.labels.map(l=>l.hidden),[true,false]);if(fraction>.95)assert.deepEqual(state.labels.map(l=>l.hidden),[false,true]);assert(state.images.every(x=>x.loaded));assert.deepEqual(held,start);positions.push(state);
   }
   if(width<768){const session=await ctx.newCDPSession(page);const y=rect.y+rect.height/2; const currentControl=await loc.locator('.c-aircon-compare__handle').boundingBox();
    await session.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[{x:Math.min(rect.x+rect.width-2,currentControl.x+currentControl.width/2),y}]});
    await session.send('Input.dispatchTouchEvent',{type:'touchMove',touchPoints:[{x:rect.x+rect.width*.3,y}]});
    await session.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]});await page.waitForTimeout(150);
    const percent=await loc.evaluate(e=>parseFloat(e.style.getPropertyValue('--compare-split')));assert(Math.abs(percent-30)<2,JSON.stringify({width,i,percent}));
   }
   tabs.push({i,positions});
  }
  const cart=[];for(const y of [0,900,1800,3500,5500,8000,99999,0]){
   await page.evaluate(y=>scrollTo(0,y),y);await page.waitForTimeout(650);
   const state=await page.locator('#js-floating').evaluate(e=>{const r=e.getBoundingClientRect(),hit=document.elementFromPoint(r.x+r.width/2,r.y+r.height/2);return {y:scrollY,classes:e.className,r:r.toJSON(),inside:r.x>=0&&r.right<=innerWidth&&r.bottom<=innerHeight,pinned:Math.abs(r.right-document.documentElement.getBoundingClientRect().right)<.5&&Math.abs(r.bottom-innerHeight)<.5,hit:hit&&e.contains(hit)};});
   assert(state.inside,JSON.stringify(state));assert.equal(Boolean(state.hit),!state.classes.includes("is-footer-area"),JSON.stringify(state));assert(state.pinned,JSON.stringify(state));cart.push(state);
  }
  await page.locator('#js-floating a').click();await page.waitForURL('**/cart/**');assert(new URL(page.url()).pathname==='/cart/');
  await page.goBack({waitUntil:'networkidle'});
  await page.locator('.c-header__menu').click();await page.waitForTimeout(450);
  assert.equal(await page.locator('#menu').getAttribute('aria-hidden'),'false');await page.keyboard.press('Escape');
  await capture('.recommend-plan');await page.screenshot({path:out+'/aircon-brackets-'+width+'.png'});
  const bracket=await page.locator('.recommend-plan__heading').evaluate(e=>({before:getComputedStyle(e,'::before').content,after:getComputedStyle(e,'::after').content,height:e.getBoundingClientRect().height,font:getComputedStyle(e,'::before').fontFamily}));
  assert.equal(bracket.before,'"("');assert.equal(bracket.after,'")"');assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);assert.deepEqual(errors,[]);
  results.push({width,photoSources,tabs,cart,bracket,errors});await ctx.close();
 }
 fs.writeFileSync(out+'/aircon-comparison-cart-brackets.json',JSON.stringify({local,results},null,2));console.log(JSON.stringify({local,viewports:results.length,tabs:12,mouseDrags:48,touchDrags:6,cartLinks:4,errors:[]}));await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
