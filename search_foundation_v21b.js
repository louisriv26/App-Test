/* LDC SEARCH-V2.1B FOUNDATION — completeness/order/state contracts.
   Does NOT alter BM25 scoring or exact-text authority. */
(function(root,factory){
  const core=(root&&root.LDCSearchV2)||(typeof require==='function'?require('./search_engine_v2.js'):null);
  const api=factory(core);
  if(typeof module==='object'&&module.exports)module.exports=api;
  if(root)root.LDCSearchFoundationV21B=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(Core){
'use strict';
if(!Core)throw new Error('SEARCH-V2.1B requires SEARCH-V2 core');
const VERSION='ldc-search-v21b-foundation-r1';
const VALID_MODES=new Set(['aflp','additions','enriched']);
const VALID_ORDERS=new Set(['book','relevance']);
const VALID_LANES=new Set(['exact','words','partial']);
const MONTHS=['','janvier','fevrier','mars','avril','mai','juin','juillet','aout','septembre','octobre','novembre','decembre'];
const MONTH_PATTERN='janvier|f[ée]vrier|mars|avril|mai|juin|juillet|ao[uû]t|septembre|octobre|novembre|d[ée]cembre';
const ROMAN={I:1,II:2,III:3,IV:4,V:5,VI:6,VII:7,VIII:8,IX:9,X:10,XI:11,XII:12,XIII:13,XIV:14,XV:15,XVI:16,XVII:17,XVIII:18,XIX:19,XX:20,XXI:21,XXII:22,XXIII:23,XXIV:24,XXV:25,XXVI:26,XXVII:27,XXVIII:28,XXIX:29,XXX:30,XXXI:31,XXXII:32,XXXIII:33,XXXIV:34,XXXV:35,XXXVI:36};
function nfc(s){return String(s==null?'':s).normalize('NFC');}
function validDate(y,m,d){if(y<1800||y>2099||m<1||m>12||d<1||d>31)return false;const x=new Date(Date.UTC(y,m-1,d));return x.getUTCFullYear()===y&&x.getUTCMonth()===m-1&&x.getUTCDate()===d;}
function replaceSpan(s,m,repl){return s.slice(0,m.index)+repl+s.slice(m.index+m[0].length);}
function preprocessQuery(raw){
  const original=nfc(raw),chips=[];let s=original,error=null;
  // Stable references are structural atoms. Shield them before date/Tome parsing so
  // embedded identifiers such as .1901-01-30. can never be rewritten as a user date.
  const refm=s.match(/\b(?:LDC|LDCSUP)\.[A-Za-z0-9._:-]+/i);let shieldedRef=null;
  if(refm){shieldedRef=refm[0].replace(/[.,;:!?]+$/,'');s=replaceSpan(s,refm,'__LDCREF0__');}
  // Tome locators: normalize leading zeros, support I..XXXVI, fail closed otherwise.
  const tm=s.match(/\btome\s+([^\s,;]+)/i);
  if(tm){let token=tm[1].replace(/[.,;:!?]+$/,'').toUpperCase(),v=null;if(/^\d+$/.test(token))v=Number(token);else if(Object.prototype.hasOwnProperty.call(ROMAN,token))v=ROMAN[token];
    if(!Number.isInteger(v)||v<1||v>36)error={code:'INVALID_TOME',message:'Tome invalide. Indiquez un numéro de 1 à 36.'};
    else{s=replaceSpan(s,tm,`Tome ${v}`);chips.push({kind:'tome',label:`Tome ${v}`,value:v});}
  }
  // Numeric/ISO dates. A clearly date-shaped but impossible date fails closed.
  if(!error){
    let dm=s.match(/\b((?:18|19|20)\d{2})[-/](\d{1,2})[-/](\d{1,2})\b/);
    if(dm){const y=Number(dm[1]),m=Number(dm[2]),d=Number(dm[3]);if(!validDate(y,m,d))error={code:'INVALID_DATE',message:'Date invalide. Vérifiez le jour, le mois et l’année.'};else{s=replaceSpan(s,dm,`${d} ${MONTHS[m]} ${y}`);chips.push({kind:'date',label:`${String(d).padStart(2,'0')}/${String(m).padStart(2,'0')}/${y}`,value:`${y}-${String(m).padStart(2,'0')}-${String(d).padStart(2,'0')}`});}}
    else{
      dm=s.match(/\b(\d{1,2})[/-](\d{1,2})[/-]((?:18|19|20)\d{2})\b/);
      if(dm){const d=Number(dm[1]),m=Number(dm[2]),y=Number(dm[3]);if(!validDate(y,m,d))error={code:'INVALID_DATE',message:'Date invalide. Vérifiez le jour, le mois et l’année.'};else{s=replaceSpan(s,dm,`${d} ${MONTHS[m]} ${y}`);chips.push({kind:'date',label:`${String(d).padStart(2,'0')}/${String(m).padStart(2,'0')}/${y}`,value:`${y}-${String(m).padStart(2,'0')}-${String(d).padStart(2,'0')}`});}}
      else{
        dm=s.match(new RegExp(`\\b(0?\\d|[12]\\d|3[01])\\s+(${MONTH_PATTERN})\\s+((?:18|19|20)\\d{2})\\b`,'i'));
        if(dm){const d=Number(dm[1]),m=MONTHS.indexOf(Core.normalise(dm[2])),y=Number(dm[3]);if(!validDate(y,m,d))error={code:'INVALID_DATE',message:'Date invalide. Vérifiez le jour, le mois et l’année.'};else{s=replaceSpan(s,dm,`${d} ${MONTHS[m]} ${y}`);chips.push({kind:'date',label:`${String(d).padStart(2,'0')}/${String(m).padStart(2,'0')}/${y}`,value:`${y}-${String(m).padStart(2,'0')}-${String(d).padStart(2,'0')}`});}}
      }
    }
  }
  if(shieldedRef)s=s.replace('__LDCREF0__',shieldedRef);
  return {raw:original,sanitized:s,error,chips};
}
function atomDi(a){return Number.isInteger(a)?a:(Array.isArray(a)?a[0]:-1);}
function parseBase(row,overrides){return {id:'P:'+row[0],entry_id:row[0],volume:Number(row[1]),book_order:Number(row[2]||0),atoms:(overrides&&overrides.get(row[0]))||row[4],supplement_id:null};}
function parseSupp(row){return {id:String(row[0]),entry_id:String(row[1]),volume:Number(row[2]),book_order:Number(row[3]||0),supplement_id:String(row[5]||''),atoms:row[6]};}
function createOrderMaps(top,documents){
  const overrides=new Map((top.enriched_overrides||[]).map(r=>[r[0],r[1]]));
  const base=(top.base_units||[]).map(r=>parseBase(r,null));
  const enriched=base.map((u,i)=>parseBase(top.base_units[i],overrides)).concat((top.complete_units||[]).map(parseSupp)).sort((a,b)=>a.volume-b.volume||a.book_order-b.book_order||a.id.localeCompare(b.id));
  const additions=(top.complement_units||[]).map(parseSupp).sort((a,b)=>a.volume-b.volume||a.book_order-b.book_order||a.id.localeCompare(b.id));
  const sets={aflp:base,additions,enriched},out={aflp:new Map(),additions:new Map(),enriched:new Map()},suppByDoc=new Map();
  for(const row of top.complement_units||[]){const sid=String(row[5]||'');for(const a of row[6]||[]){const di=atomDi(a);if(di>=0&&!suppByDoc.has(di))suppByDoc.set(di,sid);}}
  for(const [mode,units] of Object.entries(sets)){
    let unitOrdinal=0;for(const u of units){let atomOrdinal=0;for(const a of u.atoms||[]){const di=atomDi(a);if(di>=0&&!out[mode].has(di))out[mode].set(di,[u.volume,u.book_order,unitOrdinal,atomOrdinal]);atomOrdinal++;}unitOrdinal++;}
  }
  const idToIndex=new Map();documents.forEach((d,i)=>idToIndex.set(String(d[0]),i));
  return {order:out,idToIndex,suppByDoc};
}
function levBounded(a,b,max){if(Math.abs(a.length-b.length)>max)return max+1;let prev=Array(b.length+1);for(let j=0;j<=b.length;j++)prev[j]=j;for(let i=1;i<=a.length;i++){const cur=[i];let rowMin=i;for(let j=1;j<=b.length;j++){const v=Math.min(prev[j]+1,cur[j-1]+1,prev[j-1]+(a[i-1]===b[j-1]?0:1));cur[j]=v;if(v<rowMin)rowMin=v;}if(rowMin>max)return max+1;prev=cur;}return prev[b.length];}
function createFoundation(payload){
  const {lexical,exact,documents,entries,topology,index}=payload;if(!lexical||!exact||!documents||!entries||!topology||!index)throw new Error('SEARCH-V2.1B incomplete foundation payload');
  const maps=createOrderMaps(topology,documents),vocab=Object.keys(index.terms||{}),vocabSet=new Set(vocab);
  function orderTuple(row,mode){const di=maps.idToIndex.get(String(row.id||''));const t=Number.isInteger(di)?maps.order[mode].get(di):null;return t||[Number(row.volume)||99,Number(row.book_order)||1e12,1e12,1e12];}
  function compareBook(a,b,mode){const x=orderTuple(a,mode),y=orderTuple(b,mode);for(let i=0;i<4;i++)if(x[i]!==y[i])return x[i]-y[i];return String(a.stable_ref||a.id||'').localeCompare(String(b.stable_ref||b.id||''));}
  function surfaceTerm(norm){for(const d of documents){const txt=String(d[5]||'');for(const m of txt.matchAll(/[A-Za-zÀ-ÖØ-öø-ÿŒœÆæ]+/g)){if(Core.normalise(m[0])===norm)return m[0].toLowerCase();}}return norm;}
  function suggestionsFor(parsed,hasStrong){if(hasStrong)return[];const out=[];for(const t of Core.normalise(parsed.lexical||'').split(' ').filter(Boolean)){if(t.length<4||vocabSet.has(t))continue;let best=null,bestD=99;const max=t.length<=5?1:2;for(const v of vocab){if(v[0]!==t[0]||Math.abs(v.length-t.length)>max)continue;const d=levBounded(t,v,max);if(d<bestD){bestD=d;best=v;if(d===1&&max===1)break;}}if(best&&bestD<=max)out.push({from:t,to:surfaceTerm(best),distance:bestD});if(out.length>=2)break;}return out;}
  function semanticTarget(row,mode){
    if(row.primary_target)return row.primary_target;
    const ref=String(row.stable_ref||'');const paraRef=/\.(?:P|p)\d+\.?$/.test(ref);
    const di=maps.idToIndex.get(String(row.id||'')),sid=Number.isInteger(di)?maps.suppByDoc.get(di):null;
    if(row.matchType==='metadata'){
      if(row._metaKind==='Référence'&&paraRef)return {target_kind:'EXACT_SPAN',id:row.id,entry_id:row.entry_id,volume:row.volume,stable_ref:row.stable_ref,canonical_start:0,canonical_end:null,supplement_id:sid||null};
      if(mode==='additions'&&(sid||row.is_supplement))return {target_kind:'SUPPLEMENT_SPAN',id:row.id,entry_id:row.entry_id,volume:row.volume,supplement_id:sid||null};
      return {target_kind:'ENTRY_START',id:null,entry_id:row.entry_id,volume:row.volume,supplement_id:null};
    }
    return {target_kind:'PARAGRAPH',id:row.id,entry_id:row.entry_id,volume:row.volume,stable_ref:row.stable_ref,supplement_id:sid||null};
  }
  function search(raw,options){
    const pre=preprocessQuery(raw),opt={mode:'enriched',volMin:0,volMax:0,jesus:false,page:1,pageSize:30,metadataPage:1,metadataPageSize:10,order:null,resultLane:null,...(options||{})};
    if(!VALID_MODES.has(opt.mode))throw new Error('SEARCH-V2.1B invalid source mode');
    if(pre.error)return {results:[],metadata:[],metadataTotalMatches:0,totalMatches:0,totalBodyMatches:0,matchCounts:{exact:0,words:0,partial:0},parsed:{raw:pre.raw,lexical:'',tokens:[]},structuralError:pre.error,structuralChips:pre.chips,foundation:{schema:'ldc-search-v21b-result-r1',mode:opt.mode}};
    // Complete populations are assembled before sorting/paging. 100000 exceeds the governed 74,522-doc universe.
    const fullOpt={...opt,cap:100000,metadataCap:100000,metadataOffset:0};
    const base=lexical.search(pre.sanitized,fullOpt),applied=exact.apply(pre.sanitized,fullOpt,base),all=(applied.results||[]).map((r,i)=>({...r,_relevanceRank:i,primary_target:semanticTarget(r,opt.mode)}));
    const lanes={exact:[],words:[],partial:[]};for(const r of all)(lanes[r.matchType]||lanes.partial).push(r);
    const counts={exact:lanes.exact.length,words:lanes.words.length,partial:lanes.partial.length};
    const exactTokens=applied.exactTruth&&Number(applied.exactTruth.queryTokens)||0;
    let lane=VALID_LANES.has(opt.resultLane)?opt.resultLane:(counts.exact?'exact':(counts.words?'words':'partial'));
    const indexedTokens=(applied.parsed&&applied.parsed.tokens&&applied.parsed.tokens.length)||0;
    let order=VALID_ORDERS.has(opt.order)?opt.order:((exactTokens===1||indexedTokens===0)?'book':'relevance');
    const selected=lanes[lane].slice();
    if(order==='book')selected.sort((a,b)=>compareBook(a,b,opt.mode)||a._relevanceRank-b._relevanceRank);else selected.sort((a,b)=>a._relevanceRank-b._relevanceRank);
    const pageSize=Math.max(1,Math.min(100,Number(opt.pageSize)||30)),pageCount=Math.max(1,Math.ceil(selected.length/pageSize)),page=Math.max(1,Math.min(pageCount,Number(opt.page)||1));
    const clean=r=>{const x={...r};delete x._relevanceRank;return x;};
    const results=selected.slice((page-1)*pageSize,page*pageSize).map(clean);
    const metaAll=(base.metadata||[]).map((r,i)=>({...r,_relevanceRank:i,primary_target:semanticTarget(r,opt.mode)}));
    const mpSize=Math.max(1,Math.min(50,Number(opt.metadataPageSize)||10)),metaCount=Number(base.metadataTotalMatches||metaAll.length),metaPages=Math.max(1,Math.ceil(metaCount/mpSize)),metaPage=Math.max(1,Math.min(metaPages,Number(opt.metadataPage)||1));
    // base.metadata is complete because metadataCap=100000; slice only after deterministic engine ranking.
    const metadata=metaAll.slice((metaPage-1)*mpSize,metaPage*mpSize).map(clean);
    const suggestions=suggestionsFor(applied.parsed||base.parsed||{},counts.exact>0||counts.words>0);
    return {...applied,results,metadata,metadataTotalMatches:metaCount,totalMatches:selected.length,totalBodyMatches:counts.exact+counts.words+counts.partial,matchCounts:counts,parsed:applied.parsed||base.parsed,structuralChips:pre.chips,suggestions,foundation:{schema:'ldc-search-v21b-result-r1',version:VERSION,mode:opt.mode,lane,order,page,pageSize,pageCount,metadataPage:metaPage,metadataPageSize:mpSize,metadataPageCount:metaPages,defaultOrderReason:VALID_ORDERS.has(opt.order)?'explicit':(exactTokens===1?'one_token_book_order':(indexedTokens===0?'no_bm25_terms_book_order':'multi_token_relevance'))}};
  }
  return Object.freeze({search,preprocessQuery,stats:{documents:documents.length,vocabulary:vocab.length}});
}
return Object.freeze({VERSION,preprocessQuery,createFoundation});
});
