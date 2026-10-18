// Fixed upstream endpoints only. No arbitrary URL proxy, credentials or client health data.
const SEARCH_FIELDS='code,product_name,brands,quantity,countries_tags';
const DETAIL_FIELDS='code,product_name,product_name_en,brands,quantity,ingredients_text,ingredients_text_en,allergens_tags,traces_tags,categories_tags,countries,nutriments,nutriscore,nutriscore_data,nutriscore_grade,nutriscore_score,nutriscore_version,nova_group,additives_tags,last_modified_t';
const memory=new Map();let recent=[];
const json=(body,status=200,headers={})=>new Response(JSON.stringify(body),{status,headers:{'Content-Type':'application/json; charset=utf-8','X-Content-Type-Options':'nosniff',...headers}});
export async function handleAPI(request,env={},ctx={},fetcher=fetch){
 const url=new URL(request.url);
 if(request.method!=='GET')return json({error:'Only GET requests are supported.'},405,{'Allow':'GET'});
 let upstream,ttl;
 if(url.pathname==='/api/search'){
  const q=(url.searchParams.get('q')||'').trim(),page=Number(url.searchParams.get('page')||1);
  if(q.length<2||q.length>100||!Number.isInteger(page)||page<1||page>100)return json({error:'Enter 2–100 characters and a page from 1–100.'},400);
  upstream=new URL('https://search.openfoodfacts.org/search');upstream.search=new URLSearchParams({q,langs:'en',page:String(page),page_size:'12',fields:SEARCH_FIELDS,charts:''}).toString();ttl=300;
 }else if(/^\/api\/product\/\d{8,14}$/.test(url.pathname)){
  const code=url.pathname.split('/').pop();if(![8,12,13,14].includes(code.length))return json({error:'Invalid barcode length.'},400);
  upstream=new URL('https://world.openfoodfacts.org/api/v3/product/'+code);upstream.searchParams.set('fields',DETAIL_FIELDS);ttl=3600;
 }else return json({error:'Endpoint not found.'},404);
 const cacheKey=new Request(url.origin+'/api/cache?key='+encodeURIComponent(upstream.href));
 const edge=globalThis.caches?.default;
 if(edge){const cached=await edge.match(cacheKey);if(cached)return cached;}
 const cached=memory.get(upstream.href);if(cached&&cached.expires>Date.now())return json(cached.data);
 // Best-effort per-isolate upstream quota; a shared limiter is a public-scale upgrade.
 recent=recent.filter(t=>Date.now()-t<60000);if(recent.length>=9)return json({error:'Search is busy. Wait a minute before trying again.'},429,{'Retry-After':'60'});recent.push(Date.now());
 try{
  const r=await fetcher(upstream.href,{headers:{Accept:'application/json','User-Agent':'NutriLens/1.1 (+https://nutrilens-food-guide-rk.mistyyew128.chatgpt.site)'},signal:AbortSignal.timeout(18000)});
  if(r.status===404)return json({error:'Product not found. Try another barcode or enter the label.'},404);
  if(r.status===429)return json({error:'The product database is busy. Try again in a minute.'},429,{'Retry-After':'60'});
  if(!r.ok)return json({error:'The product database is temporarily unavailable. Try again or enter the label.'},503);
  const data=await r.json();if(data.timed_out)return json({error:'The database search timed out. Try a more specific product name.'},504);
  if(url.pathname==='/api/search'&&!Array.isArray(data.hits))return json({error:'The search service returned an unexpected response.'},502);
  if(memory.size>=100)memory.delete(memory.keys().next().value);memory.set(upstream.href,{data,expires:Date.now()+ttl*1000});
  const result=json(data,200,{'Cache-Control':`public, max-age=${ttl}`});
  if(edge&&ctx.waitUntil)ctx.waitUntil(edge.put(cacheKey,result.clone()));return result;
 }catch(e){return json({error:e.name==='TimeoutError'?'Product lookup timed out. Please try again.':'Could not reach the product database. Try again or enter the label.'},504)}
}
