(function(root){
'use strict';
function index(data){return new Map(data.products.flatMap(p=>p.variants.map(v=>[v.id,{...v,product:p}])))}
function clean(raw,map){if(!Array.isArray(raw))return [];const result=new Map();for(const item of raw){if(!item||typeof item.id!=='string')continue;const v=map.get(item.id);if(!v||!Number.isSafeInteger(item.qty)||item.qty<1)continue;result.set(item.id,{id:item.id,qty:Math.min(v.max,(result.get(item.id)?.qty||0)+item.qty)})}return [...result.values()]}
function unitPrice(v,qty){return qty>=2&&Number.isFinite(v.multiPrice)?v.multiPrice:v.price}
function totals(cart,map){return cart.reduce((r,l)=>{const v=map.get(l.id);if(!v)return r;r.total+=(unitPrice(v,l.qty)||0)*l.qty;r.lines++;if(v.price===null)r.quote=true;return r},{total:0,lines:0,quote:false})}
const api={index,clean,totals,unitPrice};root.CCHCart=api;if(typeof module!=='undefined')module.exports=api;
})(typeof window==='undefined'?globalThis:window);
