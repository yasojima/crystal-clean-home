const fs = require('fs');
const path = require('path');
const assert = require('assert/strict');
const {chromium, webkit} = require(process.env.PLAYWRIGHT_MODULE || 'C:/Users/yasoj/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const origin = process.argv[2] || 'https://yasojima.github.io';
const output = process.argv[3] || 'evidence/2026-10-04/recheck/sliders';
fs.mkdirSync(output, {recursive: true});

async function state(comparison) {
  return comparison.evaluate(e => {
    const handle = e.querySelector('[role="slider"]'), rect = e.getBoundingClientRect();
    return {
      split: parseFloat(e.style.getPropertyValue('--compare-split')),
      aria: Number(handle.getAttribute('aria-valuenow')),
      description: handle.getAttribute('aria-valuetext'),
      width: rect.width, height: rect.height, scroll: scrollY,
      bodyOverflow: getComputedStyle(document.body).overflow,
      pageOverflow: document.documentElement.scrollWidth > innerWidth + 1,
      beforeClip: getComputedStyle(e.querySelector(':scope > .c-compare-image__item:first-child')).clipPath,
      afterClip: getComputedStyle(e.querySelector(':scope > .c-compare-image__item:nth-child(2)')).clipPath,
      handlePosition: (handle.getBoundingClientRect().left+handle.getBoundingClientRect().width/2-rect.left)/rect.width*100,
      labels: [...e.querySelectorAll('.c-aircon-compare__label')].map(n => ({text:n.textContent, hidden:n.hidden})),
      images: [...e.querySelectorAll('img')].map(n => ({src:n.src, width:n.naturalWidth, height:n.naturalHeight, complete:n.complete})),
    };
  });
}
function check(s, expected, initial) {
  assert(Math.abs(s.split - expected) < 1.5, `split ${s.split}, expected ${expected}`);
  assert.equal(s.aria, Math.round(s.split));
  assert.equal(s.beforeClip,'none','Before base image is clipped');
  const clipped=s.afterClip.match(/([\d.]+)%\)$/);
  assert(clipped&&Math.abs(Number(clipped[1])-s.split)<.02,'After image clipping differs from split');
  assert(Math.abs(s.handlePosition-s.split)<.2,'slider handle differs from visible split');
  assert.equal(s.description, `清掃前${s.aria}%、清掃後${Math.round(100-s.split)}%`);
  assert(Math.abs(s.width/s.height-1.5) < .01, 'comparison frame is not 3:2');
  assert(s.images.length===2 && s.images.every(i=>i.complete&&i.width===1536&&i.height===1024), 'comparison image missing or distorted');
  assert(!s.pageOverflow, 'horizontal overflow');
  if (initial) {
    assert(Math.abs(initial.scroll-s.scroll)<1, 'drag changed page scroll');
    assert.equal(s.bodyOverflow, initial.bodyOverflow, 'drag changed body overflow');
  }
  if(expected<=2) assert(s.labels[0].hidden, 'Before label is outside its visible image');
  if(expected>=98) assert(s.labels[1].hidden, 'After label is outside its visible image');
  if(expected===50) assert(s.labels.every(l=>!l.hidden), 'comparison labels did not return');
}
async function center(page, comparison) {
  await comparison.evaluate(e=>scrollTo({top:scrollY+e.getBoundingClientRect().top-innerHeight*.22,behavior:'instant'}));
  await page.waitForTimeout(600);
}

