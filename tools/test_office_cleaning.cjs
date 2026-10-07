const fs=require('fs'),path=require('path'),assert=require('assert/strict');
const {chromium}=require('C:/Users/yasoj/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const root=path.resolve(__dirname,'..'),origin=process.argv[2]||'http://127.0.0.1:8773',out=process.argv[3]||path.join(root,'evidence/2026-10-07/office-cleaning/local');
const sizes=[[1920,1080],[1440,800],[1439,799],[1366,650],[1280,551],[1152,600],[1024,600],[992,700],[768,800],[600,800],[440,852],[430,852],[414,688],[393,852],[390,844],[375,812],[320,568]];
(async()=>{
 fs.mkdirSync(out,{recursive:true});const browser=await chromium.launch({channel:'chrome',headless:true});const page=await browser.newPage();const errors=[],records=[];
 page.on('pageerror',e=>errors.push(e.message));await page.route('**/*',r=>{const url=new URL(r.request().url());return url.origin===new URL(origin).origin||['fonts.googleapis.com','fonts.gstatic.com'].includes(url.hostname)?r.continue():r.abort()});
 try{
  await page.goto(origin+'/business/cleaning/',{waitUntil:'load'});
  await page.locator('.office-cleaning img').evaluateAll(async imgs=>{imgs.forEach(i=>i.loading='eager');await Promise.all(imgs.map(i=>i.decode()));});
  assert.equal(await page.locator('.office-cleaning__feature').count(),4);assert.equal(await page.locator('.office-cleaning__range li').count(),12);assert.equal(await page.locator('.office-cleaning__intro img').count(),0);
  const text=await page.evaluate(()=>({intro:[...document.querySelectorAll('.office-cleaning__intro p')].map(e=>e.textContent.length),features:[...document.querySelectorAll('.office-cleaning__feature p')].map(e=>[e.textContent.length,e.querySelectorAll('br').length]),closing:[document.querySelector('.office-cleaning__closing p').textContent.length,document.querySelectorAll('.office-cleaning__closing br').length]}));
  assert.equal(text.intro.length,1);assert(text.features.every(([,breaks])=>breaks===0));assert.equal(text.closing[1],0);assert.equal(await page.locator('.office-cleaning__contact').count(),0);
  for(const [width,height] of [...sizes,...[...sizes].reverse()]){
   await page.setViewportSize({width,height});await page.evaluate(async()=>{scrollTo(0,0);await document.fonts.ready;await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)));});
   const record=await page.evaluate(()=>{
    const rect=e=>{const r=e.getBoundingClientRect();return {x:r.x,y:r.y,w:r.width,h:r.height,b:r.bottom}};
    return {width:innerWidth,height:innerHeight,overflow:document.documentElement.scrollWidth-document.documentElement.clientWidth,images:[...document.querySelectorAll('.office-cleaning img')].map(i=>({complete:i.complete,width:i.naturalWidth})),features:[...document.querySelectorAll('.office-cleaning__feature')].map(e=>({text:rect(e.querySelector('.office-cleaning__text')),image:rect(e.querySelector('figure'))})),galleryCols:getComputedStyle(document.querySelector('.office-cleaning__range ul')).gridTemplateColumns.split(' ').length};
   });
   assert(record.overflow<=1);assert(record.images.every(i=>i.complete&&i.width>0));assert.equal(record.galleryCols,width<768?2:4);
   if(width<768)assert(record.features.every(f=>f.text.y>=f.image.b-1));else assert(record.features.every((f,i)=>i%2?f.image.x<f.text.x:f.image.x>f.text.x));
   await page.evaluate(()=>scrollTo(0,document.documentElement.scrollHeight));await page.waitForTimeout(180);await page.evaluate(()=>scrollTo(0,document.documentElement.scrollHeight));
   record.footer=await page.evaluate(()=>{const h=document.querySelector('header.c-header').getBoundingClientRect(),f=document.querySelector('footer.c-footer').getBoundingClientRect();return {top:f.top,bottom:f.bottom,headerBottom:h.bottom,height:innerHeight};});
   assert(record.footer.bottom<=height+1&&record.footer.top>=record.footer.headerBottom-1);record.passed=true;records.push(record);
  }
  for(const [width,height] of [[1439,799],[1280,551],[414,688],[320,568]]){
   await page.setViewportSize({width,height});await page.evaluate(()=>scrollTo(0,0));await page.screenshot({path:path.join(out,`office-${width}.jpg`),quality:78,fullPage:true});
  }
  await page.goto(origin+'/',{waitUntil:'load'});assert.equal(await page.locator('a.home-business-guide').getAttribute('href'),'/business/cleaning/');assert.equal(await page.locator('#home-pickup .home-pickup__slot').count(),3);assert.equal(await page.locator('#home-pickup a').count(),0);assert.equal(await page.locator('.home-pickup__banner-cta').getAttribute('href'),'/house-cleaning/aircon/');
  await page.locator('a.home-business-guide').click();await page.waitForURL('**/business/cleaning/');assert(await page.locator('.office-cleaning h1').isVisible());assert.equal(await page.locator('.office-cleaning__contact').count(),0);
  const report={origin,conditions:records.length,records,text,errors,links:true,passed:!errors.length};fs.writeFileSync(path.join(out,'report.json'),JSON.stringify(report,null,2));console.log(JSON.stringify({conditions:records.length,passed:report.passed,errors}));assert(report.passed);
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
