const fs = require('fs');
const path = require('path');
const assert = require('assert/strict');
const {chromium} = require('C:/Users/yasoj/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const root = path.resolve(__dirname,'..');
const site = path.join(root,'source/site');
const origin = process.argv[2] || 'http://127.0.0.1:8773';
const out = process.argv[3] || path.join(root,'evidence/2026-10-07/footer-fit');
const collect = dir => fs.readdirSync(dir,{withFileTypes:true}).flatMap(e=>e.isDirectory()?collect(path.join(dir,e.name)):[path.join(dir,e.name)]);
const routes = collect(site).filter(p=>p.endsWith('.html')).map(p=>'/'+path.relative(site,p).replaceAll('\\','/').replace(/index\.html$/,''));
const sizes = [[1920,1080],[1440,800],[1366,650],[1280,551],[1024,600],[992,700],[768,800],[600,800],[440,852],[430,852],[414,688],[393,852],[390,844],[375,812],[320,568]];
async function bottom(page) {
  await page.waitForLoadState("load");
  await page.evaluate(async()=>{
    document.querySelectorAll('footer img').forEach(i=>i.loading='eager');
    document.body.getBoundingClientRect();
    await document.fonts.ready;
    await Promise.all([...document.querySelectorAll('footer img')].map(i=>i.decode().catch(()=>{})));
    window.scrollTo({top:document.documentElement.scrollHeight,behavior:'instant'});
    await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)));
    await new Promise(r=>setTimeout(r,120));
    window.scrollTo({top:document.documentElement.scrollHeight,behavior:'instant'});
    await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)));
    window.scrollTo({top:document.documentElement.scrollHeight,behavior:'instant'});
    await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)));
  });
}
async function measure(page) {
  return page.evaluate(()=>{
    const header=document.querySelector('header.c-header'),footer=document.querySelector('footer.c-footer');
    const h=header.getBoundingClientRect(),f=footer.getBoundingClientRect();
    const floating=[...document.querySelectorAll('.home-quick-estimate,#js-floating,.c-corporate-floating')];
    const phone=footer.querySelector(innerWidth<768?'.footer-tel-sp':'.footer-tel-pc').getBoundingClientRect();
    return {width:innerWidth,height:innerHeight,header:h.height,headerContained:[...header.querySelectorAll(".c-header__logo,.c-header__icons,.c-header-contact,.c-header__navigation")].filter(e=>e.getBoundingClientRect().height>0).every(e=>e.getBoundingClientRect().bottom<=h.bottom+1),footer:f.height,footerTop:f.top,footerBottom:f.bottom,phoneTop:phone.top,overlap:Math.max(0,h.bottom-f.top),bottomGap:innerHeight-f.bottom,overflow:document.documentElement.scrollWidth-document.documentElement.clientWidth,spacing:getComputedStyle(footer).getPropertyValue('--footer-fit-space'),floatersHidden:floating.every(e=>getComputedStyle(e).visibility==='hidden'||getComputedStyle(e).display==='none'),floaters:floating.map(e=>({classes:e.className,visibility:getComputedStyle(e).visibility,display:getComputedStyle(e).display})),mobileHeaderVisible:innerWidth>=768||header.classList.contains('is-footer-visible'),rows:footer.querySelectorAll('.aircon-footer-menu__row').length};
  });
}
function check(record,strict=true) {
  assert(record.overflow<=1,'horizontal overflow');
  assert(record.headerContained,'header child extends outside its frame');
  assert(record.floatersHidden,'floating CTA covers footer');
  assert(record.mobileHeaderVisible,'mobile header absent at end');
  assert.equal(record.rows,5);
  if(strict){assert(record.overlap<=1,'header overlaps footer');assert(Math.abs(record.bottomGap)<=1,'footer does not end at viewport bottom');}
}
(async()=>{
  fs.mkdirSync(out,{recursive:true});
  const browser=await chromium.launch({channel:'chrome',headless:true});
  const page=await browser.newPage();
  await page.route('**/*', route => {
    const url=new URL(route.request().url());
    if(url.origin!==new URL(origin).origin)return route.abort();
    if(url.pathname.startsWith('/assets/images/')&&!/header|footer|common-parts|crystal-clean-home/.test(url.pathname))return route.abort();
    return route.continue();
  });
  const cases=[],errors=[];page.on('pageerror',e=>errors.push(e.message));
  page.on('console',m=>{if(m.type()==='error'&&m.text().includes('ResizeObserver'))errors.push(m.text());});
  const run=async(route,size,strict=true)=>{
    await page.setViewportSize({width:size[0],height:size[1]});await page.goto(origin+route,{waitUntil:'domcontentloaded'});await bottom(page);
    const record={route,...await measure(page)};try{check(record,strict);record.passed=true;}catch(e){record.passed=false;record.reason=e.message;}cases.push(record);console.log(JSON.stringify({route,width:size[0],passed:record.passed,...(!record.passed?record:{})}));return record;
  };
  try {
    for(const size of sizes)await run('/',size,![992,768,600].includes(size[0]));
    for(const size of [...sizes].reverse())await run('/beginner/',size,![992,768,600].includes(size[0]));
    for(const size of process.argv.includes("--quick")?[]:[[1280,551],[414,688]]) {
      for(const route of routes)await run(route,size);
      console.log(JSON.stringify({viewport:size,pages:routes.length}));
    }
    for(const size of [[1280,551],[414,688]]) {
      await run('/',size);
      const before=await measure(page);
      await page.evaluate(()=>{const s=document.createElement('section');s.id='test-extra-section';s.style.height='4000px';document.querySelector('main').append(s);});
      await bottom(page);const added=await measure(page);check(added);assert(Math.abs(added.footer-before.footer)<=1);
      await page.evaluate(()=>document.querySelector('#test-extra-section').remove());await bottom(page);check(await measure(page));
      await page.locator('.c-header__menu.js-menu-modal-opener').click();
      assert.equal(await page.locator('.c-header__menu.js-menu-modal-opener').getAttribute('aria-expanded'),'true');
      await page.keyboard.press('Escape');await bottom(page);check(await measure(page));
      await page.screenshot({path:path.join(out,`footer-${size[0]}.jpg`),quality:76});
    }
    await run('/',[320,568]);await page.screenshot({path:path.join(out,'footer-320.jpg'),quality:76});
    const report={origin,cases,errors,sectionAdditionAndRemoval:true,menuAtFooter:true,passed:cases.every(c=>c.passed)&&!errors.length};
    fs.writeFileSync(path.join(out,process.argv.includes('--quick')?'matrix.json':(origin.startsWith('http://127.')?'local.json':'public.json')),JSON.stringify(report,null,2));
    console.log(JSON.stringify({cases:cases.length,passed:report.passed,failures:cases.filter(c=>!c.passed),errors}));
    assert(report.passed,'footer checks failed');
  } finally {await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
