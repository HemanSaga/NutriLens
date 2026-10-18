import {readFile,mkdir,writeFile} from 'node:fs/promises';
const files=['index.html','app.js','analysis.js','insights.js','styles.css','icon.svg'];
const assets={};for(const name of files)assets[name]=await readFile('public/'+name,'utf8');
const manifest=JSON.parse(await readFile('.openai/hosting.json','utf8'));if(manifest.static)throw Error('Remove static configuration for Worker hosting.');
const api=(await readFile('worker/api.js','utf8')).replace('export async function handleAPI','async function handleAPI');
const runtime=`${api}\nconst assets=${JSON.stringify(assets)};\nconst types={html:'text/html; charset=utf-8',js:'text/javascript; charset=utf-8',css:'text/css; charset=utf-8',svg:'image/svg+xml'};\nexport default {async fetch(request,env,ctx){const path=new URL(request.url).pathname;if(path.startsWith('/api/'))return handleAPI(request,env,ctx);if(!['GET','HEAD'].includes(request.method))return new Response('Method not allowed',{status:405});const name=path==='/'?'index.html':path.slice(1);if(!Object.hasOwn(assets,name))return new Response('Not found',{status:404});return new Response(request.method==='HEAD'?null:assets[name],{headers:{'Content-Type':types[name.split('.').pop()]||'text/plain','X-Content-Type-Options':'nosniff','Cache-Control':'no-cache','Referrer-Policy':'strict-origin-when-cross-origin'}})}};`;
await mkdir('dist/server',{recursive:true});await mkdir('dist/.openai',{recursive:true});
await writeFile('dist/server/index.js',runtime);await writeFile('dist/.openai/hosting.json',JSON.stringify(manifest,null,2));
console.log('Built self-contained Worker with 6 embedded assets and same-origin product API.');
