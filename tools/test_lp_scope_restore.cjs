const fs = require('fs');
const path = require('path');
const assert = require('assert/strict');
const {execFileSync} = require('child_process');
const {chromium} = require('C:/Users/yasoj/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const root = path.resolve(__dirname, '..');
const deploy = 'C:/Users/yasoj/AppData/Local/Temp/cch-pages-deploy-20261003';
const out = path.join(root, 'evidence/2026-10-07/lp-scope-restore');
const candidate = fs.readFileSync(path.join(root,'source/site/assets/css/beginner-lp.css'));
const original = execFileSync('git',['show','b3de973:source/site/assets/css/beginner-lp.css'],{cwd:root});
const origin = process.argv[2] || 'http://127.0.0.1:8773';
const publicMode = origin.startsWith('https:');
(async()=>{
  fs.mkdirSync(out,{recursive:true});
  const browser = await chromium.launch({channel:'chrome',headless:true});
  const page = await browser.newPage();
  let useOriginal = false;
  const errors=[];
  page.on('pageerror',e=>errors.push(e.message));
  if(!publicMode) await page.route('**/*',async r=>{
    const u=new URL(r.request().url());
    if(u.origin!==new URL(origin).origin) return r.abort();
    if(u.pathname==='/assets/css/beginner-lp.css') return r.fulfill({body:useOriginal?original:candidate,contentType:'text/css'});
    let file=path.join(deploy,decodeURIComponent(u.pathname));
    if(fs.existsSync(file)&&fs.statSync(file).isDirectory()) file=path.join(file,'index.html');
    if(!fs.existsSync(file)) return r.abort();
    return r.fulfill({path:file});
  });
  const metrics=()=>page.evaluate(()=>{
    const canvas=document.querySelector('.lp-canvas');const r=canvas.getBoundingClientRect();
    const nodes=[...canvas.querySelectorAll('section,.lp-estimate-button,.lp-opening-actions,.lp-cta-action,.lp-services,.lp-voices')].map(e=>{
      const b=e.getBoundingClientRect(),s=getComputedStyle(e);
      return [e.id||e.className,b.width,b.height,s.paddingTop,s.paddingBottom,s.fontSize];
    });
    return {width:innerWidth,height:innerHeight,available:canvas.parentElement.getBoundingClientRect().width,canvas:{x:r.x,width:r.width},overflow:document.documentElement.scrollWidth-document.documentElement.clientWidth,nodes};
  });
  const records=[];
  try{
    for(const [width,height] of [[1439,799],[1440,800],[1920,1080],[768,800],[1280,551],[1366,650],[1024,600],[414,688],[320,568]]){
      await page.setViewportSize({width,height});
      useOriginal=false;await page.goto(origin+'/beginner/?lp_restore=2026100702',{waitUntil:'load'});await page.evaluate(()=>document.fonts.ready);
      const current=await metrics();console.log(JSON.stringify({width,height,canvas:current.canvas,available:current.available}));assert(current.overflow<=1,`${width} horizontal overflow`);
      const reduced=width>=768&&height<=720;
      if(reduced){assert(current.canvas.width<=880.5);assert(Math.abs(current.canvas.x-(current.available-current.canvas.width)/2)<=1);}
      else{
        if(!publicMode){useOriginal=true;await page.reload({waitUntil:'load'});await page.evaluate(()=>document.fonts.ready);const before=await metrics();assert.deepEqual(current.canvas,before.canvas,`${width} original width not restored`);assert.deepEqual(current.nodes,before.nodes,`${width} existing LP layout changed`);}
      }
      records.push({width,height,canvas:current.canvas,available:current.available,reduced,overflow:current.overflow,unchangedOutsideScope:!reduced,passed:true});
    }
    if(!publicMode){
      useOriginal=false;
      for(const [width,height] of [[1439,799],[1280,551],[414,688]]){
        await page.setViewportSize({width,height});await page.goto(origin+'/beginner/',{waitUntil:'load'});
        await page.locator('#first-concerns').evaluate(e=>scrollTo(0,e.getBoundingClientRect().top+scrollY-document.querySelector('header').offsetHeight));
        await page.waitForTimeout(150);await page.screenshot({path:path.join(out,`${width}-${height}.jpg`),quality:78});
      }
    }
    const report={origin,conditions:records.length,records,errors,passed:!errors.length};
    fs.writeFileSync(path.join(out,publicMode?'public.json':'local.json'),JSON.stringify(report,null,2));
    console.log(JSON.stringify(report));assert(report.passed);
  }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
