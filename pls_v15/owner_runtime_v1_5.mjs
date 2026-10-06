import { AutoTokenizer, AutoModel, env, mean_pooling } from './runtime/transformers.min.js';
const VERSION='ldc-pls-owner-prototype-v142.2-v2';
const BASE=new URL('./',import.meta.url);
const MODEL_ID='model';
let initPromise=null, index=null, bm25=null, tokenizer=null, model=null, passages=null, jesusBits=null;
let lastError=null;
function assert(c,m){if(!c)throw new Error(m);}
function status(){return {schema:'ldc-pls-owner-prototype-status-v1',version:VERSION,available:true,ready:!!index,loading:!!initPromise&&!index,error:lastError,prototype:true,source_mode:'enriched',chunk_policy_id:'96-72',fusion:'RRF60_EQUAL'};}
async function fetchBytes(rel){const r=await fetch(new URL(rel,BASE),{cache:'force-cache'});if(!r.ok)throw new Error('PLS_ASSET_FETCH_'+rel+':'+r.status);return new Uint8Array(await r.arrayBuffer());}
async function fetchText(rel){const r=await fetch(new URL(rel,BASE),{cache:'force-cache'});if(!r.ok)throw new Error('PLS_ASSET_FETCH_'+rel+':'+r.status);return await r.text();}
function f32FromBytes(u8){assert(u8.byteLength%4===0,'PLS_F32_GEOMETRY');const b=u8.buffer.slice(u8.byteOffset,u8.byteOffset+u8.byteLength);return new Float32Array(b);}
async function init(){
 if(index)return status(); if(initPromise)return initPromise;
 initPromise=(async()=>{try{
  assert(globalThis.LDCSearchSemanticV3R4,'PLS_DENSE_CORE_REQUIRED');assert(globalThis.LDCPLSHybridV15,'PLS_HYBRID_CORE_REQUIRED');
  const [mt,vb,ib,jb]=await Promise.all([fetchText('pack/metadata.jsonl'),fetchBytes('pack/vectors.i8'),fetchBytes('pack/inverse_norms.f32le'),fetchBytes('pack/jesus_mask.bits')]);
  passages=mt.trimEnd().split(/\r?\n/).filter(Boolean).map(JSON.parse);jesusBits=jb;
  index=globalThis.LDCSearchSemanticV3R4.createIndex({passages,dim:384,vectors:new Int8Array(vb.buffer,vb.byteOffset,vb.byteLength),inverseNorms:f32FromBytes(ib),jesusBits});
  bm25=globalThis.LDCPLSHybridV15.buildBm25(passages,jesusBits);
  env.allowRemoteModels=false;env.allowLocalModels=true;env.localModelPath=BASE.href;env.useBrowserCache=false;
  const modelParts=['model/onnx/model_int8.onnx.part01','model/onnx/model_int8.onnx.part02','model/onnx/model_int8.onnx.part03','model/onnx/model_int8.onnx.part04'];
  let joinedModelResponse=null;
  env.useCustomCache=true;env.customCache={
    async match(key){const k=String(key||'');if(!k.endsWith('/model/onnx/model_int8.onnx')&&!k.endsWith('model/onnx/model_int8.onnx'))return undefined;if(joinedModelResponse)return joinedModelResponse.clone();const chunks=[];let total=0;for(const rel of modelParts){const u=await fetchBytes(rel);chunks.push(u);total+=u.byteLength;}const all=new Uint8Array(total);let off=0;for(const u of chunks){all.set(u,off);off+=u.byteLength;}joinedModelResponse=new Response(all,{status:200,headers:{'content-type':'application/octet-stream','content-length':String(total)}});return joinedModelResponse.clone();},
    async put(){return;}
  };
  if(env.backends&&env.backends.onnx&&env.backends.onnx.wasm){env.backends.onnx.wasm.numThreads=1;env.backends.onnx.wasm.proxy=false;env.backends.onnx.wasm.wasmPaths=new URL('./runtime/',BASE).href;}
  tokenizer=await AutoTokenizer.from_pretrained(MODEL_ID,{local_files_only:true});
  model=await AutoModel.from_pretrained(MODEL_ID,{local_files_only:true,subfolder:'onnx',model_file_name:'model',dtype:'int8',device:'wasm'});
  lastError=null;return status();
 }catch(e){lastError=String(e&&e.message||e);index=null;bm25=null;tokenizer=null;model=null;throw e;} finally {if(!index)initPromise=null;}})();
 return initPromise;
}
async function embed(userText){await init();const canonical='query: '+String(userText||'');const t=await tokenizer([canonical],{padding:true,truncation:true,max_length:512});const out=await model(t);const h=out.last_hidden_state||out[Object.keys(out)[0]];assert(h,'PLS_MODEL_OUTPUT_MISSING');const pooled=mean_pooling(h,t.attention_mask).normalize(2,-1);const v=Float32Array.from(pooled.data);assert(v.length===384,'PLS_QUERY_DIMENSION');return v;}
function enrichHybrid(rows){const byPid=new Map(passages.map(x=>[String(x.passage_id),x]));return rows.map(x=>Object.assign({},byPid.get(String(x.passage_id))||{},x));}
async function search(query,options={}){
 const q=String(query||'').trim();if(!q)throw new Error('PLS_QUERY_EMPTY');await init();const vec=await embed(q);
 const opt={sourceMode:'enriched',volMin:options.volMin||0,volMax:options.volMax||0,dateIso:options.dateIso||null,year:options.year||0,stableRef:options.stableRef||null,jesus:!!options.jesus};
 const dense=index.denseSearch(vec,{...opt,candidatePool:160,maxResults:160,collapseThreshold:.5});
 const sparse=globalThis.LDCPLSHybridV15.bm25Search(bm25,q,{...opt,maxCandidates:160});
 const fused=enrichHybrid(globalThis.LDCPLSHybridV15.fuse(dense.dense_candidates,sparse.results,{maxResults:20}));
 return {schema:'ldc-pls-owner-prototype-result-v142.2-v2',prototype_owner_v15:true,version:VERSION,query:q,source_mode:'enriched',candidate_population:'DENSE_96_72_PLUS_BM25_96_72_RRF60',confidence:{state:'possible',label:'Prototype personnel — pistes classées par combinaison sémantique et lexicale'},results:fused,diagnostics:{dense_candidates:dense.dense_candidates.length,bm25_candidates:sparse.results.length,compatible_passages:passages.length}};
}
globalThis.LDCPLSOwnerPrototypeV15=Object.freeze({VERSION,status,init,search});
