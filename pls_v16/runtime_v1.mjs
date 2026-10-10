import {AutoTokenizer,AutoModel,env,mean_pooling} from '../pls_v15/runtime/transformers.min.js';

const VERSION='ldc-pls-v16-runtime-v1';
const PACK_ID='ldc-pls-v16-current-v14215-enriched-96-72-r1';
const EXPECTED_MANIFEST_SHA256='37dc813c06c4358eb66c0e0c5d6f4fa4c7b8f7e2d775b66c957df68c5f171ef0';
const BASE=new URL('./',import.meta.url);
const APP_ROOT=new URL('../',BASE);
const MANIFEST_URL=new URL('semantic_pack_manifest.json',BASE);
const MODEL_ROOT=new URL('../pls_v15/',BASE);
const MODEL_ID='model';

let phase='idle',lastError=null,initPromise=null,manifest=null,tokenizer=null,model=null;
let verifiedAssetCache=new Map();

function assert(c,m){if(!c)throw new Error(m);}
function hex(u){return Array.from(u,x=>x.toString(16).padStart(2,'0')).join('');}
async function sha256(u){return hex(new Uint8Array(await crypto.subtle.digest('SHA-256',u instanceof Uint8Array?u:new Uint8Array(u))));}
function urlFor(path){return new URL(String(path),APP_ROOT);}
async function fetchBytes(path,{cache='force-cache'}={}){
  const key=String(path);
  if(verifiedAssetCache.has(key))return verifiedAssetCache.get(key);
  const r=await fetch(urlFor(key),{cache});
  if(!r.ok)throw new Error('PLS_V16_ASSET_HTTP_'+r.status+':'+key);
  const u=new Uint8Array(await r.arrayBuffer());
  if(manifest){
    const d=(manifest.files||[]).find(x=>x.path===key);
    if(d&&String(key).startsWith('pls_v16/')){
      assert(u.byteLength===Number(d.bytes),'PLS_V16_ASSET_SIZE:'+key);
      assert(await sha256(u)===d.sha256,'PLS_V16_ASSET_HASH:'+key);
      verifiedAssetCache.set(key,u);
    }
  }
  return u;
}
async function fetchManifest(){
  const r=await fetch(MANIFEST_URL,{cache:'no-store'});
  if(!r.ok)throw new Error('PLS_V16_MANIFEST_HTTP_'+r.status);
  const u=new Uint8Array(await r.arrayBuffer());
  assert(await sha256(u)===EXPECTED_MANIFEST_SHA256,'PLS_V16_MANIFEST_HASH');
  const m=JSON.parse(new TextDecoder('utf-8',{fatal:true}).decode(u));
  assert(m.pack_id===PACK_ID,'PLS_V16_PACK_ID');
  assert(m.status==='QUALIFIED__ACTIVATION_ELIGIBLE_AFTER_GUARD_VERIFICATION','PLS_V16_MANIFEST_NOT_QUALIFIED');
  assert(m.deployment_authorized===false&&m.app_runtime_wired===false,'PLS_V16_ENGINEERING_MANIFEST_FLAGS');
  return m;
}
function globals(){
  assert(globalThis.LDCSemanticPackGuardR4,'PLS_V16_GUARD_R4_REQUIRED');
  assert(globalThis.LDCSearchSemanticV3R4,'PLS_V16_DENSE_R4_REQUIRED');
  assert(globalThis.LDCSemanticHybridR6,'PLS_V16_HYBRID_R6_REQUIRED');
  assert(globalThis.LDCSemanticPackRegistryR6,'PLS_V16_REGISTRY_R6_REQUIRED');
  return globalThis.LDCSemanticPackRegistryR6;
}
function descriptor(path){
  const d=(manifest&&manifest.files||[]).find(x=>x.path===path);
  assert(d,'PLS_V16_DESCRIPTOR_MISSING:'+path);return d;
}
async function fetchVerified(path){
  const d=descriptor(path),r=await fetch(urlFor(path),{cache:'force-cache'});
  if(!r.ok)throw new Error('PLS_V16_MODEL_ASSET_HTTP_'+r.status+':'+path);
  const u=new Uint8Array(await r.arrayBuffer());
  assert(u.byteLength===Number(d.bytes),'PLS_V16_MODEL_ASSET_SIZE:'+path);
  assert(await sha256(u)===d.sha256,'PLS_V16_MODEL_ASSET_HASH:'+path);
  return u;
}
async function ensureModel(){
  if(tokenizer&&model)return true;
  assert(manifest,'PLS_V16_MANIFEST_REQUIRED');
  env.allowRemoteModels=false;
  env.allowLocalModels=true;
  env.localModelPath=MODEL_ROOT.href;
  env.useBrowserCache=false;
  env.useFSCache=false;
  const tokenizerBySuffix=new Map((manifest.model.tokenizer_files||[]).map(d=>['/model/'+d.path.split('/').pop(),d.path]));
  let joinedModelResponse=null;
  env.useCustomCache=true;
  env.customCache={
    async match(key){
      const k=String(key||'');
      if(k.endsWith('/model/onnx/model_int8.onnx')||k.endsWith('model/onnx/model_int8.onnx')){
        if(joinedModelResponse)return joinedModelResponse.clone();
        const total=Number(manifest.model.delivery.original_model_bytes),all=new Uint8Array(total);let off=0;
        for(const p of manifest.model.delivery.parts){
          const u=await fetchVerified(p.path);all.set(u,off);off+=u.byteLength;
        }
        assert(off===total,'PLS_V16_MODEL_REASSEMBLY_SIZE');
        // Exact ordered part hashes are already Guard-bound and rechecked above.
        joinedModelResponse=new Response(all,{status:200,headers:{'content-type':'application/octet-stream','content-length':String(total)}});
        return joinedModelResponse.clone();
      }
      for(const [suffix,p] of tokenizerBySuffix)if(k.endsWith(suffix)||k.endsWith(suffix.slice(1))){
        const u=await fetchVerified(p);
        return new Response(u,{status:200,headers:{'content-type':p.endsWith('.json')?'application/json':'application/octet-stream','content-length':String(u.byteLength)}});
      }
      return undefined;
    },
    async put(){return;}
  };
  if(env.backends?.onnx?.wasm){
    env.backends.onnx.wasm.numThreads=1;
    env.backends.onnx.wasm.proxy=false;
    env.backends.onnx.wasm.wasmPaths=new URL('../pls_v15/runtime/',BASE).href;
  }
  tokenizer=await AutoTokenizer.from_pretrained(MODEL_ID,{local_files_only:true,revision:manifest.model.immutable_revision});
  model=await AutoModel.from_pretrained(MODEL_ID,{local_files_only:true,revision:manifest.model.immutable_revision,subfolder:'onnx',model_file_name:'model',dtype:'int8',device:'wasm'});
  joinedModelResponse=null;
  return true;
}
async function encodeQuery(text){
  await ensureModel();
  const canonical=manifest.model.query_prefix+String(text||'');
  const t=await tokenizer([canonical],{padding:true,truncation:true,max_length:Number(manifest.model.max_length)});
  const out=await model(t),h=out.last_hidden_state||out[Object.keys(out)[0]];
  assert(h,'PLS_V16_MODEL_OUTPUT_MISSING');
  const pooled=mean_pooling(h,t.attention_mask).normalize(2,-1),v=Float32Array.from(pooled.data);
  assert(v.length===Number(manifest.model.embedding_dim),'PLS_V16_QUERY_DIMENSION');
  for(const x of v)assert(Number.isFinite(x),'PLS_V16_QUERY_NONFINITE');
  return v;
}
function status(){
  let registry=null;
  try{registry=globalThis.LDCSemanticPackRegistryR6?.status?.('enriched')||null;}catch(_){}
  const ready=phase==='ready'&&registry?.available===true&&registry?.calibration_status==='QUALIFIED';
  return {
    schema:'ldc-pls-v16-runtime-status-v1',version:VERSION,pack_id:PACK_ID,
    available:!!ready,ready:!!ready,loading:phase==='loading',can_initialize:phase==='idle'||phase==='loading'||phase==='failed',
    calibration_status:ready?'QUALIFIED':(phase==='failed'?'UNAVAILABLE':'PENDING_VERIFICATION'),
    model_ready:!!(tokenizer&&model),persistent_semantic_storage:false,
    error:lastError,registry
  };
}
async function init(){
  if(phase==='ready')return status();
  if(initPromise)return initPromise;
  phase='loading';lastError=null;
  initPromise=(async()=>{
    try{
      const R=globals();
      manifest=await fetchManifest();
      const bind=await R.bindModePack('enriched',{manifest,getBytes:p=>fetchBytes(p),encodeQuery});
      assert(bind&&bind.available===true&&bind.calibration_status==='QUALIFIED','PLS_V16_REGISTRY_BIND_FAILED');
      // The verified semantic bytes have been copied into the bound index/BM25 structures.
      // Drop raw verification buffers before loading the model to bound mobile peak memory.
      verifiedAssetCache.clear();
      await ensureModel();
      phase='ready';lastError=null;
      return status();
    }catch(e){
      phase='failed';lastError=String(e&&e.message||e);
      try{globalThis.LDCSemanticPackRegistryR6?.unbindMode?.('enriched');}catch(_){}
      verifiedAssetCache.clear();tokenizer=null;model=null;
      throw e;
    }finally{initPromise=null;}
  })();
  return initPromise;
}
async function search(query,options={}){
  const q=String(query||'').trim();assert(q,'PLS_V16_QUERY_EMPTY');
  await init();
  const R=globals();
  const result=await R.search(q,{...options,sourceMode:'enriched'});
  assert(result&&result.pack_id===PACK_ID,'PLS_V16_RESULT_PACK_ID');
  return result;
}
function resetForTests(){
  try{globalThis.LDCSemanticPackRegistryR6?.unbindMode?.('enriched');}catch(_){}
  phase='idle';lastError=null;initPromise=null;manifest=null;tokenizer=null;model=null;verifiedAssetCache.clear();
}
globalThis.LDCPLSV16Runtime=Object.freeze({VERSION,PACK_ID,EXPECTED_MANIFEST_SHA256,status,init,search,_resetForTests:resetForTests});
