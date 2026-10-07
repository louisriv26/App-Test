const http=require('http'),fs=require('fs'),path=require('path');
const port=Number(process.env.PORT||8216);
const activeFile='/tmp/ldc14215_active_root';
const mime={'.html':'text/html; charset=utf-8','.js':'application/javascript; charset=utf-8','.mjs':'application/javascript; charset=utf-8','.json':'application/json; charset=utf-8','.css':'text/css; charset=utf-8','.svg':'image/svg+xml','.png':'image/png','.jpg':'image/jpeg','.jpeg':'image/jpeg','.webp':'image/webp','.wasm':'application/wasm','.onnx':'application/octet-stream','.bin':'application/octet-stream','.txt':'text/plain; charset=utf-8','.ico':'image/x-icon'};
http.createServer((req,res)=>{
  try{
    const root=fs.readFileSync(activeFile,'utf8').trim();
    let raw=new URL(req.url,'http://127.0.0.1').pathname;
    raw=decodeURIComponent(raw);
    if(raw==='/'||raw==='')raw='/index.html';
    const rel=path.posix.normalize(raw).replace(/^\/+/, '');
    if(rel.startsWith('..')){res.writeHead(403);return res.end('forbidden');}
    const file=path.resolve(root,rel);
    const rr=path.resolve(root);
    if(file!==rr&&!file.startsWith(rr+path.sep)){res.writeHead(403);return res.end('forbidden');}
    if(!fs.existsSync(file)||!fs.statSync(file).isFile()){res.writeHead(404,{'Cache-Control':'no-store'});return res.end('not found');}
    const st=fs.statSync(file);
    res.writeHead(200,{'Content-Type':mime[path.extname(file).toLowerCase()]||'application/octet-stream','Content-Length':st.size,'Cache-Control':'no-store, max-age=0','Pragma':'no-cache','Service-Worker-Allowed':'/'});
    fs.createReadStream(file).pipe(res);
  }catch(e){res.writeHead(500,{'Content-Type':'text/plain'});res.end(String(e&&e.stack||e));}
}).listen(port,'127.0.0.1',()=>console.log('switch server',port));
