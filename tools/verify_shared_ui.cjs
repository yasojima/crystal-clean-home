const fs = require('fs');
const path = require('path');
const assert = require('assert/strict');
const {chromium, webkit} = require('C:/Users/yasoj/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const base = process.argv[2] || 'http://127.0.0.1:8769';
const out = process.argv[3] || 'evidence/2026-10-03/local';
fs.mkdirSync(out, {recursive: true});
const routes = process.env.SHARED_ROUTES ? process.env.SHARED_ROUTES.split(',') : ['/', '/house-cleaning/aircon/', '/house-cleaning/water/', '/house-cleaning/room/', '/house-cleaning/coating/floor/', '/cart/', '/beginner/', '/contact/house-cleaning/', '/office/floor/', '/business/racn/', '/house-cleaning/aircon/2027problem/', '/error/403/'];
let activeCase;

(async () => {
  const results = [];
  for (const [engine, launch] of [['Chrome', () => chromium.launch({channel: 'chrome', headless: true})], ['WebKit', () => webkit.launch({headless: true})]]) {
    const browser = await launch();
    try {
      for (const [width, height] of [[414,688],[1440,800]]) {
        for (const route of routes) {
          activeCase={engine,route,width,height};
          const page = await browser.newPage({viewport: {width,height}, isMobile: width < 768, hasTouch: width < 768});
          const errors=[];
          page.on('pageerror', error => errors.push(error.message));
          const response=await page.goto(base+route, {waitUntil:'load'});
          assert.equal(response.status(),200,route);
          await page.evaluate(() => document.fonts.ready);
          const initial=await page.evaluate(() => {
            const rect=n=>{const r=n.getBoundingClientRect();return {x:r.x,y:r.y,width:r.width,height:r.height};};
            const phone=document.querySelector('.c-header-contact__number');
            const floating=document.querySelector('.c-corporate-floating');
            return {header:rect(document.querySelector('.c-header')),menu:rect(document.querySelector('.c-header__menu')),phone:phone?.textContent,guide:document.querySelector('.c-main-menu__link')?.textContent,footerDetails:document.querySelectorAll('.aircon-footer-menu .c-footer-accordion__content a').length,footerRows:document.querySelectorAll('.aircon-footer-menu__row').length,footers:document.querySelectorAll('footer.c-footer').length,menus:document.querySelectorAll('#menu').length,corporateFloating:floating?getComputedStyle(floating).visibility:null};
          });
          assert.equal(initial.phone,'00-0000-0000');
          assert.equal(initial.guide,'ご利用ガイド');
          assert.equal(initial.footerDetails,43);assert.equal(initial.footerRows,5);
          assert.equal(initial.footers,1);assert.equal(initial.menus,1);
          assert(initial.menu.x>=0&&initial.menu.x+initial.menu.width<=width);
          if(initial.corporateFloating!==null)assert.equal(initial.corporateFloating,'visible');
          const opener=page.locator('.c-header__menu');
          await opener.click();await page.waitForTimeout(500);
          await page.waitForFunction(()=>getComputedStyle(document.querySelector('.c-header')).backgroundColor==='rgb(245, 245, 245)');
          assert.equal(await opener.getAttribute('aria-expanded'),'true');
          const menu=await page.evaluate(()=>({sections:document.querySelectorAll('.aircon-full-menu__section').length,header:getComputedStyle(document.querySelector('.c-header')).backgroundColor,labels:document.querySelectorAll('.aircon-full-menu__body a').length}));
          assert.equal(menu.sections,10);assert.equal(menu.header,'rgb(245, 245, 245)');
          assert(menu.labels>=43);
          if(route==='/'||route==='/contact/house-cleaning/')await page.screenshot({path:path.join(out,`shared-menu-${engine}-${width}-${route==='/'?'home':'contact'}.png`)});
          await page.keyboard.press('Escape');await page.waitForTimeout(450);
          assert.equal(await opener.getAttribute('aria-expanded'),'false');
          if(width===1440){
            const top=page.locator('.c-main-menu__link').nth(3);
            await top.hover();await page.waitForTimeout(500);
            const before=page.url(),scroll=await page.evaluate(()=>scrollY);
            await top.click();assert.equal(page.url(),before);assert.equal(await page.evaluate(()=>scrollY),scroll);
            assert(await page.locator('.aircon-mega').getAttribute('class').then(x=>x.includes('is-open')));
            await page.mouse.move(5,500);
            await page.waitForTimeout(500);
          }
          await page.evaluate(()=>scrollTo({top:document.documentElement.scrollHeight,behavior:'instant'}));
          await page.waitForTimeout(750);
          const footer=await page.evaluate(()=>({rect:(()=>{const r=document.querySelector('footer.c-footer').getBoundingClientRect();return {x:r.x,width:r.width,bottom:r.bottom}})(),first:document.querySelector('.aircon-footer-menu .c-footer-accordion__content').firstElementChild.tagName,labels:[...document.querySelectorAll('.c-footer-bottom-links__link')].map(a=>a.textContent.trim())}));
          assert.equal(footer.first,'UL');assert(footer.rect.x>=-1&&footer.rect.width<=width+1);
          assert(footer.labels.some(t=>t==='お問い合わせ'));
          let corporateFloating=null;
          if(initial.corporateFloating!==null){
            corporateFloating=await page.evaluate(()=>{
              const floating=document.querySelector('.c-corporate-floating'),style=getComputedStyle(floating);
              const links=[...document.querySelectorAll('.c-footer-sns__link,.c-footer-bottom-links__link')].filter(a=>a.getBoundingClientRect().height&&a.getBoundingClientRect().top>=0);
              return {visibility:style.visibility,pointerEvents:style.pointerEvents,links:links.map(a=>{
                const r=a.getBoundingClientRect(),hit=document.elementFromPoint(r.x+r.width/2,r.y+r.height/2);
                return {text:a.textContent.trim()||a.getAttribute('aria-label'),unobscured:a===hit||a.contains(hit)};
              })};
            });
            assert.equal(corporateFloating.visibility,'hidden');assert.equal(corporateFloating.pointerEvents,'none');
            assert.equal(corporateFloating.links.length,8);assert(corporateFloating.links.every(a=>a.unobscured));
            await page.screenshot({path:path.join(out,`shared-corporate-footer-${engine}-${width}.png`)});
          }
          if(width<768){
            assert(Math.abs(footer.rect.bottom-height)<2);
            const button=page.locator('.aircon-footer-menu__row .js-accordion-trigger').nth(1);
            await button.tap();await page.waitForTimeout(400);
            assert.equal(await button.getAttribute('aria-expanded'),'true');
            const panel=page.locator('#'+await button.getAttribute('aria-controls'));
            assert.equal(await panel.getAttribute('aria-hidden'),'false');
            assert.equal(await panel.locator('.aircon-footer-menu__detail-heading').count(),0);
          }
          if(route==='/'||route==='/house-cleaning/aircon/')await page.screenshot({path:path.join(out,`shared-footer-${engine}-${width}-${route==='/'?'home':'aircon'}.png`)});
          assert.deepEqual(errors,[],route);
          if(corporateFloating){
            await page.evaluate(()=>scrollTo({top:0,behavior:'instant'}));await page.waitForTimeout(750);
            assert.equal(await page.locator('.c-corporate-floating').evaluate(n=>getComputedStyle(n).visibility),'visible');
            corporateFloating.restored=true;
          }
          results.push({engine,route,width,height,initial,menu,footer,corporateFloating,errors});
          await page.close();
        }
      }
    } finally {await browser.close();}
  }
  fs.writeFileSync(path.join(out,'shared-ui-browser.json'),JSON.stringify({base,results},null,2)+'\n');
  process.stdout.write(JSON.stringify({passed:results.length})+'\n');
})().catch(error=>{console.error(activeCase,error);process.exit(1)});
