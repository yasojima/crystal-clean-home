const fs=require('fs');
const path=require('path');
const assert=require('assert/strict');
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'C:/Users/yasoj/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const sharp=require('C:/Users/yasoj/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/sharp');
const root=path.resolve(__dirname,'..');
const routes=Object.keys(JSON.parse(fs.readFileSync(path.join(root,'source/service-pages/catalogue.json'),'utf8')).pages).filter(r=>!process.env.PHOTO_ROUTES||process.env.PHOTO_ROUTES.split(',').includes(r));
const origin=process.argv[2]||'https://yasojima.github.io';
const output=process.argv[3]||'evidence/2026-10-04/recheck/photo-frames';
fs.mkdirSync(output,{recursive:true});
(async()=>{
 const browser=await chromium.launch({channel:'chrome',headless:true}),records=[];
 try{
  for(const width of [1734,414]){
   const page=await browser.newPage({viewport:{width,height:width<768?688:1321},isMobile:width<768,hasTouch:width<768});
   const images=[];
   for(const route of routes){
    const response=await page.goto(`${origin}/house-cleaning/${route}/`,{waitUntil:'load'});assert.equal(response.status(),200);
    await page.evaluate(async()=>{await document.fonts.ready;const pictures=[...document.querySelectorAll('#service-introduction img')];pictures.forEach(i=>i.loading='eager');await Promise.all(pictures.map(i=>i.decode()));});
    const content=page.locator('#service-introduction .p-content-box');
    await content.evaluate(e=>scrollTo({top:scrollY+e.getBoundingClientRect().top,behavior:'instant'}));await page.waitForTimeout(600);
    const fileName=`${width}-${route.replaceAll('/','-')}.png`;
    const buffer=await content.screenshot({style:'.c-header,#js-floating,#viewport-hud{visibility:hidden!important;}'});
    images.push({route,buffer});
    if(route==='aircon')fs.writeFileSync(path.join(output,fileName),buffer);
    records.push({route,width,section:'introduction',captured:true});
    if(['aircon','pack','water','kitchen'].includes(route)){
     const section=page.locator('#apply > section:has([data-service-offer])');
     await section.evaluate(async e=>Promise.all([...e.querySelectorAll('img')].map(async i=>{i.loading='eager';await i.decode();})));
     await section.evaluate(e=>scrollTo({top:scrollY+e.getBoundingClientRect().top,behavior:'instant'}));await page.waitForTimeout(600);
     const offerName=`offers-${width}-${route}.png`;
     await section.screenshot({path:path.join(output,offerName),style:'.c-header,#js-floating,#viewport-hud{visibility:hidden!important;}'});
     records.push({route,width,section:'offers',file:offerName});
    }
   }
   for(let offset=0;offset<images.length;offset+=8){
    const tileWidth=width<768?310:440,tileHeight=width<768?590:350,cols=4,tiles=[];
    const batch=images.slice(offset,offset+8);
    for(let i=0;i<batch.length;i++){
     const item=batch[i],png=await sharp(item.buffer).resize({width:tileWidth-8,height:tileHeight-30,fit:'inside'}).png().toBuffer();
     const label=Buffer.from(`<svg width="${tileWidth}" height="24"><rect width="100%" height="100%" fill="white"/><text x="5" y="17" font-family="Arial" font-size="14">${item.route}</text></svg>`);
     const x=i%cols*tileWidth,y=Math.floor(i/cols)*tileHeight;
     tiles.push({input:label,left:x,top:y},{input:png,left:x+4,top:y+26});
    }
    const name=`${width}-gallery-${offset/8+1}.png`;
    await sharp({create:{width:tileWidth*cols,height:tileHeight*Math.ceil(batch.length/cols),channels:3,background:'#ddd'}}).composite(tiles).png().toFile(path.join(output,name));
   }
   await page.close();console.log(JSON.stringify({width,introductions:routes.length,offers:records.filter(r=>r.width===width&&r.section==='offers').length}));
  }
 }finally{await browser.close();}
 fs.writeFileSync(path.join(output,'screens.json'),JSON.stringify({origin,checked_at:new Date().toISOString(),records},null,2)+'\n');
})().catch(e=>{console.error(e);process.exitCode=1});