(async()=>{
  const checks=[], errors=[];
  for(const [engine, launch] of [['Chrome',()=>chromium.launch({channel:'chrome',headless:true})],['WebKit',()=>webkit.launch({headless:true})]]) {
    const browser=await launch();
    try {
      for(const width of [1734,414,320]) {
        const context=await browser.newContext({viewport:{width,height:width<768?688:1321},isMobile:width<768,hasTouch:width<768});
        const page=await context.newPage();page.setDefaultNavigationTimeout(45000);
        const runtime=[];page.on('pageerror',e=>runtime.push(e.message));
        await page.goto(`${origin}/house-cleaning/aircon/`,{waitUntil:'load'});
        await page.evaluate(async()=>{
          await document.fonts.ready;
          const images=[...document.querySelectorAll('.c-aircon-compare img')];
          images.forEach(i=>i.loading='eager');await Promise.all(images.map(i=>i.decode()));
        });
        const cdp=engine==='Chrome'&&width<768?await context.newCDPSession(page):null;
        for(let tab=1;tab<=3;tab++) {
          const record={engine,width,tab,mouseDrags:[],keyboard:[],touch:null,passed:false};
          try {
            await page.locator(`#service-tab-${tab}`).evaluate(e=>scrollTo({top:scrollY+e.getBoundingClientRect().top-innerHeight*.3,behavior:'instant'}));
            await page.waitForTimeout(600);await page.locator(`#service-tab-${tab}`).click();
            const comparison=page.locator(`#service-panel-${tab} .c-aircon-compare`),handle=comparison.locator('[role="slider"]');
            await center(page,comparison);record.initial=await state(comparison);check(record.initial,50);
            assert.equal(await handle.getAttribute('aria-valuemin'),'0');assert.equal(await handle.getAttribute('aria-valuemax'),'100');
            for(const fraction of [.2,.8,.02,.98]) {
              const rect=await comparison.boundingBox(),control=await handle.boundingBox();
              await page.mouse.move(control.x+control.width/2,control.y+control.height/2);await page.mouse.down();
              await page.mouse.move(rect.x+rect.width*fraction,rect.y+rect.height/2,{steps:8});
              await page.mouse.up();const s=await state(comparison);check(s,fraction*100,record.initial);record.mouseDrags.push(s);
              if(engine==='Chrome'&&tab===1&&fraction===.2&&width!==320) await comparison.screenshot({path:path.join(output,`${engine}-${width}-split20.png`),style:'.c-header,#js-floating,#viewport-hud{visibility:hidden!important;}'});
            }
            await handle.focus();
            for(const [key,expected] of [['Home',0],['ArrowRight',2],['Shift+ArrowRight',12],['ArrowLeft',10],['ArrowDown',8],['End',100],['ArrowUp',100]]) {
              await handle.press(key);const s=await state(comparison);check(s,expected,record.initial);record.keyboard.push({key,...s});
            }
            await handle.press('Home');for(let i=0;i<25;i++)await handle.press('ArrowRight');check(await state(comparison),50,record.initial);
            if(cdp) {
              const rect=await comparison.boundingBox(),control=await handle.boundingBox(),y=rect.y+rect.height/2;
              const touchPoints=[{x:control.x+control.width/2,y,id:1,radiusX:2,radiusY:2}];
              await cdp.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints});
              for(const fraction of [.45,.4,.35,.3])await cdp.send('Input.dispatchTouchEvent',{type:'touchMove',touchPoints:[{x:rect.x+rect.width*fraction,y,id:1,radiusX:2,radiusY:2}]});
              await cdp.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]});
              record.touch=await state(comparison);check(record.touch,30,record.initial);
              await handle.press('Home');for(let i=0;i<25;i++)await handle.press('ArrowRight');
            }
            const rect=await comparison.boundingBox();
            await page.mouse.move(rect.x+rect.width/2,rect.y+rect.height/2);await page.mouse.down();
            await page.mouse.move(rect.x-30,rect.y+rect.height/2,{steps:4});check(await state(comparison),0,record.initial);
            await page.mouse.move(rect.x+rect.width+30,rect.y+rect.height/2,{steps:4});check(await state(comparison),100,record.initial);
            await page.mouse.up();
            await page.mouse.move(rect.x+rect.width*.5,rect.y+rect.height/2);check(await state(comparison),100,record.initial);
            record.pointerCaptureReleased=true;
            await handle.press('Home');for(let i=0;i<25;i++)await handle.press('ArrowRight');check(await state(comparison),50,record.initial);
            assert.deepEqual(runtime,[],'runtime errors');record.passed=true;
          } catch(e) {
            record.reason=e.message;errors.push({engine,width,tab,reason:e.message});
            console.log(JSON.stringify({FAIL:record}));
          }
          checks.push(record);
          fs.writeFileSync(path.join(output,'verification.json'),JSON.stringify({origin,checked_at:new Date().toISOString(),complete:false,passed:!errors.length,checks,errors},null,2)+'\n');
        }
        await context.close();console.log(JSON.stringify({engine,width,tabs:3}));
      }
    } finally {await browser.close();}
  }
  const report={origin,checked_at:new Date().toISOString(),complete:true,passed:!errors.length,cases:checks.length,checks,errors,real_device_acceptance:false};
  fs.writeFileSync(path.join(output,'verification.json'),JSON.stringify(report,null,2)+'\n');
  console.log(JSON.stringify({cases:checks.length,passed:report.passed,errors}));process.exitCode=errors.length?1:0;
})().catch(e=>{console.error(e);process.exitCode=1;});
