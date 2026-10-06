import { chromium } from 'playwright-core';
import fs from 'node:fs';import {spawn} from 'node:child_process';
const fixtures=JSON.parse(fs.readFileSync('tools/ldc_v1422_vector_probe/fixtures.json','utf8'));
const exp=(s)=>{const b=Buffer.from(s,'base64');return Array.from(b,x=>x>127?x-256:x)};
function qrow(v){let m=0;for(const x of v)m=Math.max(m,Math.abs(x));const scale=127/m;return v.map(x=>Math.max(-127,Math.min(127,Math.round(x*scale))));}
function cmp(a,b){let n=0,max=0,sum=0;for(let i=0;i<a.length;i++){const d=Math.abs(a[i]-b[i]);if(d)n++;if(d>max)max=d;sum+=d;}return {mismatches:n,max_abs_diff:max,sum_abs_diff:sum};}
const server=spawn('python3',['-m','http.server','8765','--bind','127.0.0.1'],{cwd:'/tmp/ldc-browser-probe',stdio:'ignore'});
try{
 await new Promise(r=>setTimeout(r,800));
 const exe=process.env.CHROME_PATH||'/usr/bin/google-chrome';
 const browser=await chromium.launch({headless:true,executablePath:exe,args:['--no-sandbox']});
 const page=await browser.newPage();page.on('console',m=>console.log('BROWSER',m.type(),m.text()));
 await page.goto('http://127.0.0.1:8765/browser_probe.html',{waitUntil:'load',timeout:30000});
 await page.waitForFunction(()=>document.querySelector('#status')?.textContent==='ready');
 let ok=true;const report=[];
 for(const f of fixtures){
   const v=await page.evaluate(async t=>await window.embedPassage(t),f.text);
   const q=qrow(v), e=exp(f.vector_b64), c=cmp(q,e);
   const inv=1/Math.sqrt(q.reduce((s,x)=>s+x*x,0));
   report.push({row:f.row,passage_id:f.passage_id,float_max_abs:Math.max(...v.map(Math.abs)),...c,generated_inverse_norm:inv,expected_inverse_norm:f.inverse_norm});
   if(c.mismatches!==0 || Math.abs(inv-f.inverse_norm)>1e-10)ok=false;
 }
 console.log(JSON.stringify({schema:'ldc-v1422-browser-vector-repro-v1',runtime:'wasm',quantization:'round(v*127/maxabs)',report,exact:ok},null,2));
 await browser.close();
 if(!ok)process.exitCode=2;
} finally {server.kill('SIGTERM');}