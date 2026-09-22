(function(root){
'use strict';
function index(data){return new Map(data.products.flatMap(p=>p.variants.map(v=>[v.id,{...v,product:p}])))}
function clean(raw,map){if(!Array.isArray(raw))return [];const result=new Map();for(const item of raw){if(!item||typeof item.id!=='string')continue;const v=map.get(item.id);if(!v||!Number.isSafeInteger(item.qty)||item.qty<1)continue;for(const id of v.components||[item.id]){const part=map.get(id);if(!part)continue;result.set(id,{id,qty:Math.min(part.max,(result.get(id)?.qty||0)+item.qty)})}}return [...result.values()]}
function unitPrice(v,qty){return qty>=2&&Number.isFinite(v.multiPrice)?v.multiPrice:v.price}
function remove(cart,id,map){return cart.filter(l=>l.id!==id&&map.get(l.id)?.requires!==id)}
function totals(cart,map){return cart.reduce((r,l)=>{const v=map.get(l.id);if(!v)return r;r.total+=(unitPrice(v,l.qty)||0)*l.qty;r.lines++;if(v.price===null)r.quote=true;return r},{total:0,lines:0,quote:false})}
function breakdown(cart,map){let gross=0;const discounts=[];for(const l of cart){const v=map.get(l.id),regular=v.regularPrice||v.price;gross+=(regular||0)*l.qty;const d=((regular||0)-(unitPrice(v,l.qty)||0))*l.qty;if(d>0)discounts.push({name:v.product.name+(v.name==='標準'?'':'／'+v.name),amount:Math.round(d/1.1)})}const t=totals(cart,map),net=Math.round(t.total/1.1),before=Math.round(gross/1.1);return {total:t.total,net,before,discount:before-net,tax:t.total-net,discounts,count:cart.reduce((s,l)=>s+l.qty,0),quote:t.quote}}
const api={index,clean,totals,unitPrice,breakdown,remove};root.CCHCart=api;if(typeof module!=='undefined')module.exports=api;
})(typeof window==='undefined'?globalThis:window);
