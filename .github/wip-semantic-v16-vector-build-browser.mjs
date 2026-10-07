import fs from 'node:fs';import path from 'node:path';import crypto from 'node:crypto';import cp from 'node:child_process';
import {chromium} from 'playwright-core';
const CONTRACT_PATH='pls_v16/BINDING_CONTRACT.json',CONTRACT_SHA='6e8558b4545c1084b3a8342eb2f66611de97dc2e78db46f60919666313164140';
const META_SHA='55499700d4e760671573c7e476a3709d08a9aa3aeb4ce8ce7861ee7f40d36909',MASK_SHA='8935332736286b4b8238966e7a12ee2049d5fab0816a666061db7cb2c9ee56b0';
const OUT=process.env.PLS_V16_OUT||'wip-pls-v16-vector-build',BATCH=Math.max(1,Math.min(32,Number(process.env.PLS_V16_BATCH||8))),PORT=Number(process.env.PLS_V16_PORT||8766);
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex'),hash=b=>crypto.createHash('sha256').update(b).digest('hex'),ok=(c,m)=>{if(!c)throw new Error(m);};
fs.mkdirSync(OUT,{recursive:true});ok(sha(CONTRACT_PATH)===CONTRACT_SHA,'BINDING_CONTRACT_SHA');const C=JSON.parse(fs.readFileSync(CONTRACT_PATH,'utf8'));
for(const f of [...C.model.tokenizer_and_config_files,...C.model.delivery.parts,...C.runtime.files]){ok(fs.existsSync(f.path),'SUPPORT_MISSING '+f.path);ok(fs.statSync(f.path).size===Number(f.bytes),'SUPPORT_SIZE '+f.path);ok(sha(f.path)===f.sha256,'SUPPORT_HASH '+f.path);}
cp.execFileSync(process.execPath,['.github/wip-semantic-current-pack-build.cjs'],{stdio:['ignore','pipe','inherit'],maxBuffer:32*1024*1024});
const metaPath='wip-current-semantic-pack/metadata.jsonl',maskPath='wip-current-semantic-pack/jesus_mask.bits';ok(sha(metaPath)===META_SHA,'METADATA_HASH');ok(sha(maskPath)===MASK_SHA,'MASK_HASH');
const rows=fs.readFileSync(metaPath,'utf8').trimEnd().split(/\r?\n/).filter(Boolean).map(JSON.parse);ok(rows.length===C.chunker.expected_passages,'PASSAGE_COUNT');
const root='/tmp/ldc-pls-v16-browser',modelDir=path.join(root,'model'),onnxDir=path.join(modelDir,'onnx'),runtimeDir=path.join(root,'runtime');fs.rmSync(root,{recursive:true,force:true});fs.mkdirSync(onnxDir,{recursive:true});fs.mkdirSync(runtimeDir,{recursive:true});
for(const f of C.model.tokenizer_and_config_files)fs.copyFileSync(f.path,path.join(modelDir,path.basename(f.path)));
for(const f of C.runtime.files)fs.copyFileSync(f.path,path.join(runtimeDir,path.basename(f.path)));
const joined=Buffer.concat(C.model.delivery.parts.map(x=>fs.readFileSync(x.path)));ok(joined.length===C.model.delivery.original_model_bytes,'MODEL_BYTES');ok(hash(joined)===C.model.model_sha256,'MODEL_REASSEMBLY_HASH');fs.writeFileSync(path.join(onnxDir,'model_int8.onnx'),joined);
fs.copyFileSync('.github/wip-semantic-v16-vector-build-browser.html',path.join(root,'builder.html'));
const server=cp.spawn('python3',['-m','http.server',String(PORT),'--bind','127.0.0.1'],{cwd:root,stdio:['ignore','pipe','pipe']});
let browser=null;const t0=Date.now();
try{
 await new Promise((res,rej)=>{let done=false;const timer=setTimeout(()=>{if(!done){done=true;res();}},900);server.on('exit',code=>{if(!done){done=true;clearTimeout(timer);rej(new Error('HTTP_SERVER_EXIT '+code));}});});
 const exe=process.env.CHROME_PATH||'/usr/bin/google-chrome';ok(fs.existsSync(exe),'CHROME_NOT_FOUND '+exe);
 browser=await chromium.launch({headless:true,executablePath:exe,args:['--no-sandbox']});const page=await browser.newPage();page.setDefaultTimeout(180000);
 page.on('console',m=>{if(m.type()==='error')console.error('BROWSER',m.text());});
 await page.goto('http://127.0.0.1:'+PORT+'/builder.html',{waitUntil:'load',timeout:30000});await page.waitForFunction(()=>document.querySelector('#status')?.textContent==='module-ready');
 await page.evaluate(()=>window.initModel());await page.waitForFunction(()=>document.querySelector('#status')?.textContent==='ready',{timeout:180000});
 const fixtures=JSON.parse(fs.readFileSync('tools/ldc_v1422_vector_probe/fixtures.json','utf8')),fixtureReport=[];
 for(const f of fixtures){const [z]=await page.evaluate(async t=>await window.embedQuantizedBatch([t]),f.text),exp=Buffer.from(f.vector_b64,'base64');let mismatch=0;for(let j=0;j<z.q.length;j++)if(z.q[j]!==exp.readInt8(j))mismatch++;const invDiff=Math.abs(Number(z.inv)-Number(f.inverse_norm));fixtureReport.push({passage_id:f.passage_id,mismatches:mismatch,inverse_norm_abs_diff:invDiff});ok(mismatch===0&&invDiff<1e-10,'PROTECTED_VECTOR_FIXTURE '+f.passage_id);}
 const batchFixture=await page.evaluate(async xs=>await window.embedQuantizedBatch(xs),fixtures.map(x=>x.text));
 for(let i=0;i<fixtures.length;i++){const exp=Buffer.from(fixtures[i].vector_b64,'base64');let mismatch=0;for(let j=0;j<batchFixture[i].q.length;j++)if(batchFixture[i].q[j]!==exp.readInt8(j))mismatch++;ok(mismatch===0,'BATCH_FIXTURE_PARITY '+fixtures[i].passage_id);}
 const dim=C.model.embedding_dim,vectors=Buffer.alloc(rows.length*dim),norms=Buffer.alloc(rows.length*4);
 for(let start=0;start<rows.length;start+=BATCH){
   const batch=rows.slice(start,start+BATCH),zs=await page.evaluate(async xs=>await window.embedQuantizedBatch(xs),batch.map(x=>String(x.text||'')));
   ok(zs.length===batch.length,'BATCH_RESULT_COUNT');
   for(let i=0;i<zs.length;i++){const z=zs[i],row=start+i;ok(z.q.length===dim,'VECTOR_DIM');for(let j=0;j<dim;j++)vectors.writeInt8(Number(z.q[j]),row*dim+j);norms.writeFloatLE(Number(z.inv),row*4);}
   if(start%(BATCH*50)===0)console.log(JSON.stringify({phase:'browser-vectors',completed:Math.min(rows.length,start+BATCH),total:rows.length,elapsed_s:Math.round((Date.now()-t0)/1000)}));
 }
 const vecPath=path.join(OUT,'vectors.i8'),normPath=path.join(OUT,'inverse_norms.f32le');fs.writeFileSync(vecPath,vectors);fs.writeFileSync(normPath,norms);
 const report={schema:'ldc-pls-v16-browser-vector-build-v1',status:'ENGINEERING_ONLY__NOT_QUALIFIED__NOT_DEPLOYABLE',binding_contract_sha256:CONTRACT_SHA,pack_id:C.pack_id,backend:'BROWSER_WASM_PINNED',metadata:{bytes:fs.statSync(metaPath).size,sha256:sha(metaPath)},jesus_mask:{bytes:fs.statSync(maskPath).size,sha256:sha(maskPath)},model:{id:C.model.model_id,revision:C.model.immutable_revision,sha256:C.model.model_sha256,protected_fixture_parity:fixtureReport,batch_fixture_parity:true},vectors:{rows:rows.length,cols:dim,dtype:'int8_row_symmetric',bytes:vectors.length,sha256:sha(vecPath)},inverse_norms:{bytes:norms.length,sha256:sha(normPath)},batch:BATCH,elapsed_seconds:Math.round((Date.now()-t0)/1000),app_runtime_wired:false,deployment_authorized:false};
 fs.writeFileSync(path.join(OUT,'vector_build_report.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report,null,2));
} finally {if(browser)await browser.close().catch(()=>{});server.kill('SIGTERM');}
