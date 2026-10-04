const fs = require('fs');
const path = require('path');
const assert = require('assert/strict');
const {chromium, webkit} = require('C:/Users/yasoj/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const root = path.resolve(__dirname, '..');
const catalogue = JSON.parse(fs.readFileSync(path.join(root, 'source/service-pages/catalogue.json'), 'utf8'));
const origin = process.argv[2] || 'http://127.0.0.1:8769';
const output = process.argv[3] || 'evidence/2026-10-04/category-only/navigation-local';
fs.mkdirSync(output, {recursive:true});
(async()=>{
 const checks=[];
 for(const [engine,launch] of [['Chrome',()=>chromium.launch({channel:'chrome',headless:true})],['WebKit',()=>webkit.launch({headless:true})]]){
  const browser=await launch();
  try{
   for(const viewport of [{width:1440,height:800},{width:414,height:688}]){
    const context=await browser.newContext({viewport,isMobile:viewport.width<768,hasTouch:viewport.width<768});
    const page=await context.newPage();
    for(const route of Object.keys(catalogue.pages)){
     const url=`${origin}/house-cleaning/${route}/`;
     assert.equal((await page.goto(url,{waitUntil:'load'})).status(),200);
     await page.evaluate(()=>document.fonts.ready);
     const images=page.locator('.c-lineup-card__image');
     assert.equal(await page.locator('.c-lineup-card__image[href],.c-lineup-card__heading a[href]').count(),0);
     const image=images.first();
     await image.evaluate(async n=>{const img=n.querySelector('img');img.loading='eager';await img.decode();scrollTo({top:scrollY+n.getBoundingClientRect().top-innerHeight*.25,behavior:'instant'});});
     await image.click();assert.equal(page.url(),url,'product image navigates');
     const title=page.locator('.c-lineup-card__heading').first();
     await title.evaluate(n=>scrollTo({top:scrollY+n.getBoundingClientRect().top-innerHeight*.3,behavior:'instant'}));
     await title.click();assert.equal(page.url(),url,'service name navigates');
     assert.equal(await title.locator('span').evaluate(n=>getComputedStyle(n).color),'rgb(0, 91, 172)','non-link heading lost its blue color');
     const card=page.locator('.c-lineup-card').first();
     if(engine==='Chrome'&&['aircon','room'].includes(route)){
      await card.locator('img').evaluate(async n=>{n.loading='eager';await n.decode();});
      await card.screenshot({path:path.join(output,`${engine}-${viewport.width}-${route}.png`),style:'.c-header,#js-floating,#viewport-hud{visibility:hidden!important}'});
     }
     const quantity=card.locator('.js-product-quantity.is-active select,.js-product-quantity:not(:has(~ .js-product-quantity)) select').first();
     if(await quantity.count()){
      await quantity.selectOption({index:1});assert.equal(await quantity.evaluate(n=>n.selectedIndex),1);
      await quantity.selectOption({index:0});
     }
     const button=card.locator('.js-add-cart').first();
     await button.evaluate(n=>scrollTo({top:scrollY+n.getBoundingClientRect().top-innerHeight*.45,behavior:'instant'}));
     if(await button.getAttribute('data-demo-dialog')!==null){
      const dialog=page.waitForEvent('dialog');const clicking=button.click();
      const popup=await dialog;assert.equal(popup.message(),'デモ表示のためリンク未設定です。');await popup.accept();await clicking;
     }else{
      // The static demo has no ordering API; retain its existing failure dialog.
      await button.click();await page.locator('#add-cart-modal[open]').waitFor();
      assert((await page.locator('#js-add-products').innerText()).includes('カートへの追加に失敗しました'));
      await page.keyboard.press('Escape');
     }
     assert.equal(page.url(),url);
     assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),'horizontal overflow');
     await page.goto(url,{waitUntil:'load'});
     await page.evaluate(async()=>{await document.fonts.ready;const images=[...document.querySelectorAll('footer img')];images.forEach(i=>i.loading='eager');await Promise.all(images.map(i=>i.decode().catch(()=>{})));scrollTo({top:document.documentElement.scrollHeight,behavior:'instant'});});
     const footerLink=page.locator(`footer a[href^="/house-cleaning/${route}/#"]`).first();
     const destination=await footerLink.getAttribute('href');assert(destination);
     // On mobile the footer category opens before its child link can be tapped.
     if(viewport.width<768){
      // Use the actual accordion owning this link; category labels can be abbreviated.
      const owner=await page.locator(`.aircon-footer-menu a[href="${destination}"]`).first().evaluate(n=>n.closest('.c-footer-accordion__content')?.id);
      if(owner){const control=page.locator(`button[aria-controls="${owner}"]`);if(await control.getAttribute('aria-expanded')!=='true')await control.click();}
     }
     const visibleLink=page.locator(`footer a[href="${destination}"]:visible`).first();
     await visibleLink.click();await page.waitForURL(origin+destination);
     const id=destination.split('#')[1];assert(await page.locator(`[id="${id}"]`).count());
     checks.push({engine,viewport,route,productImageAndTitleStayOnPage:true,quantityAndDemoCart:true,footerDestination:destination});
    }
    await context.close();
    console.log(JSON.stringify({engine,viewport,completed:8}));
   }
  }finally{await browser.close();}
 }
 fs.writeFileSync(path.join(output,'verification.json'),JSON.stringify({passed:true,cases:checks.length,checks},null,2)+'\n');
 console.log(JSON.stringify({passed:true,cases:checks.length}));
})().catch(e=>{console.error(e);process.exitCode=1;});
