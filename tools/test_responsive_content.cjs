const fs = require('fs');
const path = require('path');
const assert = require('assert/strict');
const {chromium} = require('C:/Users/yasoj/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const root = path.resolve(__dirname, '..');
const origin = process.argv[2] || 'http://127.0.0.1:8773';
const out = process.argv[3] || path.join(root, 'evidence/2026-10-07/responsive-content');
const sizes = [[1920,1080],[1440,800],[1439,799],[1366,650],[1280,551],[1152,600],[1024,600],[992,700],[768,800],[600,800],[440,852],[430,852],[414,688],[393,852],[390,844],[375,812],[320,568]];
const walk = dir => fs.readdirSync(dir,{withFileTypes:true}).flatMap(e=>e.isDirectory()?walk(path.join(dir,e.name)):[path.join(dir,e.name)]);
const routes = walk(path.join(root,'source/site')).filter(p=>p.endsWith('.html')).map(p=>'/'+path.relative(path.join(root,'source/site'),p).replaceAll('\\','/').replace(/index\.html$/,''));
async function settle(page) { await page.evaluate(async()=>{document.body.getBoundingClientRect();await document.fonts.ready;await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)));}); }
async function metrics(page) { return page.evaluate(()=>{
  const rect=e=>{const r=e.getBoundingClientRect();return {x:r.x,y:r.y,width:r.width,height:r.height};};
  const isScrolled=e=>{for(let a=e.parentElement;a&&a!==document.body;a=a.parentElement){if(['auto','scroll'].includes(getComputedStyle(a).overflowX))return true;}return false;};
  const clipped=[...document.querySelectorAll('main button,main .c-category-simple-card__text,main .lp-estimate-button')].filter(e=>e.getBoundingClientRect().width>0&&getComputedStyle(e).visibility!=='hidden'&&!isScrolled(e)&&(e.scrollWidth>e.clientWidth+2)).map(e=>({text:e.textContent.trim().slice(0,80),class:e.className,width:e.clientWidth,scrollWidth:e.scrollWidth}));
  const canvas=document.querySelector('.lp-canvas');
  const cards=[...document.querySelectorAll('.p-page-anchors__cards > a')].map(rect);
  const iconErrors=[...document.querySelectorAll('main .c-category-simple-card__icon')].filter(e=>e.getBoundingClientRect().width>0).flatMap(e=>{const card=e.closest('.c-category-simple-card');const arrow=card.classList.contains('c-category-simple-card--icon-down');const w=innerWidth<768?(arrow?72:98):(arrow?100:120);const r=rect(e),white=rect(card.querySelector('.c-category-simple-card__top'));const h=w*10/13+(arrow?(innerWidth<768?28:32):(innerWidth<768?33:28));return Math.abs(r.width-w)>1||Math.abs(r.height-w*10/13)>1||Math.abs(white.height-h)>1?[{classes:e.className,expected:w,icon:r,white,whiteExpected:h}]:[];});
  return {width:innerWidth,height:innerHeight,overflow:document.documentElement.scrollWidth-document.documentElement.clientWidth,clipped,iconErrors,header:rect(document.querySelector('header')),canvas:canvas?rect(canvas):null,cards,ctas:[...document.querySelectorAll('.lp-estimate-button')].map(e=>({href:e.getAttribute('href'),...rect(e)}))};
}); }
(async()=>{
  fs.mkdirSync(out,{recursive:true});
  const browser=await chromium.launch({channel:'chrome',headless:true});
  const page=await browser.newPage();const records=[],errors=[];
  page.on('pageerror',e=>errors.push({url:page.url(),message:e.message}));
  let capture=false;
  await page.route('**/*',r=>{const u=new URL(r.request().url());if(u.origin!==new URL(origin).origin)return r.abort();if(!capture&&u.pathname.startsWith('/assets/images/')&&!/header|footer|common-parts|crystal-clean-home|cleaning-illustrations/.test(u.pathname))return r.abort();return r.continue();});
  try {
    for(const route of routes) {
      await page.setViewportSize({width:1280,height:551});
      await page.goto(origin+route,{waitUntil:'load'});
      const sequence=['/','/beginner/'].includes(route)?[...sizes,...[...sizes].reverse()]:sizes;
      for(const size of sequence) {
        await page.setViewportSize({width:size[0],height:size[1]});await settle(page);
        const record={route,...await metrics(page)};
        record.passed=record.overflow<=1&&!record.clipped.length&&!record.iconErrors.length;
        if(record.canvas){const available=record.width-15;const reduced=record.width>=768&&record.height<=720;record.passed&&=reduced?record.canvas.width<=880.5&&Math.abs(record.canvas.x-(available-record.canvas.width)/2)<=1:Math.abs(record.canvas.width-available)<=1&&Math.abs(record.canvas.x)<=1;}
        if(route==='/house-cleaning/water/'&&record.width===1280&&record.height===551){record.selectorColumns=record.cards.filter(c=>Math.abs(c.y-record.cards[0].y)<1).length;record.passed&&=record.selectorColumns===4;}
        records.push(record);
      }
      console.log(JSON.stringify({route,failures:records.filter(r=>r.route===route&&!r.passed)}));
    }
    capture=true;
    for(const [route,anchor,label,size] of [
      ['/beginner/','#first-introduction','lp-opening',[1280,551]],
      ['/beginner/','#first-comic','lp-comic',[1280,551]],
      ['/beginner/','#first-services','lp-services',[1280,551]],
      ['/beginner/','#first-cases','lp-cases',[414,688]],
      ['/house-cleaning/water/','.c-service-selector','water-selector',[1280,551]],
      ['/house-cleaning/water/','.c-service-selector','water-mobile',[320,568]],
      ['/quick_cart/','main','quick-cart',[1280,551]],
      ['/','#home-pickup','pickup-desktop',[1280,551]],
      ['/','#home-pickup','pickup-mobile',[414,688]],
      ['/','#home-pickup-banner','upper-banner-mobile',[320,568]],
    ]) {
      await page.setViewportSize({width:size[0],height:size[1]});await page.goto(origin+route,{waitUntil:'load'});await settle(page);
      await page.locator(anchor).evaluate(e=>{scrollTo({top:e.getBoundingClientRect().top+scrollY-document.querySelector('header.c-header').offsetHeight,behavior:'instant'});});
      await page.waitForTimeout(450);
      await page.locator(anchor).evaluate(e=>{scrollTo({top:e.getBoundingClientRect().top+scrollY-document.querySelector('header.c-header').offsetHeight,behavior:'instant'});});
      await settle(page);await page.screenshot({path:path.join(out,label+'.jpg'),quality:76});
    }
    await page.goto(origin+'/home-wireframe/',{waitUntil:'load'});
    for(const size of [...sizes].reverse()){
      await page.setViewportSize({width:size[0],height:size[1]});await settle(page);
      const result=await metrics(page);assert(result.overflow<=1&&!result.clipped.length,`prototype does not fit ${size}`);
    }
    await page.setViewportSize({width:1280,height:551});
    assert.equal(await page.locator('.home-pickup__slot').count(),3);
    assert.equal(await page.locator('.home-pickup__slot a').count(),0);
    assert.equal(await page.locator('.home-pickup__banner').getAttribute('href'),'/house-cleaning/aircon/');
    for(const letter of ['B','C','A']){await page.locator(`[data-wf-choice="${letter}"]`).click();assert(await page.locator(`#wf-news-${letter}`).isVisible());}
    await page.locator('#wf-news-A [data-wf-news-id]').first().click();assert(await page.locator('.wf-news-dialog').isVisible());await page.keyboard.press('Escape');
    const report={origin,pages:routes.length,conditions:records.length,records,errors,prototypeInteractions:true,passed:records.every(r=>r.passed)&&!errors.length};
    fs.writeFileSync(path.join(out,'local.json'),JSON.stringify(report,null,2));console.log(JSON.stringify({conditions:report.conditions,passed:report.passed,errors}));assert(report.passed);
  } finally {await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
