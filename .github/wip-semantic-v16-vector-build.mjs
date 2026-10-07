import fs from 'node:fs';import path from 'node:path';import crypto from 'node:crypto';import cp from 'node:child_process';
import {AutoTokenizer,AutoModel,env,mean_pooling} from '@huggingface/transformers';
const CONTRACT_PATH='pls_v16/BINDING_CONTRACT.json',CONTRACT_SHA='6e8558b4545c1084b3a8342eb2f66611de97dc2e78db46f60919666313164140';
const META_SHA='55499700d4e760671573c7e476a3709d08a9aa3aeb4ce8ce7861ee7f40d36909',MASK_SHA='8935332736286b4b8238966e7a12ee2049d5fab0816a666061db7cb2c9ee56b0';
const OUT=process.env.PLS_V16_OUT||'wip-pls-v16-vector-build',BATCH=Math.max(1,Math.min(64,Number(process.env.PLS_V16_BATCH||16)));
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex'),hash=b=>crypto.createHash('sha256').update(b).digest('hex');
const ok=(c,m)=>{if(!c)throw new Error(m);};fs.mkdirSync(OUT,{recursive:true});
ok(sha(CONTRACT_PATH)===CONTRACT_SHA,'BINDING_CONTRACT_SHA');
const C=JSON.parse(fs.readFileSync(CONTRACT_PATH,'utf8'));
ok(C.status==='ENGINEERING_INPUT_FROZEN__NOT_QUALIFIED__NOT_DEPLOYABLE','CONTRACT_STATUS');
for(const f of [...C.model.tokenizer_and_config_files,...C.model.delivery.parts,...C.runtime.files]){ok(fs.existsSync(f.path),'SUPPORT_MISSING '+f.path);ok(fs.statSync(f.path).size===Number(f.bytes),'SUPPORT_SIZE '+f.path);ok(sha(f.path)===f.sha256,'SUPPORT_HASH '+f.path);}
cp.execFileSync(process.execPath,['.github/wip-semantic-current-pack-build.cjs'],{stdio:['ignore','pipe','inherit'],maxBuffer:32*1024*1024});
const metaPath='wip-current-semantic-pack/metadata.jsonl',maskPath='wip-current-semantic-pack/jesus_mask.bits';
ok(sha(metaPath)===META_SHA,'METADATA_HASH');ok(sha(maskPath)===MASK_SHA,'MASK_HASH');
const rows=fs.readFileSync(metaPath,'utf8').trimEnd().split(/\r?\n/).filter(Boolean).map(JSON.parse);
ok(rows.length===C.chunker.expected_passages,'PASSAGE_COUNT');
const modelRoot='/tmp/ldc-pls-v16-model',modelDir=path.join(modelRoot,'model'),onnxDir=path.join(modelDir,'onnx');fs.rmSync(modelRoot,{recursive:true,force:true});fs.mkdirSync(onnxDir,{recursive:true});
for(const f of C.model.tokenizer_and_config_files){fs.copyFileSync(f.path,path.join(modelDir,path.basename(f.path)));}
const parts=C.model.delivery.parts.map(x=>fs.readFileSync(x.path)),joined=Buffer.concat(parts);ok(joined.length===C.model.delivery.original_model_bytes,'MODEL_BYTES');ok(hash(joined)===C.model.model_sha256,'MODEL_REASSEMBLY_HASH');fs.writeFileSync(path.join(onnxDir,'model_int8.onnx'),joined);
env.allowRemoteModels=false;env.allowLocalModels=true;env.localModelPath=modelRoot+'/';env.useFS=true;env.useFSCache=false;env.useBrowserCache=false;
const tokenizer=await AutoTokenizer.from_pretrained('model',{local_files_only:true,revision:C.model.immutable_revision});
const model=await AutoModel.from_pretrained('model',{local_files_only:true,revision:C.model.immutable_revision,subfolder:'onnx',model_file_name:'model',dtype:'int8',device:'cpu'});
function quantize(v){let m=0;for(let i=0;i<v.length;i++)m=Math.max(m,Math.abs(v[i]));ok(m>0,'ZERO_EMBEDDING');const scale=127/m,q=new Int8Array(v.length);let ss=0;for(let i=0;i<v.length;i++){const z=Math.max(-127,Math.min(127,Math.round(v[i]*scale)));q[i]=z;ss+=z*z;}return {q,inv:1/Math.sqrt(ss)};}
async function embed(texts,prefix){const t=await tokenizer(texts.map(x=>prefix+x),{padding:true,truncation:true,max_length:C.model.max_length});const o=await model(t),h=o.last_hidden_state||o[Object.keys(o)[0]];ok(h,'MODEL_OUTPUT');const pooled=mean_pooling(h,t.attention_mask).normalize(2,-1),data=Float32Array.from(pooled.data),dim=C.model.embedding_dim;ok(data.length===texts.length*dim,'EMBED_GEOMETRY '+data.length);const out=[];for(let i=0;i<texts.length;i++)out.push(data.subarray(i*dim,(i+1)*dim));return out;}
const fixtures=JSON.parse(fs.readFileSync('tools/ldc_v1422_vector_probe/fixtures.json','utf8')),fixtureVectors=await embed(fixtures.map(x=>x.text),C.model.passage_prefix),fixtureReport=[];
for(let i=0;i<fixtures.length;i++){const z=quantize(fixtureVectors[i]),exp=Buffer.from(fixtures[i].vector_b64,'base64');let mismatch=0;for(let j=0;j<z.q.length;j++)if(z.q[j]!==exp.readInt8(j))mismatch++;const invDiff=Math.abs(z.inv-Number(fixtures[i].inverse_norm));fixtureReport.push({passage_id:fixtures[i].passage_id,mismatches:mismatch,inverse_norm_abs_diff:invDiff});ok(mismatch===0&&invDiff<1e-10,'PROTECTED_VECTOR_FIXTURE '+fixtures[i].passage_id);}
const dim=C.model.embedding_dim,vectors=Buffer.alloc(rows.length*dim),norms=Buffer.alloc(rows.length*4);
for(let start=0;start<rows.length;start+=BATCH){const batch=rows.slice(start,start+BATCH),vs=await embed(batch.map(x=>String(x.text||'')),C.model.passage_prefix);for(let i=0;i<vs.length;i++){const z=quantize(vs[i]),row=start+i;for(let j=0;j<dim;j++)vectors.writeInt8(z.q[j],row*dim+j);norms.writeFloatLE(z.inv,row*4);}if(start%(BATCH*50)===0)console.log(JSON.stringify({phase:'vectors',completed:Math.min(rows.length,start+BATCH),total:rows.length}));}
const vecPath=path.join(OUT,'vectors.i8'),normPath=path.join(OUT,'inverse_norms.f32le');fs.writeFileSync(vecPath,vectors);fs.writeFileSync(normPath,norms);
const report={schema:'ldc-pls-v16-vector-build-v1',status:'ENGINEERING_ONLY__NOT_QUALIFIED__NOT_DEPLOYABLE',binding_contract_sha256:CONTRACT_SHA,pack_id:C.pack_id,metadata:{bytes:fs.statSync(metaPath).size,sha256:sha(metaPath)},jesus_mask:{bytes:fs.statSync(maskPath).size,sha256:sha(maskPath)},model:{id:C.model.model_id,revision:C.model.immutable_revision,sha256:C.model.model_sha256,runtime:'@huggingface/transformers@3.8.1 cpu',protected_fixture_parity:fixtureReport},vectors:{rows:rows.length,cols:dim,dtype:'int8_row_symmetric',bytes:vectors.length,sha256:sha(vecPath)},inverse_norms:{bytes:norms.length,sha256:sha(normPath)},batch:BATCH,app_runtime_wired:false,deployment_authorized:false};
fs.writeFileSync(path.join(OUT,'vector_build_report.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report,null,2));
