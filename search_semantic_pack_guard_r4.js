/* LDC current-corpus semantic pack guard R4.
   Successor of R3: exact v142.15 authority binding + hybrid/coverage qualification gates. */
(function(root,factory){const api=factory();if(typeof module==='object'&&module.exports)module.exports=api;if(root)root.LDCSemanticPackGuardR4=api;})(typeof globalThis!=='undefined'?globalThis:this,function(){
'use strict';
const VERSION='ldc-search-v3-semantic-pack-guard-r4';
const BINDING_CONTRACT_SHA256='54b8fa9a9e21224d02377371c96e5c878e1e92ab45dff461b826c341f608f2d9';
const PACK_ID='ldc-pls-v16-current-v14215-enriched-96-72-r1';
const EXPECTED=Object.freeze({
 corpus_generation:'G036-AFLP-R8-SUP-T5-FAST1-STAGE2-221',
 backbone_generation:'G036-AFLP-R8-UWR2-FAST1-STAGE2-221',
 offline_content_binding_sha256:'1fb8d6d8a532806ad6a25b32250091deed174ddb54130f1b05d3da2233a05384',
 corpus_manifest_sha256:'92426c8aaac6fc7c6b8a02b0a7e00cd5870e80b805b411ae64c55e59bec1ad8b',
 search_v2_manifest_sha256:'e87da88a709a1b81f6e76e1afe119a8ad946df602977a88c45c8b0d6e35dc250',
 search_v21_manifest_sha256:'86baf5f7a74c2840b9c1a48c504c402d050d59fa85526b87081f068d403ee996',
 search_documents_sha256:'65cfeb954ce9ecaa02c761024f2802436c9fcd07982e20438486d1a793fc195a',
 search_entries_sha256:'ae74aceaa596c72afa5727f1dceb39b4e349ceffbb07e926a6aab30c70a5c54c',
 search_index_sha256:'5b12b6c52dd0633ae2bf2318cd7959b04bbdd886e0adfbdef8862b41d2575b99',
 search_jesus_filter_sha256:'67bd9e80c8ed1702c95072adff9859e7a25a521df14fd1be6efb496aa0ddf31d',
 search_topology_sha256:'9d939051a8eca6929c208dcefeb1b2f41cb794fb175762dbfe18b645a9ed497f'
});
const MODEL=Object.freeze({
 model_id:'Xenova/multilingual-e5-small',immutable_revision:'761b726dd34fb83930e26aab4e9ac3899aa1fa78',
 model_sha256:'4d24e2bc01a447951524466ef533e52944bf48509e6552810bcee1a2711cb02c',
 embedding_dim:384,pooling:'mean_pooling',normalization:'l2',query_prefix:'query: ',passage_prefix:'passage: ',max_length:512
});
const RETRIEVAL=Object.freeze({id:'DENSE96_72_PLUS_BM25_96_72_EQUAL_RRF60',dense_candidate_depth:160,bm25_candidate_depth:160,fusion:'RRF',rrf_k:60,dense_weight:1,bm25_weight:1,entry_deduplication:true,output_depth:20});
function fail(code,detail){return {ok:false,code,detail:detail==null?null:detail,activation:false};}
function safePath(p){return typeof p==='string'&&p.length>0&&!p.startsWith('/')&&!p.split('/').includes('..')&&!p.includes('\\');}
function hex(bytes){return Array.from(bytes,x=>x.toString(16).padStart(2,'0')).join('');}
async function sha256(data){const u=data instanceof Uint8Array?data:new Uint8Array(data);if(!globalThis.crypto||!crypto.subtle)throw new Error('WEBCRYPTO_REQUIRED');return hex(new Uint8Array(await crypto.subtle.digest('SHA-256',u)));}
function fileMap(m){const map=new Map();for(const f of (m.files||[])){if(!f||!safePath(f.path)||map.has(f.path))return null;map.set(f.path,f);}return map;}
function sameNum(a,b){return Number(a)===Number(b);}
function validateManifestShape(m){
 if(!m||m.schema!=='ldc-search-v3-semantic-pack-r3')return fail('MANIFEST_SCHEMA');
 if(m.pack_id!==PACK_ID)return fail('PACK_ID');
 if(m.binding_contract_sha256!==BINDING_CONTRACT_SHA256)return fail('BINDING_CONTRACT');
 if(!m.bindings||!m.chunker||!m.model||!m.index||!m.speaker_filter||!m.runtime||!m.retrieval||!m.coverage||!m.calibration||!Array.isArray(m.files))return fail('MANIFEST_REQUIRED_FIELDS');
 for(const [k,v] of Object.entries(EXPECTED))if(m.bindings[k]!==v)return fail('STALE_PACK_BINDING',k);
 if(m.chunker.mode!=='enriched'||m.chunker.policy_id!=='96-72-current-v14215-r1'||!sameNum(m.chunker.window_words,96)||!sameNum(m.chunker.stride_words,72)||m.chunker.tail_anchor!=='ADD_MAX_0_N_MINUS_96_IF_DISTINCT'||!sameNum(m.chunker.expected_passages,22873))return fail('CHUNKER_CONTRACT');
 for(const [k,v] of Object.entries(MODEL))if(typeof v==='number'?!sameNum(m.model[k],v):m.model[k]!==v)return fail('MODEL_CONTRACT',k);
 for(const [k,v] of Object.entries(RETRIEVAL))if(typeof v==='number'?!sameNum(m.retrieval[k],v):m.retrieval[k]!==v)return fail('RETRIEVAL_CONTRACT',k);
 if(!sameNum(m.coverage.current_documents,74528)||!sameNum(m.coverage.covered_documents,74528)||!sameNum(m.coverage.missing_documents,0)||m.coverage.status!=='PASS')return fail('COVERAGE_CONTRACT');
 const map=fileMap(m);if(!map)return fail('INVALID_OR_DUPLICATE_FILE_PATH');
 const refs=[...(m.model.tokenizer_files||[]),m.index.vectors_file,m.index.metadata_file,m.index.inverse_norms_file,m.speaker_filter.jesus_mask_file,...(m.runtime.files||[]),m.coverage.proof_file,m.calibration.evidence_file].filter(Boolean);
 for(const r of refs){const f=r&&map.get(r.path);if(!f||f.sha256!==r.sha256||!sameNum(f.bytes,r.bytes))return fail('NESTED_FILE_REF_MISMATCH',r&&r.path);}
 if(!m.files.some(f=>f.sha256===m.model.model_sha256))return fail('MODEL_FILE_NOT_BOUND');
 const rows=Number(m.index.rows),cols=Number(m.index.cols);if(rows!==22873||cols!==384||Number(m.chunker.expected_passages)!==rows)return fail('INDEX_GEOMETRY');
 if(m.index.dtype!=='int8_row_symmetric'||Number(m.index.vectors_file.bytes)!==rows*cols||Number(m.index.inverse_norms_file.bytes)!==rows*4)return fail('VECTOR_GEOMETRY');
 const sf=m.speaker_filter;if(Number(sf.rows)!==rows||sf.mode!=='enriched'||sf.policy_id!==m.chunker.policy_id||Number(sf.jesus_mask_file.bytes)!==Math.ceil(rows/8)||sf.rule!=='HIGH_CONFIDENCE_JESUS_CANONICAL_SPAN_OVERLAP_GT_0')return fail('JESUS_MASK_CONTRACT');
 const c=m.calibration,qualified=c.status==='QUALIFIED';
 if(qualified){
   if(c.owner_real_query_gate!=='PASS'||c.hard_negative_gate!=='PASS'||c.blind_challenge_gate!=='PASS')return fail('QUALIFICATION_GATES_OPEN');
   const p=c.hybrid_policy,ks=['close_min_rrf','close_min_margin','possible_min_rrf','possible_min_margin','close_min_channels','possible_min_channels'];
   if(!p||p.policy_id!=='HYBRID_RRF60_ABSTENTION_V1'||ks.some(k=>!Number.isFinite(Number(p[k]))))return fail('HYBRID_CALIBRATION_POLICY_INVALID');
   if(Number(p.close_min_rrf)<Number(p.possible_min_rrf)||Number(p.close_min_margin)<Number(p.possible_min_margin)||Number(p.possible_min_margin)<0)return fail('HYBRID_CALIBRATION_POLICY_ORDER');
   if(Number(p.close_min_channels)<Number(p.possible_min_channels)||Number(p.possible_min_channels)<1||Number(p.close_min_channels)>2)return fail('HYBRID_CALIBRATION_CHANNEL_ORDER');
 }
 return {ok:true,code:qualified?'MANIFEST_QUALIFIED':'MANIFEST_ENGINEERING_ONLY',activation:false,qualified,fileMap:map};
}
function popcountMask(u,rows){let n=0;for(let i=0;i<rows;i++)if(u[i>>3]&(1<<(i&7)))n++;return n;}
async function verifyAssets(m,getBytes){const shape=validateManifestShape(m);if(!shape.ok)return shape;if(typeof getBytes!=='function')return fail('ASSET_READER_REQUIRED');let maskCount=null;
 for(const f of m.files){let data;try{data=await getBytes(f.path);}catch(e){return fail('ASSET_READ_FAILED',{path:f.path,error:String(e&&e.message||e)});}const u=data instanceof Uint8Array?data:new Uint8Array(data||[]);if(u.byteLength!==Number(f.bytes))return fail('ASSET_SIZE_MISMATCH',f.path);if(await sha256(u)!==f.sha256)return fail('ASSET_HASH_MISMATCH',f.path);if(f.path===m.speaker_filter.jesus_mask_file.path)maskCount=popcountMask(u,Number(m.index.rows));}
 if(maskCount!==Number(m.speaker_filter.eligible_count))return fail('JESUS_MASK_POPULATION_MISMATCH',{actual:maskCount,declared:Number(m.speaker_filter.eligible_count)});
 const activation=shape.qualified===true;return {ok:true,code:activation?'READY_QUALIFIED':'ENGINEERING_ONLY',activation,qualified:shape.qualified,verified_files:m.files.length,jesus_eligible_count:maskCount};
}
return Object.freeze({VERSION,PACK_ID,BINDING_CONTRACT_SHA256,EXPECTED,MODEL,RETRIEVAL,validateManifestShape,verifyAssets,sha256,popcountMask});
});
