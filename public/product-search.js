// Coalesce typing, reuse results, and never publish an outdated response.
export function createProductSearch({fetchResults,onChange,delay=450,interval=7000}) {
  let revision=0,timer,lastRequest=0;
  const cache=new Map();
  function cancel(){revision++;clearTimeout(timer)}
  function search(query,page=1,immediate=false){
    cancel();const id=revision;query=query.trim();
    if(query.length<2){onChange({query,page,products:[],count:0,busy:false,error:''});return}
    const key=query.toLowerCase()+':'+page;
    if(cache.has(key)){onChange({...cache.get(key),query});return}
    onChange({query,page,products:[],count:0,busy:true,error:''});
    timer=setTimeout(async()=>{
      lastRequest=Date.now();
      try{
        const data=await fetchResults(query,page);
        const state={query,page,...data,busy:false,error:''};
        cache.set(key,state);if(cache.size>50)cache.delete(cache.keys().next().value);
        if(id===revision)onChange(state);
      }catch(e){if(id===revision)onChange({query,page,products:[],count:0,busy:false,error:e.message||'Search unavailable. Please try again.'})}
    },Math.max(immediate?0:delay,lastRequest+interval-Date.now()));
  }
  return {search,cancel};
}
