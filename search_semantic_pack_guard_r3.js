/* LDC SEARCH-V3 semantic pack guard R3 — binds exact Jesus-speech mask as activation-critical. */
(function(root,factory){const api=factory();if(typeof module==='object'&&module.exports)module.exports=api;if(root)root.LDCSemanticPackGuardR3=api;})(typeof globalThis!=='undefined'?globalThis:this,function(){
'use strict';
const VERSION='ldc-search-v3-semantic-pack-guard-r3';
const EXPECTED=Object.freeze({
 corpus_generation:'G036-AFLP-R7-SUP-T5-FAST1',backbone_generation:'G036-AFLP-R7-UWR2-FAST1',
 offline_content_binding_sha256:'36e9d99ef1474bf4dfd15651bc5894f072afe0aab80c38567937552d057d5b55',
 corpus_manifest_sha256:'8d831c437fa6c2caa56ac637c3d539279ec24b57711d209b264804cca19c0ab7',
 search_documents_sha256:'5320c32f3a72421c8859f92dc3f1f53b1f7da37f81ac429e00c07377250b950b',
 search_topology_sha256:'e57ab52b3cf46f8be3221b455ed826efe65a6a6e359387b1a9348319c53690da',
 search_manifest_sha256:'a656c6b39dd5a6e4ba5649aaf1dc2a32516009c87ec38422bc1a6472a67baec4'
});
function fail(code,detail){return {ok:false,code,detail:detail||null,activation:false};}
function safePath(p){return typeof p==='string'&&p.length>0&&!p.startsWith('/')&&!p.split('/').includes('..')&&!p.includes('\\');}
function hex(bytes){return Array.from(bytes,x=>x.toString(16).padStart(2,'0')).join('');}
async function sha256(data){const u=data instanceof Uint8Array?data:new Uint8Array(data);if(!globalThis.crypto||!crypto.subtle)throw new Error('WEBCRYPTO_REQUIRED');return hex(new Uint8Array(await crypto.subtle.digest('SHA-256',u)));}
function fileMap(m){const map=new Map();for(const f of (m.files||[])){if(!f||!safePath(f.path)||map.has(f.path))return null;map.set(f.path,f);}return map;}
function validateManifestShape(m){
 if(!m||m.schema!=='ldc-search-v3-semantic-pack-r2')return fail('MANIFEST_SCHEMA');
 if(!m.bindings||!m.chunker||!m.model||!m.index||!m.speaker_filter||!m.runtime||!m.calibration||!Array.isArray(m.files))return fail('MANIFEST_REQUIRED_FIELDS');
 for(const [k,v] of Object.entries(EXPECTED)){if(m.bindings[k]!==v)return fail('STALE_PACK_BINDING',k);}
 const map=fileMap(m);if(!map)return fail('INVALID_OR_DUPLICATE_FILE_PATH');
 const refs=[...(m.model.tokenizer_files||[]),m.index.vectors_file,m.index.metadata_file,m.speaker_filter.jesus_mask_file,...(m.runtime.files||[])];if(m.index.inverse_norms_file)refs.push(m.index.inverse_norms_file);
 for(const r of refs){const f=r&&map.get(r.path);if(!f||f.sha256!==r.sha256||Number(f.bytes)!==Number(r.bytes))return fail('NESTED_FILE_REF_MISMATCH',r&&r.path);}
 if(!m.files.some(f=>f.sha256===m.model.model_sha256))return fail('MODEL_FILE_NOT_BOUND');
 const rows=Number(m.index.rows),cols=Number(m.index.cols);if(!Number.isInteger(rows)||rows<1||!Number.isInteger(cols)||cols<1)return fail('INDEX_GEOMETRY');if(Number(m.chunker.expected_passages)!==rows)return fail('CHUNKER_ROW_MISMATCH');if(Number(m.model.embedding_dim)!==cols)return fail('MODEL_INDEX_DIM_MISMATCH');
 const vf=m.index.vectors_file,expected=m.index.dtype==='int8_row_symmetric'?rows*cols:(m.index.dtype==='float16'?rows*cols*2:(m.index.dtype==='float32'?rows*cols*4:null));if(expected==null||Number(vf.bytes)!==expected)return fail('VECTOR_FILE_GEOMETRY',{actual:vf.bytes,expected});
 if(m.index.dtype==='int8_row_symmetric'){if(!m.index.inverse_norms_file||Number(m.index.inverse_norms_file.bytes)!==rows*4)return fail('INVERSE_NORM_GEOMETRY');}
 const sf=m.speaker_filter;if(Number(sf.rows)!==rows)return fail('JESUS_MASK_ROW_MISMATCH');if(sf.mode!==m.chunker.mode||sf.policy_id!==m.chunker.policy_id)return fail('JESUS_MASK_POLICY_MISMATCH');if(Number(sf.jesus_mask_file.bytes)!==Math.ceil(rows/8))return fail('JESUS_MASK_GEOMETRY');if(sf.rule!=='HIGH_CONFIDENCE_JESUS_CANONICAL_SPAN_OVERLAP_GT_0')return fail('JESUS_MASK_RULE');if(!Number.isInteger(Number(sf.eligible_count))||Number(sf.eligible_count)<0||Number(sf.eligible_count)>rows)return fail('JESUS_MASK_ELIGIBLE_COUNT');
 const c=m.calibration,qualified=c.status==='QUALIFIED';if(qualified){if(c.human_query_gate!=='PASS'||c.hard_negative_gate!=='PASS'||!c.threshold_policy||typeof c.threshold_policy!=='object')return fail('QUALIFICATION_GATES_OPEN');const t=c.threshold_policy,ks=['close_min','possible_min','close_margin','abstain_margin'];if(ks.some(k=>!Number.isFinite(Number(t[k]))))return fail('CALIBRATION_THRESHOLD_INVALID');if(Number(t.close_min)<Number(t.possible_min)||Number(t.close_margin)<Number(t.abstain_margin)||Number(t.abstain_margin)<0)return fail('CALIBRATION_THRESHOLD_ORDER');}
 return {ok:true,code:qualified?'MANIFEST_QUALIFIED':'MANIFEST_ENGINEERING_ONLY',activation:false,qualified,fileMap:map};
}
function popcountMask(u,rows){let n=0;for(let i=0;i<rows;i++)if(u[i>>3]&(1<<(i&7)))n++;return n;}
async function verifyAssets(m,getBytes){const shape=validateManifestShape(m);if(!shape.ok)return shape;if(typeof getBytes!=='function')return fail('ASSET_READER_REQUIRED');let maskCount=null;for(const f of m.files){let data;try{data=await getBytes(f.path);}catch(e){return fail('ASSET_READ_FAILED',{path:f.path,error:String(e&&e.message||e)});}const u=data instanceof Uint8Array?data:new Uint8Array(data||[]);if(u.byteLength!==Number(f.bytes))return fail('ASSET_SIZE_MISMATCH',f.path);if(await sha256(u)!==f.sha256)return fail('ASSET_HASH_MISMATCH',f.path);if(f.path===m.speaker_filter.jesus_mask_file.path)maskCount=popcountMask(u,Number(m.index.rows));}if(maskCount!==Number(m.speaker_filter.eligible_count))return fail('JESUS_MASK_POPULATION_MISMATCH',{actual:maskCount,declared:Number(m.speaker_filter.eligible_count)});const activation=shape.qualified===true;return {ok:true,code:activation?'READY_QUALIFIED':'ENGINEERING_ONLY',activation,qualified:shape.qualified,verified_files:m.files.length,jesus_eligible_count:maskCount};}
return Object.freeze({VERSION,EXPECTED,validateManifestShape,verifyAssets,sha256,popcountMask});
});
