const fs = require('fs');
const path = require('path');
const assert = require('assert/strict');
const {chromium} = require('C:/Users/yasoj/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const root = path.resolve(__dirname, '..');
const origin = process.argv[2] || 'http://127.0.0.1:8773';
const out = process.argv[3] || path.join(root, 'evidence/2026-10-07/first-view-fit');
const routes = ['aircon','pack','water','washer','kitchen','room','coating','others'];
const sizes = [[1920,1080],[1440,800],[1439,799],[1366,650],[1280,551],[1152,600],[1024,600],[992,700],[768,800],[600,800],[440,852],[430,852],[414,688],[393,852],[390,844],[375,812],[320,568]];
async function measure(page) {
  return page.evaluate(() => {
    const f=document.querySelector('.c-first-view'), h=document.querySelector('.c-header'),g=f.querySelector('.p-page-anchors__cards');
    const box=e=>{const r=e.getBoundingClientRect();return {x:r.x,y:r.y,width:r.width,height:r.height,bottom:r.bottom,right:r.right}};
    const visible=[...g.children];
    const clipped=[];
    visible.forEach(c=>{const t=c.querySelector('.c-category-simple-card__text'), b=c.querySelector('.c-category-simple-card__bottom');const range=document.createRange();range.selectNodeContents(t);const br=b.getBoundingClientRect();const rects=[...range.getClientRects()].filter(r=>r.width&&r.height);if(rects.some(r=>r.right>br.right+1||r.left<br.left-1||r.bottom>br.bottom+1))clipped.push(t.textContent.trim());});
    return {width:innerWidth,height:innerHeight,frame:box(f),header:box(h),hero:box(f.querySelector('.c-house-cleaning-mv')),grid:box(g),scrollHeight:g.scrollHeight,scrollable:g.scrollHeight>g.clientHeight+1,headingFonts:[...f.querySelectorAll('.c-cleaning-menu-heading__brand,.c-cleaning-menu-heading__title')].map(e=>getComputedStyle(e).fontSize),cards:visible.map(c=>({box:box(c),white:box(c.querySelector('.c-category-simple-card__top')),blue:box(c.querySelector('.c-category-simple-card__bottom')),icon:box(c.querySelector('.c-category-simple-card__icon')),font:getComputedStyle(c.querySelector('.c-category-simple-card__text')).fontSize,href:c.getAttribute('href')})),clipped,overflow:document.documentElement.scrollWidth-document.documentElement.clientWidth};
  });
}
(async()=>{
 fs.mkdirSync(out,{recursive:true});const b=await chromium.launch({channel:'chrome',headless:true});const p=await b.newPage();const cases=[],errors=[];
 let capture=false;
 await p.route('**/*',r=>{const u=new URL(r.request().url());if(u.origin!==new URL(origin).origin)return r.abort();if(!capture&&u.pathname.startsWith('/assets/images/')&&!/header|footer|common-parts|crystal-clean-home|cleaning-illustrations/.test(u.pathname))return r.abort();return r.continue();});p.on('pageerror',e=>errors.push(e.message));
 const run=async(route,size)=>{await p.setViewportSize({width:size[0],height:size[1]});const url=origin+'/house-cleaning/'+route+'/';if(p.url()!==url)await p.goto(url,{waitUntil:'domcontentloaded'});await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(100);const r={route,...await measure(p)};try{assert(r.frame.bottom<=Math.min(size[1],800)+1,'top frame extends below viewport');assert(r.frame.y>=r.header.bottom-1,'header overlap');assert(r.overflow<=1,'horizontal overflow');assert(!r.clipped.length,'card text clipped');assert(r.hero.height>=112,'hero too short');assert(r.headingFonts.every(v=>v===(size[0]<768?'17px':'20px')),'heading differs from reference');const w=size[0]<768?72:100;assert(r.cards.every(c=>Math.abs(c.icon.width-w)<1&&Math.abs(c.icon.height-w*10/13)<1),'selector icon differs from reference');assert(r.cards.every(c=>Math.abs(c.white.height-(w*10/13+(w===72?28:32)))<1),'white card area differs from reference');assert(r.cards.filter(c=>c.box.y<r.grid.bottom-1).every(c=>c.box.bottom<=r.grid.bottom+1),'partially visible card row');if(r.scrollable){await p.locator('.p-page-anchors__cards').evaluate(e=>e.scrollTop=e.scrollHeight);const last=await p.locator('.p-page-anchors__cards > a').last().boundingBox();const grid=await p.locator('.p-page-anchors__cards').boundingBox();assert(last.y+last.height<=grid.y+grid.height+1,'last card inaccessible');await p.locator('.p-page-anchors__cards').evaluate(e=>e.scrollTop=0);}r.passed=true;}catch(e){r.passed=false;r.reason=e.message;}cases.push(r);return r;};
 try {
  for(const route of routes){for(const size of process.argv.includes('--quick')?[[1439,799],[1280,551],[414,688],[320,568]]:sizes)await run(route,size);console.log(JSON.stringify({route,checked:true}));}
  for(const size of process.argv.includes('--quick')?[]:[...sizes].reverse())await run('water',size);
  capture=true;
  for(const [route,size] of [['aircon',[1439,799]],['water',[1280,551]],['room',[414,688]],['water',[320,568]]]){await p.goto(origin+'/house-cleaning/'+route+'/',{waitUntil:'load'});await run(route,size);await p.screenshot({path:path.join(out,`${route}-${size[0]}.jpg`),quality:76});}
  await run('water',[414,688]);
  const g=p.locator('.p-page-anchors__cards');await g.evaluate(e=>{const a=e.firstElementChild.cloneNode(true);a.dataset.testAdded='true';e.append(a);});await p.waitForTimeout(100);let modified=await measure(p);assert(modified.frame.bottom<=689);
  await g.evaluate(e=>e.querySelector('[data-test-added]').remove());await p.waitForTimeout(100);assert((await measure(p)).frame.bottom<=689);
  await p.goto(origin+'/',{waitUntil:'domcontentloaded'});await p.setViewportSize({width:1439,height:799});await p.waitForTimeout(100);
  const tabs=await p.locator('.home-concerns__places').boundingBox();assert(Math.abs(tabs.width-750)<1,'HOME tab bar not 750px');
  for(const button of await p.locator('[data-concern-place]').all()){await button.click();assert.equal(await button.getAttribute('aria-selected'),'true');}
  await p.locator('[data-concern-place]').first().click();await p.locator('.home-concerns__places').evaluate(e=>window.scrollTo({top:e.getBoundingClientRect().top+scrollY-160,behavior:'instant'}));await p.waitForTimeout(350);await p.screenshot({path:path.join(out,'home-concerns-1439.jpg'),quality:76});
  const report={origin,cases,errors,cardAdditionRemoval:true,homeTabWidth:tabs.width,homeFiveTabs:true,passed:cases.every(c=>c.passed)&&!errors.length};fs.writeFileSync(path.join(out,process.argv.includes('--quick')?'quick.json':(origin.includes('127.')?'local.json':'public.json')),JSON.stringify(report,null,2));
  console.log(JSON.stringify({cases:cases.length,passed:report.passed,failures:cases.filter(c=>!c.passed).map(c=>({route:c.route,size:[c.width,c.height],end:c.frame.bottom,clipped:c.clipped,reason:c.reason})),errors}));assert(report.passed);
 } finally {await b.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
