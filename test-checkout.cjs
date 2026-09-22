const assert=require('node:assert/strict'),fs=require('node:fs'),core=require('./brand/shop/cart-core.js');
const data=JSON.parse(fs.readFileSync('docs/reference/catalog.json','utf8')),map=core.index(data),samples=JSON.parse(fs.readFileSync('source/osouji/checkout/set-samples.json','utf8'));
for(const [id,parts] of Object.entries(samples)){
 const cart=core.clean([{id:'ref-'+id,qty:1}],map),t=core.breakdown(cart,map);
 const expected=parts.reduce((sum,p)=>sum+p.amounts.reduce((a,x)=>a+x.price+x.price_tax-x.price_discount-x.price_discount_tax,0),0);
 assert.equal(t.total,expected,id);assert.equal(cart.length,parts.length,id+' components');assert.equal(t.before-t.discount+t.tax,t.total,id+' tax');
 assert.deepEqual(core.clean(JSON.parse(JSON.stringify(cart)),map),cart,id+' persistence');
}
const t=core.breakdown(core.clean([{id:'ref-666_479',qty:1}],map),map);
assert.deepEqual([t.count,t.before,t.discount,t.net,t.tax,t.total],[2,33000,2000,31000,3100,34100]);
const pair=core.clean([{id:'ref-666_479',qty:1},{id:'ref-666',qty:1}],map);
assert.equal(pair.find(l=>l.id==='ref-666').qty,2);assert.equal(core.totals(pair,map).total,52800);
assert.deepEqual(core.remove(pair,'ref-666',map),[]);
assert.equal(core.totals(core.remove(pair,'ref-666~479',map),map).total,37400);
assert.equal(core.totals([{id:'ref-1',qty:2}],map).total,22000);
for(const route of ['cart','estimate','cart/estimate']){
 const html=fs.readFileSync(`docs/${route}/index.html`,'utf8');assert(html.includes('reference/checkout.js'));assert(!html.includes('brand/shop/script.js'));assert(!/<form[^>]+action="https?:/i.test(html));assert(!html.includes('name="_token"'));
}
assert.equal(fs.readFileSync('brand/reference/brand.css','utf8').includes('c-cart-confirm){background-color:#075b91'),false);
console.log('PASS: 16 source cart compositions, tax/discount detail, set merging, persisted cart, tier pricing, local-only checkout routes');
