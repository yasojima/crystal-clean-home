const fs = require('fs');
const path = require('path');
const assert = require('assert/strict');
const {chromium, webkit} = require(process.env.PLAYWRIGHT_MODULE || 'C:/Users/yasoj/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const sharp = require('C:/Users/yasoj/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/sharp');
const root = path.resolve(__dirname, '..');
const catalogue = JSON.parse(fs.readFileSync(path.join(root, 'source/service-pages/catalogue.json'), 'utf8'));
const copy = JSON.parse(fs.readFileSync(path.join(root, 'source/service-pages/copy.json'), 'utf8'));
const origin = process.argv[2] || 'http://127.0.0.1:8769';
const output = process.argv[3] || 'evidence/2026-10-04/sections/selector';
const phase = process.argv[4] || 'selector';
const sizes = (process.env.SECTION_SIZES || '1734x1321,414x688').split(',').map(s => {const [width, height] = s.split('x').map(Number); return {width, height};});
const routes = Object.keys(catalogue.pages).filter(r => !process.env.SECTION_ROUTES || process.env.SECTION_ROUTES.split(',').includes(r));
const inspectOnly = process.env.SECTION_INSPECT === '1';
const styleKeys = ['fontFamily','fontSize','fontWeight','lineHeight','letterSpacing','textAlign','color','backgroundColor','backgroundImage','padding','marginTop','marginBottom','rowGap','columnGap','borderRadius','borderColor','borderWidth','boxShadow','alignItems','justifyContent'];
const definitions = {
 selector: {root: '.c-service-selector', components: {
  heading: '.p-page-anchors__heading', card: '.c-page-anchors__anchor', top: '.c-category-simple-card__top', bottom: '.c-category-simple-card__bottom', label: '.c-category-simple-card__text', icon: '.c-category-simple-card__icon'
 }},
 concerns: {root:'#service-introduction .c-issue-list',components:{heading:'.c-issue-list__heading',card:'.c-issue-card',inner:'.c-issue-card__inner',icon:'.c-issue-card__icon-circle',text:'.c-issue-card__text'}},
 introduction: {root:'#service-introduction .p-content-box',components:{heading:'.p-content-box__heading',content:'.p-content-box__content',tabs:'.c-tab__buttons',button:'.c-tab__button[aria-selected="true"]',photo:'.c-compare-image-tab__compare-image',text:'.c-compare-image-tab__text'}},
 reasons: {root:'main > section:has(.p-reasons)',components:{heading:'.p-reasons__heading',grid:'.c-reasons',item:'.c-reasons__item',circle:'.c-reasons__card',point:'.c-reasons__point',title:'.c-reason-card__heading',text:'.c-reason-card__description',navy:'.c-reasons__navy'}},
 lineup: {root:'#apply',capture:'.c-lineup-heading',needImages:false,components:{band:'#apply > .c-lineup-heading:not(#service-sets):not(#anchor00)',title:'#apply > .c-lineup-heading:not(#service-sets):not(#anchor00) .c-lineup-heading__contain',label:'#apply > .c-lineup-heading:not(#service-sets):not(#anchor00) .c-lineup-heading__label'}},
};
assert(definitions[phase], `Unknown phase ${phase}`);
fs.mkdirSync(output, {recursive: true});
async function read(page) {
 return page.evaluate(({definition, styleKeys}) => {
  const root = document.querySelector(definition.root);
  if (!root) return null;
  const rect = node => {const r = node.getBoundingClientRect(); return {x:r.x,y:r.y,width:r.width,height:r.height};};
  const style = (node, pseudo) => {const s = getComputedStyle(node,pseudo);return Object.fromEntries(styleKeys.map(key=>[key,s[key]]));};
  const textOverflow = n => {if(!n.textContent.trim())return false;const range=document.createRange();range.selectNodeContents(n);const box=n.getBoundingClientRect();return [...range.getClientRects()].some(r=>r.left<box.left-1||r.right>box.right+1);};
  const components = {};
  for (const [key, selector] of Object.entries(definition.components)) components[key] = [...root.querySelectorAll(selector)].filter(n=>n.getBoundingClientRect().height>0).map(n=>({rect:rect(n),style:style(n),text:n.innerText||'',overflow:textOverflow(n),after:{...style(n,'::after'),content:getComputedStyle(n,'::after').content,mask:getComputedStyle(n,'::after').maskImage},mask:getComputedStyle(n).maskImage}));
  const section=root.closest('section');
  return {rect:rect(root),style:style(root),context:section?{style:style(section),before:{...style(section,'::before'),mask:getComputedStyle(section,'::before').maskImage},curves:[...section.querySelectorAll('.c-section-curve')].map(c=>({rect:rect(c),style:style(c),mask:getComputedStyle(c).maskImage}))}:null,components,images:definition.needImages===false?[]:[...root.querySelectorAll('img')].filter(i=>i.getBoundingClientRect().height>0).map(i=>({src:new URL(i.currentSrc||i.src).pathname,alt:i.alt,width:i.naturalWidth,height:i.naturalHeight})),anchors:[...root.querySelectorAll('.c-page-anchors a')].map(a=>({href:a.getAttribute('href'),exists:!!document.querySelector(a.getAttribute('href')),text:a.textContent.trim()})),overflow:document.documentElement.scrollWidth>innerWidth+1};
 }, {definition:definitions[phase], styleKeys});
}
function checkSelector(actual, reference, route, viewport) {
 assert(actual, 'missing selector');
 assert(!actual.overflow, 'page overflows horizontally');
 assert(actual.anchors.length >= 1 && actual.anchors.every(a=>a.exists), 'selector destination missing');
 for (const [key, components] of Object.entries(actual.components)) {
  assert(components.length, `missing ${key}`);
  for (const component of components) {
   const canonical = reference.components[key][0];
   assert.deepEqual(component.style, canonical.style, `${key} styles differ from aircon`);
   assert.deepEqual(component.after, canonical.after, `${key} decoration differs from aircon`);
   assert(!component.overflow, `${key} clips full text: ${component.text}`);
   if (['card','top','bottom','label'].includes(key)) assert(Math.abs(component.rect.width-canonical.rect.width)<.1, `${key} width differs`);
   if (key==='icon') {
    assert(component.mask !== 'none', 'empty selector illustration');
    assert(Math.abs(component.rect.width-canonical.rect.width)<.1 && Math.abs(component.rect.height-canonical.rect.height)<.1,'icon dimensions differ');
   }
  }
 }
 assert.equal(actual.style.padding, reference.style.padding, 'selector outside space differs');
}
function checkConcerns(actual,reference,route,viewport){
 assert(actual && !actual.overflow,'concerns missing or page overflows');
 const expected=(route.includes('/')?copy.details[route]:copy.categories[catalogue.pages[route].category]).concerns;
 assert.deepEqual(actual.components.text.map(c=>c.text.split('\n').join('')),expected.map(p=>p.join('')),'concerns do not match this service');
 assert.deepEqual(actual.context.style,reference.context.style,'section space or background differs');
 assert.deepEqual(actual.context.before,reference.context.before,'wave or arrow decoration differs');
 assert.equal(actual.context.curves.length,reference.context.curves.length);
 for(let i=0;i<actual.context.curves.length;i++){
  assert.deepEqual(actual.context.curves[i].style,reference.context.curves[i].style);
  assert.equal(actual.context.curves[i].mask,reference.context.curves[i].mask);
 }
 for(const [key,items] of Object.entries(actual.components))for(const item of items){
  const canonical=reference.components[key][0];
  assert.deepEqual(item.style,canonical.style,`${key} styles differ from aircon`);
  assert.deepEqual(item.after,canonical.after,`${key} decoration differs from aircon`);
  assert(!item.overflow,`${key} clips full text`);
  if(key!=='text')assert(Math.abs(item.rect.width-canonical.rect.width)<.1,`${key} width differs from aircon`);
  if(key==='text')assert(Math.abs(item.rect.height-canonical.rect.height)<.1,'concern text wraps beyond the original two lines');
  if(key==='card' || key==='icon')assert(Math.abs(item.rect.height-canonical.rect.height)<.1,`${key} height differs from aircon`);
 }
}
function checkIntroduction(actual,reference,route,viewport){
 assert(actual && !actual.overflow,'introduction missing or page overflows');
 for(const [key,items] of Object.entries(actual.components))for(const item of items){
  const canonical=reference.components[key][0];
  assert.deepEqual(item.style,canonical.style,`${key} styles differ from aircon`);
  assert(!item.overflow,`${key} clips full text`);
  if(['heading','content','photo'].includes(key))assert(Math.abs(item.rect.width-canonical.rect.width)<.1,`${key} width differs from aircon`);
  if(key==='photo')assert(Math.abs(item.rect.height-canonical.rect.height)<.1,'photo ratio differs from aircon');
  if(key==='heading')assert(Math.abs(item.rect.height-canonical.rect.height)<.1,'introductory heading adds unintended lines');
 }
 assert(actual.images.length && actual.images.every(i=>i.width===1536&&i.height===1024),'introduction photo missing');
}
function checkExactFrame(actual,reference){
 assert(actual && !actual.overflow,'section missing or page overflows');
 assert.deepEqual(actual.style,reference.style,'outer section styles differ');
 assert(Math.abs(actual.rect.height-reference.rect.height)<.1,'outer section height differs');
 for(const [key,items] of Object.entries(actual.components)){
  assert.equal(items.length,reference.components[key].length,`${key} count differs`);
  for(let i=0;i<items.length;i++){
   const item=items[i],canonical=reference.components[key][i];
   assert.deepEqual(item.style,canonical.style,`${key} styles differ from aircon`);
   assert.deepEqual(item.after,canonical.after,`${key} decoration differs from aircon`);
   for(const dimension of ['width','height'])assert(Math.abs(item.rect[dimension]-canonical.rect[dimension])<.1,`${key}.${dimension} differs`);
   for(const axis of ['x','y'])assert(Math.abs((item.rect[axis]-actual.rect[axis])-(canonical.rect[axis]-reference.rect[axis]))<.1,`${key}.${axis} differs within this section`);
   assert(!item.overflow,`${key} clips full text`);
  }
 }
 if(actual.context){
  assert.deepEqual(actual.context.style,reference.context.style,'section background or spacing differs');
  assert.deepEqual(actual.context.before,reference.context.before,'section arrows differ');
  assert.deepEqual(actual.context.curves.map(c=>({style:c.style,mask:c.mask})),reference.context.curves.map(c=>({style:c.style,mask:c.mask})),'section curves differ');
 }
}
function checkLineup(actual,reference,route){
 assert(actual && !actual.overflow,'lineup missing or page overflows');
 assert.equal(actual.components.band.length,catalogue.pages[route].groups.length,'lineup heading count');
 assert.deepEqual(actual.components.title.map(c=>c.text),catalogue.pages[route].groups.map(g=>g.title),'lineup title missing');
 for(const [key,items] of Object.entries(actual.components))for(const item of items){
  assert.deepEqual(item.style,reference.components[key][0].style,`${key} styles differ from aircon`);
  assert.deepEqual(item.after,reference.components[key][0].after,`${key} decoration differs from aircon`);
  assert(!item.overflow,`${key} clips title`);
 }
}
const checkPhase = {selector:checkSelector,concerns:checkConcerns,introduction:checkIntroduction,reasons:checkExactFrame,lineup:checkLineup};
async function interact(page,route,viewport){
 if(phase!=='introduction')return;
 const primary=catalogue.pages[route].groups[0].products[0];
 const subjects=route.includes('/')?[primary]:copy.categories[catalogue.pages[route].category].subjects;
 const buttons=page.locator('#service-introduction .c-tab__button');
 assert.equal(await buttons.count(),subjects.length);
 for(let i=0;i<subjects.length;i++){
  const button=buttons.nth(i);
  if(subjects.length>1){
   await button.evaluate(e=>scrollTo({top:scrollY+e.getBoundingClientRect().top-innerHeight*.35,behavior:'instant'}));
   await button.click();
  }
  assert.equal(await button.getAttribute('aria-selected'),'true','photo tab did not activate');
  const panel=page.locator('#'+await button.getAttribute('aria-controls'));
  assert(await panel.isVisible(),'photo tab panel hidden');
  const expected=copy.products[subjects[i]];
  assert.equal((await panel.locator('.c-compare-image-tab__text').innerText()).trim(),expected.description);
  if(route!=='aircon')assert((await panel.locator('.c-service-photo img').getAttribute('src')).endsWith('/'+expected.scene+'.webp'),'photo belongs to a different service');
 }
 if(subjects.length>1)await buttons.first().click();
 return {photoTabsOpened:subjects.length};
}
async function capture(page, route, engine, viewport, items) {
 const file = `${engine}-${viewport.width}-${route.replaceAll('/','-')}.png`;
 const locator = page.locator(definitions[phase].capture||definitions[phase].root).first();
 await locator.scrollIntoViewIfNeeded();
 const buffer = await locator.screenshot({animations:'disabled',style:'.c-header, #js-floating, #viewport-hud { visibility: hidden !important; }'});
 if(['aircon','pack','room','water'].includes(route))fs.writeFileSync(path.join(output,file),buffer);
 items.push({route, file, buffer});
}
async function gallery(items, engine, viewport) {
 for(let offset=0;offset<items.length;offset+=16){
  const batch=items.slice(offset,offset+16), columns=4, tileWidth=400, tileHeight=viewport.width<768?760:300;
  const overlays=[];
  for(let i=0;i<batch.length;i++){
   const png=await sharp(batch[i].buffer).resize({width:tileWidth-8,height:tileHeight-28,fit:'inside',withoutEnlargement:false}).png().toBuffer();
   const label=Buffer.from(`<svg width="400" height="24"><rect width="400" height="24" fill="white"/><text x="5" y="17" font-size="14" font-family="Arial">${batch[i].route}</text></svg>`);
   const x=(i%columns)*tileWidth,y=Math.floor(i/columns)*tileHeight;
   overlays.push({input:label,left:x,top:y},{input:png,left:x+4,top:y+26});
  }
  await sharp({create:{width:columns*tileWidth,height:Math.ceil(batch.length/columns)*tileHeight,channels:3,background:'#ddd'}}).composite(overlays).png().toFile(path.join(output,`${engine}-${viewport.width}-gallery-${Math.floor(offset/16)+1}.png`));
 }
}
(async()=>{
 const checks=[], references=[],errors=[];
 for (const [engine,launch] of [['Chrome',()=>chromium.launch({channel:'chrome',headless:true})],['WebKit',()=>webkit.launch({headless:true})]].filter(([e])=>!process.env.SECTION_ENGINES||process.env.SECTION_ENGINES.split(',').includes(e))) {
  const browser=await launch();
  try {for(const viewport of sizes){
   const context=await browser.newContext({viewport,isMobile:viewport.width<768,hasTouch:viewport.width<768});
   const page=await context.newPage();page.setDefaultTimeout(10000);
   const runtime=[];page.on('pageerror',e=>runtime.push(e.message));
   const settle=async()=>{await page.evaluate(async({selector,images})=>{await document.fonts.ready;const section=document.querySelector(selector);if(section&&images){section.querySelectorAll('img').forEach(i=>i.loading='eager');await Promise.all([...section.querySelectorAll('img')].map(i=>i.decode().catch(()=>{})));}},{selector:definitions[phase].root,images:definitions[phase].needImages!==false});};
   await page.goto(`${origin}/house-cleaning/aircon/`,{waitUntil:'load'});await settle();
   const reference=await read(page);references.push({engine,viewport,reference});
   const captures=[];
   for(const route of routes){
    const result={engine,viewport,route,passed:false};runtime.length=0;
    try {
     const response=await page.goto(`${origin}/house-cleaning/${route}/`,{waitUntil:'load'});assert.equal(response.status(),200);await settle();
     result.measurement=await read(page);
     if(!inspectOnly) checkPhase[phase](result.measurement,reference,route,viewport);
     if(!inspectOnly) result.operations=await interact(page,route,viewport);
     assert.deepEqual(runtime,[],'runtime errors');result.passed=true;
   if(engine==='Chrome' && process.env.SECTION_SCREENSHOTS!=='none') await capture(page,route,engine,viewport,captures);
    }catch(e){result.reason=e.message;errors.push({engine,viewport,route,reason:e.message});console.log(JSON.stringify({FAIL:route,engine,viewport,reason:e.message}));}
    if(!inspectOnly && result.measurement)result.measurement={rect:result.measurement.rect,images:result.measurement.images,anchors:result.measurement.anchors,components:Object.fromEntries(Object.entries(result.measurement.components).map(([key,items])=>[key,items.map(({text,rect,overflow,mask})=>({text,rect,overflow,mask}))]))};
    checks.push(result);
   }
   if(captures.length)await gallery(captures,engine,viewport);
   await context.close();console.log(JSON.stringify({engine,viewport,phase,completed:routes.length}));
  }}finally{await browser.close();}
 }
 const report={checkedAt:new Date().toISOString(),origin,phase,pages:routes.length,cases:checks.length,inspectOnly,complete:true,passed:!errors.length,errors,references,checks};
 fs.writeFileSync(path.join(output,'verification.json'),JSON.stringify(report,null,2)+'\n');
 console.log(JSON.stringify({phase,cases:checks.length,passed:report.passed,errors:errors.length}));process.exitCode=errors.length?1:0;
})().catch(e=>{console.error(e);process.exitCode=1;});
