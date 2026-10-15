/* LDC SEARCH-V3 current-corpus registry R6.
   Qualified packs only; dense + BM25 RRF60; hybrid confidence may abstain. */
(function(root){
'use strict';const VERSION='ldc-search-v3-pack-registry-r6';
const MODES=Object.freeze({aflp:'aflp',principal:'aflp',additions:'additions','complément':'additions',complement:'additions',enriched:'enriched',enrichi:'enriched'});
const LABELS=Object.freeze({aflp:'PRINCIPAL',additions:'COMPLÉMENT',enriched:'ENRICHI'});let slots=new Map();
function normMode(m){return MODES[String(m||'').trim().toLowerCase()]||null;}
function unavailable(mode,reason,detail){return {schema:'ldc-semantic-pack-registry-v6',version:VERSION,mode:mode||null,label:mode?LABELS[mode]||mode:null,available:false,calibration_status:'UNQUALIFIED',reason,detail:detail||null};}
function apis(){if(!root.LDCSemanticPackGuardR4)throw new Error('SEMANTIC_PACK_GUARD_R4_REQUIRED');if(!root.LDCSearchSemanticV3R4)throw new Error('SEMANTIC_CORE_R4_REQUIRED');if(!root.LDCSemanticHybridR6)throw new Error('SEMANTIC_HYBRID_R6_REQUIRED');}
function u8(x){if(x instanceof Uint8Array)return new Uint8Array(x.buffer.slice(x.byteOffset,x.byteOffset+x.byteLength));if(x instanceof ArrayBuffer)return new Uint8Array(x.slice(0));return new Uint8Array(x||[]);}
function f32le(bytes,count){const b=u8(bytes);if(b.byteLength!==count*4)throw new Error('FLOAT32_BYTE_GEOMETRY');const v=new DataView(b.buffer,b.byteOffset,b.byteLength),out=new Float32Array(count);for(let i=0;i<count;i++)out[i]=v.getFloat32(i*4,true);return out;}
function parseMetadata(bytes,rows){const text=new TextDecoder('utf-8',{fatal:true}).decode(u8(bytes)),out=[];for(const line of text.split(/\r?\n/)){if(!line.trim())continue;out.push(JSON.parse(line));}if(out.length!==rows)throw new Error('METADATA_ROW_COUNT_MISMATCH');return out;}
async function buildVerifiedPayload(manifest,getBytes,mode){const rows=Number(manifest.index.rows),cols=Number(manifest.index.cols),meta=parseMetadata(await getBytes(manifest.index.metadata_file.path),rows);if(meta.some(p=>normMode(p&&p.mode)!==mode))throw new Error('INDEX_SOURCE_MODE_MISMATCH');const vb=u8(await getBytes(manifest.index.vectors_file.path)),vectors=new Int8Array(vb.buffer,vb.byteOffset,vb.byteLength),inverseNorms=f32le(await getBytes(manifest.index.inverse_norms_file.path),rows),jesusBits=u8(await getBytes(manifest.speaker_filter.jesus_mask_file.path));return {passages:meta,dim:cols,vectors,inverseNorms,jesusBits};}
function hashList(xs){return (xs||[]).map(x=>x&&x.sha256||'').join(',');}
function compatKey(entry){const m=entry.manifest;return JSON.stringify({model_sha256:m.model.model_sha256,model_id:m.model.model_id,immutable_revision:m.model.immutable_revision,embedding_dim:m.model.embedding_dim,pooling:m.model.pooling,normalization:m.model.normalization,query_prefix:m.model.query_prefix,passage_prefix:m.model.passage_prefix,tokenizers:hashList(m.model.tokenizer_files),policy_id:m.chunker.policy_id,dtype:m.index.dtype,retrieval:m.retrieval&&m.retrieval.id});}
// R198 -- small additive, cryptographically-bound projection overlay.
// The original calibrated 22,873-passage pack and frozen guard are unchanged.
// Fail closed rather than run the 15 superseded v142.15 snippets without the patch.
async function applyR198Overlay(payload,patch,manifest){
  if(!patch||patch.schema!=='ldc-pls-r198-reviewed-projections-overlay-v1'||patch.base_pack_id!==manifest.pack_id||patch.replacement_rows!==44||patch.fresh_embeddings!==11||!Array.isArray(patch.rows)||patch.rows.length!==44)throw Error('R198_OVERLAY_CONTRACT');
  const sha=globalThis.LDCSemanticPackGuardR4.sha256;
  const originalMetaSha=manifest.index.metadata_file.sha256;
  if(originalMetaSha!==patch.base_metadata_sha256)throw Error('R198_FROZEN_BASE_SHA');
  const seen=new Set();let fresh=0;
  for(const entry of patch.rows){
    const idx=Number(entry.row_index),row=entry.replacement;
    if(!Number.isInteger(idx)||idx<0||idx>=payload.passages.length||seen.has(idx)||!row||row.passage_id!==payload.passages[idx].passage_id||entry.passage_id!==row.passage_id)throw Error('R198_OVERLAY_ROW_ID');
    seen.add(idx);
    const bytes=new TextEncoder().encode(String(payload.passages[idx].text||''));
    const original=await sha(bytes);if(original!==entry.previous_text_sha256)throw Error('R198_ORIGINAL_ROW_TAMPER');
    if(!Array.isArray(row.source_spans)||!row.source_spans.length||!Number.isInteger(row.visible_char_start)||!Number.isInteger(row.visible_char_end)||row.visible_char_end<row.visible_char_start)throw Error('R198_SPANS_INVALID');
    if(entry.vector_i8!==undefined){
      if(!Array.isArray(entry.vector_i8)||entry.vector_i8.length!==payload.dim||!entry.vector_i8.every(n=>Number.isInteger(n)&&n>=-127&&n<=127)||!(Number(entry.inverse_norm)>0))throw Error('R198_VECTOR_GEOMETRY');
      const current=await sha(new TextEncoder().encode(String(row.text||'')));
      if(current!==entry.replacement_text_sha256)throw Error('R198_VECTOR_TEXT_HASH');
      payload.vectors.set(Int8Array.from(entry.vector_i8),idx*payload.dim);
      payload.inverseNorms[idx]=Number(entry.inverse_norm);
      fresh++;
    }else if(String(row.text)!==String(payload.passages[idx].text))throw Error('R198_CHANGED_ROW_NOT_REEMBEDDED');
    payload.passages[idx]=row;
  }
  if(fresh!==11)throw Error('R198_VECTOR_POPULATION');
  return {updated_rows:seen.size,fresh_vectors:fresh};
}
async function prepare(mode,spec){apis();const m=normMode(mode);if(!m)return {ok:false,status:unavailable(null,'INVALID_SOURCE_MODE',mode)};if(!spec||!spec.manifest||typeof spec.getBytes!=='function'||typeof spec.encodeQuery!=='function')return {ok:false,status:unavailable(m,'BINDING_INPUT_INCOMPLETE')};if(m!=='enriched')return {ok:false,status:unavailable(m,'CURRENT_PACK_SUPPORTS_NORMAL_READING_ONLY')};const v=await root.LDCSemanticPackGuardR4.verifyAssets(spec.manifest,spec.getBytes);if(!v.ok||v.activation!==true)return {ok:false,status:unavailable(m,v.code||'PACK_NOT_QUALIFIED',v)};let payload,index,bm25,passageById;try{payload=await buildVerifiedPayload(spec.manifest,spec.getBytes,m);if(!spec.overlay)throw Error('R198_OVERLAY_REQUIRED');await applyR198Overlay(payload,spec.overlay,spec.manifest);index=root.LDCSearchSemanticV3R4.createIndex(payload);bm25=root.LDCSemanticHybridR6.buildBm25(payload.passages,payload.jesusBits);passageById=new Map(payload.passages.map(p=>[String(p.passage_id),p]));}catch(e){return {ok:false,status:unavailable(m,'INDEX_BIND_FAILED',String(e&&e.message||e))};}if(Number(spec.manifest.index.rows)!==Number(index.passages)||Number(spec.manifest.index.cols)!==Number(index.dim)||bm25.N!==index.passages||passageById.size!==index.passages)return {ok:false,status:unavailable(m,'INDEX_MANIFEST_GEOMETRY_MISMATCH')};if(!index.jesusMaskBound)return {ok:false,status:unavailable(m,'JESUS_MASK_NOT_BOUND')};return {ok:true,mode:m,entry:{mode:m,manifest:spec.manifest,index,bm25,passageById,encodeQuery:spec.encodeQuery,verification:v}};}
async function preparePackSet(specByMode,{requireCompatible=true}={}){const entries=[];for(const[mode,spec]of Object.entries(specByMode||{})){const p=await prepare(mode,spec);if(!p.ok)return {ok:false,activation:false,code:'PACK_SET_REJECTED',failed_mode:normMode(mode)||mode,detail:p.status};entries.push(p);}if(!entries.length)return {ok:false,activation:false,code:'PACK_SET_EMPTY'};const modes=new Set(entries.map(x=>x.mode));if(modes.size!==entries.length)return {ok:false,activation:false,code:'PACK_SET_DUPLICATE_MODE'};if(requireCompatible){const keys=new Set(entries.map(x=>compatKey(x.entry)));if(keys.size!==1)return {ok:false,activation:false,code:'PACK_SET_INCOMPATIBLE_TUPLES'};}return {ok:true,activation:false,prepared:true,version:VERSION,modes:entries.map(x=>x.mode),_entries:entries};}
function commitPreparedSet(token,{replaceAll=false}={}){if(!token||token.ok!==true||token.prepared!==true||!Array.isArray(token._entries))return {ok:false,activation:false,code:'INVALID_PREPARED_TOKEN'};const next=replaceAll?new Map():new Map(slots);for(const p of token._entries)next.set(p.mode,p.entry);slots=next;return {ok:true,activation:true,version:VERSION,modes:token._entries.map(x=>x.mode),available_modes:[...slots.keys()]};}
async function bindPackSet(specByMode,opts={}){const p=await preparePackSet(specByMode,opts);if(!p.ok)return p;return commitPreparedSet(p,{replaceAll:!!opts.replaceAll});}
async function bindModePack(mode,spec){const p=await preparePackSet({[mode]:spec},{requireCompatible:false});if(!p.ok)return p.detail||unavailable(normMode(mode),'PACK_NOT_QUALIFIED');commitPreparedSet(p,{replaceAll:false});return status(normMode(mode));}
function unbindMode(mode){const m=normMode(mode);if(m)slots.delete(m);return status(m);}function unbindAll(){slots=new Map();return status();}
function status(mode){const m=mode==null?null:normMode(mode);if(mode!=null&&!m)return unavailable(null,'INVALID_SOURCE_MODE',mode);if(m){const e=slots.get(m);if(!e)return unavailable(m,'PACK_NOT_INSTALLED_OR_QUALIFIED');return {schema:'ldc-semantic-pack-registry-v6',version:VERSION,mode:m,label:LABELS[m],available:true,calibration_status:'QUALIFIED',pack_id:e.manifest.pack_id||null,model_id:e.manifest.model&&e.manifest.model.model_id||null,chunker_id:e.manifest.chunker&&e.manifest.chunker.policy_id||null,retrieval_id:e.manifest.retrieval&&e.manifest.retrieval.id||null,calibration_policy_id:e.manifest.calibration&&e.manifest.calibration.hybrid_policy&&e.manifest.calibration.hybrid_policy.policy_id||null,jesus_filter_bound:true,verified_files:e.verification.verified_files||0};}const modes={};for(const x of['aflp','additions','enriched'])modes[x]=status(x);return {schema:'ldc-semantic-pack-registry-v6',version:VERSION,available_modes:[...slots.keys()],modes};}
/* R147 targeted non-ONNX lexical-evidence disclosure. Scores do NOT become semantic confidence. */
const R147_STOPWORDS=new Set('la le les de des du d au aux un une est et que qui quel quelle quels quelles a à tres très grande grand dans sur pour avec je ma mon ton sa notre comme vous nous aujourd hui'.split(/\s+/));
function independentLexicalEvidence(q,rows,index=null){
  const H=root.LDCSemanticHybridR6;
  const normalized=H.normalise(q);
  const informative=[...new Set(H.terms(q).filter(t=>!R147_STOPWORDS.has(t)))];
  const exact=[],leads=[],exactPassages=new Set(),leadPassages=new Set();
  if(!normalized||informative.length<1)return {exact_text:exact,lexical_leads:leads};
  // Suppress weak topical noise where multiple discriminating query terms
  // never occur anywhere in this corpus (e.g. "cuivre à Londres").
  const absent=index&&index.postings?informative.filter(t=>!index.postings.has(t)):[];
  if(absent.length>=2&&absent.length*2>=informative.length)return {exact_text:exact,lexical_leads:leads};
  for(const r of rows||[]){
    const text=H.normalise(r.text||'');
    if(!text)continue;
    const passage=String(r.passage_id||'');if(!passage)continue;
    const exactQuote=text.includes(normalized);
    if(exactQuote){if(!exactPassages.has(passage)&&exact.length<5){exactPassages.add(passage);exact.push({...r,r150_evidence:'normalized_contiguous_source_quote'});}continue;}
    const have=new Set(H.terms(r.text));
    const overlaps=informative.filter(t=>have.has(t));
    // Weak lexical overlap is NOT a sufficient semantic claim.
    if(informative.length>=2&&overlaps.length>=2&&!leadPassages.has(passage)&&leads.length<8){
      leadPassages.add(passage);leads.push({...r,r150_evidence:'unverified_lexical_overlap',r150_overlap_terms:overlaps.length});
    }
  }
  return {exact_text:exact,lexical_leads:leads.filter(r=>!exactPassages.has(String(r.passage_id)))};
}
function lexicalSearch(query,options={}){
  const m=normMode(options.sourceMode);
  if(m!=='enriched')throw new Error('SEMANTIC_CURRENT_PACK_REQUIRES_ENRICHED_MODE');
  const e=slots.get(m);if(!e)throw new Error('SEMANTIC_PACK_NOT_AVAILABLE_FOR_MODE');
  const q=String(query||'').trim();if(!q)throw new Error('SEMANTIC_QUERY_EMPTY');
  const r=e.manifest.retrieval;
  const opt={sourceMode:m,volMin:options.volMin||0,volMax:options.volMax||0,dateIso:options.dateIso||null,year:options.year||0,stableRef:options.stableRef||null,jesus:!!options.jesus};
  const sparse=root.LDCSemanticHybridR6.bm25Search(e.bm25,q,{...opt,maxCandidates:r.bm25_candidate_depth});
  return {q,m,e,r,opt,sparse,independent_evidence:independentLexicalEvidence(q,sparse.results,e.bm25)};
}
async function search(query,options={}){
  // BM25 and traceable quotes are computed before the ONNX query encoder is awaited.
  const {q,m,e,r,opt,sparse,independent_evidence}=lexicalSearch(query,options);
  const vec=await e.encodeQuery(q,e.manifest.model);
  const dense=e.index.denseSearch(vec,{...opt,candidatePool:r.dense_candidate_depth,maxResults:r.dense_candidate_depth,collapseThreshold:.5});
  const fused=root.LDCSemanticHybridR6.fuse(dense.dense_candidates,sparse.results,{maxResults:r.output_depth});
  const confidence=root.LDCSemanticHybridR6.classify(fused,e.manifest.calibration.hybrid_policy);
  const enriched=fused.map(x=>Object.assign({},e.passageById.get(String(x.passage_id))||{},x));
  return {schema:'ldc-search-v3-hybrid-result-r6',version:VERSION,query:q,source_mode:m,candidate_population:'DENSE_96_72_PLUS_BM25_96_72_RRF60',filters:dense.filters,confidence,results:confidence.state==='abstain'?[]:enriched,independent_evidence,diagnostics:{dense_candidates:dense.dense_candidates.length,bm25_candidates:sparse.results.length,hybrid_features:confidence.features},pack_id:e.manifest.pack_id||null};
}
root.LDCSemanticPackRegistryR6=Object.freeze({VERSION,normMode,buildVerifiedPayload,preparePackSet,commitPreparedSet,bindModePack,bindPackSet,unbindMode,unbindAll,status,search});
})(typeof globalThis!=='undefined'?globalThis:this);
