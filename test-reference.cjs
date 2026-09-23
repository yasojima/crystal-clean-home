const assert=require('node:assert/strict'),fs=require('node:fs');
const C=require('./brand/shop/cart-core');
const data=JSON.parse(fs.readFileSync('docs/reference/catalog.json','utf8')),m=C.index(data);
assert.equal(C.totals([{id:'ref-666_479',qty:2}],m).total,68200);
assert.equal(C.totals([{id:'ref-104',qty:1}],m).total,35200);
assert.equal(C.totals([{id:'ref-1',qty:1}],m).total,13200);
assert.equal(C.totals([{id:'ref-1',qty:2}],m).total,22000);
assert.equal(C.totals([{id:'ref-666_479',qty:2},{id:'ref-104',qty:1},{id:'ref-1',qty:2}],m).total,125400);
for(const v of m.values()){if(v.requires)assert(m.has(v.requires),v.id);assert(v.price===null||Number.isSafeInteger(v.price),v.id)}
const report=JSON.parse(fs.readFileSync('reference-report.json','utf8'));
assert.equal(Object.keys(report.pages).length,52);
for(const route of Object.keys(report.pages))assert(fs.existsSync('docs'+route+'index.html'));
console.log('PASS: 52 routes, reference set/room/tier totals, option parent IDs, integer prices');

assert.equal(C.clean([{id:'ref-1',qty:2}],m)[0].qty,2,'Quantity options without value attributes must retain their displayed limits');
