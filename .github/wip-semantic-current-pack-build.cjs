const fs=require('fs'),crypto=require('crypto');
const Exact=require('../search_exact_v21.js');
const Core=require('../search_engine_v2.js');

const OUT_DIR='wip-current-semantic-pack';
fs.mkdirSync(OUT_DIR,{recursive:true});
const EXPECTED=Object.freeze({
 'corpus/manifest.json':'92426c8aaac6fc7c6b8a02b0a7e00cd5870e80b805b411ae64c55e59bec1ad8b',
 'corpus/search_v2_manifest.json':'e87da88a709a1b81f6e76e1afe119a8ad946df602977a88c45c8b0d6e35dc250',
 'corpus/search_v21_manifest.json':'86baf5f7a74c2840b9c1a48c504c402d050d59fa85526b87081f068d403ee996',
 'corpus/search_v2_documents.json':'65cfeb954ce9ecaa02c761024f2802436c9fcd07982e20438486d1a793fc195a',
 'corpus/search_v2_entries.json':'ae74aceaa596c72afa5727f1dceb39b4e349ceffbb07e926a6aab30c70a5c54c',
 'corpus/search_v2_jesus_filter.json':'67bd9e80c8ed1702c95072adff9859e7a25a521df14fd1be6efb496aa0ddf31d',
 'corpus/search_v21_topology.json':'9d939051a8eca6929c208dcefeb1b2f41cb794fb175762dbfe18b645a9ed497f',
 'pls_v15/pack/metadata.jsonl':'58246f6906d1f5fce6b726a443f43c3d875ef4e2ca850b17c0e87521cb67dda1',
 'pls_v15/pack/jesus_mask.bits':'9b84ce9dc9a66c3498111769fb10d2f3e56b6309f659be8c343fc6c946bbb739'
});
function shaFile(p){const h=crypto.createHash('sha256');h.update(fs.readFileSync(p));return h.digest('hex');}
function assert(c,m){if(!c)throw new Error(m);}
for(const [p,want] of Object.entries(EXPECTED)){const got=shaFile(p);assert(got===want,'AUTHORITY_HASH_MISMATCH '+p+' '+got+' != '+want);}

const documents=JSON.parse(fs.readFileSync('corpus/search_v2_documents.json','utf8'));
const entries=JSON.parse(fs.readFileSync('corpus/search_v2_entries.json','utf8'));
const jesusFilter=JSON.parse(fs.readFileSync('corpus/search_v2_jesus_filter.json','utf8'));
const topology=JSON.parse(fs.readFileSync('corpus/search_v21_topology.json','utf8'));
const docs=documents.documents, ents=entries.entries;
assert(Array.isArray(docs)&&docs.length===74528,'CURRENT_DOCUMENT_POPULATION');
const exact=Exact.createExactLayer({documents,entries,jesusFilter,topology});
const authority=exact.nearAuthority;
const units=authority.units('enriched');
const entryById=new Map(ents.map((e,i)=>[String(e[0]),{row:e,index:i}]));

function coalesce(tokens){
 const out=[];
 for(const t of tokens){
  const di=Number(t.di), d=docs[di];
  assert(Number.isInteger(di)&&d,'TOKEN_DOC_MISSING');
  const s=Number(t.s),e=Number(t.e);
  assert(Number.isInteger(s)&&Number.isInteger(e)&&s>=0&&e>=s&&e<=String(d[5]||'').length,'TOKEN_SPAN_INVALID');
  const last=out[out.length-1];
  if(last&&last.doc_index===di) last.canonical_end=Math.max(last.canonical_end,e);
  else out.push({doc_index:di,para_id:String(d[0]),stable_ref:String(d[4]),canonical_start:s,canonical_end:e});
 }
 return out;
}
function starts96_72(n){
 if(n<=0)return[];
 const s=new Set();
 for(let i=0;i<n;i+=72)s.add(i);
 s.add(Math.max(0,n-96));
 return [...s].sort((a,b)=>a-b);
}
function sig(row){
 return String(row.unit_id)+'|'+JSON.stringify(row.source_spans)+'|'+String(row.text);
}
function bitHas(bits,i){return !!(bits[i>>3]&(1<<(i&7)));}
function setBit(bits,i,v){if(v)bits[i>>3]|=(1<<(i&7));}

