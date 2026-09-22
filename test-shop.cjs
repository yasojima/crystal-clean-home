const assert=require('node:assert/strict'),fs=require('node:fs'),{index,clean,totals}=require('./brand/shop/cart-core');
const d=JSON.parse(fs.readFileSync('brand/shop/catalog.json','utf8')),m=index(d);
assert.equal(m.size,40);
assert.deepEqual(clean(null,m),[]);
assert.deepEqual(clean([{id:'invalid',qty:1},{id:'kitchen',qty:-1},{id:'kitchen',qty:1.5},{id:'kitchen',qty:'2'}],m),[]);
assert.deepEqual(clean([{id:'kitchen',qty:1},{id:'kitchen',qty:2}],m),[{id:'kitchen',qty:3}]);
assert.equal(clean([{id:'kitchen',qty:999999}],m)[0].qty,20);
assert.equal(totals([{id:'airconOsoujiKinou',qty:2},{id:'rangeHood',qty:1}],m).total,50600);
assert.equal(totals([{id:'packKitchen',qty:1}],m).total,26400);
assert.equal(totals([{id:'fukisoujiPlusSoujiki',qty:25}],m).total,11000);
assert.deepEqual(totals([{id:'coating',qty:1}],m),{total:0,lines:1,quote:true});
for(const p of d.products){assert(p.images.length);for(const img of p.images)assert(fs.existsSync('docs/'+img.replace('/crystal-clean-home/','')));for(const v of p.variants)assert(['台','式','室','ヶ所','㎡','枠','件'].includes(v.unit))}
console.log('PASS: price totals, variant IDs, duplicate merge, invalid storage, quantity limits, quote-only, all image files');
