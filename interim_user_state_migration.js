'use strict';

function deepClone(x){ return x == null ? x : JSON.parse(JSON.stringify(x)); }
function sha256(s){
  const ascii=unescape(encodeURIComponent(String(s))); const mathPow=Math.pow,maxWord=mathPow(2,32);
  let result='',words=[],asciiBitLength=ascii.length*8,hash=sha256.h=sha256.h||[],k=sha256.k=sha256.k||[],primeCounter=k.length,isComposite={};
  for(let candidate=2;primeCounter<64;candidate++){if(!isComposite[candidate]){for(let i=0;i<313;i+=candidate)isComposite[i]=candidate;hash[primeCounter]=(mathPow(candidate,.5)*maxWord)|0;k[primeCounter++]=(mathPow(candidate,1/3)*maxWord)|0;}}
  let a=ascii+'\x80'; while(a.length%64-56)a+='\x00';
  for(let i=0;i<a.length;i++){let j=a.charCodeAt(i);if(j>>8)return '';words[i>>2]|=j<<((3-i)%4)*8;}
  words[words.length]=((asciiBitLength/maxWord)|0);words[words.length]=asciiBitLength;
  for(let j=0;j<words.length;){let w=words.slice(j,j+=16),oldHash=hash;hash=hash.slice(0,8);for(let i=0;i<64;i++){let i2=i+j,w15=w[i-15],w2=w[i-2];let A=hash[0],E=hash[4];let temp1=hash[7]+((E>>>6|E<<26)^(E>>>11|E<<21)^(E>>>25|E<<7))+((E&hash[5])^((~E)&hash[6]))+k[i]+(w[i]=(i<16)?w[i]:(w[i-16]+((w15>>>7|w15<<25)^(w15>>>18|w15<<14)^(w15>>>3))+w[i-7]+((w2>>>17|w2<<15)^(w2>>>19|w2<<13)^(w2>>>10)))|0);let temp2=((A>>>2|A<<30)^(A>>>13|A<<19)^(A>>>22|A<<10))+((A&hash[1])^(A&hash[2])^(hash[1]&hash[2]));hash=[(temp1+temp2)|0,A,hash[1],hash[2],(hash[3]+temp1)|0,E,hash[5],hash[6]];}for(let i=0;i<8;i++)hash[i]=(hash[i]+oldHash[i])|0;}
  for(let i=0;i<8;i++)for(let j=3;j+1;j--){let b=(hash[i]>>(j*8))&255;result+=(b<16?'0':'')+b.toString(16);}return result;
}
function clamp01(v){ const n=Number(v); return Number.isFinite(n)?Math.max(0,Math.min(1,n)):0; }
function uniqueRaw(text, needle){
  if(!needle) return null;
  const a=text.indexOf(needle); if(a<0) return null;
  if(text.indexOf(needle,a+1)>=0) return null;
  return {start:a,end:a+needle.length,text:needle};
}
function lexicalTokens(s){
  const out=[]; const re=/\p{L}+(?:['’]\p{L}+)*/gu; let m;
  while((m=re.exec(s))!==null) out.push({word:m[0].replace(/’/g,"'").toLowerCase(),start:m.index,end:m.index+m[0].length});
  return out;
}
function legacyOf(r){
  return {entry_id:r.entry_id||null,para_id:r.para_id||null,stable_ref:r.stable_ref||null,start_char:Number.isInteger(r.start_char)?r.start_char:null,end_char:Number.isInteger(r.end_char)?r.end_char:null,text:String(r.text||r.selected_text_snapshot||r.quote||''),approx_char:Number.isFinite(Number(r.approx_char))?Number(r.approx_char):null,fraction_within_paragraph:Number.isFinite(Number(r.fraction_within_paragraph))?Number(r.fraction_within_paragraph):null};
}
function markStale(r,status,reason,legacy){
  r.needs_reanchor=true; r.stale_status=status; r.migrated_reason=reason; r.legacy_anchor=r.legacy_anchor||legacy;
  r.corpus_generation='INTERIM_SUCCESSOR_REV4';
  return r;
}
function markActive(r,reason,legacy){
  r.needs_reanchor=false; r.stale_status='active'; r.migrated_reason=reason; r.legacy_anchor=r.legacy_anchor||legacy;
  r.corpus_generation='INTERIM_SUCCESSOR_REV4';
  return r;
}
function D1Model(map){
  const old=map.D1.old_text, oldTok=lexicalTokens(old), flat=[];
  for(const t of map.D1.retained){ for(const x of lexicalTokens(t.text)) flat.push({...x,para_id:t.para_id,stable_ref:t.stable_ref,para_text:t.text}); }
  if(oldTok.length!==flat.length || oldTok.some((x,i)=>x.word!==flat[i].word)) throw new Error('D1 lexical sequence mismatch');
  return {old,oldTok,flat,retained:map.D1.retained};
}
function d1MapSpan(model,start,end){
  const {old,oldTok,flat,retained}=model;
  if(!(Number.isInteger(start)&&Number.isInteger(end)&&0<=start&&start<=end&&end<=old.length)) return {status:'NEEDS_REANCHOR',reason:'INVALID_BOUNDS'};
  const raw=old.slice(start,end);
  if(start===end) return {status:'NEEDS_REANCHOR',reason:'EMPTY_OR_CARET_ONLY'};
  const exact=[];
  for(const t of retained){ const h=uniqueRaw(t.text,raw); if(h) exact.push({...h,para_id:t.para_id,stable_ref:t.stable_ref,para_text:t.text}); }
  if(exact.length===1){const z=exact[0];return {status:'MIGRATED_EXACT',parts:[{para_id:z.para_id,stable_ref:z.stable_ref,start_char:z.start,end_char:z.end,text:z.text,para_text:z.para_text}],method:'UNIQUE_RAW'};}
  const inds=[]; for(let i=0;i<oldTok.length;i++){ const x=oldTok[i]; if(x.end>start && x.start<end) inds.push(i); }
  if(!inds.length) return {status:'NEEDS_REANCHOR',reason:'NO_LEXICAL_ANCHOR'};
  const a=inds[0], b=inds[inds.length-1], parts=[];
  for(let i=a;i<=b;i++){
    const o=oldTok[i], t=flat[i]; if(o.word!==t.word) return {status:'NEEDS_REANCHOR',reason:'TOKEN_MISMATCH'};
    let ss=t.start, ee=t.end;
    if(i===a && start>o.start) ss=t.start+(start-o.start);
    if(i===b && end<o.end) ee=t.start+(end-o.start);
    if(ss<t.start || ee>t.end || ss>ee) return {status:'NEEDS_REANCHOR',reason:'BOUNDARY_UNMAPPABLE'};
    const prev=parts[parts.length-1];
    if(prev && prev.para_id===t.para_id && prev.end_char<=ss){ prev.end_char=ee; prev.text=t.para_text.slice(prev.start_char,ee); }
    else parts.push({para_id:t.para_id,stable_ref:t.stable_ref,start_char:ss,end_char:ee,text:t.para_text.slice(ss,ee),para_text:t.para_text});
  }
  return {status:parts.length===1?'MIGRATED_EXACT':'MIGRATED_SPLIT',parts,method:'LEXICAL_SEQUENCE_ONE_TO_ONE'};
}
function isD1(r,map){ return r && (r.para_id===map.D1.deleted_para_id || r.stable_ref===map.D1.deleted_ref); }
function isD2P1(r,map){ return r && (r.para_id===map.D2.deleted_para_id || r.stable_ref===map.D2.deleted_ref); }
function isD2P2(r,map){ return r && (r.para_id===map.D2.trimmed_para_id || r.stable_ref===map.D2.trimmed_ref); }
function d2MapSpan(map,start,end){
  const cut=map.D2.prefix_length, old=map.D2.old_trimmed_text, newer=map.D2.new_trimmed_text;
  if(!(Number.isInteger(start)&&Number.isInteger(end)&&0<=start&&start<=end&&end<=old.length)) return {status:'NEEDS_REANCHOR',reason:'INVALID_BOUNDS'};
  if(end<=cut) return {status:'RETIRED_SOURCE_CONTENT',retired_part:old.slice(start,end)};
  if(start>=cut){ const ns=start-cut,ne=end-cut; return {status:'MIGRATED_EXACT',parts:[{para_id:map.D2.trimmed_para_id,stable_ref:map.D2.trimmed_ref,start_char:ns,end_char:ne,text:newer.slice(ns,ne),para_text:newer}],method:'PREFIX_SHIFT'}; }
  return {status:'MIGRATED_SPLIT',retired_part:old.slice(start,cut),parts:[{para_id:map.D2.trimmed_para_id,stable_ref:map.D2.trimmed_ref,start_char:0,end_char:end-cut,text:newer.slice(0,end-cut),para_text:newer}],method:'PREFIX_CROSS_BOUNDARY'};
}
function updateTextAnchorRecord(r,p,reason,legacy){
  r.para_id=p.para_id; if(r.stable_ref && p.stable_ref) r.stable_ref=p.stable_ref;
  r.start_char=p.start_char; r.end_char=p.end_char;
  if('text' in r) r.text=p.text;
  if('selected_text_snapshot' in r) r.selected_text_snapshot=p.text;
  if('quote' in r) r.quote=p.text;
  r.para_fingerprint=p.para_text.slice(0,32); r.para_fingerprint_v3=sha256(p.para_text);
  return markActive(r,reason,legacy);
}
function migrateHighlightRow(r,map,d1){
  const row=deepClone(r), legacy=legacyOf(row);
  if(isD1(row,map)){
    const res=d1MapSpan(d1,Number(row.start_char),Number(row.end_char));
    if(res.status==='NEEDS_REANCHOR') return [markStale(row,'needs_reanchor','interim_d1_'+res.reason.toLowerCase(),legacy)];
    return res.parts.map((p,i)=>{ const x=deepClone(row); if(i>0) delete x.id; updateTextAnchorRecord(x,p,'interim_d1_'+res.status.toLowerCase(),legacy); return x; });
  }
  if(isD2P1(row,map)) return [markStale(row,'retired_source_content','interim_d2_deleted_heading_preserved',legacy)];
  if(isD2P2(row,map)){
    const res=d2MapSpan(map,Number(row.start_char),Number(row.end_char));
    if(res.status==='MIGRATED_EXACT') return [updateTextAnchorRecord(row,res.parts[0],'interim_d2_prefix_shift',legacy)];
    if(res.status==='RETIRED_SOURCE_CONTENT') return [markStale(row,'retired_source_content','interim_d2_removed_prefix_preserved',legacy)];
    if(res.status==='MIGRATED_SPLIT'){
      const stale=markStale(row,'retired_source_content_partial','interim_d2_cross_boundary_retired_component_preserved',legacy);
      const active=deepClone(row); delete active.id; updateTextAnchorRecord(active,res.parts[0],'interim_d2_cross_boundary_survivor',legacy); active.legacy_retired_part=res.retired_part;
      return [stale,active];
    }
    return [markStale(row,'needs_reanchor','interim_d2_invalid_bounds',legacy)];
  }
  row.corpus_generation='INTERIM_SUCCESSOR_REV4'; return [row];
}
function normalizeHighlightGroups(rows){
  const by=new Map();
  rows.forEach((r,i)=>{ const gid=r.highlight_group_id||`__single_${i}`; if(!by.has(gid))by.set(gid,[]);by.get(gid).push(r); });
  for(const arr of by.values()){
    if(arr.length>1){ arr.forEach((r,i)=>{r.part_index=i;r.part_count=arr.length;}); }
    else if(arr[0].highlight_group_id){arr[0].part_index=0;arr[0].part_count=1;}
  }
  return rows;
}
function migrateNoteRow(r,map,d1){
  const row=deepClone(r), legacy=legacyOf(row);
  const quote=String(row.quote||'');
  if(isD1(row,map)){
    if(!quote) return markStale(row,'needs_reanchor','interim_d1_note_deleted_paragraph_without_quote',legacy);
    const h=uniqueRaw(map.D1.old_text,quote); if(!h) return markStale(row,'needs_reanchor','interim_d1_note_quote_not_unique_in_source',legacy);
    const res=d1MapSpan(d1,h.start,h.end);
    if(res.status!=='MIGRATED_EXACT' || res.parts.length!==1) return markStale(row,'needs_reanchor','interim_d1_note_cross_fragment_or_ambiguous',legacy);
    const p=res.parts[0]; updateTextAnchorRecord(row,p,'interim_d1_note_unique_single_target',legacy); row.para_ids=[p.para_id]; row.anchor_parts=[{para_id:p.para_id,start_char:p.start_char,end_char:p.end_char,text:p.text}]; return row;
  }
  if(isD2P1(row,map)) return markStale(row,'retired_source_content','interim_d2_note_deleted_heading_preserved',legacy);
  if(isD2P2(row,map)){
    let start=null,end=null;
    if(Array.isArray(row.anchor_parts)&&row.anchor_parts.length===1&&Number.isInteger(row.anchor_parts[0].start_char)){start=row.anchor_parts[0].start_char;end=row.anchor_parts[0].end_char;}
    else if(quote){const h=uniqueRaw(map.D2.old_trimmed_text,quote); if(h){start=h.start;end=h.end;}}
    if(start===null) return markStale(row,'needs_reanchor','interim_d2_note_anchor_ambiguous',legacy);
    const res=d2MapSpan(map,start,end);
    if(res.status==='MIGRATED_EXACT') {const p=res.parts[0];updateTextAnchorRecord(row,p,'interim_d2_note_prefix_shift',legacy);row.para_ids=[p.para_id];row.anchor_parts=[{para_id:p.para_id,start_char:p.start_char,end_char:p.end_char,text:p.text}];return row;}
    if(res.status==='RETIRED_SOURCE_CONTENT') return markStale(row,'retired_source_content','interim_d2_note_removed_content_preserved',legacy);
    return markStale(row,'needs_reanchor','interim_d2_note_cross_boundary_preserved',legacy);
  }
  row.corpus_generation='INTERIM_SUCCESSOR_REV4'; return row;
}
function migrateColItem(r,map,d1){
  const row=deepClone(r), legacy=legacyOf(row), text=String(row.text||'');
  if(isD1(row,map)){
    if(!text) return markStale(row,'needs_reanchor','interim_d1_collection_no_text_anchor',legacy);
    const exact=[]; for(const t of map.D1.retained){const h=uniqueRaw(t.text,text);if(h)exact.push({...h,para_id:t.para_id,stable_ref:t.stable_ref,para_text:t.text});}
    if(exact.length===1){const p=exact[0];row.para_id=p.para_id;row.stable_ref=p.stable_ref;row.para_fingerprint_v3=sha256(p.para_text);return markActive(row,'interim_d1_collection_unique_target',legacy);}
    return markStale(row,'needs_reanchor','interim_d1_collection_split_or_ambiguous',legacy);
  }
  if(isD2P1(row,map)) return markStale(row,'retired_source_content','interim_d2_collection_deleted_heading_preserved',legacy);
  if(isD2P2(row,map)){
    if(!text) return markStale(row,'needs_reanchor','interim_d2_collection_no_text_anchor',legacy);
    const h=uniqueRaw(map.D2.old_trimmed_text,text); if(!h) return markStale(row,'needs_reanchor','interim_d2_collection_text_ambiguous',legacy);
    const res=d2MapSpan(map,h.start,h.end);
    if(res.status==='MIGRATED_EXACT'){const p=res.parts[0];row.para_id=p.para_id;row.stable_ref=p.stable_ref;row.text=p.text;row.para_fingerprint_v3=sha256(p.para_text);return markActive(row,'interim_d2_collection_prefix_shift',legacy);}
    if(res.status==='RETIRED_SOURCE_CONTENT') return markStale(row,'retired_source_content','interim_d2_collection_removed_content_preserved',legacy);
    return markStale(row,'needs_reanchor','interim_d2_collection_cross_boundary_preserved',legacy);
  }
  row.corpus_generation='INTERIM_SUCCESSOR_REV4'; return row;
}
function migrateReadingPos(r,map){
  const row=deepClone(r), legacy=legacyOf(row);
  if(isD1(row,map)) return markStale(row,'needs_reanchor','interim_d1_reading_position_deleted_duplicate_no_guess',legacy);
  if(isD2P1(row,map)) return markStale(row,'retired_source_content','interim_d2_reading_position_deleted_heading_preserved',legacy);
  if(isD2P2(row,map)){
    const oldLen=map.D2.old_trimmed_text.length,newLen=map.D2.new_trimmed_text.length,cut=map.D2.prefix_length;
    let pos=Number.isFinite(Number(row.approx_char))?Math.max(0,Math.min(oldLen,Math.round(Number(row.approx_char)))):Math.round(clamp01(row.fraction_within_paragraph)*oldLen);
    if(pos<cut) return markStale(row,'needs_reanchor','interim_d2_reading_position_in_removed_prefix',legacy);
    const np=pos-cut; row.approx_char=np; row.fraction_within_paragraph=newLen?clamp01(np/newLen):0; row.excerpt=map.D2.new_trimmed_text.slice(0,80)+(map.D2.new_trimmed_text.length>80?'…':''); return markActive(row,'interim_d2_reading_position_prefix_shift',legacy);
  }
  row.corpus_generation='INTERIM_SUCCESSOR_REV4'; return row;
}
function speakerAliasRewrite(r,map){
  if(!r || !r.segment_id) return r;
  const n=map.speaker_segment_aliases[r.segment_id]; if(n){r.legacy_segment_id=r.segment_id;r.segment_id=n;r.migrated_reason=(r.migrated_reason?`${r.migrated_reason}__`:``)+'interim_speaker_segment_alias';}
  return r;
}

function dateIdAliasMaps(map){ return {entry:new Map((map.entry_aliases||[]).map(x=>[x.old_entry_id,x])),para:new Map((map.paragraph_aliases||[]).map(x=>[x.old_para_id,x]))}; }
function dateIdRewriteObjectIdentity(r,maps){
  let changed=false,entryAlias=null,paraAlias=null;
  if(r && r.entry_id && maps.entry.has(r.entry_id)){ entryAlias=maps.entry.get(r.entry_id); r.legacy_entry_id=r.entry_id; r.entry_id=entryAlias.new_entry_id; changed=true; }
  if(r && r.host_entry_id && maps.entry.has(r.host_entry_id)){ const a=maps.entry.get(r.host_entry_id); r.legacy_host_entry_id=r.host_entry_id; r.host_entry_id=a.new_entry_id; changed=true; }
  if(r && r.para_id && maps.para.has(r.para_id)){ paraAlias=maps.para.get(r.para_id); r.legacy_para_id=r.para_id; r.para_id=paraAlias.new_para_id; changed=true; }
  if(r && r.stable_ref){
    if(paraAlias && r.stable_ref===paraAlias.old_stable_ref){r.legacy_stable_ref=r.stable_ref;r.stable_ref=paraAlias.new_stable_ref;changed=true;}
    else if(entryAlias && r.stable_ref===entryAlias.old_stable_ref){r.legacy_stable_ref=r.stable_ref;r.stable_ref=entryAlias.new_stable_ref;changed=true;}
  }
  if(changed){r.identity_migration_generation='POST_R6_DATE_ID_A2_PREAUTH_2026-09-05';r.migrated_reason=(r.migrated_reason?`${r.migrated_reason}__`:``)+'r7_date_id_exact_alias';}
  return {changed,entryAlias,paraAlias};
}
function migrateDateIdEnvelope(input,map){
  const st=deepClone(input||{}); for(const s of ['reading_pos','highlights','notes','favorites','collections','col_items','settings','read_entries'])if(!Array.isArray(st[s]))st[s]=[];
  const maps=dateIdAliasMaps(map);
  for(const store of ['highlights','notes','col_items'])for(const r of st[store])dateIdRewriteObjectIdentity(r,maps);
  if(Array.isArray(st.favorites)){const by=new Map();for(const r of st.favorites){const res=dateIdRewriteObjectIdentity(r,maps);if(res.entryAlias&&res.entryAlias.new_date_display)r.date_display=res.entryAlias.new_date_display;const prev=by.get(r.entry_id);if(!prev||Number(r.ts||0)>=Number(prev.ts||0))by.set(r.entry_id,r);}st.favorites=[...by.values()];}
  if(Array.isArray(st.read_entries)){const by=new Map();for(const r of st.read_entries){dateIdRewriteObjectIdentity(r,maps);if(r.vol&&r.entry_id)r.key=`${r.vol}:${r.entry_id}`;const prev=by.get(r.key);if(!prev||Number(r.ts||0)>=Number(prev.ts||0))by.set(r.key,r);}st.read_entries=[...by.values()];}
  if(Array.isArray(st.reading_pos)){const by=new Map();for(const r of st.reading_pos){const oldKey=r.key,res=dateIdRewriteObjectIdentity(r,maps);if(res.entryAlias&&res.entryAlias.new_date_display&&r.label)r.label=`Tome ${Number(r.vol)||res.entryAlias.volume} · ${res.entryAlias.new_date_display}`;if(typeof oldKey==='string'&&oldKey.startsWith('entry:'))r.key=`entry:${Number(r.vol)}:${String(r.entry_id||'')}`;by.set(r.key,r);}st.reading_pos=[...by.values()];}
  return st;
}
function migrateV65ToInterim(input,dateIdMap,interimMap){ return migrateEnvelope(migrateDateIdEnvelope(input,dateIdMap),interimMap); }
function migrateEnvelope(input,map){
  const st=deepClone(input||{}); for(const s of map.stores) if(!Array.isArray(st[s])) st[s]=[];
  if(st.settings.some(x=>x&&x.key===map.idempotence_marker)) return {state:st,summary:{skipped:true,reason:'marker_present'}};
  const d1=D1Model(map), summary={skipped:false,highlights_in:st.highlights.length,highlights_out:0,notes:0,col_items:0,reading_pos:0,favorites:0,read_entries:0,collections:0,settings:0,stale_or_retired:0,new_highlight_parts:0};
  let hs=[]; for(const h of st.highlights){const out=migrateHighlightRow(h,map,d1);summary.new_highlight_parts+=Math.max(0,out.length-1);hs.push(...out);} st.highlights=normalizeHighlightGroups(hs.map(h=>speakerAliasRewrite(h,map)));summary.highlights_out=st.highlights.length;
  st.notes=st.notes.map(x=>speakerAliasRewrite(migrateNoteRow(x,map,d1),map));summary.notes=st.notes.length;
  st.col_items=st.col_items.map(x=>speakerAliasRewrite(migrateColItem(x,map,d1),map));summary.col_items=st.col_items.length;
  st.reading_pos=st.reading_pos.map(x=>speakerAliasRewrite(migrateReadingPos(x,map),map));summary.reading_pos=st.reading_pos.length;
  for(const s of ['favorites','read_entries','collections']){st[s]=st[s].map(x=>{const r=deepClone(x);r.corpus_generation='INTERIM_SUCCESSOR_REV4';return r;});summary[s]=st[s].length;}
  summary.stale_or_retired=[...st.highlights,...st.notes,...st.col_items,...st.reading_pos].filter(x=>x&&x.stale_status&&x.stale_status!=='active').length;
  st.settings=st.settings.map(deepClone); st.settings.push({key:map.idempotence_marker,value:map.fixed_point_sha256,ts:0});summary.settings=st.settings.length;
  return {state:st,summary};
}
function canonicalUserState(st){
  const x=deepClone(st); if(Array.isArray(x.settings))x.settings=x.settings.filter(r=>r.key!=='user_data_migration_log_interim_rev4').map(r=>{if(r&&r.key&&String(r.key).includes('migration')){const y={...r};delete y.ts;return y;}return r;});
  return x;
}
function verifyNoSilentDrop(before,after){
  const failures=[];
  for(const s of ['notes','col_items','reading_pos','favorites','collections','read_entries']) if((after[s]||[]).length!==(before[s]||[]).length) failures.push(`${s}_count_changed`);
  if((after.highlights||[]).length<(before.highlights||[]).length) failures.push('highlight_count_decreased');
  return failures;
}
const LDCInterimMigrationAPI={migrateEnvelope,migrateDateIdEnvelope,migrateV65ToInterim,canonicalUserState,verifyNoSilentDrop,d1MapSpan,d2MapSpan,D1Model,sha256};
if(typeof module!=='undefined'&&module.exports)module.exports=LDCInterimMigrationAPI;
if(typeof window!=='undefined')window.LDCInterimMigration=LDCInterimMigrationAPI;
