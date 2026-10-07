const fs=require('fs'),crypto=require('crypto'),cp=require('child_process'),path=require('path');
const R7='35970c21b1e679647120f7c9bd228f22d7354239';
const EXPECT={
 'corpus/manifest.json':'8d831c437fa6c2caa56ac637c3d539279ec24b57711d209b264804cca19c0ab7',
 'corpus/search_v2_documents.json':'5320c32f3a72421c8859f92dc3f1f53b1f7da37f81ac429e00c07377250b950b',
 'corpus/search_v2_entries.json':'96fe47767e76f8b7981ce479ee66290ac49976de6482cfaaa8f2858c7fbf4793',
 'corpus/search_v2_jesus_filter.json':'092514bba4699dd68c326ed1753432f94c238ff50073bd095583d12765080667',
 'corpus/search_v21_topology.json':'e57ab52b3cf46f8be3221b455ed826efe65a6a6e359387b1a9348319c53690da',
 'corpus/search_v21_manifest.json':'a656c6b39dd5a6e4ba5649aaf1dc2a32516009c87ec38422bc1a6472a67baec4'
};
function shab(b){return crypto.createHash('sha256').update(b).digest('hex')}
function show(p){return cp.execFileSync('git',['show',R7+':'+p],{maxBuffer:64*1024*1024});}
const raw={};for(const [p,h] of Object.entries(EXPECT)){raw[p]=show(p);if(shab(raw[p])!==h)throw new Error('R7_HASH_FAIL '+p+' '+shab(raw[p]));}
const tmp=fs.mkdtempSync('/tmp/ldc-r7-');
for(const p of ['search_engine_v2.js','search_exact_v21.js'])fs.writeFileSync(path.join(tmp,p),show(p));
const Core=require(path.join(tmp,'search_engine_v2.js'));
const Exact=require(path.join(tmp,'search_exact_v21.js'));
const documents=JSON.parse(raw['corpus/search_v2_documents.json']);
const entries=JSON.parse(raw['corpus/search_v2_entries.json']);
const jesusFilter=JSON.parse(raw['corpus/search_v2_jesus_filter.json']);
const topology=JSON.parse(raw['corpus/search_v21_topology.json']);
const docs=documents.documents;
const authority=Exact.createExactLayer({documents,entries,jesusFilter,topology}).nearAuthority;
const units=authority.units('enriched');
function atomParts(a){if(Number.isInteger(a))return[a,0,String(docs[a]?.[5]||'').length];if(Array.isArray(a)&&a.length===3)return a;throw new Error('ATOM_SHAPE');}
const overrides=new Map((topology.enriched_overrides||[]).map(r=>[String(r[0]),r[1]]));
const atomMap=new Map();
for(const r of topology.base_units||[])atomMap.set('P:'+String(r[0]),overrides.get(String(r[0]))||r[4]||[]);
for(const r of topology.complete_units||[])atomMap.set(String(r[0]),r[6]||[]);
function spansOfAtoms(atoms){const out=[];for(const a of atoms){const [di,s,e]=atomParts(a),d=docs[di];if(!d)throw new Error('DOC');const last=out[out.length-1];if(last&&last.doc_index===di&&last.canonical_end===s)last.canonical_end=e;else out.push({doc_index:di,para_id:String(d[0]),stable_ref:String(d[4]),canonical_start:s,canonical_end:e});}return out;}
const WORD=/[\p{L}\p{N}]+(?:['’][\p{L}\p{N}]+)?/gu;
function tokens(text){const a=[];let m;WORD.lastIndex=0;while((m=WORD.exec(text)))a.push({s:m.index,e:m.index+m[0].length,t:m[0]});return a;}
function starts(n){if(!n)return[];const s=new Set();for(let i=0;i<n;i+=72)s.add(i);s.add(Math.max(0,n-96));return[...s].sort((a,b)=>a-b);}
const generated=[];let ordinal=1;
for(const u of units){
 const atoms=atomMap.get(String(u.id));if(!atoms)throw new Error('NO_ATOMS '+u.id);
 const full=authority.visibleText(spansOfAtoms(atoms));
 const tt=tokens(full), ss=starts(tt.length);
 for(const st of ss){const en=Math.min(tt.length,st+96),a=tt[st],z=tt[en-1];generated.push({passage_id:'E-96-72-'+String(ordinal++).padStart(6,'0'),unit_id:String(u.id),start_word:st,end_word:en,word_count:en-st,text:full.slice(a.s,z.e)});}
}
const old=fs.readFileSync('pls_v15/pack/metadata.jsonl','utf8').trim().split(/\r?\n/).map(JSON.parse);
const gm=new Map(generated.map(r=>[r.passage_id,r]));
let text=0,unit=0,start=0,all=0;const mism=[];
for(const o of old){
 const g=gm.get(o.passage_id);if(!g){if(mism.length<30)mism.push({id:o.passage_id,reason:'MISSING_ID'});continue;}
 if(g.text===o.text)text++;if(g.unit_id===o.unit_id)unit++;if(g.start_word===o.start_word&&g.end_word===o.end_word)start++;
 if(g.text===o.text&&g.unit_id===o.unit_id&&g.start_word===o.start_word&&g.end_word===o.end_word)all++;
 else if(mism.length<30)mism.push({id:o.passage_id,old_unit:o.unit_id,new_unit:g.unit_id,old_start:o.start_word,new_start:g.start_word,old_end:o.end_word,new_end:g.end_word,old_text:String(o.text).slice(0,500),new_text:String(g.text).slice(0,500)});
}
const report={schema:'ldc-wip-r7-semantic-text-reproduction-v1',status:'ENGINEERING_EVIDENCE_ONLY',r7_commit:R7,bindings:EXPECT,counts:{r7_documents:docs.length,r7_units:units.length,generated_windows:generated.length,protected_filtered_rows:old.length},parity:{text,unit,start_end:start,combined:all,combined_fraction:all/old.length},mismatches:mism};
fs.writeFileSync('wip-r7-semantic-text-reproduction.json',JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify(report,null,2));
if(generated.length!==20583||all!==old.length)process.exitCode=4;
