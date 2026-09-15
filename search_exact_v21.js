/* LDC SEARCH-V2.1A TEXTUAL TRUTH — mapped visible-token exact verifier.
   Keeps SEARCH-V2/BM25 unchanged and independently governs only exactness.
   Browser/Worker: globalThis.LDCSearchExactV21. Node: module.exports. */
(function(root,factory){
  const core=(root&&root.LDCSearchV2)||(typeof require==='function'?require('./search_engine_v2.js'):null);
  const api=factory(core);
  if(typeof module==='object'&&module.exports)module.exports=api;
  if(root)root.LDCSearchExactV21=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(Core){
'use strict';
if(!Core)throw new Error('SEARCH-V2.1A requires SEARCH-V2 core');
const VERSION='ldc-search-v21-exact-r1-v21b-compatible';
const EXPECTED_SCHEMA='ldc-search-v21-topology-r1';
const EXPECTED_NORMALIZER='NFC+SEARCH_V2_NORMALISE_V1_ALL_NONEMPTY_TOKENS';
const EXPECTED_COMPOSITION='STAGE12_V21A_READER_EQUIVALENT_TOPOLOGY_R1';

function b64bytes(s){
  if(typeof Buffer!=='undefined')return Uint8Array.from(Buffer.from(s,'base64'));
  const bin=atob(s),a=new Uint8Array(bin.length);for(let i=0;i<bin.length;i++)a[i]=bin.charCodeAt(i);return a;
}
function bitHas(bits,i){return !!(bits[i>>3]&(1<<(i&7)));}
function nfc(s){return String(s==null?'':s).normalize('NFC');}
function exactTerms(s){return Core.normalise(nfc(s)).split(' ').filter(Boolean);}
function atomParts(a,documents){
  if(Number.isInteger(a))return [a,0,String(documents[a][5]||'').length];
  if(!Array.isArray(a)||a.length!==3||!Number.isInteger(a[0])||!Number.isInteger(a[1])||!Number.isInteger(a[2]))throw new Error('SEARCH-V2.1A invalid atom');
  return a;
}
function unitScopeAllows(u,p,opt){
  if(opt.volMin&&u.volume<opt.volMin)return false;
  if(opt.volMax&&u.volume>opt.volMax)return false;
  if(p.volume&&u.volume!==p.volume)return false;
  const iso=String(u.date_iso||'');
  if(p.date&&!iso.startsWith(p.date))return false;
  if(p.year&&!iso.startsWith(String(p.year)))return false;
  return true;
}
function lpsFor(q){
  const lps=new Uint32Array(q.length);let j=0;
  for(let i=1;i<q.length;){if(q[i]===q[j])lps[i++]=++j;else if(j)j=lps[j-1];else lps[i++]=0;}
  return lps;
}
function makeEntryMaps(entries){const m=new Map();for(let i=0;i<entries.length;i++)m.set(entries[i][0],i);return m;}

function createExactLayer(payload){
  const documents=payload.documents.documents, entries=payload.entries.entries, jf=payload.jesusFilter, top=payload.topology;
  if(!top||top.schema!==EXPECTED_SCHEMA)throw new Error('SEARCH-V2.1A topology schema mismatch');
  if(!top.bindings||top.bindings.normalizer!==EXPECTED_NORMALIZER||top.bindings.composition_contract!==EXPECTED_COMPOSITION)throw new Error('SEARCH-V2.1A topology authority mismatch');
  if(Number(top.counts&&top.counts.search_documents)!==documents.length||Number(top.counts&&top.counts.explicit_placements)!==76||Number(top.counts&&top.counts.legacy_fallbacks)!==1)throw new Error('SEARCH-V2.1A topology population mismatch');
  if(jf.schema!=='ldc-search-v2-jesus-filter-v1'||jf.N!==documents.length)throw new Error('SEARCH-V2.1A Jesus authority mismatch');
  const bits=b64bytes(jf.bits_b64), entryById=makeEntryMaps(entries), lexOps=new Map(), enriched=new Map();
  for(const row of top.lexical_ops||[]){if(!Array.isArray(row)||!Number.isInteger(row[0])||!Array.isArray(row[1]))throw new Error('SEARCH-V2.1A lexical-op schema mismatch');lexOps.set(row[0],row[1]);}
  for(const row of top.enriched_overrides||[]){if(!Array.isArray(row)||row.length!==2||typeof row[0]!=='string'||!Array.isArray(row[1]))throw new Error('SEARCH-V2.1A enriched override mismatch');enriched.set(row[0],row[1]);}
  function parseBase(row){return {id:'P:'+row[0],entry_id:row[0],volume:Number(row[1]),book_order:Number(row[2]||0),date_iso:String(row[3]||''),atoms:row[4],kind:'principal',supplement_id:null};}
  function parseSupp(row,kind){return {id:String(row[0]),entry_id:String(row[1]),volume:Number(row[2]),book_order:Number(row[3]||0),date_iso:String(row[4]||''),supplement_id:String(row[5]||''),atoms:row[6],kind};}
  const base=(top.base_units||[]).map(parseBase), complete=(top.complete_units||[]).map(r=>parseSupp(r,'complete')), complement=(top.complement_units||[]).map(r=>parseSupp(r,'supplement'));
  if(base.length!==Number(top.counts.base_units)||complete.length!==Number(top.counts.complete_units)||complement.length!==Number(top.counts.complement_units))throw new Error('SEARCH-V2.1A logical-unit count mismatch');
  const enrichedUnits=base.map(u=>enriched.has(u.entry_id)?{...u,atoms:enriched.get(u.entry_id)}:u).concat(complete).sort((a,b)=>a.volume-b.volume||a.book_order-b.book_order||a.id.localeCompare(b.id));
  const modeUnits={aflp:base,additions:complement,enriched:enrichedUnits};

  function emitPiece(text,baseStart,forcedSpan,emit){
    if(nfc(text)!==text)throw new Error('SEARCH-V2.1A non-NFC source text');
    let cur='',cs=-1,ce=-1,surface='';
    function flush(){if(!cur)return;emit({w:cur,s:forcedSpan?forcedSpan[0]:cs,e:forcedSpan?forcedSpan[1]:ce,surface});cur='';cs=-1;ce=-1;surface='';}
    const foldMap={'é':'e','è':'e','ê':'e','ë':'e','à':'a','â':'a','î':'i','ï':'i','ô':'o','ö':'o','ù':'u','û':'u','ü':'u','ç':'c','œ':'oe','æ':'ae'};
    for(let i=0;i<text.length;i++){
      const c=text[i],low=c.toLowerCase();let f;
      if(foldMap[low]!==undefined)f=foldMap[low];
      else if(/[\u00A0\u202F\s‘’‚‛\-–—]/.test(c))f=' ';
      else f=/[A-Za-z0-9]/.test(c)?low:' ';
      let surfaceAdded=false;
      for(const ch of f){
        if(ch===' '){flush();continue;}
        if(cs<0)cs=baseStart+i;ce=baseStart+i+1;cur+=ch;if(!surfaceAdded){surface+=c;surfaceAdded=true;}
      }
    }
    flush();
  }
  function emitAtom(a,emit){
    const [i,start,end]=atomParts(a,documents),d=documents[i];
    if(!d)throw new Error('SEARCH-V2.1A atom document missing');
    const text=String(d[5]||'');if(start<0||end<start||end>text.length)throw new Error('SEARCH-V2.1A impossible source span');
    const ops=lexOps.get(i)||[];let cur=start;
    for(const o of ops){const s=Number(o[0]),e=Number(o[1]),r=nfc(String(o[2]||''));if(e<=start||s>=end)continue;if(s<start||e>end)throw new Error('SEARCH-V2.1A display op straddles atom');if(s<cur||e<s)throw new Error('SEARCH-V2.1A overlapping display op');if(s>cur)emitPiece(text.slice(cur,s),cur,null,t=>emit({...t,di:i}));if(r)emitPiece(r,s,[s,e],t=>emit({...t,di:i}));cur=e;}
    if(cur<end)emitPiece(text.slice(cur,end),cur,null,t=>emit({...t,di:i}));
  }
  function matchParts(tokens){
    const out=[];for(const t of tokens){const d=documents[t.di],last=out[out.length-1];if(last&&last.doc_index===t.di){last.canonical_end=Math.max(last.canonical_end,t.e);last.token_count++;}else out.push({doc_index:t.di,id:d[0],para_id:d[0],stable_ref:d[4],canonical_start:t.s,canonical_end:t.e,source_kind:d[3]===1?'supplement':(String(d[0]).includes('_editorial_')?'editorial':'principal'),token_count:1});}return out;
  }
  function visibleRange(di,start,end){
    const d=documents[di],text=String(d&&d[5]||'');if(start<0||end<start||end>text.length)throw new Error('SEARCH-V2.1A impossible display excerpt span');
    const ops=lexOps.get(di)||[];let cur=start,out='';
    for(const o of ops){const s=Number(o[0]),e=Number(o[1]),r=nfc(String(o[2]||''));if(e<=start||s>=end)continue;if(s<start||e>end)throw new Error('SEARCH-V2.1A display excerpt straddles operation');if(s<cur||e<s)throw new Error('SEARCH-V2.1A overlapping display excerpt operation');if(s>cur)out+=text.slice(cur,s);out+=r;cur=e;}
    if(cur<end)out+=text.slice(cur,end);return out;
  }
  function exactVisibleText(parts){return parts.map(p=>visibleRange(p.doc_index,p.canonical_start,p.canonical_end)).join(' ').replace(/\s+/g,' ').trim();}
  function makeCard(u,tokens){
    const parts=matchParts(tokens),pi=parts[0].doc_index,d=documents[pi],ei=entryById.has(u.entry_id)?entryById.get(u.entry_id):d[1],e=entries[ei]||entries[d[1]];
    if(!e)throw new Error('SEARCH-V2.1A result entry missing');
    return {id:d[0],entry_id:u.entry_id||e[0],stable_ref:d[4],volume:u.volume,title:e[3],date_display:e[4],date_iso:u.date_iso||e[5],text:d[5],is_supplement:d[3]===1,supplement_id:u.supplement_id||null,score:0,matchType:'exact',exact_v21:true,logical_unit_id:u.id,book_order:u.book_order,match_parts:parts,primary_target:{target_kind:'EXACT_SPAN',id:d[0],entry_id:u.entry_id||e[0],stable_ref:d[4],volume:u.volume,supplement_id:u.supplement_id||null,canonical_start:parts[0].canonical_start,canonical_end:parts[0].canonical_end},exact_match_text:exactVisibleText(parts),_primary_doc_index:pi};
  }
  function scanUnit(u,q,lps,opt,cardMap){
    let state=0,queue=[];
    function acceptToken(t){
      queue.push(t);if(queue.length>q.length)queue.shift();
      while(state&&t.w!==q[state])state=lps[state-1];if(t.w===q[state])state++;
      if(state===q.length){
        const mt=queue.slice(queue.length-q.length);if(!opt.jesus||mt.some(x=>bitHas(bits,x.di))){
          const card=makeCard(u,mt),key=u.id+'|'+card._primary_doc_index,existing=cardMap.get(key);
          if(existing){existing.match_count=(existing.match_count||1)+1;if(!existing.exact_matches)existing.exact_matches=[existing.match_parts];existing.exact_matches.push(card.match_parts);}else{card.match_count=1;cardMap.set(key,card);}
        }
        state=lps[state-1];
      }
    }
    for(const a of u.atoms||[])emitAtom(a,acceptToken);
  }
  function buildStream(u){const words=[];for(const a of u.atoms||[])emitAtom(a,t=>words.push(t.w));return words.join(' ');}
  function tokenCount(stream){if(!stream)return 0;let n=1;for(let i=0;i<stream.length;i++)if(stream.charCodeAt(i)===32)n++;return n;}
  function containsPhrase(stream,phrase){
    if(!stream||!phrase)return false;let from=0,at;
    while((at=stream.indexOf(phrase,from))!==-1){const end=at+phrase.length;if((at===0||stream.charCodeAt(at-1)===32)&&(end===stream.length||stream.charCodeAt(end)===32))return true;from=at+1;}return false;
  }
  // Compact representation B is expanded only into normalized logical-unit strings.
  // Canonical source-span token objects are reconstructed only for units that actually match.
  for(const u of base)u._stream=buildStream(u);
  for(const u of complement)u._stream=buildStream(u);
  for(const u of complete)u._stream=buildStream(u);
  for(const u of enrichedUnits)if(!u._stream)u._stream=buildStream(u);
  for(const [mode,units] of Object.entries(modeUnits)){
    const expected=top.reference&&top.reference[mode]&&Number(top.reference[mode].tokens),actual=units.reduce((n,u)=>n+tokenCount(u._stream),0);
    if(expected!==actual)throw new Error(`SEARCH-V2.1A ${mode} token-count mismatch`);
  }
  function searchExact(raw,options){
    const opt={mode:'enriched',volMin:0,volMax:0,jesus:false,cap:30,...(options||{})}, mode=modeUnits[opt.mode]?opt.mode:'enriched';
    const canonical=nfc(raw),p=Core.parseQuery(canonical),q=exactTerms(p.lexical);if(!q.length)return {cards:[],totalExact:0,parsed:p,exactTokens:q};
    const phrase=q.join(' '),lps=lpsFor(q),cards=new Map();
    for(const u of modeUnits[mode]){if(!unitScopeAllows(u,p,opt)||!containsPhrase(u._stream,phrase))continue;scanUnit(u,q,lps,opt,cards);}
    const all=[...cards.values()];all.sort((a,b)=>a.volume-b.volume||a.book_order-b.book_order||String(a.stable_ref).localeCompare(String(b.stable_ref))||a.primary_target.canonical_start-b.primary_target.canonical_start);
    return {cards:all,totalExact:all.length,parsed:p,exactTokens:q};
  }
  function apply(raw,options,baseResult){
    const opt={mode:'enriched',volMin:0,volMax:0,jesus:false,cap:30,...(options||{})},ex=searchExact(raw,opt),byId=new Map();
    for(const c of ex.cards){if(!byId.has(c.id))byId.set(c.id,c);}
    const used=new Set(),exactExisting=[],other=[];
    for(const r0 of (baseResult.results||[])){
      const r={...r0},c=byId.get(r.id);
      if(c){Object.assign(r,{matchType:'exact',exact_v21:true,logical_unit_id:c.logical_unit_id,book_order:c.book_order,match_parts:c.match_parts,exact_matches:c.exact_matches,match_count:c.match_count,primary_target:c.primary_target,exact_match_text:c.exact_match_text});used.add(c.logical_unit_id+'|'+c._primary_doc_index);exactExisting.push(r);}
      else {if(r.matchType==='exact')r.matchType='words';other.push(r);}
    }
    const added=[];for(const c of ex.cards){const k=c.logical_unit_id+'|'+c._primary_doc_index;if(!used.has(k))added.push(c);}
    const cap=Math.max(1,Number(opt.cap||30));const results=exactExisting.concat(added,other).slice(0,cap).map(r=>{if(r&&Object.prototype.hasOwnProperty.call(r,'_primary_doc_index')){const x={...r};delete x._primary_doc_index;return x;}return r;});
    const counts={...(baseResult.matchCounts||{})};counts.exact=ex.totalExact;
    return {...baseResult,results,totalMatches:Math.max(Number(baseResult.totalMatches||0),ex.totalExact),matchCounts:counts,exactTruth:{schema:'ldc-search-v21-exact-result-r1',totalExact:ex.totalExact,normalizer:EXPECTED_NORMALIZER,sourceMode:opt.mode,queryTokens:ex.exactTokens.length}};
  }
  const unitMaps={aflp:new Map(base.map(u=>[u.id,u])),additions:new Map(complement.map(u=>[u.id,u])),enriched:new Map(enrichedUnits.map(u=>[u.id,u]))};
  function verifyUnitQuery(mode,logicalUnitId,raw){const u=unitMaps[mode]&&unitMaps[mode].get(logicalUnitId);if(!u)return false;const q=exactTerms(raw);return !!q.length&&containsPhrase(u._stream,q.join(' '));}
  function exactInUnit(mode,logicalUnitId,raw){const u=unitMaps[mode]&&unitMaps[mode].get(logicalUnitId);if(!u)return [];const q=exactTerms(raw);if(!q.length)return [];const cards=new Map();scanUnit(u,q,lpsFor(q),{jesus:false},cards);return [...cards.values()].map(c=>{const x={...c};delete x._primary_doc_index;return x;});}
  // Read-only V2.2 bridge. It exposes the already-governed V2.1A visible logical-unit
  // streams and reconstructs canonical token spans lazily, so Formulation proche does
  // not duplicate the corpus or invent a second textual authority.
  const nearUnits={};
  for(const [mode,units] of Object.entries(modeUnits))nearUnits[mode]=Object.freeze(units.map(u=>Object.freeze({id:u.id,entry_id:u.entry_id,volume:u.volume,book_order:u.book_order,date_iso:u.date_iso,supplement_id:u.supplement_id||null,stream:u._stream})));
  const nearAuthority=Object.freeze({
    units(mode){return nearUnits[mode]||nearUnits.enriched;},
    tokens(mode,logicalUnitId){const u=unitMaps[mode]&&unitMaps[mode].get(logicalUnitId);if(!u)return[];const out=[];let atom_index=0;for(const a of u.atoms||[]){emitAtom(a,t=>out.push({...t,atom_index}));atom_index++;}return out;},
    visibleText(parts){return exactVisibleText(parts||[]);},
    touchesJesus(tokens){return (tokens||[]).some(t=>Number.isInteger(t.di)&&bitHas(bits,t.di));}
  });
  return Object.freeze({searchExact,apply,verifyUnitQuery,exactInUnit,nearAuthority,stats:{baseUnits:base.length,complementUnits:complement.length,enrichedUnits:enrichedUnits.length,lexicalOps:lexOps.size}});
}
return Object.freeze({VERSION,createExactLayer,exactTerms});
});
