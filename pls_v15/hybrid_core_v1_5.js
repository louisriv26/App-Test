/* LDC Par le sens V1.5 browser-ready sparse + fusion core.
   Development successor only. No corpus/model/query mutation.
   BM25 semantics mirror 09_RUN_BM25_RAW_TOP160_V1_2.py. */
(function(root,factory){const api=factory();if(typeof module==='object'&&module.exports)module.exports=api;if(root)root.LDCPLSHybridV15=api;})(typeof globalThis!=='undefined'?globalThis:this,function(){
'use strict';
const VERSION='ldc-pls-hybrid-v1.5';
const K1=1.2,B=0.75,RRF_K=60,SOURCE_DEPTH=160,OUTPUT_DEPTH=20;
function req(c,m){if(!c)throw new Error(m);}
function normalise(s){
 s=String(s||'').toLowerCase();
 const repl=[['é','e'],['è','e'],['ê','e'],['ë','e'],['à','a'],['â','a'],['î','i'],['ï','i'],['ô','o'],['ö','o'],['ù','u'],['û','u'],['ü','u'],['ç','c'],['œ','oe'],['æ','ae']];
 for(const [a,b] of repl)s=s.split(a).join(b);
 s=s.replace(/\u00a0|\u202f/g,' ').replace(/[‘’‚‛]/g,' ').replace(/[-–—]/g,' ');
 s=s.replace(/[^A-Za-z0-9\s]/g,' ').replace(/\s+/g,' ').trim();return s;
}
function terms(s){return normalise(s).split(' ').filter(t=>t&&t.length>=3);}
function bitHas(bits,i){return !!(bits&&bits[i>>3]&(1<<(i&7)));}
function refMatches(p,ref){const r=String(ref||'').trim().toUpperCase();if(!r)return true;const spans=Array.isArray(p&&p.source_spans)?p.source_spans:[];return spans.some(s=>{const x=String(s&&s.stable_ref||'').trim().toUpperCase();return x&&(x===r||x.startsWith(r+'.')||r.startsWith(x+'.'));});}
function dateMatches(p,opt){const d=String(p&&p.date_iso||'');if(opt.dateIso&&d!==String(opt.dateIso))return false;if(opt.year){const y=String(Number(opt.year));if(!/^\d{4}/.test(d)||d.slice(0,4)!==y)return false;}return true;}
function rowAllowed(p,opt,row,jesusBits){if(opt.sourceMode&&String(p.mode)!==String(opt.sourceMode))return false;if(opt.volMin&&+p.volume<+opt.volMin)return false;if(opt.volMax&&+p.volume>+opt.volMax)return false;if(!dateMatches(p,opt))return false;if(opt.stableRef&&!refMatches(p,opt.stableRef))return false;if(opt.jesus){req(jesusBits instanceof Uint8Array,'HYBRID_JESUS_MASK_REQUIRED');if(!bitHas(jesusBits,row))return false;}return true;}
function buildBm25(passages,jesusBits=null){
 req(Array.isArray(passages)&&passages.length,'HYBRID_PASSAGES_REQUIRED');
 const N=passages.length,dl=new Int32Array(N),tmp=new Map();let total=0;
 for(let i=0;i<N;i++){
  const ts=terms(passages[i]&&passages[i].text);dl[i]=ts.length;total+=ts.length;
  const c=new Map();for(const t of ts)c.set(t,(c.get(t)||0)+1);
  for(const [t,tf] of c){let a=tmp.get(t);if(!a){a=[];tmp.set(t,a);}a.push(i,tf);}
 }
 const postings=new Map();for(const [t,a] of tmp){const n=a.length/2,ids=new Int32Array(n),tfs=new Float32Array(n);for(let j=0;j<n;j++){ids[j]=a[j*2];tfs[j]=a[j*2+1];}postings.set(t,{ids,tfs});}
 tmp.clear();return Object.freeze({version:VERSION,passages,N,dl,avgdl:total/N,postings,vocab:postings.size,jesusBits});
}
function bm25Search(index,qtext,options={}){
 const opt={sourceMode:null,volMin:0,volMax:0,dateIso:null,year:0,stableRef:null,jesus:false,maxCandidates:SOURCE_DEPTH,...options};
 const scores=new Float32Array(index.N);const q=[...new Set(terms(qtext))];
 for(const t of q){const p=index.postings.get(t);if(!p)continue;const df=p.ids.length,idf=Math.log(1+(index.N-df+.5)/(df+.5));for(let j=0;j<df;j++){const i=p.ids[j];if(!rowAllowed(index.passages[i],opt,i,index.jesusBits))continue;const tf=p.tfs[j],den=tf+K1*(1-B+B*index.dl[i]/index.avgdl);scores[i]=Math.fround(scores[i]+Math.fround(idf*tf*(K1+1)/den));}}
 const rows=[];for(let i=0;i<index.N;i++)if(scores[i]>0&&rowAllowed(index.passages[i],opt,i,index.jesusBits))rows.push(i);
 rows.sort((a,b)=>scores[b]-scores[a]||a-b);const top=rows.slice(0,Math.max(1,Math.min(SOURCE_DEPTH,+opt.maxCandidates||SOURCE_DEPTH)));
 const results=top.map((i,k)=>Object.assign({},index.passages[i],{_row:i,bm25_score:scores[i],bm25_rank:k+1}));
 return {schema_version:'LDC_PLS_BROWSER_BM25_RAW_TOP160_V1_5',source_mode:opt.sourceMode||null,chunk_policy_id:'96-72',eligible_rows:index.N,positive_score_candidates:rows.length,results};
}
function uniqueEntryRows(rows){const u=[],seen=new Set();for(const row of rows||[]){const eid=row&& (row.entry_id||row.id);if(!eid||seen.has(String(eid)))continue;seen.add(String(eid));u.push({entry_rank:u.length+1,entry_id:String(eid),row});}return u;}
function fuse(denseCandidates,bm25Results,options={}){
 const maxResults=Math.max(1,Math.min(OUTPUT_DEPTH,+options.maxResults||OUTPUT_DEPTH));const D=uniqueEntryRows(denseCandidates),B=uniqueEntryRows(bm25Results),scores=new Map(),prov=new Map(),ex=new Map();
 for(const [channel,rows] of [['dense_96_72',D],['bm25_96_72',B]])for(const x of rows){scores.set(x.entry_id,(scores.get(x.entry_id)||0)+1/(RRF_K+x.entry_rank));if(!prov.has(x.entry_id))prov.set(x.entry_id,{});prov.get(x.entry_id)[channel]=x.entry_rank;if(!ex.has(x.entry_id))ex.set(x.entry_id,x.row);}
 const ids=[...scores.keys()].sort((a,b)=>scores.get(b)-scores.get(a)||(a<b?-1:(a>b?1:0))); // Python-compatible code-point tie-break for ASCII IDs
 return ids.slice(0,maxResults).map((eid,i)=>{const r=ex.get(eid);return {rank:i+1,entry_id:eid,rrf60_score:scores.get(eid),source_ranks:prov.get(eid),volume:r.volume,date:r.date,title:r.title,text:r.text,passage_id:r.passage_id||null};});
}
return Object.freeze({VERSION,K1,B,RRF_K,SOURCE_DEPTH,OUTPUT_DEPTH,normalise,terms,buildBm25,bm25Search,uniqueEntryRows,fuse});
});
