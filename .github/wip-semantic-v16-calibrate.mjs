import fs from 'node:fs';import path from 'node:path';import crypto from 'node:crypto';import cp from 'node:child_process';import {chromium} from 'playwright-core';
import Core from '../search_semantic_v3_core_r4.js';import Hybrid from '../search_semantic_hybrid_r6.js';
const PROTOCOL='pls_v16/CALIBRATION_PROTOCOL.json',PROTOCOL_AUTHORITY_COMMIT='007c44c158071ca3b774710b0c1ee228afb99a86';
const CONTRACT='pls_v16/BINDING_CONTRACT.json',CONTRACT_SHA='6e8558b4545c1084b3a8342eb2f66611de97dc2e78db46f60919666313164140';
const PACK=process.env.PLS_V16_PACK_DIR||'wip-pls-v16-vector-build',META=process.env.PLS_V16_METADATA||'wip-current-semantic-pack/metadata.jsonl',MASK=process.env.PLS_V16_MASK||'wip-current-semantic-pack/jesus_mask.bits',OUT=process.env.PLS_V16_CAL_OUT||'wip-pls-v16-calibration',PORT=Number(process.env.PLS_V16_CAL_PORT||8767);
const ok=(c,m)=>{if(!c)throw new Error(m);},shaBytes=b=>crypto.createHash('sha256').update(b).digest('hex'),sha=p=>shaBytes(fs.readFileSync(p));
fs.mkdirSync(OUT,{recursive:true});
ok(sha(CONTRACT)===CONTRACT_SHA,'BINDING_CONTRACT_SHA');
const frozen=cp.execFileSync('git',['show',PROTOCOL_AUTHORITY_COMMIT+':'+PROTOCOL],{maxBuffer:2*1024*1024}),current=fs.readFileSync(PROTOCOL);ok(Buffer.compare(frozen,current)===0,'CALIBRATION_PROTOCOL_MUTATED_AFTER_FREEZE');
const protocol=JSON.parse(current),contract=JSON.parse(fs.readFileSync(CONTRACT,'utf8'));ok(protocol.status==='FROZEN_BEFORE_V16_RETRIEVAL_OUTCOMES','PROTOCOL_STATUS');ok(protocol.binding_contract_sha256===CONTRACT_SHA&&protocol.pack_id===contract.pack_id,'PROTOCOL_BINDING');
const metaText=fs.readFileSync(META,'utf8'),passages=metaText.trimEnd().split(/\r?\n/).filter(Boolean).map(JSON.parse);ok(passages.length===contract.chunker.expected_passages,'PASSAGE_COUNT');
const vb=fs.readFileSync(path.join(PACK,'vectors.i8')),nb=fs.readFileSync(path.join(PACK,'inverse_norms.f32le')),jb=fs.readFileSync(MASK);ok(vb.length===passages.length*contract.model.embedding_dim,'VECTOR_BYTES');ok(nb.length===passages.length*4,'NORM_BYTES');
const vectors=new Int8Array(vb.buffer,vb.byteOffset,vb.byteLength),norms=new Float32Array(nb.buffer.slice(nb.byteOffset,nb.byteOffset+nb.byteLength)),jesusBits=new Uint8Array(jb.buffer,jb.byteOffset,jb.byteLength);
const index=Core.createIndex({passages,dim:contract.model.embedding_dim,vectors,inverseNorms:norms,jesusBits}),bm25=Hybrid.buildBm25(passages,jesusBits);
const root='/tmp/ldc-pls-v16-calibration',modelDir=path.join(root,'model'),onnxDir=path.join(modelDir,'onnx'),runtimeDir=path.join(root,'runtime');fs.rmSync(root,{recursive:true,force:true});fs.mkdirSync(onnxDir,{recursive:true});fs.mkdirSync(runtimeDir,{recursive:true});
for(const f of contract.model.tokenizer_and_config_files)fs.copyFileSync(f.path,path.join(modelDir,path.basename(f.path)));for(const f of contract.runtime.files)fs.copyFileSync(f.path,path.join(runtimeDir,path.basename(f.path)));
const joined=Buffer.concat(contract.model.delivery.parts.map(x=>fs.readFileSync(x.path)));ok(joined.length===contract.model.delivery.original_model_bytes,'MODEL_BYTES');ok(shaBytes(joined)===contract.model.model_sha256,'MODEL_HASH');fs.writeFileSync(path.join(onnxDir,'model_int8.onnx'),joined);fs.copyFileSync('.github/wip-semantic-v16-query-embed.html',path.join(root,'query.html'));
const server=cp.spawn('python3',['-m','http.server',String(PORT),'--bind','127.0.0.1'],{cwd:root,stdio:['ignore','ignore','inherit']});let browser=null;
function targetRank(rows,target){const i=(rows||[]).findIndex(x=>String(x.entry_id)===String(target));return i<0?null:i+1;}
function features(rows){return Hybrid.features(rows);}
async function evaluateQuery(page,id,text,target=null){
 const raw=await page.evaluate(async q=>await window.embedQuery(q),text),vec=Float32Array.from(raw),opt={sourceMode:'enriched',volMin:0,volMax:0,dateIso:null,year:0,stableRef:null,jesus:false};
 const dense=index.denseSearch(vec,{...opt,candidatePool:160,maxResults:160,collapseThreshold:.5}),sparse=Hybrid.bm25Search(bm25,text,{...opt,maxCandidates:160}),fused=Hybrid.fuse(dense.dense_candidates,sparse.results,{maxResults:20}),f=features(fused);
 return {id,text_sha256:shaBytes(Buffer.from(text,'utf8')),target_entry_id:target,target_rank:target?targetRank(fused,target):null,top_entry_id:fused[0]?.entry_id||null,top20:fused.map(x=>x.entry_id),features:f,dense_candidates:dense.dense_candidates.length,bm25_candidates:sparse.results.length};
}
try{
 await new Promise(r=>setTimeout(r,900));const exe=process.env.CHROME_PATH||'/usr/bin/google-chrome';ok(fs.existsSync(exe),'CHROME_NOT_FOUND');browser=await chromium.launch({headless:true,executablePath:exe,args:['--no-sandbox']});const page=await browser.newPage();page.setDefaultTimeout(180000);await page.goto('http://127.0.0.1:'+PORT+'/query.html',{waitUntil:'load'});await page.waitForFunction(()=>document.querySelector('#status')?.textContent==='module-ready');await page.evaluate(()=>window.initModel());await page.waitForFunction(()=>document.querySelector('#status')?.textContent==='ready');
 const positives=[];for(const q of protocol.positives)positives.push(await evaluateQuery(page,q.id,q.text,q.target_entry_id));
 const dev=[];for(const q of protocol.development_negatives)dev.push(await evaluateQuery(page,q.id,q.text,null));
 const positiveScores=positives.map(x=>x.features.top_dense_score),negativeScores=dev.map(x=>x.features.top_dense_score);ok(positiveScores.every(Number.isFinite)&&negativeScores.every(Number.isFinite),'CALIBRATION_SCORE_MISSING');
 const minPos=Math.min(...positiveScores),maxNeg=Math.max(...negativeScores),separated=minPos>maxNeg;
 let policy=null;if(separated)policy={policy_id:'HYBRID_DENSE_ABSTENTION_V1',close_enabled:false,possible_min_dense:(minPos+maxNeg)/2,possible_min_channels:Number(protocol.prospective_policy_selection.possible_min_channels)};
 function apply(rows){if(!policy)return {state:'abstain',reason:'NO_SEPARATION_POLICY'};return Hybrid.classify([{rrf60_score:rows.features.top_rrf,dense_score:rows.features.top_dense_score,source_ranks:{...(rows.features.dense_rank!=null?{dense_96_72:rows.features.dense_rank}:{}),...(rows.features.bm25_rank!=null?{bm25_96_72:rows.features.bm25_rank}:{})}}],policy);}
 const positiveDecisions=positives.map(x=>({...x,decision:apply(x)})),devDecisions=dev.map(x=>({...x,decision:apply(x)}));
 const positiveGate=separated&&positiveDecisions.every(x=>x.target_rank!=null&&x.target_rank<=10&&x.features.channels===2&&x.decision.state==='possible');
 const devGate=separated&&devDecisions.every(x=>x.decision.state==='abstain');
 const hold=[];if(positiveGate&&devGate){for(const q of protocol.blind_holdout_negatives)hold.push(await evaluateQuery(page,q.id,q.text,null));}
 const holdDecisions=hold.map(x=>({...x,decision:apply(x)})),holdGate=positiveGate&&devGate&&holdDecisions.length===protocol.blind_holdout_negatives.length&&holdDecisions.every(x=>x.decision.state==='abstain');
 const qualified=positiveGate&&devGate&&holdGate;
 const report={schema:'ldc-pls-v16-calibration-evidence-v1',status:qualified?'PASS_QUALIFIABLE':'FAIL_ENGINEERING_ONLY',protocol_authority_commit:PROTOCOL_AUTHORITY_COMMIT,protocol_sha256:sha(PROTOCOL),binding_contract_sha256:CONTRACT_SHA,pack_id:contract.pack_id,pack_assets:{metadata_sha256:sha(META),vectors_sha256:sha(path.join(PACK,'vectors.i8')),inverse_norms_sha256:sha(path.join(PACK,'inverse_norms.f32le')),jesus_mask_sha256:sha(MASK)},retrieval:{dense_candidate_depth:160,bm25_candidate_depth:160,rrf_k:60,output_depth:20},selection:{min_owner_positive_top_hybrid_dense_score:minPos,max_development_negative_top_hybrid_dense_score:maxNeg,separated,threshold:policy?.possible_min_dense??null,policy},gates:{owner_real_query_gate:positiveGate?'PASS':'FAIL',hard_negative_gate:devGate?'PASS':'FAIL',blind_challenge_gate:holdGate?'PASS':'FAIL'},positives:positiveDecisions,development_negatives:devDecisions,blind_holdout_negatives:holdDecisions,close_label_authorized:false,posthoc_rule_changes:0,production_claim:false,deployment_authorized:false};
 fs.writeFileSync(path.join(OUT,'calibration_evidence.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify({status:report.status,selection:report.selection,gates:report.gates,positive_ranks:positives.map(x=>x.target_rank)},null,2));if(!qualified)process.exitCode=4;
}finally{if(browser)await browser.close().catch(()=>{});server.kill('SIGTERM');}
