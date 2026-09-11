/* LDC SEARCH-V2 CORE — deterministic lexical retrieval engine.
   Browser/Worker: globalThis.LDCSearchV2. Node: module.exports. */
(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  if(root)root.LDCSearchV2=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(){
'use strict';
const VERSION='ldc-search-v2-engine-v1.1';
const MONTHS={janvier:1,fevrier:2,mars:3,avril:4,mai:5,juin:6,juillet:7,aout:8,septembre:9,octobre:10,novembre:11,decembre:12};
function normalise(input){
  return String(input==null?'':input).toLowerCase()
    .replace(/[éèêë]/g,'e').replace(/[àâ]/g,'a').replace(/[îï]/g,'i')
    .replace(/[ôö]/g,'o').replace(/[ùûü]/g,'u').replace(/ç/g,'c')
    .replace(/œ/g,'oe').replace(/æ/g,'ae')
    .replace(/[\u00A0\u202F]/g,' ').replace(/[‘’‚‛]/g,' ').replace(/[-–—]/g,' ')
    .replace(/[^A-Za-z0-9\s]/g,' ').replace(/\s+/g,' ').trim();
}
function terms(input,minLength=3){return normalise(input).split(' ').filter(Boolean).filter(t=>t.length>=minLength);}
function unique(xs){return [...new Set(xs)];}
function parseQuery(raw){
  const original=String(raw||''); let volume=null,year=null,date=null,ref=null;
  // Remove an exact LDC/LDCSUP reference before parsing Tome/date/year so digits
  // embedded in the reference cannot leak into independent structural filters.
  let rm=original.match(/\b(?:LDC|LDCSUP)\.[A-Za-z0-9._-]+/i);
  if(rm)ref=rm[0].toUpperCase();
  let q=normalise((rm?original.slice(0,rm.index)+' '+original.slice(rm.index+rm[0].length):original).replace(/\(\s*\d+\s*\)\s*$/,''));
  let m=q.match(/\btome\s+([1-9]|[12][0-9]|3[0-6])\b/);
  if(m){volume=Number(m[1]);q=(q.slice(0,m.index)+q.slice(m.index+m[0].length)).replace(/\s+/g,' ').trim();}
  for(const [month,mi] of Object.entries(MONTHS)){
    const rx=new RegExp(`\\b(1er|[1-9]|[12]\\d|3[01])\\s+${month}\\s+((?:18|19|20)\\d{2})\\b`);const dm=q.match(rx);
    if(dm){const day=dm[1]==='1er'?1:Number(dm[1]);year=Number(dm[2]);date=`${String(year).padStart(4,'0')}-${String(mi).padStart(2,'0')}-${String(day).padStart(2,'0')}`;q=(q.slice(0,dm.index)+q.slice(dm.index+dm[0].length)).replace(/\s+/g,' ').trim();break;}
  }
  // Month/year is a month-prefix constraint (YYYY-MM), matching all entries in that month.
  if(!date){for(const [month,mi] of Object.entries(MONTHS)){const rx=new RegExp(`\\b${month}\\s+((?:18|19|20)\\d{2})\\b`);const mm=q.match(rx);if(mm){year=Number(mm[1]);date=`${String(year).padStart(4,'0')}-${String(mi).padStart(2,'0')}`;q=(q.slice(0,mm.index)+q.slice(mm.index+mm[0].length)).replace(/\s+/g,' ').trim();break;}}}
  if(!date){m=q.match(/\b((?:18|19|20)\d{2})\b/);if(m){year=Number(m[1]);q=(q.slice(0,m.index)+q.slice(m.index+m[0].length)).replace(/\s+/g,' ').trim();}}
  return {raw:original,lexical:q,tokens:unique(terms(q,3)),volume,year,date,ref};
}
function b64bytes(s){
  if(typeof Buffer!=='undefined')return Uint8Array.from(Buffer.from(s,'base64'));
  const bin=atob(s),a=new Uint8Array(bin.length);for(let i=0;i<bin.length;i++)a[i]=bin.charCodeAt(i);return a;
}
function readVar(buf,state){let n=0,shift=0;for(;;){const b=buf[state.i++];n|=(b&127)<<shift;if(!(b&128))return n;shift+=7;}}
function decodePosting(s){const buf=b64bytes(s),st={i:0},out=[];let prev=0,first=true;while(st.i<buf.length){const delta=readVar(buf,st),tf=readVar(buf,st),di=first?delta:prev+delta;first=false;prev=di;out.push([di,tf]);}return out;}
function decodeDocLengths(s,N){const b=b64bytes(s);if(b.length!==N*2)throw new Error('SEARCH-V2 document-length array mismatch');const out=new Uint16Array(N);for(let i=0;i<N;i++)out[i]=b[i*2]|(b[i*2+1]<<8);return out;}
function bitHas(bits,i){return !!(bits[i>>3]&(1<<(i&7)));}
function phraseContains(bodyNorm,phrase){return !!phrase&&(` ${bodyNorm} `).includes(` ${phrase} `);}
function createEngine(payload){
  const index=payload.index,documents=payload.documents.documents,entries=payload.entries.entries,jf=payload.jesusFilter;
  if(index.schema!=='ldc-search-v2-index-v1'||payload.documents.schema!=='ldc-search-v2-documents-v1'||payload.entries.schema!=='ldc-search-v2-entries-v1'||jf.schema!=='ldc-search-v2-jesus-filter-v1')throw new Error('SEARCH-V2 schema mismatch');
  if(index.N!==documents.length||jf.N!==documents.length)throw new Error('SEARCH-V2 population mismatch');
  const N=index.N,dl=decodeDocLengths(index.doc_lengths_u16le_b64,N),bits=b64bytes(jf.bits_b64),postCache=new Map(),normCache=new Map(),entryDocs=Array.from({length:entries.length},()=>[]),docRefMap=new Map(),entryRefMap=new Map();
  for(let i=0;i<documents.length;i++){const d=documents[i],ei=d[1];if(entryDocs[ei])entryDocs[ei].push(i);const r=String(d[4]||'').toUpperCase();if(r){if(!docRefMap.has(r))docRefMap.set(r,[]);docRefMap.get(r).push(i);}}
  for(let ei=0;ei<entries.length;ei++){const r=String(entries[ei][1]||'').toUpperCase();if(r){if(!entryRefMap.has(r))entryRefMap.set(r,[]);entryRefMap.get(r).push(ei);}}
  const k=Number(index.bm25.k1),b=Number(index.bm25.b),avgdl=Number(index.avgdl);
  function posting(t){if(!postCache.has(t))postCache.set(t,index.terms[t]?decodePosting(index.terms[t]):[]);return postCache.get(t);}
  function docNorm(i){if(!normCache.has(i))normCache.set(i,normalise(documents[i][5]));return normCache.get(i);}
  function modeAllows(flag,mode){return mode==='aflp'?flag===0:mode==='additions'?flag===1:true;}
  function entryModeAllows(e,mode){if(mode==='aflp')return e[6]===0;if(mode==='additions')return e[6]===1||e[8]===1;return true;}
  function scopeAllows(i,d,p,opt){
    if(!modeAllows(d[3],opt.mode))return false;
    if(opt.volMin&&d[2]<opt.volMin)return false;if(opt.volMax&&d[2]>opt.volMax)return false;
    if(p.volume&&d[2]!==p.volume)return false;
    const e=entries[d[1]],iso=e[5]||'';
    if(p.date&&!iso.startsWith(p.date))return false;if(p.year&&!iso.startsWith(String(p.year)))return false;
    if(opt.jesus&&!bitHas(bits,i))return false;
    return true;
  }
  function bm25(t,tf,i){const df=Number(index.dfs[t]||0);if(!df||!tf)return 0;const idf=Math.log(1+(N-df+.5)/(df+.5));return idf*tf*(k+1)/(tf+k*(1-b+b*dl[i]/avgdl));}
  function bodySearch(p,opt){
    const qt=p.tokens;if(!qt.length)return {results:[],totalMatches:0,matchCounts:{exact:0,words:0,partial:0}};
    const candidates=new Map();
    for(const t of qt)for(const [i,tf] of posting(t)){let m=candidates.get(i);if(!m){m=new Map();candidates.set(i,m);}m.set(t,tf);}
    const rows=[],counts={exact:0,words:0,partial:0};
    for(const [i,tfs] of candidates){const d=documents[i];if(!scopeAllows(i,d,p,opt))continue;const present=qt.filter(t=>tfs.has(t));if(!present.length)continue;
      const phrase=phraseContains(docNorm(i),p.lexical);let tier,matchType;
      if(phrase){tier=3;matchType='exact';counts.exact++;}
      else if(present.length===qt.length){tier=2;matchType='words';counts.words++;}
      else{tier=1;matchType='partial';counts.partial++;}
      let score=0;for(const t of present)score+=bm25(t,tfs.get(t),i);const coverage=present.length/qt.length;
      rows.push({i,tier,coverage,score,matchType});
    }
    rows.sort((a,b)=>b.tier-a.tier||(a.tier===1?b.coverage-a.coverage:0)||b.score-a.score||a.i-b.i);
    const cap=Number(opt.cap||30);
    return {results:rows.slice(0,cap).map(r=>resultRecord(r.i,r)),totalMatches:rows.length,matchCounts:counts};
  }
  function resultRecord(i,r){const d=documents[i],e=entries[d[1]];return {id:d[0],entry_id:e[0],stable_ref:d[4],volume:d[2],title:e[3],date_display:e[4],date_iso:e[5],text:d[5],is_supplement:d[3]===1,score:r.score,matchType:r.matchType};}
  function entryHasEligible(ei,opt,p){for(const i of entryDocs[ei]||[]){const d=documents[i];if(scopeAllows(i,d,p,opt))return true;}return false;}
  function metadataSearch(p,opt){
    const rows=[]; const q=p.lexical,qt=p.tokens,structural=!!(p.volume||p.year||p.date||p.ref);
    // Exact paragraph stable-reference lookup. Paragraph refs are unique in the governed
    // SEARCH-V2 document universe and must resolve to the paragraph itself.
    if(p.ref){
      for(const i of (docRefMap.get(p.ref)||[])){const d=documents[i];if(!scopeAllows(i,d,p,opt))continue;const e=entries[d[1]];rows.push({id:d[0],entry_id:e[0],stable_ref:d[4],volume:d[2],title:e[3],date_display:e[4],date_iso:e[5],text:d[5],is_supplement:d[3]===1,score:2200,matchType:'metadata',_metaKind:'Référence'});}
      for(const ei of (entryRefMap.get(p.ref)||[])){const e=entries[ei];if(!entryModeAllows(e,opt.mode))continue;if(opt.volMin&&e[2]<opt.volMin)continue;if(opt.volMax&&e[2]>opt.volMax)continue;if(p.volume&&e[2]!==p.volume)continue;const first=findFirstVisibleDoc(ei,opt,p);if(first<0)continue;const d=documents[first];rows.push({id:d[0],entry_id:e[0],stable_ref:e[1]||d[4],volume:e[2],title:e[3],date_display:e[4],date_iso:e[5],text:d[5],is_supplement:d[3]===1,score:2000,matchType:'metadata',_metaKind:'Référence'});}
      if(rows.length){rows.sort((a,b)=>b.score-a.score||a.volume-b.volume||String(a.id).localeCompare(String(b.id)));return rows.slice(0,10);}
    }
    for(let ei=0;ei<entries.length;ei++){const e=entries[ei];if(!entryModeAllows(e,opt.mode))continue;if(opt.volMin&&e[2]<opt.volMin)continue;if(opt.volMax&&e[2]>opt.volMax)continue;if(p.volume&&e[2]!==p.volume)continue;
      const iso=e[5]||'';if(p.date&&!iso.startsWith(p.date))continue;if(p.year&&!iso.startsWith(String(p.year)))continue;
      let score=0,kind='Titre';const titleN=normalise(e[3]||''),ref=String(e[1]||'').toUpperCase();
      if(p.ref){if(ref.startsWith(p.ref))score=1800;else continue;kind='Référence';}
      else if(!q&&structural){score=p.date?1700:p.year?1600:p.volume?1500:1000;kind=p.date||p.year?'Date':'Tome';}
      else if(q){if(titleN===q)score=1400;else if(q.length>=3&&phraseContains(titleN,q))score=1200;else if(qt.length&&qt.every(t=>(` ${titleN} `).includes(` ${t} `)))score=900+qt.length;else continue;kind='Titre';}
      else continue;
      if(opt.jesus&&!entryHasEligible(ei,opt,p))continue;
      const first=findFirstVisibleDoc(ei,opt,p);if(first<0)continue;const d=documents[first];rows.push({id:d[0],entry_id:e[0],stable_ref:e[1]||d[4],volume:e[2],title:e[3],date_display:e[4],date_iso:e[5],text:d[5],is_supplement:d[3]===1,score,matchType:'metadata',_metaKind:kind});
    }
    rows.sort((a,b)=>b.score-a.score||a.volume-b.volume||String(a.entry_id).localeCompare(String(b.entry_id)));
    return rows.slice(0,10);
  }
  function findFirstVisibleDoc(ei,opt,p){for(const i of entryDocs[ei]||[]){const d=documents[i];if(scopeAllows(i,d,p,opt))return i;}return -1;}
  function search(raw,options){const opt={mode:'enriched',volMin:0,volMax:0,jesus:false,cap:30,...(options||{})};const p=parseQuery(raw);const body=bodySearch(p,opt),metadata=metadataSearch(p,opt);return {...body,metadata,parsed:p};}
  return Object.freeze({search,parseQuery,normalise,terms,stats:{N,indexVocabulary:index.vocabulary_count,indexPostings:index.posting_count}});
}
return Object.freeze({VERSION,normalise,terms,parseQuery,createEngine,decodePosting});
});