const oldRows=fs.readFileSync('pls_v15/pack/metadata.jsonl','utf8').trimEnd().split(/\r?\n/).filter(Boolean).map(JSON.parse);
const oldBits=fs.readFileSync('pls_v15/pack/jesus_mask.bits');
assert(oldRows.length===20236,'OLD_FILTERED_ROWS');
const oldBySig=new Map();
for(let i=0;i<oldRows.length;i++){const k=sig(oldRows[i]);let a=oldBySig.get(k);if(!a){a=[];oldBySig.set(k,a);}a.push(i);}

const rows=[], rowJesus=[], cover=new Uint8Array(docs.length), unitReports=[];
let ordinal=1, visibleFailures=0, emptyTokenUnits=0;
for(const u of units){
 const tokens=authority.tokens('enriched',u.id);
 if(!tokens.length){emptyTokenUnits++;unitReports.push({unit_id:u.id,tokens:0,windows:0});continue;}
 const wholeSpans=coalesce(tokens), fullText=authority.visibleText(wholeSpans);
 const starts=starts96_72(tokens.length);
 let priorVisible=-1;
 for(const start of starts){
  const end=Math.min(tokens.length,start+96), slice=tokens.slice(start,end);
  assert(slice.length>0&&slice.length<=96,'WINDOW_GEOMETRY');
  const spans=coalesce(slice), text=authority.visibleText(spans);
  assert(text.length>0,'WINDOW_TEXT_EMPTY '+u.id+' '+start);
  let vstart=fullText.indexOf(text,Math.max(0,priorVisible+1));
  if(vstart<0){
   // Extremely defensive fallback for a repeated/overlap ambiguity: enumerate
   // occurrences and choose the first one whose position is strictly monotone.
   let at=fullText.indexOf(text),cand=-1;
   while(at>=0){if(at>priorVisible){cand=at;break;}at=fullText.indexOf(text,at+1);}
   vstart=cand;
  }
  if(vstart<0){visibleFailures++;throw new Error('VISIBLE_OFFSET_NOT_FOUND '+u.id+' '+start);}
  priorVisible=vstart;
  for(const s of spans)cover[s.doc_index]=1;
  const entRec=entryById.get(String(u.entry_id));
  assert(entRec,'ENTRY_NOT_FOUND '+u.entry_id);
  const e=entRec.row;
  rowJesus.push(authority.touchesJesus(slice));
  rows.push({
   passage_id:'E-96-72-'+String(ordinal++).padStart(6,'0'),
   chunk_policy_id:'96-72',
   mode:'enriched',
   unit_id:String(u.id),
   entry_id:String(u.entry_id),
   volume:Number(u.volume),
   book_order:Number(u.book_order||0),
   date_iso:String(u.date_iso||e[5]||''),
   supplement_id:u.supplement_id==null?null:String(u.supplement_id),
   kind:String(u.id).startsWith('P:')?'principal':'complete',
   title:String(e[3]||''),
   date_display:String(e[4]||''),
   start_word:start,
   end_word:end,
   word_count:end-start,
   visible_char_start:vstart,
   visible_char_end:vstart+text.length,
   text,
   source_spans:spans
  });
 }
 unitReports.push({unit_id:u.id,tokens:tokens.length,windows:starts.length,starts_tail:starts.slice(-4)});
}

const bits=Buffer.alloc(Math.ceil(rows.length/8));
let jesusRows=0;
for(let i=0;i<rows.length;i++){const yes=!!rowJesus[i];setBit(bits,i,yes);if(yes)jesusRows++;}
const metadataText=rows.map(x=>JSON.stringify(x)).join('\n')+'\n';
fs.writeFileSync(OUT_DIR+'/metadata.jsonl',metadataText);
fs.writeFileSync(OUT_DIR+'/jesus_mask.bits',bits);

const covered=cover.reduce((a,b)=>a+(b?1:0),0),missing=[];
for(let i=0;i<cover.length;i++)if(!cover[i])missing.push({doc_index:i,id:docs[i][0],entry_index:docs[i][1],volume:docs[i][2],stable_ref:docs[i][4],text:String(docs[i][5]||'').slice(0,240)});

