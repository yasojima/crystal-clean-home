const fs=require('fs'),path=require('path'),assert=require('assert/strict');
const {chromium}=require('C:/Users/yasoj/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const root=path.resolve(__dirname,'..');
const origin=process.argv[2]||'http://127.0.0.1:8773';
const out=process.argv[3]||path.join(root,'evidence/2026-10-08/office-reference-rebuild/local');
const sizes=[[1440,800],[1920,1080],[1280,551],[1024,600],[900,800],[899,800],[768,1024],[600,800],[414,688],[390,844],[375,667],[320,568]];
const titles=['エアコン清掃','床・カーペット','除菌・抗菌','引き渡し清掃'];
const labels=['フロア','カーペット','ガラス・サッシ','業務用エアコン','照明器具','レンジフード','厨房器具','浴室・シャワー','トイレ','廊下・階段','洗面所','ベランダ'];
(async()=>{
  fs.mkdirSync(out,{recursive:true});
  const browser=await chromium.launch({channel:'chrome',headless:true});
  const page=await browser.newPage(),errors=[],records=[];
  page.on('pageerror',e=>errors.push(e.message));
  try{
    await page.goto(origin+'/business/cleaning/',{waitUntil:'networkidle'});
    await page.locator('.office-wf img').evaluateAll(async imgs=>{imgs.forEach(i=>i.loading='eager');await Promise.all(imgs.map(i=>i.decode()));});
    assert.equal(await page.locator('.office-wf h1').textContent(),'法人向けサービス');
    assert.equal(await page.locator('.office-wf h1').count(),1);
    assert.equal(await page.locator('.office-wf__intro p').count(),2);
    assert.deepEqual(await page.locator('.office-wf__service h3').allTextContents(),titles);
    assert.deepEqual(await page.locator('.office-wf__gallery figcaption').allTextContents(),labels);
    assert.equal(await page.locator('.office-wf__closing p').count(),1);
    assert.equal(await page.locator('.office-wf__hero,.office-wf__mosaic,.office-wf__kitchen,.office-wf__points,.office-wf__contact,.office-wf br,.office-wf svg').count(),0);
    const body=await page.locator('.office-wf').textContent();
    assert(!/イエキレ|iekire|1988|2000㎡|株式会社|ビルメンテナンス発|光触媒コーティング/i.test(body));
    assert.equal(await page.locator('.c-header').count(),1);
    assert.equal(await page.locator('.c-footer').count(),1);
    for(const [width,height] of [...sizes,...sizes.slice().reverse()]){
      await page.setViewportSize({width,height});
      await page.evaluate(async()=>{scrollTo({top:0,behavior:'instant'});await document.fonts.ready;await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)));});
      const r=await page.evaluate(()=>{
        const box=e=>{const r=e.getBoundingClientRect();return {x:r.x,y:r.y,w:r.width,h:r.height,right:r.right,bottom:r.bottom};};
        const container=box(document.querySelector('.office-wf__container'));
        const cards=[...document.querySelectorAll('.office-wf__service')].map(e=>({copy:box(e.querySelector('.office-wf__service-copy')),photo:box(e.querySelector('img')),panel:box(e.querySelector('.office-wf__service-panel'))}));
        const textOverflow=[];
        for(const e of document.querySelectorAll('.office-wf p,.office-wf h1:not(.c-house-cleaning-mv__sr-heading),.office-wf h2,.office-wf h3,.office-wf figcaption')){
          const bounds=box(e),range=document.createRange();range.selectNodeContents(e);
          for(const rect of range.getClientRects())if(rect.left<bounds.x-1||rect.right>bounds.right+1||rect.bottom>bounds.bottom+1)textOverflow.push(e.textContent);
        }
        return {width:innerWidth,height:innerHeight,container,cards,textOverflow,overflow:Math.max(0,document.documentElement.scrollWidth-document.documentElement.clientWidth),galleryColumns:getComputedStyle(document.querySelector('.office-wf__gallery')).gridTemplateColumns.split(' ').length,images:[...document.querySelectorAll('.office-wf img')].every(i=>i.complete&&i.naturalWidth>0&&i.getAttribute('src').startsWith('/assets/images/office-cleaning/')),bodyFont:parseFloat(getComputedStyle(document.querySelector('.office-wf')).fontSize)};
      });
      assert(r.overflow<=1,`Horizontal overflow at ${width}`);
      assert.deepEqual(r.textOverflow,[],`Clipped text at ${width}`);
      assert(r.images&&r.bodyFont>=15);
      assert.equal(r.galleryColumns,width<768?2:4);
      for(const [i,c] of r.cards.entries()){
        assert(c.photo.x>=r.container.x-1&&c.photo.right<=r.container.right+1,`Photo escapes section at ${width}`);
        assert(Math.abs(c.photo.w/c.photo.h-1.5)<.001);
        if(width<768){
          assert(c.photo.bottom<=c.copy.y+1,'Mobile copy must follow its photo');
          assert(Math.abs(c.photo.w-c.copy.w)<1);
        }else{
          assert(Math.abs(c.photo.y-(c.panel.y-32))<1,'Photo must rise above its panel');
          assert(i%2===0?c.copy.right<=c.photo.x:c.photo.right<=c.copy.x,'Alternating photo and copy overlap');
        }
      }
      r.passed=true;records.push(r);
    }
    for(const width of [1440,414]){
      await page.setViewportSize({width,height:width===1440?800:688});
      await page.evaluate(async()=>{scrollTo({top:0,behavior:'instant'});await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)));});
      await page.screenshot({path:path.join(out,`first-view-${width}.png`)});
      await page.screenshot({path:path.join(out,`page-${width}.jpg`),quality:80,fullPage:true});
      for(const [selector,name] of [['.office-wf__service-list','services'],['.office-wf__range-section','gallery']]){
        const clip=await page.locator(selector).boundingBox();
        await page.screenshot({path:path.join(out,`${name}-${width}.png`),fullPage:true,clip});
      }
    }
    await page.goto(origin+'/',{waitUntil:'load'});
    assert.equal(await page.locator('a.home-business-guide').getAttribute('href'),'/business/cleaning/');
    await page.locator('a.home-business-guide').click();await page.waitForURL('**/business/cleaning/');
    assert(await page.locator('.office-wf .c-house-cleaning-mv__text').isVisible());
    assert.deepEqual(errors,[]);
    fs.writeFileSync(path.join(out,'report.json'),JSON.stringify({origin,conditions:records.length,records,errors,homeLink:true,serviceTitles:titles,galleryLabels:labels,passed:true},null,2));
    console.log(JSON.stringify({conditions:records.length,passed:true,errors}));
  }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
