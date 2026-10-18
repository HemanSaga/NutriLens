import http from 'node:http';
import {readFile} from 'node:fs/promises';
import {resolve, extname} from 'node:path';
const root=resolve('dist');
const types={'.html':'text/html','.css':'text/css','.js':'text/javascript','.svg':'image/svg+xml','.json':'application/json'};
http.createServer(async(req,res)=>{try{const pathname=decodeURIComponent(new URL(req.url,'http://localhost').pathname);const file=resolve(root,'.'+(pathname==='/'?'/index.html':pathname));if(!file.startsWith(root+'/')){res.writeHead(403).end();return;}res.setHeader('Content-Type',types[extname(file)]||'application/octet-stream');res.setHeader('X-Content-Type-Options','nosniff');res.end(await readFile(file));}catch{res.writeHead(404).end('Not found');}}).listen(Number(process.env.PORT)||4173,'127.0.0.1',()=>console.log('NutriLens ready: http://localhost:4173'));