let overlap=0,jesusParity=0,visibleParity=0,startParity=0,fullParity=0;
const overlapExamples=[],oldUnmatched=[];
const newBySig=new Map();
for(let i=0;i<rows.length;i++){const k=sig(rows[i]);let a=newBySig.get(k);if(!a){a=[];newBySig.set(k,a);}a.push(i);}
for(let oi=0;oi<oldRows.length;oi++){
 const o=oldRows[oi], ni=(newBySig.get(sig(o))||[])[0];
 if(ni==null){if(oldUnmatched.length<50)oldUnmatched.push({old_row:oi,passage_id:o.passage_id,unit_id:o.unit_id,start_word:o.start_word,end_word:o.end_word});continue;}
 overlap++;
 const n=rows[ni], oj=bitHas(oldBits,oi),nj=bitHas(bits,ni);
 if(oj===nj)jesusParity++;
 if(o.visible_char_start===n.visible_char_start&&o.visible_char_end===n.visible_char_end)visibleParity++;
 if(o.start_word===n.start_word&&o.end_word===n.end_word)startParity++;
 const cloneN={...n,passage_id:o.passage_id};
 if(JSON.stringify(o)===JSON.stringify(cloneN))fullParity++;
 if(overlapExamples.length<8)overlapExamples.push({old_passage_id:o.passage_id,new_passage_id:n.passage_id,unit_id:o.unit_id,old_start:o.start_word,new_start:n.start_word,visible_equal:o.visible_char_start===n.visible_char_start&&o.visible_char_end===n.visible_char_end,jesus_equal:oj===nj});
}

