import test from 'node:test';import assert from 'node:assert/strict';import {handleAPI} from '../worker/api.js';
const request=path=>new Request('https://nutrilens.test'+path);
test('API validates input and never accepts arbitrary target URLs',async()=>{for(const path of ['/api/search?q=x','/api/search?q=test&page=-1','/api/search?q=test&page=1.5','/api/product/123','/api/proxy?url=https://example.com']){const r=await handleAPI(request(path),{},{},()=>{throw Error('Must not fetch')});assert.ok([400,404].includes(r.status))}});
test('search uses fixed upstream, app identification and cached responses',async()=>{let calls=0;const fake=async(url,opts)=>{calls++;assert.equal(new URL(url).origin,'https://search.openfoodfacts.org');assert.match(new URL(url).searchParams.get('q'),/countries_tags:"en:india"/);assert.match(opts.headers['User-Agent'],/NutriLens/);return Response.json({hits:[{code:'3017620422003',product_name:'Test'}],count:1})};const r=await handleAPI(request('/api/search?q=test-cached'),{},{},fake);assert.equal(r.status,200);assert.equal((await r.json()).hits.length,1);await handleAPI(request('/api/search?q=test-cached'),{},{},fake);assert.equal(calls,1)});
test('upstream errors are handled without leaking upstream response bodies',async()=>{const r=await handleAPI(request('/api/search?q=test-error'),{},{},async()=>new Response('private upstream diagnostics',{status:503}));assert.equal(r.status,503);assert.doesNotMatch(await r.text(),/private upstream/) });
test('unexpected search shape is rejected',async()=>{const r=await handleAPI(request('/api/search?q=test-shape'),{},{},async()=>Response.json({foo:true}));assert.equal(r.status,502)});
test('product detail fetch is restricted to its validated barcode',async()=>{const r=await handleAPI(request('/api/product/3017620422003'),{},{},async url=>{assert.match(url,/^https:\/\/world.openfoodfacts.org\/api\/v3\/product\/3017620422003\?/);return Response.json({product:{product_name:'Test'}})});assert.equal(r.status,200)});
test('mutations are not proxied',async()=>{const r=await handleAPI(new Request('https://nutrilens.test/api/search?q=test',{method:'POST'}));assert.equal(r.status,405)});
test('search succeeds when the host rejects access to its default cache',async()=>{
 const original=Object.getOwnPropertyDescriptor(globalThis,'caches');
 Object.defineProperty(globalThis,'caches',{configurable:true,get(){throw Error('This Worker is not permitted to access the default cache.')}});
 try {const r=await handleAPI(request('/api/search?q=Amul'),{},{},async url=>{
  const q=new URL(url).searchParams.get('q');assert.match(q,/amul\*/);assert.match(q,/AND countries_tags:"en:india"/);
  return Response.json({hits:[{code:'8901262020268',countries_tags:['en:india']}],count:1});
 });assert.equal(r.status,200);assert.equal((await r.json()).market,'india');}
 finally{if(original)Object.defineProperty(globalThis,'caches',original);else delete globalThis.caches;}
});
test('explicit worldwide search has a distinct cache and no country constraint',async()=>{
 const r=await handleAPI(request('/api/search?q=Amul&market=world'),{},{},async url=>{assert.doesNotMatch(new URL(url).searchParams.get('q'),/countries_tags/);return Response.json({hits:[],count:0})});
 assert.equal(r.status,200);assert.equal((await r.json()).market,'world');
});
test('plain input cannot inject search filters and dairy correction is disclosed',async()=>{
 const r=await handleAPI(request('/api/search?q=diary%20milk'),{},{},async url=>{assert.match(new URL(url).searchParams.get('q'),/dairy\*/);return Response.json({hits:[],count:0})});
 assert.equal((await r.json()).correctedQuery,'dairy milk');
 const invalid=await handleAPI(request('/api/search?q=Amul&market=other'));assert.equal(invalid.status,400);
});
