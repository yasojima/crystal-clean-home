const fs = require('fs');
const path = require('path');
const assert = require('assert/strict');
const {chromium} = require('C:/Users/yasoj/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const root = path.resolve(__dirname, '..');
const site = path.join(root, 'source/site');
const origin = process.argv[2] || 'http://127.0.0.1:8769';
const output = process.argv[3] || 'evidence/2026-10-04/sections/shared-ui';
const files = directory => fs.readdirSync(directory, {withFileTypes:true}).flatMap(entry => entry.isDirectory() ? files(path.join(directory,entry.name)) : [path.join(directory,entry.name)]);
const routes = files(site).filter(file => file.endsWith('.html')).map(file => '/' + path.relative(site,file).replaceAll('\\','/').replace(/index\.html$/,''));
const styles = ['fontFamily','fontSize','fontWeight','lineHeight','color','backgroundColor','padding','gap','borderWidth','borderRadius','display'];
async function measure(page) {
  await page.evaluate(async () => {
    await document.fonts.ready;
    const images = [...document.querySelectorAll('header.c-header img,footer.c-footer img')];
    images.forEach(image => image.loading='eager');
    await Promise.all(images.map(image => image.decode().catch(() => {})));
  });
  return page.evaluate(styles => {
    const parts = {};
    for (const selector of ['header.c-header','footer.c-footer']) {
      const root = document.querySelector(selector), origin = root.getBoundingClientRect();
      parts[selector] = [root,...root.querySelectorAll('*')].filter(node => node.getBoundingClientRect().width > 0 && node.getBoundingClientRect().height > 0).map(node => {
        const rect = node.getBoundingClientRect(), style = getComputedStyle(node);
        return {tag:node.tagName,classes:node.className,rect:{x:rect.x-origin.x,y:rect.y-origin.y,width:rect.width,height:rect.height},style:Object.fromEntries(styles.map(key=>[key,style[key]])),image:node.tagName==='IMG'?{src:node.getAttribute('src'),width:node.naturalWidth,height:node.naturalHeight}:null};
      });
    }
    return parts;
  }, styles);
}
function compare(actual, reference) {
  for (const selector of Object.keys(reference)) {
    assert.equal(actual[selector].length,reference[selector].length,`${selector} visible element count`);
    for(let index=0;index<reference[selector].length;index++) {
      const a=actual[selector][index],r=reference[selector][index],label=`${selector} ${r.classes||r.tag}`;
      assert.deepEqual(a.style,r.style,`${label} styles differ`);
      assert.deepEqual(a.image,r.image,`${label} image differs or failed to load`);
      for(const key of Object.keys(r.rect))assert(Math.abs(a.rect[key]-r.rect[key])<.15,`${label} ${key} differs: ${a.rect[key]} / ${r.rect[key]}`);
    }
  }
}
(async () => {
  fs.mkdirSync(output,{recursive:true});
  const browser=await chromium.launch({channel:'chrome',headless:true}),checks=[],references=[];
  try {for(const viewport of [{width:1440,height:800},{width:414,height:688}]) {
    const context=await browser.newContext({viewport,isMobile:viewport.width<768,hasTouch:viewport.width<768}),page=await context.newPage(),runtime=[];
    page.on('pageerror',error=>runtime.push(error.message));
    await page.goto(origin+'/house-cleaning/aircon/');const reference=await measure(page);references.push({viewport,reference});
    for(const route of routes) {
      const check={route,viewport,passed:false};runtime.length=0;
      try {const response=await page.goto(origin+route);assert.equal(response.status(),200);compare(await measure(page),reference);assert.deepEqual(runtime,[],'runtime errors');check.passed=true;}
      catch(error){check.reason=error.message;console.log(JSON.stringify(check));}
      checks.push(check);
    }
    await context.close();console.log(JSON.stringify({viewport,completed:routes.length}));
  }}finally{await browser.close();}
  const report={checkedAt:new Date().toISOString(),origin,engine:'Chrome',pages:routes.length,cases:checks.length,passed:checks.every(check=>check.passed),references,checks};
  fs.writeFileSync(path.join(output,'all-pages-layout.json'),JSON.stringify(report,null,2)+'\n');
  console.log(JSON.stringify({cases:checks.length,passed:report.passed}));process.exitCode=report.passed?0:1;
})().catch(error=>{console.error(error);process.exit(1)});