const newByUnit=new Map();for(const r of rows){let a=newByUnit.get(r.unit_id);if(!a){a=[];newByUnit.set(r.unit_id,a);}a.push(r);}
const oldByUnit=new Map();for(const r of oldRows){let a=oldByUnit.get(r.unit_id);if(!a){a=[];oldByUnit.set(r.unit_id,a);}a.push(r);}
function countsForText(s){
 const str=String(s||'');
 return {
  whitespace:(str.match(/\S+/g)||[]).length,
  unicode_apostrophe:(str.match(/[\p{L}\p{N}]+(?:['’][\p{L}\p{N}]+)*/gu)||[]).length,
  unicode_plain:(str.match(/[\p{L}\p{N}]+/gu)||[]).length,
  search_all:Core.normalise(str).split(' ').filter(Boolean).length,
  search_min3:Core.terms(str,3).length
 };
}
function rawFromSpans(spans){
 return (spans||[]).map(s=>String(docs[s.doc_index]?.[5]||'').slice(Number(s.canonical_start),Number(s.canonical_end))).join(' ');
}
const builderDiagnostics=[];
for(let oi=0;oi<oldRows.length&&builderDiagnostics.length<12;oi++){
 const o=oldRows[oi];if((newBySig.get(sig(o))||[]).length)continue;
 const nu=newByUnit.get(o.unit_id)||[], nearest=nu.reduce((best,x)=>!best||Math.abs(x.start_word-o.start_word)<Math.abs(best.start_word-o.start_word)?x:best,null);
 const ou=oldByUnit.get(o.unit_id)||[], raw=rawFromSpans(o.source_spans), rawCollapsed=raw.replace(/\s+/g,' ').trim(), visible=authority.visibleText(o.source_spans||[]);
 const unitTokens=authority.tokens('enriched',o.unit_id);
 builderDiagnostics.push({
  old_row:oi,passage_id:o.passage_id,unit_id:o.unit_id,
  old_start:o.start_word,old_end:o.end_word,old_word_count:o.word_count,
  old_unit_max_end:Math.max(...ou.map(x=>Number(x.end_word)||0)),
  current_exact_unit_tokens:unitTokens.length,
  old_text_chars:String(o.text||'').length,
  token_counts_old_text:countsForText(o.text),
  old_text_equals_raw_join:o.text===raw,
  old_text_equals_raw_collapsed:o.text===rawCollapsed,
  old_text_equals_exact_visible:o.text===visible,
  raw_join_chars:raw.length,raw_collapsed_chars:rawCollapsed.length,exact_visible_chars:visible.length,
  nearest_new:nearest?{start:nearest.start_word,end:nearest.end_word,word_count:nearest.word_count,text_chars:nearest.text.length,token_counts:countsForText(nearest.text),same_text:o.text===nearest.text,same_spans:JSON.stringify(o.source_spans)===JSON.stringify(nearest.source_spans)}:null,
  old_text_prefix:String(o.text||'').slice(0,500),
  raw_prefix:raw.slice(0,500),
  exact_visible_prefix:visible.slice(0,500),
  nearest_new_prefix:nearest?nearest.text.slice(0,500):null
 });
}

const report={
 schema:'ldc-wip-current-semantic-pack-build-report-v1',
 status:'ENGINEERING_ONLY__NOT_QUALIFIED__NOT_DEPLOYABLE',
 exact_text_authority:'search_exact_v21.js nearAuthority enriched logical-unit token/span stream',
 current_authorities:EXPECTED,
 chunk_policy:{id:'96-72',window_words:96,stride_words:72,tail_anchor:'ADD_MAX_0_N_MINUS_96_IF_DISTINCT',ordering:'ASCENDING_START_WITHIN_ENRICHED_UNIT_ORDER'},
 counts:{documents:docs.length,entries:ents.length,enriched_units:units.length,windows:rows.length,jesus_windows:jesusRows,covered_documents:covered,missing_documents:missing.length,empty_token_units:emptyTokenUnits,visible_offset_failures:visibleFailures},
 coverage_fraction:covered/docs.length,
 coverage_pass:covered===docs.length,
 missing_documents:missing,
 builder_diagnostics:builderDiagnostics,
 protected_filtered_overlap:{
   old_rows:oldRows.length,
   exact_source_text_signature_overlap:overlap,
   unmatched_old_rows:oldRows.length-overlap,
   jesus_mask_parity_on_overlap:jesusParity,
   visible_offset_parity_on_overlap:visibleParity,
   start_end_word_parity_on_overlap:startParity,
   full_row_parity_after_passage_id_rebind:fullParity,
   examples:overlapExamples,
   unmatched_examples:oldUnmatched
 },
 unit_tail_samples:unitReports.filter(x=>x.windows>=3).slice(0,30),
 output:{
   metadata:{path:OUT_DIR+'/metadata.jsonl',bytes:Buffer.byteLength(metadataText),sha256:shaFile(OUT_DIR+'/metadata.jsonl')},
   jesus_mask:{path:OUT_DIR+'/jesus_mask.bits',bytes:bits.length,sha256:shaFile(OUT_DIR+'/jesus_mask.bits')}
 }
};
fs.writeFileSync('wip-current-semantic-pack-build-report.json',JSON.stringify(report,null,2)+'\n');
const manifest={
 schema:'ldc-search-v3-semantic-pack-current-corpus-engineering-v1',
 status:'ENGINEERING_ONLY__NOT_QUALIFIED__NOT_DEPLOYABLE',
 corpus_generation:'G036-AFLP-R8-SUP-T5-FAST1-STAGE2-221',
 retrieval_target:'E5_DENSE_96_72_PLUS_MATCHED_BM25_96_72_EQUAL_RRF60',
 chunk_policy:report.chunk_policy,
 bindings:{
  corpus_manifest_sha256:EXPECTED['corpus/manifest.json'],
  search_v2_manifest_sha256:EXPECTED['corpus/search_v2_manifest.json'],
  search_v21_manifest_sha256:EXPECTED['corpus/search_v21_manifest.json'],
  search_documents_sha256:EXPECTED['corpus/search_v2_documents.json'],
  search_entries_sha256:EXPECTED['corpus/search_v2_entries.json'],
  search_jesus_filter_sha256:EXPECTED['corpus/search_v2_jesus_filter.json'],
  search_topology_sha256:EXPECTED['corpus/search_v21_topology.json']
 },
 counts:report.counts,
 files:{
  'metadata.jsonl':report.output.metadata,
  'jesus_mask.bits':report.output.jesus_mask
 },
 calibration:{status:'NOT_BUILT',hybrid_specific_required:true,production_claim:false},
 deployment_authorized:false
};
fs.writeFileSync(OUT_DIR+'/engineering_manifest.json',JSON.stringify(manifest,null,2)+'\n');
report.output.manifest={path:OUT_DIR+'/engineering_manifest.json',bytes:fs.statSync(OUT_DIR+'/engineering_manifest.json').size,sha256:shaFile(OUT_DIR+'/engineering_manifest.json')};
fs.writeFileSync('wip-current-semantic-pack-build-report.json',JSON.stringify(report,null,2)+'\n');

console.log(JSON.stringify({
 status:report.status,
 documents:docs.length,
 enriched_units:units.length,
 windows:rows.length,
 covered_documents:covered,
 missing_documents:missing.length,
 protected_overlap:report.protected_filtered_overlap,
 output:report.output
},null,2));
if(!report.coverage_pass)process.exitCode=3;
