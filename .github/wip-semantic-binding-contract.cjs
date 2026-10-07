const fs=require('fs'),crypto=require('crypto');
const G=require('../search_semantic_pack_guard_r4.js');
const CONTRACT='pls_v16/BINDING_CONTRACT.json';
const EXPECTED_CONTRACT_SHA='54b8fa9a9e21224d02377371c96e5c878e1e92ab45dff461b826c341f608f2d9';
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const ok=(c,m)=>{if(!c)throw new Error(m);};
const C=JSON.parse(fs.readFileSync(CONTRACT,'utf8'));
ok(sha(CONTRACT)===EXPECTED_CONTRACT_SHA,'BINDING_CONTRACT_SHA');
ok(G.BINDING_CONTRACT_SHA256===EXPECTED_CONTRACT_SHA,'GUARD_CONTRACT_SHA');
ok(G.PACK_ID===C.pack_id,'PACK_ID_MATCH');
for(const [k,v] of Object.entries(C.bindings))ok(G.EXPECTED[k]===v,'GUARD_BINDING_'+k);
const actual={
 corpus_manifest_sha256:sha('corpus/manifest.json'),
 search_v2_manifest_sha256:sha('corpus/search_v2_manifest.json'),
 search_v21_manifest_sha256:sha('corpus/search_v21_manifest.json'),
 search_documents_sha256:sha('corpus/search_v2_documents.json'),
 search_entries_sha256:sha('corpus/search_v2_entries.json'),
 search_index_sha256:sha('corpus/search_v2_index.json'),
 search_jesus_filter_sha256:sha('corpus/search_v2_jesus_filter.json'),
 search_topology_sha256:sha('corpus/search_v21_topology.json')
};
for(const [k,v] of Object.entries(actual))ok(C.bindings[k]===v,'CURRENT_AUTHORITY_'+k+' '+v);
const off=JSON.parse(fs.readFileSync('offline_manifest.json','utf8'));
ok(off.content_binding_sha256===C.bindings.offline_content_binding_sha256,'OFFLINE_CONTENT_BINDING');
ok(off.corpus_generation===C.bindings.corpus_generation,'CORPUS_GENERATION');
const ver=JSON.parse(fs.readFileSync('version.json','utf8'));
ok(ver.app_version===C.base_candidate.technical_identity&&ver.public_version===C.base_candidate.public_version,'FROZEN_BASE_IDENTITY');
const proto=JSON.parse(fs.readFileSync('pls_v15/pack/prototype_manifest.json','utf8'));
ok(proto.status==='OWNER_PROTOTYPE_ONLY__NOT_PRODUCTION_QUALIFIED','OLD_PROTOTYPE_STATUS');
ok(proto.original_rows===20583&&proto.compatible_rows===20236&&proto.excluded_rows===347,'OLD_COMPAT_COUNTS');
ok(!fs.readFileSync('index.html','utf8').includes('search_semantic_pack_guard_r4.js'),'NO_RUNTIME_WIRING_AT_BINDING_STAGE');
const fake=(path,bytes,hash='a'.repeat(64))=>({path,bytes,sha256:hash});
const model=fake('model/onnx/model_int8.onnx',118054593,G.MODEL.model_sha256);
const tok=fake('model/tokenizer.json',10,'b'.repeat(64)),vec=fake('pack/vectors.i8',22873*384,'c'.repeat(64)),norm=fake('pack/inverse_norms.f32le',22873*4,'d'.repeat(64)),meta=fake('pack/metadata.jsonl',100,'e'.repeat(64)),mask=fake('pack/jesus_mask.bits',Math.ceil(22873/8),'f'.repeat(64)),cov=fake('evidence/coverage.json',50,'1'.repeat(64)),cal=fake('evidence/calibration.json',50,'2'.repeat(64));
const manifest={
 schema:'ldc-search-v3-semantic-pack-r3',pack_id:G.PACK_ID,binding_contract_sha256:G.BINDING_CONTRACT_SHA256,bindings:{...G.EXPECTED},
 chunker:{mode:'enriched',policy_id:'96-72-current-v14215-r1',window_words:96,stride_words:72,tail_anchor:'ADD_MAX_0_N_MINUS_96_IF_DISTINCT',expected_passages:22873},
 model:{...G.MODEL,tokenizer_files:[tok]},index:{rows:22873,cols:384,dtype:'int8_row_symmetric',vectors_file:vec,metadata_file:meta,inverse_norms_file:norm},
 speaker_filter:{rows:22873,mode:'enriched',policy_id:'96-72-current-v14215-r1',rule:'HIGH_CONFIDENCE_JESUS_CANONICAL_SPAN_OVERLAP_GT_0',eligible_count:20098,jesus_mask_file:mask},
 runtime:{files:[]},retrieval:{...G.RETRIEVAL},coverage:{status:'PASS',current_documents:74528,covered_documents:74528,missing_documents:0,proof_file:cov},
 calibration:{status:'ENGINEERING_ONLY',evidence_file:cal},files:[model,tok,vec,norm,meta,mask,cov,cal]
};
let v=G.validateManifestShape(manifest);ok(v.ok&&v.qualified===false&&v.activation===false,'ENGINEERING_MANIFEST_FAIL_CLOSED');
v=G.validateManifestShape({...manifest,bindings:{...manifest.bindings,search_documents_sha256:'0'.repeat(64)}});ok(!v.ok&&v.code==='STALE_PACK_BINDING','STALE_BINDING_REJECTED');
v=G.validateManifestShape({...manifest,pack_id:'wrong'});ok(!v.ok&&v.code==='PACK_ID','WRONG_PACK_REJECTED');
v=G.validateManifestShape({...manifest,calibration:{...manifest.calibration,status:'QUALIFIED'}});ok(!v.ok&&v.code==='QUALIFICATION_GATES_OPEN','UNPROVEN_QUALIFICATION_REJECTED');
const out={schema:'ldc-wip-semantic-binding-contract-qa-v1',status:'PASS',binding_contract_sha256:EXPECTED_CONTRACT_SHA,guard_version:G.VERSION,current_authorities:actual,old_prototype:{original_rows:proto.original_rows,compatible_rows:proto.compatible_rows,excluded_rows:proto.excluded_rows},checks:['CURRENT_AUTHORITY_HASHES','FROZEN_BASE_IDENTITY','NO_RUNTIME_WIRING','ENGINEERING_FAIL_CLOSED','STALE_BINDING_REJECTED','UNPROVEN_QUALIFICATION_REJECTED']};
fs.writeFileSync('wip-semantic-binding-contract-qa.json',JSON.stringify(out,null,2)+'\n');console.log(JSON.stringify(out,null,2));
