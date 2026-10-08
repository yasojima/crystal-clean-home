const fs=require('fs'),path=require('path'),assert=require('assert/strict');
const {chromium}=require('C:/Users/yasoj/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const root=path.resolve(__dirname,'..');
const origin=process.argv[2]||'http://127.0.0.1:8773';
const out=process.argv[3]||path.join(root,'evidence/2026-10-08/office-integration/local');
const sizes=[[1440,800],[1920,1080],[1280,551],[1024,600],[900,800],[899,800],[768,1024],[600,800],[414,688],[390,844],[375,667],[320,568]];
(async()=>{
  fs.mkdirSync(out,{recursive:true});
  const browser=await chromium.launch({channel:'chrome',headless:true});
  const page=await browser.newPage();const errors=[],records=[];
  page.on('pageerror',e=>errors.push(e.message));
  try{
    await page.goto(origin+'/business/cleaning/',{waitUntil:'networkidle'});
    await page.locator('.office-wf img').evaluateAll(async imgs=>{imgs.forEach(i=>i.loading='eager');await Promise.all(imgs.map(i=>i.decode()));});
    assert.equal(await page.locator('.c-reasons__item').count(),3);
    assert.equal(await page.locator('.office-wf__gallery figure').count(),8);
    assert.equal(await page.locator('.office-wf br').count(),0);
    assert.equal(await page.locator('.office-wf__hero a').count(),1);
    assert.equal(await page.locator('.office-wf__mosaic-ellipse,.office-wf__basin-glaze').count(),0);
    for(const [width,height] of [...sizes,...sizes.slice().reverse()]){
      await page.setViewportSize({width,height});
      await page.evaluate(async()=>{scrollTo(0,0);await document.fonts.ready;await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)));});
      const r=await page.evaluate(()=>{
        const box=s=>{const r=document.querySelector(s).getBoundingClientRect();return {x:r.x,y:r.y,w:r.width,h:r.height,right:r.right,bottom:r.bottom};};
        const hero=box('.office-wf__hero'),copy=box('.office-wf__hero-copy'),photo=box('.office-wf__kitchen-pair'),text=box('.office-wf__kitchen-copy');
        const left=box('.office-wf__kitchen-pair figure:first-child'),right=box('.office-wf__kitchen-pair figure:last-child');
        const mat=box('.office-wf__mosaic-mat'),basin=box('.office-wf__basin');
        const mosaic=box('.office-wf__mosaic');
        const bodyBottom=Math.max(...[...document.querySelectorAll('.office-wf__mosaic-body-intro,.office-wf__mosaic-body span')].map(e=>e.getBoundingClientRect().bottom));
        const paragraph=document.querySelector('.office-wf__kitchen-copy'),node=paragraph.firstChild,copyText=node.textContent,lines=new Map();
        for(let i=0;i<copyText.length;i++){const range=document.createRange();range.setStart(node,i);range.setEnd(node,i+1);const y=Math.round(range.getBoundingClientRect().top);lines.set(y,(lines.get(y)||'')+copyText[i]);}
        const kitchenLines=[...lines.values()];
        return {width:innerWidth,height:innerHeight,overflow:Math.max(0,document.documentElement.scrollWidth-document.documentElement.clientWidth),hero,copy,photo,text,mosaic,bodyBottom,kitchenLines,equalPhotos:Math.abs(left.w-right.w)<.1&&Math.abs(left.h-right.h)<.1,bandEndsAtBasin:Math.abs(mat.bottom-basin.y)<1,translucentBand:getComputedStyle(document.querySelector(".office-wf__mosaic-mat"),"::after").backgroundColor==="rgba(231, 238, 240, 0.62)",noPhotoBackdrop:getComputedStyle(document.querySelector(".office-wf__carpet"),"::before").content==="none",bodyFont:parseFloat(getComputedStyle(document.querySelector('.office-wf__mosaic-body')).fontSize),bodyWriting:getComputedStyle(document.querySelector('.office-wf__mosaic-body-intro')).writingMode,galleryColumns:getComputedStyle(document.querySelector('.office-wf__gallery')).gridTemplateColumns.split(' ').length,pointColumns:getComputedStyle(document.querySelector('.c-reasons')).gridTemplateColumns.split(' ').length,pointsWidth:box('.office-wf__points').w,clientWidth:document.documentElement.clientWidth,images:[...document.querySelectorAll('.office-wf img')].every(i=>i.complete&&i.naturalWidth>0)};
      });
      assert(r.overflow<=1);assert(r.hero.bottom<=height+1);
      assert(r.copy.y>=r.hero.y-.1&&r.copy.bottom<=r.hero.bottom+.1);
      assert(r.copy.x>=r.hero.x&&r.copy.right<=r.hero.right+1);
      assert(r.equalPhotos&&r.bandEndsAtBasin&&r.images);
      assert(r.translucentBand&&r.noPhotoBackdrop);
      assert(Math.abs(r.photo.w/r.photo.h-5/3)<.001);
      assert(r.text.x>=r.photo.x-.1&&r.text.right<=r.photo.right+.1);
      assert.equal(r.galleryColumns,width<768?2:4);
      assert.equal(r.pointColumns,width<1024?1:3);
      assert(Math.abs(r.pointsWidth-r.hero.w)<1,JSON.stringify({width,points:r.pointsWidth,hero:r.hero.w}));
      assert(r.bodyFont>=12);
      assert(r.bodyBottom<=r.mosaic.bottom+1,'Introduction text exceeds its section');
      assert(r.kitchenLines.at(-1).length>=8,'Kitchen paragraph leaves an isolated short ending');
      assert.equal(r.bodyWriting,width<900?'horizontal-tb':'vertical-rl');
      r.passed=true;records.push(r);
    }
    for(const width of [1440,414]){
      await page.setViewportSize({width,height:width===1440?800:688});await page.evaluate(()=>scrollTo(0,0));
      await page.screenshot({path:path.join(out,`first-view-${width}.png`)});
      await page.screenshot({path:path.join(out,`page-${width}.jpg`),quality:80,fullPage:true});
      for(const [selector,name] of [['.office-wf__kitchen','kitchen'],['.office-wf__mosaic','introduction']]){
        const clip=await page.locator(selector).boundingBox();
        await page.screenshot({path:path.join(out,`${name}-${width}.png`),fullPage:true,clip});
      }
    }
    const dialogPromise=page.waitForEvent('dialog');
    const clicking=page.locator('.office-wf__hero .office-wf__inquiry-link').click();
    const dialog=await dialogPromise;const dialogText=dialog.message();await dialog.dismiss();await clicking;
    assert.equal(dialogText,'デモ表示のためリンク未設定です。');
    await page.goto(origin+'/',{waitUntil:'load'});
    assert.equal(await page.locator('a.home-business-guide').getAttribute('href'),'/business/cleaning/');
    await page.locator('a.home-business-guide').click();await page.waitForURL('**/business/cleaning/');
    assert(await page.locator('.office-wf__hero h1').isVisible());
    assert.deepEqual(errors,[]);
    fs.writeFileSync(path.join(out,'report.json'),JSON.stringify({origin,conditions:records.length,records,errors,homeLink:true,consultationDemo:dialogText,passed:true},null,2));
    console.log(JSON.stringify({conditions:records.length,passed:true,errors}));
  }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
